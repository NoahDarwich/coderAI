import copy
import json
import os
import re
import time
from collections import defaultdict
from typing import Dict, List, Any, Optional

import pandas as pd
from openai import OpenAI
from psycopg2 import extras

from noai_functions import DataFrameEnhancer


class ExtractInfoResponses:

    def __init__(self, config_file=None, db_manager=None):
        """
        Initialize the event extraction and processing system

        Args:
            config_file: Path to assistants configuration file (default: src/jr_assistants_config.py)
            db_manager: Optional DatabaseManager instance for database operations
        """
        self.client = OpenAI(api_key=os.getenv("JR_API_KEY"))

        # Default config file path
        if config_file is None:
            config_file = os.path.join(os.path.dirname(__file__), "jr_assistants_config.py")

        with open(config_file, "r", encoding="utf-8") as f:
            config = f.read()
            self.configs = eval(config)

        # Database manager for persistent processing
        self.db = db_manager

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


    def add_columns_to_df(self, event, columns):

        for col in columns:

            if col in ("date_extractor", "event_type"):
                response = self.get_info(event['event'] + " \n Article date: " + event['date'][:10], col)

            else:
                response = self.get_info(event['event'], col)

            cleaned_response = self.clean_response(response)

            if not cleaned_response:
                print(f"Skipping column {col}: No valid response")
                continue

            if not isinstance(cleaned_response, dict):
                print(f"Skipping column {col}: Response is not a dictionary (type: {type(cleaned_response).__name__})")
                print(f"Response value: {cleaned_response}")
                continue

            for k, v in cleaned_response.items():

                if isinstance(v, list):
                    # Deduplicate list values while preserving order
                    # Case-insensitive deduplication for string values
                    seen = set()
                    unique_values = []
                    for item in v:
                        # Normalize for comparison (lowercase if string)
                        item_key = str(item).lower() if isinstance(item, str) else item
                        if item_key not in seen:
                            seen.add(item_key)
                            unique_values.append(item)

                    response_values = " ,".join(str(j) for j in unique_values)
                    event[k] = response_values

                elif isinstance(v, dict):
                    for sub_k, sub_v in v.items():
                        # Normalize location field keys to expected case for consistency
                        if col == "location_extractor":
                            # Map lowercase keys to expected title case
                            key_map = {
                                'governorate': 'Governorate', 'district': 'District',
                                'town': 'Town', 'neighborhood': 'Neighborhood',
                                'name_of_location': 'Name_of_location', 'government_building': 'government_building',
                                'end_governorate': 'end_Governorate', 'end_district': 'end_District',
                                'end_town': 'end_Town', 'end_neighborhood': 'end_Neighborhood',
                                'end_name_of_location': 'end_Name_of_location', 'end_government_building': 'end_government_building'
                            }
                            normalized_key = key_map.get(sub_k.lower(), sub_k)
                            event[normalized_key] = sub_v
                        else:
                            event[sub_k] = sub_v

                else:
                    event[k] = v

            # For location_extractor, create raw_extracted_location columns
            if col == "location_extractor":
                # Start location fields - check both title case and lowercase keys
                start_fields = ['Governorate', 'District', 'Town', 'Neighborhood', 'Name_of_location']
                start_values = []
                for field in start_fields:
                    # Try title case first, then lowercase (model might return either)
                    value = event.get(field) or event.get(field.lower())
                    if value and isinstance(value, str) and value.strip():
                        start_values.append(value.strip())

                # Retry location extraction if all start location fields are null
                if not start_values:
                    print("  Retrying location extraction (all fields null)...")
                    retry_response = self.get_info(event['event'], col)
                    retry_cleaned = self.clean_response(retry_response)
                    if retry_cleaned and isinstance(retry_cleaned, dict):
                        # Map lowercase keys to expected title case
                        key_map = {
                            'governorate': 'Governorate', 'district': 'District',
                            'town': 'Town', 'neighborhood': 'Neighborhood',
                            'name_of_location': 'Name_of_location', 'government_building': 'government_building',
                            'end_governorate': 'end_Governorate', 'end_district': 'end_District',
                            'end_town': 'end_Town', 'end_neighborhood': 'end_Neighborhood',
                            'end_name_of_location': 'end_Name_of_location', 'end_government_building': 'end_government_building'
                        }
                        for k, v in retry_cleaned.items():
                            if isinstance(v, dict):
                                for sub_k, sub_v in v.items():
                                    normalized_key = key_map.get(sub_k.lower(), sub_k)
                                    event[normalized_key] = sub_v
                            else:
                                event[k] = v
                        # Recompute start_values after retry
                        start_values = []
                        for field in start_fields:
                            value = event.get(field) or event.get(field.lower())
                            if value and isinstance(value, str) and value.strip():
                                start_values.append(value.strip())

                event['raw_extracted_location'] = ', '.join(start_values) if start_values else None

                # End location fields - check both title case and lowercase keys
                end_fields = ['end_Governorate', 'end_District', 'end_Town', 'end_Neighborhood', 'end_Name_of_location']
                end_values = []
                for field in end_fields:
                    value = event.get(field) or event.get(field.lower())
                    if value and isinstance(value, str) and value.strip():
                        end_values.append(value.strip())
                event['raw_extracted_end_location'] = ', '.join(end_values) if end_values else None

            print('done', col)

        return event




    def extract_events(self, text: str):

        response = self.get_info(text, "event_extractor")
        cleaned_response = self.clean_response(response)
        print(cleaned_response)

        if not cleaned_response:
            print(f"No valid response from event_extractor")
            return [text]  # Return full text as single event

        # Extract events list
        if isinstance(cleaned_response, dict) and 'events' in cleaned_response:
            if isinstance(cleaned_response['events'], list):
                events = cleaned_response['events']
                # If only one event (means no events found), use full text
                if len(events) == 1:
                    return [text]
                return events
            else:
                print(f"Unexpected format for 'events': {cleaned_response['events']}")
                return [text]
        else:
            print(f"Unexpected response format: {cleaned_response}")
            return [text]

    def combine_duplicates(self, df):

        """
        Combines duplicate events into universal merged events.

        Process:
        1. Identifies duplicates from is_duplicate column
        2. Creates universal narrative using OpenAI for each duplicate cluster
        3. Tags merged event and source events appropriately
        4. Handles planned events by setting took_place=True if any source was planned
        """
        # Initialize new columns if they don't exist
        if 'merged_event' not in df.columns:
            df['merged_event'] = False
        if 'merged_from_ids' not in df.columns:
            df['merged_from_ids'] = None
        if 'merged_to' not in df.columns:
            df['merged_to'] = None
        if 'took_place' not in df.columns:
            df['took_place'] = None

        # Build clusters using Union-Find (Disjoint Set Union)
        # This properly handles transitive relationships: if A→B and B→C, then A,B,C are one cluster
        parent = {}

        def find(x):
            """Find root of set with path compression"""
            if x not in parent:
                parent[x] = x
            if parent[x] != x:
                parent[x] = find(parent[x])
            return parent[x]

        def union(x, y):
            """Union two sets"""
            px, py = find(x), find(y)
            if px != py:
                parent[px] = py

        # First pass: build unions from all duplicate relationships
        for idx, row in df.iterrows():
            if not row.get('is_duplicate', False):
                continue

            event_id = row.get('event_id') if 'event_id' in df.columns else idx
            duplicate_ids = row.get('duplicate_events_ids', [])

            if not duplicate_ids or (isinstance(duplicate_ids, str) and not duplicate_ids.strip()):
                continue

            # Convert to list if needed
            if isinstance(duplicate_ids, str):
                try:
                    duplicate_ids = eval(duplicate_ids)
                except:
                    continue

            if isinstance(duplicate_ids, list):
                for dup_id in duplicate_ids:
                    union(event_id, dup_id)

        # Group events by their root (connected component)
        components = defaultdict(set)
        for event_id in parent.keys():
            root = find(event_id)
            components[root].add(event_id)

        # Filter to only clusters with 2+ members
        clusters = {root: sorted(list(members)) for root, members in components.items() if len(members) > 1}

        # Process each cluster
        for root, duplicate_ids in clusters.items():
            # Filter dataset to get all events in this duplicate cluster
            if 'event_id' in df.columns:
                duplicate_events = df[df['event_id'].isin(duplicate_ids)]
            else:
                duplicate_events = df[df.index.isin(duplicate_ids)]

            if len(duplicate_events) == 0:
                continue

            # Collect all narratives from the event column
            narratives = duplicate_events['event'].tolist()
            narratives_text = "\n\n---\n\n".join([f"Event {i+1}: {narrative}" for i, narrative in enumerate(narratives)])

            # Use the prompt from config for merging events
            merge_prompt = f"""I have multiple reports of the same event. Please create a single comprehensive narrative that combines all the details from these duplicate reports.

            Duplicate Event Reports:
            {narratives_text}

            Please provide a unified event description that includes all relevant details from the reports above."""

            # Use OpenAI to create universal narrative

            universal_narrative_response = self.get_info(merge_prompt, 'duplicates_summarizer')

            # Parse JSON response to extract combined_summary
            universal_narrative_json = self.clean_response(universal_narrative_response)
            if not universal_narrative_json or 'combined_summary' not in universal_narrative_json:
                print(f"  ✗ Failed to parse merged narrative JSON for cluster {duplicate_ids}")
                continue
            universal_narrative = universal_narrative_json['combined_summary']

            # Check if a planned event was confirmed by a non-planned report
            has_planned_event = False
            has_non_planned_event = False
            if 'planned_event' in df.columns:
                has_planned_event = duplicate_events['planned_event'].any()
                has_non_planned_event = (~duplicate_events['planned_event'].fillna(False)).any()
            took_place = has_planned_event and has_non_planned_event

            # ENRICH THE MERGED EVENT with all fields (same as regular events)
            # This extracts classification, participants, demands, targets, etc. from the merged narrative
            first_event = duplicate_events.iloc[0]

            # Get date for date_extractor context
            date_str = first_event.get('start_date')
            if pd.notna(date_str):
                date_str = str(date_str)[:10]  # Format as YYYY-MM-DD
            elif 'date' in first_event and pd.notna(first_event['date']):
                date_str = str(first_event['date'])[:10]
            else:
                date_str = 'unknown'

            # Prepare event data for enrichment
            enrichment_input = {
                'event': universal_narrative,
                'date': date_str
            }

            # All enrichment assistants
            ALL_ENRICHMENT_ASSISTANTS = [
                "date_extractor",
                "location_extractor",
                "tactic_extractor",
                "event_classifier",
                "event_type",
                "commemorative_extractor",
                "multi_sited_extractor",
                "participants_extractor",
                "mediators_extractor",
                "organizers_extractor",
                "target_extractor",
                "demand_extractor",
                "violence_extractor"
            ]

            # Enrich with all assistants
            enriched_data = self.add_columns_to_df(enrichment_input, ALL_ENRICHMENT_ASSISTANTS)

            # Post-process with non-AI functions (date normalization & calculations)
            enriched_data = DataFrameEnhancer.normalize_dates_in_dict(enriched_data)

            # Date calculations (using pandas DataFrame temporarily)
            df_temp = pd.DataFrame([enriched_data])
            df_temp = DataFrameEnhancer.fill_missing_start_dates(df_temp)
            df_temp = DataFrameEnhancer.add_num_of_days(df_temp)
            enriched_data = df_temp.iloc[0].to_dict()

            # Create the merged event row with ALL enriched fields
            merged_row = enriched_data.copy()

            # Override/add merge-specific fields
            merged_row['event'] = universal_narrative
            merged_row['merged_event'] = True
            merged_row['merged_from_ids'] = list(duplicate_ids)
            merged_row['merged_to'] = None
            merged_row['is_duplicate'] = False  # Merged event itself is not a duplicate
            merged_row['duplicate_events_ids'] = None
            merged_row['article_id'] = first_event.get('article_id')

            # Mark took_place = True only if a planned event is confirmed by a non-planned report
            if took_place:
                merged_row['took_place'] = True

            # Add merged event to dataframe
            # Append new row to df
            # Generate new event_id for merged event starting with "UNIVERSAL_" and 4 digit index

            if 'event_id' in df.columns:
                # Create new event_id for merged event using first member of sorted cluster
                new_id = f"MERGED_{duplicate_ids[0]}"
                merged_row['event_id'] = new_id
                df = pd.concat([df, pd.DataFrame([merged_row])], ignore_index=True)
                merged_event_id = new_id
            elif 'id' in df.columns:
                new_id = df['id'].max() + 1 if len(df) > 0 else 1
                merged_row['id'] = new_id
                df = pd.concat([df, pd.DataFrame([merged_row])], ignore_index=True)
                merged_event_id = new_id
            else:
                df = pd.concat([df, pd.DataFrame([merged_row])], ignore_index=True)
                merged_event_id = len(df) - 1  # Use the new index

            # Tag all source duplicate events with merged_to
            if 'event_id' in df.columns:
                df.loc[df['event_id'].isin(duplicate_ids), 'merged_to'] = merged_event_id
                if took_place:
                    planned_mask = df['event_id'].isin(duplicate_ids) & (df['planned_event'] == True)
                    df.loc[planned_mask, 'took_place'] = True
            elif 'id' in df.columns:
                df.loc[df['id'].isin(duplicate_ids), 'merged_to'] = merged_event_id
                if took_place:
                    planned_mask = df['id'].isin(duplicate_ids) & (df['planned_event'] == True)
                    df.loc[planned_mask, 'took_place'] = True
            else:
                df.loc[df.index.isin(duplicate_ids), 'merged_to'] = merged_event_id
                if took_place:
                    planned_mask = df.index.isin(duplicate_ids) & (df['planned_event'] == True)
                    df.loc[planned_mask, 'took_place'] = True

        return df

    def duplicate_check(self, df, row):

        # Filter to events where date ranges overlap with the row's date range
        row_start = pd.to_datetime(row['start_date'], errors='coerce')
        row_end = pd.to_datetime(row['end_date'], errors='coerce') if pd.notna(row.get('end_date')) else row_start

        df_start = pd.to_datetime(df['start_date'], errors='coerce')
        df_end = pd.to_datetime(df['end_date'], errors='coerce').fillna(df_start)

        # Date ranges overlap if: row_start <= df_end AND row_end >= df_start
        filtered_df = df[(row_start <= df_end) & (row_end >= df_start)]

        columns_to_include = ['event_id', 'event', 'start_date', 'end_date', 'raw_extracted_location', 'raw_extracted_end_location']
        available_columns = [col for col in columns_to_include if col in filtered_df.columns]
        filtered_df = filtered_df[available_columns]

        df_str = filtered_df.to_markdown(index=False)


        response = self.get_info(row['event'], "duplicate_checker", file_search = True, df_str = df_str)
        cleaned_response = self.clean_response(response)


        if not cleaned_response:
            return {"is_duplicate": False, "duplicate_events_ids": []}

        return cleaned_response

    def duplicate_check_db(self, event: Dict[str, Any], candidates: Optional[List[Dict[str, Any]]] = None) -> Dict[str, Any]:
        """
        Check if an event is a duplicate by comparing against existing events

        Args:
            event: Event dictionary with start_date, end_date, and event text
            candidates: Optional list of candidate duplicate events from database.
                       If not provided, will query database using get_events_by_date_range()

        Returns:
            Dictionary with is_duplicate and duplicate_events_ids
        """
        if not self.db:
            print("Warning: No database manager available for duplicate checking")
            return {"is_duplicate": False, "duplicate_events_ids": []}

        # Use provided candidates or fetch from database
        if candidates is None:
            existing_events = self.db.get_events_by_date_range(
                event['start_date'],
                event.get('end_date', event['start_date'])
            )
        else:
            existing_events = candidates

        # If no existing events, not a duplicate
        if not existing_events:
            return {"is_duplicate": False, "duplicate_events_ids": []}

        # Convert to DataFrame for markdown formatting
        df = pd.DataFrame(existing_events)

        # Select relevant columns for duplicate checking
        columns_to_include = ['event_id', 'event', 'start_date', 'end_date', 'raw_extracted_location', 'raw_extracted_end_location']
        available_columns = [col for col in columns_to_include if col in df.columns]
        filtered_df = df[available_columns]

        # Convert to markdown string for LLM
        df_str = filtered_df.to_markdown(index=False)

        # Call LLM to check for duplicates
        response = self.get_info(event['event'], "duplicate_checker", file_search=True, df_str=df_str)
        cleaned_response = self.clean_response(response)

        if not cleaned_response:
            return {"is_duplicate": False, "duplicate_events_ids": []}

        return cleaned_response

    def combine_duplicates_db(self, filter_params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Combines duplicate events directly in the database using 3-table architecture

        Process:
        1. Identifies duplicate clusters from is_duplicate and duplicate_events_ids
        2. Creates universal narrative using AI for each cluster
        3. Inserts merged events into database
        4. Tags source events with merged_to pointer
        5. Handles planned events by setting took_place=True if any source was planned

        Args:
            filter_params: Optional dict with filters like:
                - sources: List[str] - news sources
                - year: int - year filter
                - month: int - month filter
                - start_date: str - start date (YYYY-MM-DD)
                - end_date: str - end date (YYYY-MM-DD)
                - article_ids: List[str] - specific article IDs

        Returns:
            Dict with statistics: {
                'clusters_found': int,
                'merged_events_created': int,
                'source_events_tagged': int
            }
        """
        if not self.db:
            raise RuntimeError("DatabaseManager not initialized. Cannot combine duplicates in database.")

        print("\n" + "=" * 70)
        print("COMBINING DUPLICATE EVENTS")
        print("=" * 70)

        stats = {
            'clusters_found': 0,
            'merged_events_created': 0,
            'source_events_tagged': 0
        }

        # Build WHERE clause for filtering
        where_conditions = ["is_duplicate = TRUE", "merged_to IS NULL"]
        params = []
        param_counter = 1

        # Track if we need to join with main_corpus for date filtering
        need_join = False

        if filter_params:
            if filter_params.get('article_ids'):
                placeholders = ','.join(['%s'] * len(filter_params['article_ids']))
                where_conditions.append(f"e.article_id IN ({placeholders})")
                params.extend(filter_params['article_ids'])
                param_counter += len(filter_params['article_ids'])

            if filter_params.get('year') and filter_params.get('month'):
                where_conditions.append("EXTRACT(YEAR FROM mc.date) = %s AND EXTRACT(MONTH FROM mc.date) = %s")
                params.extend([filter_params['year'], filter_params['month']])
                need_join = True
            elif filter_params.get('year'):
                where_conditions.append("EXTRACT(YEAR FROM mc.date) = %s")
                params.append(filter_params['year'])
                need_join = True

            if filter_params.get('start_date'):
                where_conditions.append("mc.date >= %s")
                params.append(filter_params['start_date'])
                need_join = True

            if filter_params.get('end_date'):
                where_conditions.append("mc.date <= %s")
                params.append(filter_params['end_date'])
                need_join = True

            if filter_params.get('sources'):
                where_conditions.append("mc.news_source = ANY(%s)")
                params.append(filter_params['sources'])
                need_join = True

        # Update where conditions to use e. prefix for events table
        where_conditions = [c.replace("is_duplicate", "e.is_duplicate").replace("merged_to", "e.merged_to")
                           if "mc." not in c and "e." not in c else c
                           for c in where_conditions]

        where_clause = " AND ".join(where_conditions)

        # Query for all duplicate events that haven't been merged yet
        if need_join:
            query = f"""
                SELECT e.event_id, e.article_id, e.event, e.duplicate_events_ids,
                       e.start_date, e.end_date, e.planned_event, e.Governorate, e.Town
                FROM events e
                JOIN main_corpus mc ON e.article_id = mc.article_id
                WHERE {where_clause}
                ORDER BY e.event_id
            """
        else:
            # No join needed, query events directly (use e. prefix for consistency)
            where_clause_no_prefix = where_clause.replace("e.", "")
            query = f"""
                SELECT event_id, article_id, event, duplicate_events_ids,
                       start_date, end_date, planned_event, Governorate, Town
                FROM events
                WHERE {where_clause_no_prefix}
                ORDER BY event_id
            """

        with self.db.get_connection() as conn:
            cursor = conn.cursor(cursor_factory=extras.RealDictCursor)
            cursor.execute(query, params)
            duplicate_events = cursor.fetchall()

        if not duplicate_events:
            print("\n✓ No duplicate events found to merge")
            return stats

        print(f"\nFound {len(duplicate_events)} duplicate events")

        # Group duplicates into clusters using Union-Find (Disjoint Set Union)
        # This properly handles transitive relationships: if A→B and B→C, then A,B,C are one cluster
        parent = {}

        def find(x):
            """Find root of set with path compression"""
            if x not in parent:
                parent[x] = x
            if parent[x] != x:
                parent[x] = find(parent[x])
            return parent[x]

        def union(x, y):
            """Union two sets"""
            px, py = find(x), find(y)
            if px != py:
                parent[px] = py

        # Build unions from duplicate relationships
        for event in duplicate_events:
            event_id = event['event_id']
            duplicate_ids = event['duplicate_events_ids']

            if not duplicate_ids:
                continue

            if not isinstance(duplicate_ids, list):
                continue

            for dup_id in duplicate_ids:
                union(event_id, dup_id)

        # Group events by their root (connected component)
        components = defaultdict(set)
        for event_id in parent.keys():
            root = find(event_id)
            components[root].add(event_id)

        # Convert to clusters dict format: {root: [list of all members]}
        # Filter to only clusters with 2+ members
        clusters = {root: sorted(list(members)) for root, members in components.items() if len(members) > 1}

        stats['clusters_found'] = len(clusters)
        print(f"Identified {len(clusters)} duplicate clusters to merge")

        # Process each cluster
        for cluster_num, (root, duplicate_ids) in enumerate(clusters.items(), 1):
            print(f"\n[{cluster_num}/{len(clusters)}] Processing cluster: {duplicate_ids[:3]}..." +
                  (" (more)" if len(duplicate_ids) > 3 else ""))

            # Generate merged event ID using the first member of the sorted cluster
            # This ensures consistent naming regardless of which event was the Union-Find root
            merged_event_id = f"MERGED_{duplicate_ids[0]}"

            # Check if merged event already exists
            with self.db.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT 1 FROM events WHERE event_id = %s", [merged_event_id])
                merged_exists = cursor.fetchone() is not None

            if merged_exists:
                # Merged event exists - tag source events AND update merged_from_ids
                print(f"  Merged event {merged_event_id} already exists, updating...")
                try:
                    with self.db.get_connection() as conn:
                        cursor = conn.cursor()

                        # Get current merged_from_ids
                        cursor.execute(
                            "SELECT merged_from_ids FROM events WHERE event_id = %s",
                            [merged_event_id]
                        )
                        result = cursor.fetchone()
                        current_merged_from = json.loads(result[0]) if result and result[0] else []

                        # Add new source events to merged_from_ids
                        updated_merged_from = list(set(current_merged_from + duplicate_ids))

                        # Update merged_from_ids on the merged event
                        cursor.execute(
                            "UPDATE events SET merged_from_ids = %s WHERE event_id = %s",
                            [json.dumps(updated_merged_from), merged_event_id]
                        )

                        # Tag source events AND set is_duplicate=true
                        update_placeholders = ','.join(['%s'] * len(duplicate_ids))
                        update_query = f"""
                            UPDATE events
                            SET merged_to = %s, is_duplicate = TRUE
                            WHERE event_id IN ({update_placeholders})
                            AND merged_to IS NULL
                        """
                        cursor.execute(update_query, [merged_event_id] + duplicate_ids)

                        # Mark original planned events as took_place = True
                        if took_place:
                            update_planned_query = f"""
                                UPDATE events
                                SET took_place = TRUE
                                WHERE event_id IN ({update_placeholders})
                                AND planned_event = TRUE
                            """
                            cursor.execute(update_planned_query, duplicate_ids)
                        updated_count = cursor.rowcount
                        conn.commit()

                        if updated_count > 0:
                            stats['source_events_tagged'] += updated_count
                            print(f"  ✓ Updated merged_from_ids and tagged {updated_count} source events")
                        else:
                            print(f"  ✓ All source events already tagged")
                except Exception as e:
                    print(f"  ✗ Error updating merged event: {e}")
                continue

            # Fetch all events in this cluster
            placeholders = ','.join(['%s'] * len(duplicate_ids))
            cluster_query = f"""
                SELECT event_id, event, article_id, start_date, end_date,
                       planned_event, Governorate, Town
                FROM events
                WHERE event_id IN ({placeholders})
                ORDER BY created_at
            """

            with self.db.get_connection() as conn:
                cursor = conn.cursor(cursor_factory=extras.RealDictCursor)
                cursor.execute(cluster_query, duplicate_ids)
                cluster_events = cursor.fetchall()

            if not cluster_events:
                print(f"  Warning: No events found for cluster {duplicate_ids}")
                continue

            # Collect narratives
            narratives = [evt['event'] for evt in cluster_events]
            narratives_text = "\n\n---\n\n".join(
                [f"Event {i+1}: {narrative}" for i, narrative in enumerate(narratives)]
            )

            # Create merge prompt (directly pass narratives to duplicates_summarizer)
            merge_prompt = narratives_text

            # Use AI to create merged narrative
            print(f"  Merging {len(narratives)} event narratives...")
            universal_narrative_response = self.get_info(merge_prompt, 'duplicates_summarizer')

            # Parse JSON response to extract combined_summary
            universal_narrative_json = self.clean_response(universal_narrative_response)
            if not universal_narrative_json or 'combined_summary' not in universal_narrative_json:
                print(f"  ✗ Failed to parse merged narrative JSON for cluster")
                continue
            universal_narrative = universal_narrative_json['combined_summary']

            # Check if a planned event was confirmed by a non-planned report
            has_planned_event = any(evt.get('planned_event', False) for evt in cluster_events)
            has_non_planned_event = any(not evt.get('planned_event', False) for evt in cluster_events)
            took_place = has_planned_event and has_non_planned_event

            # Use first event as template for merged event
            first_event = cluster_events[0]

            # ENRICH THE MERGED EVENT with all fields (same as regular events)
            # This extracts classification, participants, demands, targets, etc.
            print(f"  Enriching merged event with all fields...")
            ALL_ENRICHMENT_ASSISTANTS = [
                "date_extractor",
                "location_extractor",
                "tactic_extractor",
                "event_classifier",
                "event_type",
                "commemorative_extractor",
                "multi_sited_extractor",
                "participants_extractor",
                "mediators_extractor",
                "organizers_extractor",
                "target_extractor",
                "demand_extractor",
                "violence_extractor"
            ]

            # Get date from first event for date_extractor context
            date_str = first_event.get('start_date')
            if date_str:
                date_str = str(date_str)[:10]  # Format as YYYY-MM-DD
            else:
                date_str = 'unknown'

            # Prepare event data for enrichment
            enrichment_input = {
                'event': universal_narrative,
                'date': date_str
            }

            # Enrich with all assistants
            enriched_data = self.add_columns_to_df(enrichment_input, ALL_ENRICHMENT_ASSISTANTS)

            # Post-process with non-AI functions (date normalization & calculations)
            enriched_data = DataFrameEnhancer.normalize_dates_in_dict(enriched_data)

            # Date calculations (using pandas DataFrame temporarily)
            df_temp = pd.DataFrame([enriched_data])
            df_temp = DataFrameEnhancer.fill_missing_start_dates(df_temp)
            df_temp = DataFrameEnhancer.add_num_of_days(df_temp)
            enriched_data = df_temp.iloc[0].to_dict()

            # Geocode locations if Google Maps API key is available
            try:
                from location_agent import LocationAgent
                location_agent = LocationAgent()

                # Geocode start location
                start_query_parts = []
                if enriched_data.get('Name_of_location'):
                    start_query_parts.append(enriched_data['Name_of_location'])
                if enriched_data.get('Governorate'):
                    start_query_parts.append(enriched_data['Governorate'])

                if start_query_parts:
                    start_query = ", ".join(start_query_parts)
                    result = location_agent.geocode_location(start_query, country_code="JO")
                    if result.get('latitude') and result.get('longitude'):
                        enriched_data['Latitude'] = result['latitude']
                        enriched_data['Longitude'] = result['longitude']
                        enriched_data['location_type'] = result.get('location_type')
                        print(f"  ✓ Geocoded merged event location: {result['latitude']:.4f}, {result['longitude']:.4f}")
            except (ImportError, ValueError) as e:
                # Location agent not available or API key not configured - skip geocoding
                pass
            except Exception as e:
                # Other errors - log but continue
                print(f"  ⚠ Error geocoding merged event: {e}")

            # Create merged event data with ALL enriched fields
            merged_event_data = {
                'event_id': merged_event_id,
                'article_id': first_event['article_id'],
                'event': universal_narrative,
                'merged_event': True,
                'merged_from_ids': duplicate_ids,  # Will be json.dumps() later
                'merged_to': None,
                'is_duplicate': False,
                'duplicate_events_ids': [],  # Will be json.dumps() later
                'took_place': True if took_place else None,
                # Copy ALL enriched fields from the enrichment process
                **enriched_data
            }

            # Insert merged event into database
            try:
                with self.db.transaction():
                    with self.db.get_connection() as conn:
                        cursor = conn.cursor()

                        # Build dynamic INSERT query with all enriched fields
                        # Filter out None values, event_number, and 'date' (used for AI context only)
                        # Use 'v is not None' to avoid numpy array boolean ambiguity
                        insert_fields = {}
                        for k, v in merged_event_data.items():
                            if k in ('event_number', 'date'):
                                continue
                            # Convert numpy arrays to lists
                            if hasattr(v, 'tolist'):
                                v = v.tolist()
                            # Skip None and pandas NaN/NaT values
                            if v is None:
                                continue
                            if pd.isna(v) if not isinstance(v, (list, dict, str)) else False:
                                continue
                            insert_fields[k] = v

                        # Convert any pandas Timestamps to strings for JSON serialization
                        for key, value in list(insert_fields.items()):
                            if hasattr(value, 'isoformat'):
                                insert_fields[key] = value.isoformat()

                        # JSONB columns that need json.dumps() conversion (lowercase for matching)
                        JSONB_COLUMNS = {
                            'tactic_original_text', 'tactic_classification',
                            'participants_type_original', 'participating group',
                            'sector', 'protesters_occupation', 'work_space_name',
                            'organizing_actor', 'organization_actor_type',
                            'mediators', 'mediators_type_one', 'mediators_type_two',
                            'demands', 'demands_classification_one', 'demands_classification_two',
                            'slogans', 'repression_reports', 'responding_actor',
                            'responding_actor_class', 'protesters_violence_reports',
                            'duplicate_events_ids', 'merged_from_ids'
                        }

                        # Convert ALL JSONB column values to JSON strings
                        # (strings become JSON strings, lists/dicts become JSON arrays/objects)
                        for key, value in list(insert_fields.items()):
                            if key.lower() in JSONB_COLUMNS:
                                insert_fields[key] = json.dumps(value)

                        # Normalize column names to match PostgreSQL schema
                        # - Most columns: lowercase (PostgreSQL lowercases unquoted identifiers)
                        # - Special columns with spaces/hyphens are quoted in schema and preserve exact case
                        SPECIAL_COLUMNS = {'Participating group', 'pro-government_event'}
                        insert_fields = {
                            (k if k in SPECIAL_COLUMNS else k.lower()): v
                            for k, v in insert_fields.items()
                        }

                        # Quote column names to handle spaces and reserved words
                        columns = ', '.join([f'"{k}"' for k in insert_fields.keys()])
                        placeholders = ', '.join([f'%({k})s' for k in insert_fields.keys()])

                        insert_query = f"""
                            INSERT INTO events ({columns})
                            VALUES ({placeholders})
                        """
                        cursor.execute(insert_query, insert_fields)

                        # Update source events to point to merged event AND set is_duplicate=true
                        update_placeholders = ','.join(['%s'] * len(duplicate_ids))
                        update_query = f"""
                            UPDATE events
                            SET merged_to = %s, is_duplicate = TRUE
                            WHERE event_id IN ({update_placeholders})
                        """
                        cursor.execute(update_query, [merged_event_id] + duplicate_ids)

                        # Mark original planned events as took_place = True
                        if took_place:
                            update_planned_query = f"""
                                UPDATE events
                                SET took_place = TRUE
                                WHERE event_id IN ({update_placeholders})
                                AND planned_event = TRUE
                            """
                            cursor.execute(update_planned_query, duplicate_ids)
                        updated_count = cursor.rowcount

                        stats['merged_events_created'] += 1
                        stats['source_events_tagged'] += updated_count

                        print(f"  ✓ Created merged event: {merged_event_id}")
                        print(f"    Tagged {updated_count} source events as duplicates")

            except Exception as e:
                print(f"  ✗ Error creating merged event: {e}")
                continue

        # Print final statistics
        print("\n" + "=" * 70)
        print("MERGE COMPLETE")
        print("=" * 70)
        print(f"Clusters found:         {stats['clusters_found']}")
        print(f"Merged events created:  {stats['merged_events_created']}")
        print(f"Source events tagged:   {stats['source_events_tagged']}")
        print("=" * 70)

        return stats

    def expand_transitive_duplicates(self) -> Dict[str, int]:
        """
        Expand duplicate relationships transitively using connected components.

        If A→[B] and X→[B], then A, B, X are all in the same cluster and
        each should reference all others. This ensures that when merging,
        all related events are properly grouped together.

        Returns:
            Dict with statistics: {
                'events_processed': int,
                'events_updated': int,
                'clusters_found': int
            }
        """
        if not self.db:
            raise RuntimeError("DatabaseManager not initialized. Cannot expand duplicates.")

        print("\n" + "=" * 70)
        print("EXPANDING TRANSITIVE DUPLICATE RELATIONSHIPS")
        print("=" * 70)

        stats = {
            'events_processed': 0,
            'events_updated': 0,
            'clusters_found': 0
        }

        # Step 1: Get all events with duplicate relationships (not already merged)
        with self.db.get_connection() as conn:
            cursor = conn.cursor(cursor_factory=extras.RealDictCursor)
            cursor.execute("""
                SELECT event_id, duplicate_events_ids
                FROM events
                WHERE duplicate_events_ids IS NOT NULL
                  AND duplicate_events_ids != '[]'
                  AND merged_event = FALSE
                  AND merged_to IS NULL
            """)
            events = cursor.fetchall()

        if not events:
            print("No duplicate relationships to expand")
            return stats

        stats['events_processed'] = len(events)
        print(f"Found {len(events)} events with duplicate relationships")

        # Step 2: Build adjacency graph using Union-Find (Disjoint Set Union)
        parent = {}

        def find(x):
            """Find root of set with path compression"""
            if x not in parent:
                parent[x] = x
            if parent[x] != x:
                parent[x] = find(parent[x])
            return parent[x]

        def union(x, y):
            """Union two sets"""
            px, py = find(x), find(y)
            if px != py:
                parent[px] = py

        # Build unions from duplicate relationships
        for event in events:
            event_id = event['event_id']
            dup_ids = event['duplicate_events_ids']

            # Handle both list and JSON string formats
            if isinstance(dup_ids, str):
                try:
                    dup_ids = json.loads(dup_ids)
                except json.JSONDecodeError:
                    continue

            if isinstance(dup_ids, list):
                for dup_id in dup_ids:
                    union(event_id, dup_id)

        # Step 3: Group events by their root (connected component)
        components = defaultdict(set)
        all_event_ids = set(parent.keys())
        for event_id in all_event_ids:
            root = find(event_id)
            components[root].add(event_id)

        # Filter to only clusters with 2+ members
        clusters = {k: v for k, v in components.items() if len(v) > 1}
        stats['clusters_found'] = len(clusters)
        print(f"Identified {len(clusters)} duplicate clusters")

        # Step 4: Update each event with full cluster membership
        with self.db.get_connection() as conn:
            cursor = conn.cursor()

            for root, cluster in clusters.items():
                for event_id in cluster:
                    # All other events in cluster are duplicates
                    other_ids = sorted([eid for eid in cluster if eid != event_id])

                    cursor.execute("""
                        UPDATE events
                        SET duplicate_events_ids = %s,
                            is_duplicate = TRUE
                        WHERE event_id = %s
                          AND merged_event = FALSE
                    """, [json.dumps(other_ids), event_id])

                    if cursor.rowcount > 0:
                        stats['events_updated'] += 1

            conn.commit()

        print(f"Expanded {stats['events_updated']} events with transitive relationships")
        print("=" * 70)

        return stats
