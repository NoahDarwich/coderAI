import pandas as pd

import os
import re
import json

from openai import OpenAI



class ExtractInfoResponses:

    def __init__(self, config_file="jr_assistants_config.py"):

        self.client = OpenAI(api_key=os.getenv("JR_API_KEY"))
        with open(config_file, "r", encoding="utf-8") as f:
            config = f.read()
            self.configs = eval(config)

    def get_info(self, event: str, key: str, file_search: bool = False, file_id: str = None, df_str: str = None, max_retries: int = 3):

        cfg = self.configs.get(key)
        if not cfg:
            raise KeyError(f"No config found for '{key}'")

        # Retry logic for API calls
        for attempt in range(max_retries):
            try:
                # If caller provided a file id for file-search, pass it via tools.file_search.file_ids
                if key == "duplicate_checker" and file_search:
                    if file_id:
                        response = self.client.responses.create(
                            model=cfg["model"],
                            input=[
                                {"role": "system", "content": cfg["system_prompt"]},
                                {"role": "user", "content": event}
                            ],
                            temperature=cfg["temperature"],
                            top_p=cfg["top_p"],
                            tools=[{"type": "file_search", "file_ids": [file_id]}],
                        )
                    else:
                        # fallback: include small table/string in the prompt (string or JSON)
                        prompt_content = event
                        if df_str:
                            prompt_content = f"{event}\n\nData:\n{df_str}"
                        response = self.client.responses.create(
                            model=cfg["model"],
                            input=[
                                {"role": "system", "content": cfg["system_prompt"]},
                                {"role": "user", "content": prompt_content}
                            ],
                            temperature=cfg["temperature"],
                            top_p=cfg["top_p"],
                        )

                else:
                    response = self.client.responses.create(
                        model=cfg["model"],
                        input=[
                            {"role": "system", "content": cfg["system_prompt"]},
                            {"role": "user", "content": event}
                        ],
                        temperature=cfg["temperature"],
                        top_p=cfg["top_p"],
                    )

                return response.output_text.strip()

            except Exception as e:
                if attempt < max_retries - 1:
                    print(f"API call failed (attempt {attempt + 1}/{max_retries}): {e}. Retrying...")
                    time.sleep(2 ** attempt)  # Exponential backoff
                else:
                    print(f"API call failed after {max_retries} attempts: {e}")
                    return None


    def clean_response(self, response):
        if response is None:
            return None

        cleaned_response = re.sub(r'(\{|\[)\s+', r'\1', response).replace("\n", "").replace("```json", "").replace("```", "")
        cleaned_response = cleaned_response.replace("True", "true").replace("False", "false")
        try:
            cleaned_response = json.loads(cleaned_response)
        except Exception as e:
            print(f"Error parsing response: {cleaned_response[:200]}... Error: {e}")
            return None

        return cleaned_response


    def add_columns_to_df(self, df, columns):

        for col in columns:

            for i, event in df.iterrows():

                if col == "date_extractor":
                    response = self.get_info(event['text'] + " \n Article date: " + event['date'][:10], col)

                else:
                    response = self.get_info(event['text'], col)

                cleaned_response = self.clean_response(response)

                # Check if cleaned_response is None or not a dictionary
                if not cleaned_response:
                    print(f"Skipping row {i}, column {col}: No valid response")
                    continue

                # CRITICAL FIX: Check if cleaned_response is a dictionary before calling .items()
                if not isinstance(cleaned_response, dict):
                    print(f"Skipping row {i}, column {col}: Response is not a dictionary (type: {type(cleaned_response).__name__})")
                    print(f"Response value: {cleaned_response}")
                    continue

                for k, v in cleaned_response.items():

                    if isinstance(v, list):
                        response_values = " ,".join(str(j) for j in v)
                        df.at[i, k] = response_values

                    elif isinstance(v, dict):
                        for sub_k, sub_v in v.items():
                            df.at[i, sub_k] = sub_v

                    else:
                        df.at[i, k] = v

                print('done', i, col)


        return df




    def extract_events(self, df):

        processed_rows = []

        for i, row in df.iterrows():
            print(f"Processing row {i}/{len(df)}")

            response = self.get_info(row['text'], "event_extractor")
            cleaned_response = self.clean_response(response)
            print(cleaned_response)

            if not cleaned_response:
                print(f"Skipping row {i}: No valid response from event_extractor")
                continue

            if isinstance(cleaned_response, dict) and 'events' in cleaned_response:
                if isinstance(cleaned_response['events'], list):

                    if len(cleaned_response['events']) == 1:
                        # No event found, keep original row with 'event' column as text

                        new_row = row.copy()
                        new_row['event'] = row['text']
                        new_row['event_id'] = new_row['article_id'] + "_" + str(str(i).zfill(4))

                        new_row = self.add_columns_to_df(pd.DataFrame([new_row]), ["date_extractor", "location_extractor"]).iloc[0]

                        if processed_rows:
                            duplicate_check_results = self.duplicate_check(pd.DataFrame(processed_rows), new_row)
                            new_row['is_duplicate'] = duplicate_check_results.get('is_duplicate', False)
                            new_row['duplicate_events_ids'] = duplicate_check_results.get('duplicate_events_ids', '')

                        processed_rows.append(new_row)

                    else:
                        count = 0
                        for event in cleaned_response['events']:
                            # Create a new row for each event, copying other columns
                            new_row = row.copy()
                            new_row['event'] = event
                            new_row['event_id'] = new_row['article_id'] + "_" + str(str(i + count).zfill(4))
                            new_row = self.add_columns_to_df(pd.DataFrame([new_row]), ["date_extractor", "location_extractor"]).iloc[0]

                            if processed_rows:
                                duplicate_check_results = self.duplicate_check(pd.DataFrame(processed_rows), new_row)
                                new_row['is_duplicate'] = duplicate_check_results.get('is_duplicate', False)
                                new_row['duplicate_events_ids'] = duplicate_check_results.get('duplicate_events_ids', '')

                            count += 1
                            processed_rows.append(new_row)

                else:
                    print(f"Unexpected format for 'event': {cleaned_response['events']}")
            else:
                print(f"Unexpected response format: {cleaned_response}")

        if processed_rows:
            return pd.DataFrame(processed_rows)
        else:
            return df

    def combine_duplicates(self, df):
        pass

    def duplicate_check(self, df, row):

        filtered_df = df[df['date'] == row['date']]

        filtered_df = filtered_df[['event_id', 'event', 'date', 'Name_of_location', 'end_Name_of_location']]

        df_str = filtered_df.to_markdown(index=False)


        response = self.get_info(row['event'], "duplicate_checker", file_search = True, df_str = df_str)
        cleaned_response = self.clean_response(response)


        if not cleaned_response:
            return {"is_duplicate": False, "duplicate_events_ids": []}

        return cleaned_response
