{   "event_extractor": {
      "model": "gpt-4.1",
      "system_prompt": """
           Extract and summarize any protest events mentioned in the provided Arabic news article about Jordan.
           An event is defined as a time-limited, public gathering or interaction involving multiple participants, usually making demands directed at a target (which may be an institution, official, international actor, etc).
           Single-person actions must be public and articulate a demand centered around another individual to qualify as a protest event. Events can also occur online, and cases where a presumed target responds count as events even if no demand is explicitly stated.
            Recognized protest tactics often include: protest, sit-in, road blockage, strike, work stoppage, march, boycotts, petition, social media or advocacy campaign, self-harm, a public gathering or activity with a demand.
            Make sure to not report the same event multiple times if it is mentioned in different ways or sections of the article, or if multiple tactics are used in the same event, or it spans multiple days, or move to different locations.
            If events have different dates or time or locations, or are clearly distinct in demands, they should be reported separately.
            **Instructions:**
            - Read and internally reason through the article to identify any protest event(s) that match the definitions and criteria above.
            - For each identified event, internally evaluate all relevant details and ensure it meets the requirements for protest events.
            - Make sure to distinguish between separate events based on date, location, demands, and other key factors.
            - Make sure you are not creating duplicate events if the same event is described in multiple ways.
            - Summarize each qualifying event in a clear, self-contained narrative, including all relevant information and notable details.

            **Output Rules (IMPORTANT):**
            - Respond ONLY with a single valid JSON object and no other text.
            - The JSON object must contain exactly one key: "events".
            - If no protest events are identified, output exactly:
            {"events": []}
            - The value of "events" must be a JSON array whose elements are string summaries. Each string should be a fully self-contained narrative summary of a single protest event (these JSON arrays are directly usable as Python lists of strings).
            - Do not repeat reasoning or extract portions; only the final narratives should be output.

            # Example 1:

            **Input:**
            " أكد الناطق باسم نقابة المعلمين، الدكتور أحمد الحجايا، أن اضراب المعلمين قائم يوم الثلاثاء ولا نية للتراجع عنه بالرغم من تصريحات رئيس ديوان الخدمة المدنية خلف هميسات باستثناء المعلمين من تعديلات نظام الخدمة المدنية واعتماد المنحنى الطبيعي.واضاف الحجايا ل الاردن24 إن تنصل رئيس الوزراء الدكتور عمر الرزاز من الاتفاقات التي تمت معه وتراجعه عن موقفه السابق من خلال التلمحيات التي أطلقها مؤخرا وكذلك تناقض التصريحات من قبل ديوان الخدمة المدنية وعدم نفيها من قبل الحكومة أيضا أوصلت النقابة إلى معركة كسر عظم مع ديوان الخدمة المدنية وأوصلها إلى طريق مسدود واعلان الاضراب. اقرأ ايضا : نقابة المعلمين تعلق اضرابها.. ومجلس الوزراء يستثني المعلمين من المنحنى الطبيعيوقال ان جميع المسؤولين الذين التقتهم النقابة كانوا يؤيدون استثناء المعلمين من تطبيق المنحنى الطبيعي والخروج بنظام خاص بهم يعيد للمهنة هيبتها نظرا لوجود خصوصية لمهنة التعليم وذلك لم يحصل حتى اللحظة.واشار الى ان النقابة حاولت التواصل مع وزارة التربية والتعليم إلا أنها لم تجد مسؤولا نظرا لغياب الوزير المكلف في مهام خارج البلاد وكذلك مع الحكومة الا انها لم تجد تجاوبا، وعليه، قررت اعلان الاضراب."

            **Expected Output:**
            {"events":  ["نقابة المعلمين الأردنيين أعلنت عن إضراب للمعلمين يوم الثلاثاء، احتجاجاً على تنصل رئيس الوزراء عمر الرزاز من الاتفاقات السابقة مع النقابة، وعلى تصريحات وتناقضات ديوان الخدمة المدنية بشأن استثناء المعلمين من تعديلات نظام الخدمة المدنية واعتماد المنحنى الطبيعي. النقابة اعتبرت أن غياب الاستجابة الحكومية وإخلال الوعود أوصلها إلى 'معركة كسر عظم' مع ديوان الخدمة المدنية، ما دفعها إلى إعلان الإضراب."]}


            # Example 2:

            **Input:**
            "جو 24 : لجأ سكان قرية النقع في لواء الأغوار الجنوبية، السبت، إلى حرق الإطارات المطاطية وحاويات القمامة بهدف التخلص من بعوضة تسببت بلسع العشرات من الأشخاص في ظل ارتفاع درجات الحرارة. ويطالب أهالي المنطقة التي تعتبر بيئة مناسبة لتكاثر البعوض كونها مناطق زراعية تكثر فيها التجمعات المائيةالغد"

            **Expected Output:**
            {"events": []}

            # Example 3:

            **Input:**
            "نفذ معلمو محافظة الكرك وقفة احتجاجية أمام مديرية التربية والتعليم للمطالبة بصرف علاوة المهنة التي تم الاتفاق عليها سابقًا مع الحكومة. وفي الوقت نفسه، نظم معلمو محافظة الطفيلة اعتصامًا مماثلًا أمام مبنى المحافظة تضامنًا مع زملائهم في الكرك، مؤكدين استمرارهم بالإضراب حتى تحقيق المطالب."

            **Expected Output:**
            {"events": [ "نفذ معلمو محافظة الكرك وقفة احتجاجية أمام مديرية التربية والتعليم للمطالبة بصرف علاوة المهنة التي تم الاتفاق عليها سابقًا مع الحكومة.","نظم معلمو محافظة الطفيلة اعتصامًا أمام مبنى المحافظة تضامنًا مع زملائهم في الكرك، مؤكدين استمرارهم بالإضراب حتى تحقيق المطالب."]}

            # Notes

            - Protest can be in-person or online.
            - Event definitions and criteria must be strictly applied.
            - Output must be only the list of narratives; do not output any reasoning or internal decision-making steps.

            ---

            **REMINDER:**
            Only output the final list of protest event narratives, self-contained summaries per the rules above. All reasoning must be internal and should NEVER appear in your output.

        """,

        "response_format": "json_object",
        "temperature": 0.10,
        "top_p": 0.20
    },

    "duplicate_checker":{
        "model": "gpt-4.1",
        "system_prompt": """
            Determine if a described protest event is already listed among protest events in a provided CSV file for the same date. Respond with a JSON object indicating duplication and listing duplicate event IDs found, following careful reasoning as outlined below.

            You are given:
            - A narrative describing a protest event
            - The event's date and location
            - A CSV file (via file search) listing other events on the same date

            Your objective:
            - Analyze the narrative, date, and location both start and end location.
            - Compare all relevant details (narrative wording, location, date, demands, participants, organizers, etc.) to the events in the CSV.
            - Decide if the current event is already listed ("duplicate") or not.
            - If the location is missing or not specified in the narrative, compare events using the date and demands as your main matching criteria.

            Key instructions:
            - Always reason thoroughly and internally before making any final determination.
            - Do not make assumptions beyond information in the narrative and CSV.
            - Only output the required JSON:
            {
                "is_duplicate": true/false,
                "duplicate_events_ids": [list of matching event IDs as strings]
            }
            - For borderline or ambiguous cases, include an event as a duplicate only if there’s strong evidence that it is genuinely the same occurrence.
            - If no duplicate is found, return "is_duplicate": false and an empty duplicate_events_ids list.
            - If one or more duplicates are found, return "is_duplicate": true and a list of all matching event IDs.

            # Steps

            1. Examine all key details from the input (narrative, date, location, demands, etc.).
            2. If the location is not provided, compare based on date and the main demands.
            3. For each event in the CSV:
                - Compare all available listings, focusing on date and location (if available), demands/causes and narrative details.
                - Consider wording differences.
                - Only accept as a duplicate if references are clearly to the same event.
            4. List IDs of all clearly matching events.
            5. Your answer must be the final JSON only, without explanation or comments.

            # Output Format

            A single JSON object with:
            - "is_duplicate": (true or false)
            - "duplicate_events_ids": [list of IDs as strings]

            # Examples

            Example 1 (duplicate—location match)
            Input Narrative: "تجمع العشرات أمام مجلس النواب احتجاجًا على رفع أسعار الوقود."
            Input Date: 2019-09-05
            Input Location: مجلس النواب
            CSV Events:
            | id | date       | location | description                                         |
            |----|------------|----------|-----------------------------------------------------|
            | 77 |2019-09-05  |مجلس النواب  |احتجاج أمام مجلس النواب ضد رفع أسعار المحروقات  |
            | 78 |2019-09-05  |اربد | اعتصام لموظفي البلدية للمطالبة بزيادة الرواتب     |

            Reasoning: The date and location match (2019-09-05, Parliament). The CSV record 77 explicitly describes a protest at the Parliament against fuel price increases, which matches the narrative’s demands and venue. Record 78 differs in both topic and location. Strong evidence of duplication → match with ID 77.

            Final Output:
            {
            "is_duplicate": true,
            "duplicate_events_ids": ["77"]
            }

            Example 2 (NOT duplicate—demands/location differ)
            Input Narrative: "طلاب جامعة اليرموك نظموا وقفة احتجاجية للمطالبة بتحسين خدمات السكن الجامعي."
            Input Date: 2022-07-20
            Input Location: جامعة اليرموك
            CSV Events:
            | id | date       | location | description                              |
            |----|------------|----------|------------------------------------------|
            | 88 |2022-07-20  |شركة الكهرباء | اعتصام لموظفي شركة الكهرباء للمطالبة بالعلاوات |
            | 89 |2022-07-20  |إربد | مسيرة طلابية للمطالبة بإلغاء الامتحانات النهائية الحضورية |

            Reasoning: Although the date is the same (2022-07-20), the narrative describes a student protest at Yarmouk University about dorm services, while CSV records concern different actors and demands (utility company employees seeking allowances; a student march about exams). No strong overlap in location or demands → not a duplicate.

            Final Output:
            {
            "is_duplicate": false,
            "duplicate_events_ids": []
            }

            Example 3 (duplicate—no location in input narrative)
            Input Narrative: "خرج محتجون يطالبون بإلغاء ضريبة المبيعات على المواد الغذائية الأساسية."
            Input Date: 2018-06-10
            Input Location: None
            CSV Events:
            | id | date       | location    | description                                   |
            |----|------------|-------------|-----------------------------------------------|
            | 91 |2018-06-10  |الزرقاء |مواطنون يحتجون على ضريبة المبيعات المفروضة على السلع الغذائية      |
            | 92 |2018-06-10  |الكرك | وقفة تضامنية مع الأسرى الفلسطينيين  |

            Reasoning: Location is not provided, so comparison relies on date and demands. The narrative demands removal of sales tax on basic food items; CSV record 91 on the same date describes citizens protesting the sales tax on food—this aligns on date and main demand despite missing location. Record 92 is on a different topic. Strong evidence of duplication → match with ID 91.

            Final Output:
            {
            "is_duplicate": true,
            "duplicate_events_ids": ["91"]
            }

            # Notes

            - If multiple matching events are found, include all relevant IDs.
            - For records missing critical details, rely on date and narrative demands as primary comparison criteria.
            - If in doubt, only label as a duplicate with strong evidence.
            - Output strictly the JSON format, with boolean and list as specified.

            **REMINDER:** Your task is to determine event duplication using date, and (if available) location, and narrative, returning only the required JSON object, after reasoning internally  step-by-step before conclusion. If location is missing, compare based on date and demands.
        """,

        "response_format": "json_object",
        "temperature": 0.10,
        "top_p": 0.20
    },

    "tactic_extractor": {
      "model": "gpt-4o",
      "system_prompt": """
        Classify the described protest event in a provided Arabic article passage, using explicit definitions for protest tactics. Your goal is to carefully analyze the passage, extract the most accurate tactic based strictly on the provided information, and provide an output containing both the original Arabic text that supports your classification and the selected class/classes.
        Definitions for each class:
        - Protest: Public gathering of individuals in a public space articulating a demand.
        - Sit-in: Public gathering of individuals articulating a demand by occupying a space and causing disruption within it. Individuals occupy a space.
        - Road blockage: Individuals occupy a roadway, often in ways meant to call attention to their demands or to cause a traffic stoppage.
        - Strike: Laborers withholding their labor as part of a demand. Can be students. Workers do not show up at workspace.
        - Work stoppage: Laborers engaging in a short, within-day, work stoppage. They attend work.
        - March: Public gathering of individuals in a public space articulating a demand that moves from one location to another, either on foot or by vehicle.
        - Boycott: Public announcement of intention to not engage with a company, certain products, or events.
        - Election Boycott - An announcment of intention to not take part in an election.
        - Petition: Individuals publicly add their name to a document or statement articulating a demand.
        - Social media campaign: Individuals use their social accounts to articulate support for a demand.
        - Self-harm: An individual or individuals commit an act of publicized self-harm linked to a demand.
        - Public gatherings or activity - a public gathering or event with activities, articulating a demand.
        - Religious gatherings - a religious gathering or activity that articulating a demand.
        - Other tactic - any other form of tactic not mentioned above, linked to a demand.

        Instructions:
        - Only use information present or implied in the provided passage.
        - First, extract and present the exact Arabic word(s) or phrase(s) from the text that support your classification, this should be as minimal as possible.
        - Then, select the most fitting class/classes (from the list above) that best represents the core tactic/interaction described. If the passage is ambiguous or describes multiple tactics or the protesters switch tactics, select one or more classes that are most directly and evidently supported.
        - Do not provide any analysis, commentary, or extraneous text; only give the supporting Arabic phrase(s) and your chosen class/classes as specified.
        - Output your answer in JSON format as follows:
        {
            "original_text": "[exact Arabic text used to identify the tactic]",
            "classification": "[one or more of: Protest, Sit-in, Road blockage, Strike, Work stoppage, March, Boycott, Election Boycott, Petition, Social media campaign, Self-harm, Public gatherings or activity, Religious gatherings, Other tactic]"
        }

        # Output Format

        - Always output a single JSON object with the fields:
        - original_text: String with the Arabic phrase(s) supporting the classification
        - classification: class/classes name from the provided definitions
        - Do not include explanations, translations, or any extra commentary.
        - The output must NOT be in a code block.

        # Examples

        Example 1:
        Input passage: "نفذ عشرات العمال اعتصامًا أمام مبنى البلدية للمطالبة بتحسين شروط العمل."
        Output:
        {
        "original_text": ["اعتصامًا"],
        "classification": ["Sit-in"]
        }

        Example 2:
        Input passage: "أعلنت نقابة المعلمين عن إضراب عام في جميع المدارس الحكومية يوم الأحد."
        Output:
        {
        "original_text": ["إضراب عام"],
        "classification": ["Strike"]
        }

        Example 3:
        Input passage: " انطلقت مسيرة من ميدان التحرير إلى مجلس الوزراء للمطالبة بحقوق العمال ثم أقاموا وقفة احتجاجية."
        Output:
        {
        "original_text": ["وقفة احتجاجية , مسيرة"],
        "classification": ["March, Protest"]
        }

        # Notes

        - Always use only the new class list and definitions.
        - Your answer must include both the supporting phrase(s) (original_text) and tactic classifications (classification) as a JSON object.
        - If no relevant tactic is present in the passage, leave classification empty.
        - Do not output any other text.

        Task reminder: Analyze the passage, reason to select the most fitting class/classes, and provide both the supporting Arabic phrase(s) or word(s) and your classification in the specified JSON structure.
        """,

        "response_format": "json_object",
        "temperature": 0.10,
        "top_p": 0.20
    },

    "date_extractor": {
        "model": "gpt-4o",
        "system_prompt": """
                    Extract detailed date and time information for protest events in a given Arabic text passage. If the passage uses relative date expressions (e.g., "غدا", "يوم أمس", "اليوم", "الاسبوع الماضي"), you will also be provided with the article's publication date; use it to resolve and extract exact (normalized) dates in YYYY-MM-DD format where possible. For protest events described as ongoing, continuous, or spanning a time period (e.g., "منذ أسبوع", "للشهر الثاني على التوالي"), use the article date to calculate the relevant start or end dates. Otherwise, follow the same extraction logic as before.

                    Explicitly do NOT extract dates embedded in group, movement, or street names (such as "ثورة 25 يناير", "حركة 7 ابريل"). Only extract information where the text refers to an actual timing of a protest.

                    Your response must be formatted as a JSON object with these keys:
                    - "start_date": [if available, extracted or resolved as YYYY-MM-DD; otherwise null]
                    - "end_date": [the end date of protest if available or calculable; otherwise null]
                    - "time_of_day": [if available, any time of day details; otherwise null]

                    Think step by step, especially when resolving relative or continuous dates, and perform all analysis before producing your answer. Always ensure accuracy in using the article date for resolving relevant expressions.

                    # Steps

                    1. Read and fully understand the passage, focusing on explicit and implied mentions of protest event dates, durations, times, or expressions relative to the article date.
                    2. If the passage contains relative date terms (such as "غدا", "يوم أمس", "اليوم", "الاسبوع الماضي", etc.), use the provided article date to resolve the exact date(s).
                        - Example: If the article date is 2024-08-10 and the passage says "غدا", resolve this as "2024-08-11".
                    3. For ongoing or continuous event descriptions (like "منذ أسبوع", "للشهر الثاني على التوالي", "منذ مدة"), use the article date and calculate the appropriate date(s) backward as contextually required and put the most recent date as an End date.
                        - Example: If the article date is 2024-09-15 and the protest started "منذ ثلاثة أيام", resolved date is "2024-09-12" and End date is "2024-09-15".
                    4. Identify explicit or descriptive date or time references relating to actual protest events.
                    5. Carefully verify that any phrase resembling a date is NOT simply a group/movement/location name.
                    6. Extract and normalize the date and time info as required in the JSON object.
                    7. If no valid protest date or time information is found, the values should be null.

                    # Output Format

                    - Respond only with:
                        - A JSON object:
                        {
                            "start_date": "value" or null,
                            "end_date": "value" or null,
                            "time_of_day": "value" or null
                        }

                    - No explanations, comments, or extra text.

                    # Examples

                    Example 1:
                    Input passage: "ينظم المواطنون احتجاجاً غداً عند الساعة الخامسة مساء."
                    Article date: 2024-08-10

                    Output:
                    {
                    "start_date": "2024-08-11",
                    "end_date": null,
                    "time_of_day": "الساعة الخامسة مساء"
                    }

                    Example 2:
                    Input passage: "بدأت المظاهرات منذ ثلاثة أيام ولم تتوقف حتى الآن."
                    Article date: 2024-09-15

                    Output:
                    {
                    "start_date": "2024-09-12",
                    "end_date": "2024-09-15",
                    "time_of_day": null
                    }

                    Example 3:
                    Input passage: "خطط النشطاء تنظيم الوقفة يوم أمس أمام مقر البلدية."
                    Article date: 2024-03-20

                    Output:
                    {
                    "start_date": "2024-03-19",
                    "end_date": null,
                    "time_of_day": null
                    }

                    Example 4:
                    Input passage: "تستمر الاعتصامات للشهر الثاني على التوالي."
                    Article date: 2024-06-15

                    Output:
                    {
                    "start_date": "2024-04-15",
                    "end_date": "2024-06-15",
                    "time_of_day": null
                    }

                    Example 5:
                    Input passage: "أعلنت حركة 7 ابريل عن مظاهرة جديدة الأسبوع المقبل في المدينة."
                    Article date: 2024-06-01

                    Output:
                    {
                    "start_date": null,
                    "end_date": null,
                    "time_of_day": null
                    }

                    (# In real use, examples will be longer and more complex. The placeholder [YYYY-MM-DD] or [التاريخ الكامل] should be used if a normalized date is unavailable.)

                    # Notes

                    - Always use the article date to resolve any relative or continuous timing information.
                    - If the text mentions a specific weekday (e.g., “last Friday”), convert it into the exact calendar date corresponding to that weekday in the same year as the article date.
                    - Never extract a date if it is simply part of a group/movement/street name.
                    - Only include date or time information directly referring to an actual protest event's timing.
                    - Maintain strict output formatting—no extra commentary, explanations, or text.
                    - Think step by step for accurate extraction and calculation, and persist in your analysis until all relevant information is found.

                    REMINDER: Extract date/time information for protest events only, resolving relative/ongoing dates using the article date. Respond using the strict output format above.
        """,

        "response_format": "json_object",
        "temperature": 0.10,
        "top_p": 0.20
    },

   "event_classifier": {
        "model": "gpt-4o",
        "system_prompt": """Classify whether a given Arabic news article passage describes a protest event, based strictly on authoritative event definitions, regardless of whether the protest event is the main focus or mentioned only in passage as side information. Use provided defenitions of “protest event”. Carefully analyze and internally reason, step-by-step, about whether the passage fulfills the relevant event-defining criteria before making your classification. Your reasoning must be done internally; only the final classification should be output.
                    Definition of a Protest Event:
                    An event is defined as a time-limited, public gathering or interaction involving multiple participants, usually making demands directed at a target (which may be an institution, official, international actor, etc).The event must be taking place only in Jordan.
                    Single-person actions must be public and articulate a demand centered around another individual to qualify as a protest event. Events can also occur online, and cases where a presumed target responds count as events even if no demand is explicitly stated.
                    Recognized protest tactics often include: protest, sit-in, road blockage, strike, work stoppage, march, boycotts, petition, social media or advocacy campaign, self-harm, a public gathering or activity with a demand.

                    Inclusion Criteria:
                    - **Time-Limited:** The event must have a clear start and end; it cannot be a permanent condition.
                    - **Public:** The event is visible or directed toward an external audience beyond just the participants.
                    - **Multiple Individuals (generally, but not always):** The event typically involves a group, but a single person can qualify if the act is public and expresses a demand.
                    - **Demand Present:** There is a call for change, request, complaint, or effort to pressure for action.
                    - **Target Identified or Implied:** The demand is aimed—explicitly or implicitly—at another person, group, institution, or authority (e.g., government, manager, official, international actor).
                    - **Online Events are Allowed:** Digital protests or public demands made online qualify if they meet all the above criteria.

                    Exclusion Criteria (Not a Protest Event):
                    - Private interactions or thoughts that lack a public element.
                    - Expressions of dissatisfaction with no specific demand.
                    - Statments of opinion, announcements, or factual reporting that don’t describe an actual event/behavior.
                    - Ongoing or permanent conditions not tied to a specific time-limited action.
                    - riots or violence between groups without a clear public demand.

                    Steps:
                    - Use the provided definition of a protest event and ensure accurate application of these criteria.
                    - For each input, internally reason through the passage’s alignment to the protest event criteria; do not include these reasoning steps in your output.
                    - Only after this reasoning, output the required classification.
                    - Output must always be a JSON object with a single Boolean field: `"protest_event": True` if the passage describes a protest event, or `"protest_event": False` if not.
                    - Do not include explanation, extra data, or commentary in your output under any circumstances. Do not use code blocks in your output.

                    **Output Format:**
                    JSON object, a single Boolean field only, no code block, e.g.:
                    { "protest_event": true }

                    # Examples

                    **Example Input:**
                    ("دعا موظفون في وزارة الصحة زملاءهم لتنفيذ وقفة احتجاجية أمام وزارة الصحة نهاية شهر نيسان الحالي، وذلك احتجاجا على عدم الاستجابة لمطالبهم السابقة والمتعلقة بامتيازات وظيفية ومعيشية عديدة.  وتمثّلت مطالب الموظفين بـ"زيادة رواتب، مكافأة نهاية خدمة عادلة، الحصول على بدل عمل اضافي دون شروط، مقاعد جامعية لأبناء العاملين في الصحة، تأمين صحي درجة اولى، عطلة يوم السبت، رفع الحوافز، الحماية من اعتداءات بعض المراجعين، علاوة خطورة العمل، سكن وظيفي أو بدل سكن".")

                    **Expected Output:**
                    { "protest_event": True }

                    **Example Input:**
                    ("أوقفت جامعة اليرموك موظفا عن العمل وأحالته إلى مجلس تأديبي ولجنة تحقيق، إثر الاشتباه بتقاضيه رشاوى مالية من طلبة عرب مقابل قيامه بالتلاعب في سجلات الجامعة الخاصة بامتحان التوفل بحيث يؤهلهم للالتحاق ببرنامج الدراسات العليا. ")

                    **Expected Output:**
                    { "protest_event": False }

                    _Reminder: Strictly apply event definitions. Only output a JSON object with a single Boolean field, with no explanation or extraneous content._
        """,

        "response_format": "json_object",
        "temperature": 0.10,
        "top_p": 0.20
    },

    "event_type": {
        "model": "gpt-4o",
        "system_prompt": """
                        Classify the described protest event in the provided Arabic article passage as either a "threat_event" or a "planned_event" following these rules:

                        - "threat_event": An individual or organization announces an intention to stage a protest. This announcement occurs specifically in the context of negotiations or conversations between the actor and the target. The actual occurrence of the protest is not necessary—just the declared intention within negotiation or conversation context.  However, if the announcement includes a specific mention of a place and/or time/date for the event, it should be classified instead as a planned event.
                        - "planned_event": An individual or organization announces a protest that will occur in the future, outside of any negotiation or conversation context. A planned event is confirmed, has a specific date and/or location mentioned in the article, and is not dependent on negotiations with the target.

                        If information about the protest date is present, include it for the relevant category, the user will provide the date of the article for context, to calculate relative dates if needed.
                        Always output a JSON object with boolean fields for "threat_event", "planned_event". and If available, as a string in DD-MM-YYYY format for "planned_event_date" .
                        Do not include any additional text or explanation.

                        Chain-of-thought: First, analyze the passage to detect key details about context (negotiation/conversation vs. announcement), confirmation, and any dates. Apply the definitions to determine the correct classification. Then, structure the answer as specified.

                        Output format:
                        - JSON object structured as:
                        {
                        "threat_event": [true/false],
                        "planned_event": [true/false],
                        "planned_event_date": "[date or null]"
                        }
                        If the date is not available for a category, put null.

                        Examples:

                        Example 1
                        Input: "أعلن الاتحاد عن نيته تنظيم احتجاج إذا لم توافق الوزارة على مطالبه الأسبوع المقبل. Article date: 2024-06-01"
                        Output:
                        {
                        "threat_event": true,
                        "planned_event": false,
                        "planned_event_date": null
                        }
                        (Reasoning: The union declared their intention to protest if their demands are not met, in the context of negotiations—a threat_event.)

                        Example 2
                        Input: "أعلنت النقابة عن تنظيم مظاهرة حاشدة ضد السياسات الجديدة يوم 2024-06-10 في ساحة المدينة. Article date: 2024-05-25"
                        Output:
                        {
                        "threat_event": false,
                        "planned_event": true,
                        "planned_event_date": "2024-06-10"
                        }
                        (Reasoning: The union announced a confirmed protest with date and place outside a negotiation context—a planned_event.)

                        Example 3
                        Input: "حذرت الجمعية من القيام باعتصام إذا لم يبدأ الحوار مع السلطات قريباً. Article date: 2024-08-20"
                        Output:
                        {
                        "threat_event": true,
                        "planned_event": false,
                        "planned_event_date": null
                        }

                        Example 4
                        Input: "أعلنت جماعة الناشطين عن تنظيم اعتصام يوم السبت القادم ردا على اهمال مطالبهم. Article date: 2024-07-10"
                        Output:
                        {
                        "threat_event": false,
                        "planned_event": true,
                        "planned_event_date": "2024-07-13"
                        }

                        Important:
                        - Always reason about negotiation/conversation context before classifying.
                        - If the event has already taken place, it should be classified as neither threat nor planned.
                        - Use the article date to resolve any relative dates, but only if the time frame is clearly mentioned.
                        - Only produce the JSON output as shown, with all keys present and dates in correct fields or null.

                        REMINDER:
                        Classify the protest event from the provided Arabic passage as either a "threat_event" (negotiation context) or "planned_event" (confirmed future event), extract the event date if given, and output a strict JSON object with boolean and date values only, as in the examples.
        """,

        "response_format": "json_object",
        "temperature": 0.10,
        "top_p": 0.20
    },

    "commemorative_extractor": {
        "model": "gpt-4o",
        "system_prompt": """
                    Determine whether the provided Arabic passage describing a protest event is commemorative. The passage must explicitly state that the protest is held to mark an annual or historical event. Only classify as commemorative if the event is conducted intentionally for this commemorative reason.

                    For your output, always respond with a JSON object containing:
                    - commemorative: true if the passage clearly marks a commemorative event; otherwise, false.
                    - commemorative_name: The specific name of the memorial day or historical event commemorated (as directly mentioned in or can be precisely inferred from the passage), or null if not applicable.

                    Before delivering your answer, internally reason step-by-step about whether the passage meets these commemorative criteria, and only produce the classification and details after the justification is complete (reasoning comes before conclusion in any example). If the passage is ambiguous or does not make the commemorative purpose explicit, set both keys respectively as false and null. And only respond with the required JSON object.

                    ### Output Format
                    Always produce a JSON (no code block) with these keys:
                    {
                    "commemorative": true/false,
                    "commemorative_name": "name" or null
                    }

                    ### Examples

                    #### Example 1
                    **Input:**
                    "مظاهرة بمناسبة يوم العمال"

                    **Output:**
                    {
                    "commemorative": true,
                    "commemorative_name": "يوم العمال"
                    }

                    -------

                    #### Example 2
                    **Input:**
                    "اعتصم اهالي اربد في ذكرى النكبة تنديدا بالاحتلال"

                    **Output:**
                    {
                    "commemorative": true,
                    "commemorative_name": "ذكرى النكبة"
                    }

                    -------

                    #### Example 3
                    **Input:**
                    "تجمع العشرات في وسط البلد للاحتجاج على الغلاء"

                    **Output:**
                    {
                    "commemorative": false,
                    "commemorative_name": null
                    }

                    -------

                    #### Example 4
                    **Input:**
                    "نظمت جمعية النساء فعالية لدعم حقوق المرأة"

                    **Output:**
                    {
                    "commemorative": false,
                    "commemorative_name": null
                    }

                    ---

                    **Important:**
                    - Always reason before delivering the JSON (never classify without internal justification).
                    - Only classify as commemorative if the commemorative context is explicit or unambiguously implied by naming a day/anniversary/historical event.
                    - Output: Single JSON object, no surrounding text or code blocks, and no reasoning or explanation outside the JSON.

                    ---

                    **REMINDER:**
                    Your main goal is to examine if the Arabic protest passage is intentionally commemorative (marking a historical or annual event), and respond only with the required JSON. Reason first, then give result.

        """,

        "response_format": "json_object",
        "temperature": 0.10,
        "top_p": 0.20
    },

    "location_extractor": {
        "model": "gpt-4o",
        "system_prompt": """
                        Extract all available protest event location details from the provided Arabic passage, including governorate, district, town, neighborhood, and specific site names (if stated or implied), with explicit distinction between start and end locations. Produce the output as a single nested JSON object containing two sub-objects: one for the start location and one for the end location. Each sub-object must contain the same set of fields. If a field is not mentioned in the text, set its value to null.

                        # Steps

                        1. Read the provided Arabic passage fully.
                        2. Carefully identify all explicit or implicit details for:
                        - Where the protest started, and (if different or if the protest moved) where it ended.
                        - This may include:
                                - Governorate (المحافظة)
                                - District (اللواء أو المنطقة)
                                - Town/City (المدينة أو البلدة)
                                - Neighborhood (الحي أو المنطقة الأصغر)
                                - Name_of_location (institution, square, street, etc.)
                        3. Populate a JSON object with two nested sub-objects:
                            - "start_location": the extracted details of the protest's starting point
                            - "end_location": the extracted details of the protest's endpoint (if no movement or endpoint is provided set the values to null)
                        4. For both sub-objects, include these keys: "Governorate", "District", "Town", "Neighborhood", "Name_of_location".
                        5. Set any field not present in the text to null.
                        6. Output only the single nested JSON object.
                        7. Do not provide any explanation, extra text, or formatting outside the JSON.

                        # Output Format

                        - Output a single nested JSON object with exactly three keys: "start_location", "end_location".
                            - "start_location" and "end_location" are JSON objects with the following keys: "Governorate", "District", "Town", "Neighborhood", "Name_of_location".
                            - All string field values must be quoted.
                            - If any field (in either sub-object) is absent, set its value to null.

                        Example expected structure:
                        {
                        "start_location": {
                            "Governorate": "...",
                            "District": ...,
                            "Town": ...,
                            "Neighborhood": ...,
                            "Name_of_location": ...,
                        },
                        "end_location": {
                            "end_Governorate": "...",
                            "end_District": ...,
                            "end_Town": ...,
                            "end_Neighborhood": ...,
                            "end_Name_of_location": ...,
                        }

                        # Examples

                        **Example Input 1:**
                        نظم الحراك الشبابي الشعبي في محافظة الكرك مسيرة انطلقت بعد صلاة الجمعة من ميدان صلاح الدين الايوبي بوسط المدينة وانتهت في ساحة مدرسة الكرك الثانوية

                        **Expected Output 1:**
                        {
                        "start_location": {
                            "Governorate": "الكرك",
                            "District": null,
                            "Town": null,
                            "Neighborhood": null,
                            "Name_of_location": "ميدان صلاح الدين الايوبي",
                        },
                        "end_location": {
                            "end_Governorate": "الكرك",
                            "end_District": null,
                            "end_Town": null,
                            "end_Neighborhood": null,
                            "end_Name_of_location": "ساحة مدرسة الكرك الثانوية",
                        },

                        ---

                        **Example Input 2:**
                        انطلقت مسيرات واعتصامات في محافظات الشمال طالبت برحيل الحكومة، واعتبر مراقبون أن المسيرات والاعتصامات تميزت برفع شعارات تجاوزت الخطوط الحمراء لاسيما في محافظة جرش. مسيرة اربد : نظمت الحركة الاسلامية في محافظة اربد مسيرة جماهيرية حاشدة انطلقت من امام مسجد جامعة اليرموك. وتأتي هذه المسيرة في سياق الفعاليات التي دعت الحركة الاسلامية لتنظيمها في كافة محافظات المملكة

                        **Expected Output 2:**
                        {
                        "start_location": {
                            "Governorate": "اربد",
                            "District": null,
                            "Town": null,
                            "Neighborhood": null,
                            "Name_of_location": "مسجد جامعة اليرموك",
                        },
                        "end_location": {
                            "end_Governorate": null,
                            "end_District": null,
                            "end_Town": null,
                            "end_Neighborhood": null,
                            "end_Name_of_location": null
                        }

                        ---

                        *Note:* Real input passages may be longer and more complex; ensure all possible location fields are extracted or left null if absent.

                        # Notes

                        - Only output the single nested JSON object, formatted as shown above; do not include explanation, notes, or code formatting.
                        - Extract as much location detail as possible; fields not present in Arabic text must be set to null.
                        - If no protest movement is mentioned, set the values for "end_location" to null.
                        - Always follow the JSON key order as shown in the examples.

                        **REMINDER:**
                        Output a single nested JSON object with "start_location", and "end_location" keys. "start_location" and "end_location" each contain the full set of specified location fields. Do not output multiple JSONs or any additional text.
        """,

        "response_format": "json_object",
        "temperature": 0.10,
        "top_p": 0.20
    },

    "multi_sited_extractor": {
        "model": "gpt-4o",
        "system_prompt": """
                    Determine whether the provided Arabic passage describing a protest event and determine the following, using only internal reasoning (do not output your analytical steps):

                    - Whether the protest is multi-sited—occurring simultaneously or as part of a coordinated wave across multiple distinct locations (within a city, across cities, nationwide).
                    - If so, generate a unique tag for the event: "MULTISITE-[YYYYMMDD]-[random alphanumeric]" where [YYYYMMDD] is the date (from the passage or "UNKNOWNDATE" if not provided) and [random alphanumeric] is a unique 6-character string.
                    - Whether the passage describes an event that is part of, or describes, a series of strikes or protest actions occurring in many locations at once or at a national level.
                    - Whether the protest described is a recurring protest event.

                    Your output must be a single JSON object containing only the following fields:

                    - "multi_sited": boolean (true or false)
                    - "multi_site_tag": string (if multi_sited is true, the constructed tag as specified; null otherwise)
                    - "national_strike": boolean (true if the event is part of, or describes, a wave/series of strikes or protest actions in many locations or nationwide; false otherwise)
                    - "is_recurring": boolean (true if the protest is recurring, as indicated in the passage; false otherwise)

                    Base your evaluation on careful internal reasoning that considers:
                    - Mentions of multiple locations (locations, cities, regions, nationwide)
                    - Explicit statements of simultaneity, coordination, series, or recurring actions
                    - Phrases indicating waves, nationwide movement, or temporally distributed events
                    - Any temporal or organizational cues for multi-sited, series, or recurring character

                    # Steps

                    1. Analyze the passage internally for evidence of multi-sitedness, series/national coordination, and recurrence.
                    2. Determine and set "multi_sited" (true/false).
                    3. If multi_sited, construct a random tag ("MULTISITE-[YYYYMMDD]-[random alphanumeric]") or use "UNKNOWNDATE" if no date is found; otherwise set "multi_site_tag" to null.
                    4. Determine and set "national_strike" (true/false) based on whether this event part of or describing a series of srtikes taking place in many locations at the same time or on a national level.
                    5. Determine and set "is_recurring" (true/false) according to any indication of repeated protest activity.
                    6. Output only the JSON object as described.

                    # Output Format

                    Output only a single JSON object with these four fields (no other text, no reasoning):

                    {
                    "multi_sited": [true|false],
                    "multi_site_tag": [string|null],
                    "national_strike": [true|false],
                    "is_recurring": [true|false]
                    }

                    Replace the values in brackets according to your determinations.

                    # Examples

                    Example 1:
                    Input: "اندلعت احتجاجات في ثلاث مدن مختلفة في نفس الليلة، حيث خرج المتظاهرون إلى الشوارع للمطالبة بالإصلاح. التاريخ: 2021-09-15."
                    Output:
                    {
                    "multi_sited": true,
                    "multi_site_tag": "MULTISITE-20210915-3F2XA7",
                    "national_strike": false,
                    "is_recurring": false
                    }

                    Example 2:
                    Input: "خرج المتظاهرون في مظاهرة للاحتجاج على غلاء الأسعار."
                    Output:
                    {
                    "multi_sited": false,
                    "multi_site_tag": null,
                    "national_strike": false,
                    "is_recurring": false
                    }

                    Example 3:
                    Input: "شهدت البلاد موجة من الاحتجاجات المتزامنة في مختلف المدن، بدعوة من الحراك للنزول إلى الشوارع. التاريخ: "
                    Output:
                    {
                    "multi_sited": true,
                    "multi_site_tag": "MULTISITE-UNKNOWNDATE-K1BZQ8",
                    "national_strike": false,
                    "is_recurring": false
                    }

                    (For "multi_site_tag", the random 6-character string must be newly generated for each response; use "UNKNOWNDATE" if no date is available.)

                    # Notes

                    - Do not include any reasoning or analytical steps in your output—output only the required JSON object.
                    - The "multi_sited" value is per location object and should reflect whether the event, as described, is part of a multi-location protest or wave.
                    - "multi_site_tag" must be a unique string for each multi-sited event and must always follow the correct format.
                    - The "national_strike" value should be true only if the event is explicitly a strike AND is described as occurring at a national level or across multiple locations simultaneously (e.g., "إضراب وطني", "إضراب عام في جميع المحافظات"). If the event is not a strike or is only a local strike, set to false.
                    - "is_recurring" is true only if the protest is indicated as recurring or repeated in the passage.

                    """,
        "response_format": "json_object",
        "temperature": 0.10,
        "top_p": 0.20
    },

    "participants_extractor": {
        "model": "gpt-4o",
        "system_prompt": """
                    Extract information about participant groups from an Arabic passage about a protest event, identify their types from a fixed category list, and provide all details in the exact JSON structure below. In addition, if and only if laborers or unemployed participated in the event, extract further laborer-related workplace and sector details as specified. If laborers or unemployed did not participate, leave all new labor-specific fields blank (null or [null]). Never invent details or make unsupported inferences.

                    Analyze the passage for explicit or implied participant groups, focusing on keywords such as "شارك" (participated), "انضم" (joined), etc.

                    - Use THIS list strictly for choosing participants types:
                    [Unidentified, families, members of tribes, youth, political party members, activist group members, civil society organizations, labor unions, high school students, university students, employees, business owners, laborers, farmers, unemployed individuals].

                    - Output must use these JSON fields and logic:
                        - "participants_type_original": Array of Arabic group type references as in the passage (if any; or null if not stated).
                        - "Participant_type_1": The main category from the above list, or null if none.
                        - "Participant_type_2": Second category from the list, or null.
                        - "Participant_type_3": Third category from the list, or null.
                        - "participants_num": One of '1-10', '10-100', '100-1000', '1000+', or null.
                        - "participants_num_text": Exact phrase from the passage indicating participant number, or null.
                        - "Participating group": Array of all group names/phrases as stated in the text, or null (capture actual group names or descriptors).
                        - If “laborers” participated (i.e., “Participant_type_1”, “Participant_type_2”, or “Participant_type_3” is “laborers” or “unemployed individuals”), extract the following further fields; otherwise, set them to null (or [null] for array fields):
                            - "sector": Array listing all that apply from [Public, Private, Other, Unemployed], or [null] if not specified or laborers and unemployed did not participate.
                            - "protesters_occupation": Array(s) listing all stated occupations/roles of laborer participants as given in the passage, or [null].
                            - "Work_space": True if a workplace or workplaces are explicitly named in the article for laborers, False if explicitly stated they are not mentioned, or null if unclear or laborers not present.
                            - "Same_workspace": True if it is explicit that all laborer participants are from the same workspace, False if explicitly from different workplaces, or null if unclear or laborers not present.
                            - "Work_space_name": Array containing the names of workspaces if present in the article for laborers, or [null] if not stated.

                    Guidelines:
                    - Do NOT invent or infer group types, laborer details, or workplace names/attributes unless explicit or clearly implied.
                    - Do NOT add group types or names unless supported by the passage.
                    - If only a generic reference is present (e.g., "عدد من الحضور", "المشاركين"), set all fields to null except set "participants_num_text".
                    - Do not mix families or residents with tribes; tribes must be explicitly mentioned as "عشيرة", "قبيلة", "أفراد من قبيلة", etc.
                    - The number should only reflect actual number of participants who were present or took part of the event.
                    - Output MUST be a valid JSON object, no code block, no extra text.
                    - "null" here means the JSON null type, not the string "null".
                    - For fields with array values, output [null] if absent or no value is extracted; for single-value fields, use null.
                    - For the labor-specific five fields, only fill if laborers participated, otherwise all must be their null value ([null], null, or as applicable).
                    - If no participants/groups are found, all fields should be null or [null] as described.

                    # Steps

                    1. Read the Arabic passage.
                    2. Identify specific or implied references to participant group types and extract their Arabic names for "participants_type_original" (as an array).
                    3. Match up to three distinct group types to the category list, assign these to "Participant_type_1", "Participant_type_2", "Participant_type_3".
                    4. Extract all group/participant names/phrases as stated for "Participating group" (as an array).
                    5. Extract participant number range if present ("participants_num") and the exact phrase about numbers ("participants_num_text"), otherwise use null.
                    6. If laborers participated, extract:
                        - "sector" (from [Public, Private, Other, Unemployed])
                        - "protesters_occupation" (list all occupations/roles as stated for laborers)
                        - "Work_space" (True/False/null: is workplace(s) mentioned?)
                        - "Same_workspace" (True/False/null: all laborers from the same workspace?)
                        - "Work_space_name" (array of all workplace names as directly mentioned)
                    Otherwise, leave these fields blank ([null]/null as appropriate).
                    7. Output the completed JSON object according to the strict field scheme below.

                    # Output Format

                    Output must be a single valid JSON object using these exact fields and logic:

                    {
                    "participants_type_original": [array of group type mentions from passage as stated, or null],
                    "Participant_type_1": "<category from list, or null>",
                    "Participant_type_2": "<second category from list, or null>",
                    "Participant_type_3": "<third category from list, or null>",
                    "participants_num": "<1-10; 10-100; 100-1000; 1000+; or null>",
                    "participants_num_text": "<exact participant number phrase in Arabic, or null>",
                    "Participating group": [array of group names as stated in text, or null],
                    "sector": [array of any of: Public, Private, Other, Unemployed; or [null]],
                    "protesters_occupation": [array of occupation/role mentions as stated, or [null]],
                    "Work_space": true/false/null,
                    "Same_workspace": true/false/null,
                    "Work_space_name": [array of workplace names as mentioned, or [null]]
                    }

                    All values except the arrays should be either the required text value or null (not empty strings, not the string "null"). All array fields must be [null] if no value is extracted (never use empty lists or empty strings).

                    # Examples

                    Example 1:
                    Arabic Input:
                    "شارك طلاب الجامعة الأمريكية وأعضاء النقابات في الاحتجاجات التي حضرها أكثر من مئة شخص."

                    JSON Output:
                    {
                    "participants_type_original": ["طلاب الجامعة الأمريكية", "أعضاء النقابات"],
                    "Participant_type_1": "university students",
                    "Participant_type_2": "labor unions",
                    "Participant_type_3": null,
                    "participants_num": "100-1000",
                    "participants_num_text": "أكثر من مئة شخص",
                    "Participating group": ["طلاب الجامعة الأمريكية", "أعضاء النقابات"],
                    "sector": [null],
                    "protesters_occupation": [null],
                    "Work_space": null,
                    "Same_workspace": null,
                    "Work_space_name": [null]
                    }

                    Example 2:
                    Arabic Input:
                    "انضم شباب ورجال أعمال إلى الاعتصام أمام البرلمان."

                    JSON Output:
                    {
                    "participants_type_original": ["شباب", "رجال أعمال"],
                    "Participant_type_1": "youth",
                    "Participant_type_2": "business owners",
                    "Participant_type_3": null,
                    "participants_num": null,
                    "participants_num_text": null,
                    "Participating group": ["شباب", "رجال أعمال"],
                    "sector": [null],
                    "protesters_occupation": [null],
                    "Work_space": null,
                    "Same_workspace": null,
                    "Work_space_name": [null]
                    }

                    Example 3:
                    Arabic Input:
                    "احتشد عدد كبير من الأشخاص في الساحة."

                    JSON Output:
                    {
                    "participants_type_original": null,
                    "Participant_type_1": null,
                    "Participant_type_2": null,
                    "Participant_type_3": null,
                    "participants_num": null,
                    "participants_num_text": "عدد كبير من الأشخاص",
                    "Participating group": null,
                    "sector": [null],
                    "protesters_occupation": [null],
                    "Work_space": null,
                    "Same_workspace": null,
                    "Work_space_name": [null]
                    }

                    Example 4 (Laborers with workplace details):
                    Arabic Input:
                    "شارك عمال شركة النسيج الحديثة في الإضراب العام الذي ضم حوالي خمسين شخصا من القطاع الخاص في مقر الشركة."

                    JSON Output:
                    {
                    "participants_type_original": ["عمال شركة النسيج الحديثة"],
                    "Participant_type_1": "laborers",
                    "Participant_type_2": null,
                    "Participant_type_3": null,
                    "participants_num": "10-100",
                    "participants_num_text": "حوالي خمسين شخصا",
                    "Participating group": ["عمال شركة النسيج الحديثة"],
                    "sector": ["Private"],
                    "protesters_occupation": ["عمال"],
                    "Work_space": true,
                    "Same_workspace": true,
                    "Work_space_name": ["شركة النسيج الحديثة"]
                    }

                    # Notes

                    - Only use null (not empty string) or [null] for absent values or arrays.
                    - Do not invent information; extract only what is specific or clearly implied.
                    - Fill the five labor-specific fields ONLY if laborers participated. Always use [null] or null otherwise.
                    - The number of participants should refer strictly to the count of people who actually joined and took part in the event.
                    - Never output any explanatory text, or code block formatting (no backticks).
                    - The order and names of JSON fields must match exactly.

                    Reminder: Your objective is to extract participant information and, ONLY IF laborers are present, also extract all five additional labor/workplace fields as described. Otherwise, leave these five fields as blank ([null]/null). Output only the finalized JSON object.
        """,

        "response_format": "json_object",
        "temperature": 0.10,
        "top_p": 0.20
    },

    "mediators_extractor": {
        "model": "gpt-4o",
        "system_prompt": """
                    Extract mediators (third-party actors or groups) from an Arabic passage describing a protest event. Do not extract or mention any participant groups or participant-related details in the output. For mediators, strictly identify explicit or implied mediators per the below definition, map to the allowed type lists, and provide results in the outlined JSON format. Never invent mediator details or make unsupported inferences.

                    A "mediator" is a third-party actor or group involved in interactions between the group articulating demands and the target of those demands. This actor is distinct from both the claimant and the target, and may mediate, facilitate communication, issue statements for/against a demand, or observe the process. The mediator may volunteer or be called by either party.

                    Carefully analyze the passage for explicit or implied mediators, focusing on Arabic keywords and statements indicating mediation, facilitation, or intervention (e.g., "توسط", "تدخل", or related statements of facilitation/intervention).

                    - Use THESE lists strictly for mediators:
                        - mediators_type_one and mediators_type_two: [Labor group, political party, civil society organization, activist group, tribe, other]

                    Guidelines:
                    - Do NOT extract or output any information about protest participants/groups; restrict extraction strictly to mediators and third parties.
                    - Do NOT invent or add mediator names or types unless they are explicit or clearly implied by the passage.
                    - Output MUST be a valid JSON object (no code block, no extra text).
                    - For any array field, use [null] if no value is extracted (never empty arrays or empty strings). For single-value fields, use null if absent.
                    - If no mediators are found, set all mediator fields to null or [null] as appropriate.
                    - Adhere strictly to the allowed mediator type list and output field names/order.
                    - For multiple mediators, map each to its correct type in order in the arrays.
                    - If no suitable type is found in the list, use "other".

                    # Steps

                    1. Read the Arabic passage.
                    2. Identify unique mentions of all mediators as defined above, listing their exact names or phrases as stated in the passage.
                    3. For each mediator extracted, determine the best match,  use list: [Labor group, political party, civil society organization, activist group, tribe] or assign null if no match.
                    4. If no mediators are mentioned, set all three fields to null or [null] as described.
                    5. Output the completed JSON object using the prescribed field scheme.

                    # Output Format

                    Output must be a single valid JSON object with these exact fields and logic:

                    {
                    "mediators": [array of mediator names/phrases as stated, or null],
                    "mediators_type_one": [array of types mapping to: Labor group, political party, civil society organization, activist group, tribe, other; or [null]],
                    "mediators_type_two":  [array of types mapping to: Labor group, political party, civil society organization, activist group, tribe, other; or [null]]
                    }

                    All arrays must be [null] if no value is extracted; do not use empty arrays or empty strings.

                    # Examples

                    Example 1
                    Arabic Input:
                    "حضرت نقابة المعلمين الاجتماع بين المحتجين وممثلي الوزارة لإيحاد الحلول"

                    JSON Output:
                    {
                    "mediators": ["نقابة المعلمين"],
                    "mediators_type_one": ["Labor group"],
                    "mediators_type_two": [null]
                    }

                    Example 2
                    Arabic Input:
                    "تدخلت جمعية المتقاعدين و اتحاد العمال لمراقبة سير المباحثات بين الطرفين."

                    JSON Output:
                    {
                    "mediators": ["جمعية المتقاعدين", "اتحاد العمال"],
                    "mediators_type_one": ["civil society organization"],
                    "mediators_type_two": ["Labor group"]
                    }

                    Example 3 (no mediator present)
                    Arabic Input:
                    "اجتمع ممثلي المتظاهرين مع الإدارة لمناقشة مطالبهم."

                    JSON Output:
                    {
                    "mediators": null,
                    "mediators_type_one": [null],
                    "mediators_type_two": [null]
                    }

                    Example 4 (multiple mediators)
                    Arabic Input:
                    "سهلت نقابة العمال ووسيط من منظمة العمل الدولية المفاوضات بين العمال والإدارة."

                    JSON Output:
                    {
                    "mediators": ["نقابة العمال", "منظمة العمل الدولية"],
                    "mediators_type_one": ["Labor group"],
                    "mediators_type_two": ["other"]
                    }

                    # Notes

                    - Never output information about protest participants or groups; only extract and output mediators as defined.
                    - For each mediator, map types to the allowed lists only; assign other if a mediator does not fit a type.
                    - The order of mediators in all arrays must correspond.
                    - If no mediator is found, return null or [null] for every field as shown in Example 3.
                    - Do not output any code block or explanatory text—only the finalized JSON object.

                    Reminder: Extract only mediators from the input passage, using the exact field names and null logic, and do not invent details or output any information about participants.
                    """,

        "response_format": "json_object",
        "temperature": 0.10,
        "top_p": 0.20
    },

    "organizers_extractor": {
        "model": "gpt-4o",
        "system_prompt": """
                        Extract information about protest event organizers from an Arabic passage using the precise field scheme and logic below, focusing on organizing actors and their classifications as detailed.
                        Note that organizer must be an entity (e.g., a group, organization, or institution) that plans or calls for the event, and should not be confused with the group of participants, who just take part in the event.

                        Analyze the passage for explicit or implied references to organizers (who called for, or organized the action), guided by keywords such as "نظّم" (organized), "دعا" (called for), "بقيادة" (led by), etc.

                        - Strictly use this list to determine "organization_actor_type": [Labor group; political party; civil society organization; activist group; tribe].
                        - Output must use these JSON fields and logic:
                            - "organizing_actor": Array of organizer names/actors exactly as phrased in Arabic in the passage (or null if none described).
                            - "organizing_actor_local_class": Name of local branch or explicit local organization/party/union/traditional group as stated (name, or null).
                            - "organizing_actor_national_class": Name of national party/union/movement/tribe or equivalent as stated (name, or null).
                            - "spokesperson_name": Name of individual quoted or referenced speaking on behalf of organizers (if present; name, or null).
                            - "organization_actor_type": One or more values from [Labor group; political party; civil society organization; activist group; tribe] that best describe the organizers, as array (or null if not identified).
                        - Note that an organizer has to be an entity

                        Guidelines:
                        - Only extract organizers and spokespersons if explicitly or clearly implied in the text.
                        - For local/national class fields, only use names/branches as directly stated—do not infer organizational hierarchy if not explicit.
                        - Set any field to null (JSON null) if no relevant information is present.
                        - Do not invent actors, branches, or types beyond what is clearly justified in the passage.
                        - Only output a single, valid JSON object—absolutely no code block, extra text, or explanation.
                        - Do not confuse organizing actors with participants; only extract organizers.
                        - Organizer types definitions:
                            - Labor group: Organized associations of workers, unions, or committees (e.i.: نقابة, اتحاد ).
                            - Political party: Formal political organizations (e.i.: حزب) .
                            - Civil society organization: Non-governmental, non-profit groups (e.g., charities, NGOs, community associations) working on social, cultural, or humanitarian issues (e.i.: جمعية, منظمة).
                            - Activist group: Informal or formal groups mobilized around a specific cause, campaign, or movement (e.g., environmental, human rights, anti-corruption)  (e.i.: ناشطين, حركة).
                            -Tribe: Social group organized around kinship, clan, or ethnic lineage, often with collective leadership or identity (e.i.: عشيرة, قبيلة).

                        # Steps

                        1. Read the Arabic passage thoroughly.
                        2. Identify references to organizing actors, listing names in Arabic as "organizing_actor" (array, null if absent).
                        3. Extract the "organizing_actor_local_class" and "organizing_actor_national_class" as explicitly stated (if present).
                        4. Extract any spokesperson's name if a person is quoted or described as speaking for organizers ("spokesperson_name", Name, or null).
                        5. Assign one or more "organization_actor_type" using the strict type list provided, as an array, or null if not stated.
                        6. Output the full JSON object with fields completed per logic above.

                        # Output Format

                        Return a single valid JSON object with these exact fields and extraction logic:

                        {
                        "organizing_actor": [array of organizer names as stated in Arabic, or null],
                        "organizing_actor_local_class": "<local branch/party/union or group name as stated, or null>",
                        "organizing_actor_national_class": "<national branch/organisation name as stated, or null>",
                        "spokesperson_name": "<Arabic name if present, or null>",
                        "organization_actor_type": [array with one or more types from list, or null]
                        }

                        All values should be either required text, null, or (for arrays) as described—never empty strings and never string "null".

                        # Examples

                        Example 1:
                        Arabic Input:
                        "نظمت النقابة العامة للمعلمين الأردنيين بالتعاون مع فرعها في إربد وقفة احتجاجية أمام وزارة التعليم، وتحدث باسمهم محمد الزعبي."

                        JSON Output:
                        {
                        "organizing_actor": ["فرع النقابة العامة للمعلمين الأردنيين في إربد"],
                        "organizing_actor_local_class": "فرع النقابة العامة للمعلمين الأردنيين في إربد",
                        "organizing_actor_national_class": "النقابة العامة للمعلمين الأردنيين",
                        "spokesperson_name": "محمد الزعبي",
                        "organization_actor_type": ["Labor group"]
                        }

                        Example 2:
                        Arabic Input:
                        "دعا حزب النهضة إلى مظاهرة مركزية في العاصمة بمشاركة متضامنين من جمعيات المجتمع المدني."

                        JSON Output:
                        {
                        "organizing_actor": ["حزب النهضة"],
                        "organizing_actor_local_class": null,
                        "organizing_actor_national_class": "حزب النهضة",
                        "spokesperson_name": null,
                        "organization_actor_type": ["political party"]
                        }

                        Example 3:
                        Arabic Input:
                        "نفذ موظفون في وزارة الصحة، صباح الثلاثاء، اعتصاما أمام مبنى الوزارة"

                        JSON Output:
                        {
                        "organizing_actor": [null],
                        "organizing_actor_local_class": null,
                        "organizing_actor_national_class": null,
                        "spokesperson_name": null,
                        "organization_actor_type": [null]
                        }

                        Example 4:
                        Arabic Input:
                        "تجمّع أهالي إحدى القبائل المحلية للاحتجاج على القرار، وتحدّث باسمهم أحد وجهاء القبيلة."

                        JSON Output:
                        {
                        "organizing_actor": ["أهالي إحدى القبائل المحلية"],
                        "organizing_actor_local_class": "قبائل المحلية",
                        "organizing_actor_national_class": null,
                        "spokesperson_name": null,
                        "organization_actor_type": ["tribe"]
                        }

                        # Notes

                        - Always use the Arabic text as stated for names/branches.
                        - Do not confuse organizers with participants; only extract those who planned, called for, or organized the protest, not merely attendees.
                        - For "organization_actor_type" array: only list types justified directly by the text per the fixed allowed list.
                        - Organizers must be entities that organized or called for the protest, not just attendees, or the people who decided to protest spontaneously.
                        - No field must be omitted. Use null or [null] as defined; no empty strings.
                        - Output must be a single JSON object, no extra wrappers or explanations.

                        Reminder: Your task is to extract protest event organizer information according to these exact specifications, fields, and output format; output only the requested JSON object—no explanations, no code blocks.
        """,

        "response_format": "json_object",
        "temperature": 0.10,
        "top_p": 0.20
    },

    "target_extractor": {
        "model": "gpt-4o",
        "system_prompt": """
                        Extract detailed information about the targeted authorities or entities of a protest demand from an Arabic-language passage. Apply precision and clear logic for identifying and categorizing the target, using only the field scheme, value lists, and steps below.

                        A "target" is any authority, office, or entity explicitly or implicitly addressed by the protesters' demands—who the protest action is seeking to influence or pressure. Do not infer target unless there are clear cues in the text. Targets are generally those to whom the core demands are addressed, or about whom the protest's grievances are directed.

                        Analyze the passage for explicit or clearly implied protest targets using keywords such as "طالب" (demanded), "احتج ضد" (protested against), "ضد قرار" (against [entity] decision), etc. — but only extract targets if clearly connected to the grievance or action described.

                        - Strictly use these lists for "target_category" and "target_level":
                            - "target_category": [government; foreign government; security services; private company]
                            - "target_level": [municipality; governorate; central ministry; Prime Minister; security services; monarch]

                        - If there is more than one explicit target, include "target_category2" for the second category mentioned (otherwise null).

                        Guidelines:
                        - Extract targets only if clearly stated or strongly implied in the passage as the main addressee or object of the protest demand.
                        - Do not infer unstated targets; if target(s) are not specified, set all target fields to null/[null] as applicable.
                        - Assign categories and levels using only the fixed lists, matching as precisely as possible based on the information in the passage.
                        - Do not confuse targets (those demanded-from or opposed) with organizers, participants, or supporters.
                        - If multiple targets are referenced, capture primary and secondary (up to two) as per the scheme.

                        Only output a single, valid JSON object with NO code block, NO explanation, and NO extra text.

                        # Steps

                        1. Read the Arabic passage thoroughly.
                        2. Identify the protest's primary target, explicitly or clearly implied, and extract the "target" field as stated in Arabic (or null if absent).
                        3. Map the target(s) to "target_category" (use only allowed list).
                        4. If a second explicit target is mentioned, extract its category as "target_category2" (or null).
                        5. Assign "target_level" using only the allowed list, choosing the most specific fit based on text.
                        6. Output the completed JSON object per the scheme below. Any field with no relevant information should be set to null.

                        # Output Format

                        Return a single valid JSON object with these exact fields and logic:

                        {
                        "target": "<Target explicitly addressed or described in Arabic, or null>",
                        "target_category": "<One of [Government; foreign government; security services; private company], or null>",
                        "target_category2": "<One of the same list if secondary target present, or null>",
                        "target_level": "<One of [Municipality or municipal individual; governor or governorate; minister or central ministry; Prime Minister; security services; monarch], or null>"
                        }

                        Do not use empty strings or the string "null"—use the JSON value null when needed.

                        # Examples

                        Example 1:
                        Arabic Input:
                        "تظاهر المئات أمام مبنى وزارة التعليم للمطالبة بتحسين ظروف المعلمين."

                        JSON Output:
                        {
                        "target": "وزارة التعليم",
                        "target_category": "government",
                        "target_category2": null,
                        "target_level": "central ministry"
                        }

                        Example 2:
                        Arabic Input:
                        "نفذ السكان وقفة احتجاجية أمام بلدية الزرقاء، مطالبين رئيس البلدية بالاستقالة وتحسين الخدمات."

                        JSON Output:
                        {
                        "target": "بلدية الزرقاء",
                        "target_category": "government",
                        "target_category2": null,
                        "target_level": "municipality"
                        }

                        Example 3:
                        Arabic Input:
                        "احتج أهالي القرية للمطالبة بتحسين الخدمات في المنطقة."

                        JSON Output:
                        {
                        "target": null,
                        "target_category": null,
                        "target_category2": null,
                        "target_level": null
                        }

                        Example 4:
                        Arabic Input:
                        "شارك نشطاء في وقفة أمام السفارة الاميريكية رفضاً لتدخلاتها في الشأن المحلي."

                        JSON Output:
                        {
                        "target": "سفارة دولة أجنبية",
                        "target_category": "foreign government",
                        "target_category2": null,
                        "target_level": null
                        }

                        Example 5:
                        Arabic Input:
                        "نظم المواطنون في اربد وقفة للمطالبة بإقالة المحافظ ومحاسبة جهاز الأمن على تصرفاته."

                        JSON Output:
                        {
                        "target": "محافظ اربد",
                        "target_category": "government",
                        "target_category2": "security services",
                        "target_level": "governorate"
                        }

                        # Notes

                        - Always use the Arabic phrase as stated for the "target" field, but you are allowed to rephrase sometimes for better context if required.
                        - For category and level, only select values from the fixed lists based on explicit or clear information.
                        - "target_category2" is only used if a second explicit target appears.
                        - If no protest target is named or implied, set all fields to null.
                        - Only output a single JSON object—no explanations, extra text, or code blocks.

                        Reminder: Your task is to extract protest target information from the Arabic passage, following the exact guidelines and output format above. Output only the requested JSON object.
        """,

        "response_format": "json_object",
        "temperature": 0.10,
        "top_p": 0.20
    },

    "demand_extractor": {
        "model": "gpt-4o",
        "system_prompt": """
                        Carefully read the provided Arabic passage about a protest event. Analyze the text step-by-step to extract and reason about all relevant information needed to fill the following fields about protest demands, always reasoning about each before providing a final classification or conclusion.

                        The output must be a single JSON object, not wrapped in a code block, and must follow the structure below, including all required fields.

                        Extract and classify according to these fields and rules:

                        - Demands: List the explicit or implicit demands raised by protesters, as stated in the passage.
                        - Demands_classification_one: classify the demand according to one or more of these categories: [Political; Social; Cultural; Religious; Labor; Palestine; International solidarity; Financial]. Multiple categories can be selected.
                        - Demands_classification_two: If there is more than one demand, specify the category or categories for the other demand, using the same list as above. Multiple categories can be selected.
                        - Geographically_concentrated_demand: True or False. Do the protesters' demands call for action that is geographically limited within Jordan?
                        - Slogans: List the slogans used in this event as explicitly stated in the passage, preserving original wording.
                        - Trigger_of_protest: Indicate if the protest responds to a specific recent event, issue, or incident that directly triggered the protest. Mention the reason as stated in the passage. Note That this is not the same as the demands.
                        - Pro-government_event: True/False. Is this a pro-government event?
                        - International_solidarity: If international solidarity is mentioned, list the details as directly stated in the passage.
                        - Solidarity_with_palestine: True/False. Is this an international solidarity event specifically expressing solidarity with Palestine?

                        # Steps

                        1. Read and comprehend the passage fully.
                        2. Identify all explicit and implicit demands; reason through the context.
                        3. For each demand, assign the appropriate categories for Demands_classification_one and Demands_classification_two if there are multiple demands, one classification for each.
                        4. Determine whether the demands are geographically concentrated within Jordan.
                        5. Extract all slogans explicitly mentioned in the passage and list them, preserving original wording. If no slogans are present, return null.
                        6. Identify the trigger of the protest; reason whether the event is a reaction to a recent occurrence, and return it as stated in the passage.
                        7. Assess if the protest is pro-government.
                        8. Extract explicit mentions of international solidarity. If absent, output null.
                        9. Determine whether solidarity with Palestine is a theme of international solidarity for this event.
                        10. Only after all reasoning, produce the final JSON output.

                        # Output Format

                        - Output ONLY a JSON object structured as follows, with all keys required:
                        {
                            "demands": [ ... ],
                            "demands_classification_one": [ ... ],
                            "demands_classification_two":  [ ... ],
                            "geographically_concentrated_demand": true/false,
                            "slogans": [ ... ],
                            "trigger_of_protest": "details as stated" or null,
                            "pro-government_event": true/false,
                            "international_solidarity": "details as stated",
                            "solidarity_with_palestine": true/false
                        }

                        - Never include text outside the JSON object.
                        - If a field is not applicable or information is absent, use an empty array for lists, null for text, and maintain true/false values for boolean fields as required.

                        # Examples

                        **Example Input Passage:**
                        خرج عشرات المواطنين أمام مبنى الوزارة في وقفة احتجاجية مطالبين بخفض أسعار الوقود، كما دعوا الحكومة لمكافحة الفساد الإداري. ورفعوا لافتة كُتب عليها: "لا للفساد!".

                        **Output JSON:**
                        {
                        "demands": [
                            "خفض أسعار الوقود",
                            "مكافحة الفساد الإداري"
                        ],
                        "demands_classification_one": ["Financial"],
                        "demands_classification_two": ["Political"]
                        "geographically_concentrated_demand": true,
                        "slogans": ["لا للفساد"],
                        "trigger_of_protest": null,
                        "pro-government_event": false,
                        "international_solidarity": [],
                        "solidarity_with_palestine": false
                        }

                        (** In real passages, it may be longer and more complex; provide all relevant details for each field as found in the passage.)

                        # Notes

                        - NEVER output anything besides the JSON object in the exact format described above.
                        - If information is not available for a field, use the appropriate empty value.
                        - For categorization, select the relevant category for each demand as justified by the event's context.
                        - Slogans must be as stated in the passage and not artificially generated.
                        - Assume the passage can include explicit and implicit meanings.
                        - Remain persistent: If the passage is complex or ambiguous, continue extraction and classification for all required fields before output.
                        - Do not use code blocks or any additional commentary outside the JSON object.

                        *Reminder: Your task is to extract and classify the demand-relevant information from the passage, and output only the required JSON as specified above.*
        """,

        "response_format": "json_object",
        "temperature": 0.10,
        "top_p": 0.20
    },

    "violence_extractor": {
        "model": "gpt-4o",
        "system_prompt": """
                    Carefully read the provided Arabic passage about a protest event. Analyze the text step-by-step to extract and reason about all explicit violence-related information, always reasoning about each item before providing a final classification or conclusion.

                    The output must be a single JSON object (not in a code block) and must follow the structure below, including all required fields.

                    Extract and classify according to these fields and rules:

                    * "repression": Boolean. true if the passage explicitly reports violence or coercive actions carried out **by actors responding to the protest** (e.g., arrests, use of tear gas, live fire, beatings, detentions, dispersal), otherwise false.
                    * "repression_reports": Array of strings. Exact quoted phrases from the passage **or** very short literal paraphrases strictly confined to what the passage states, describing violence or coercive actions by responding actors. If none, use [].
                    * "responding_actor": Array of strings. Names or descriptions of those responding with violence as **explicitly named in the passage** (e.g., "الشرطة", "قوات الدرك", "الجيش"). If none named, use [].
                    * "responding_actor_class": Array of strings. For each responding actor named, assign one or more classes from: ["Police", "military", "intelligence services", "non-state actors", "null"]. Use "Police" for civilian police/gendarmerie/directions like "قوات الدرك" or "شرطة"; "military" for armed forces/army; "intelligence services" for terms clearly denoting intelligence/security agencies; "non-state actors" for militias or armed civilian groups acting outside state forces; use "null" only when no actor is named or actor cannot be assigned using the passage wording alone. If responding_actor is empty, set this to [].
                    * "protesters_violence": Boolean. true if the passage explicitly reports violent acts committed **by protesters** (e.g., burning tires, throwing stones, assault, property damage), otherwise false.
                    * "protesters_violence_reports": Array of strings. Exact quoted phrases or short literal paraphrases taken strictly from the passage that describe violence by protesters. If none, use [].
                    * "Obstruction_of_space": Boolean. true if the passage explicitly reports protesters blocking or occupying public space (e.g., "أغلقوا الطرق", "أغلقوا المدخل", "أقاموا حواجز", "اعتصام يغلق الشارع"), otherwise false.

                    Precise procedure — follow in order (reason internally; do not output your reasoning):

                    1. Read the Arabic passage carefully and mark only **explicit** statements about violence/coercion by responders, violence by protesters, and blocking/occupation of space. Do **not** infer anything beyond explicit phrases or unambiguous paraphrases in the text.
                    2. Treat ambiguous language as non-violent unless the passage uses words/phrases that clearly indicate violence or coercion (examples: "أطلقوا النار", "انتهكت بالضرب", "حرقوا", "أعمال شغب", "أوقفت بالقوة", "أطلقت الغاز المسيل للدموع", "اعتقال", "تعرضوا للضرب", "أغلقوا الطرق").
                    3. For each violence-related statement you extract, prefer the exact quoted phrase from the passage. If quoting is not possible, create a minimal, literal paraphrase that does not add context, numbers, motives, or inferred details.
                    4. When listing responding_actor, include only the actor names or descriptions as they appear in the passage. If the passage uses a general term (e.g., "قوات الأمن") list that exact term.
                    5. Map each responding_actor to classes using only the passage wording and the provided class definitions. Do not speculate beyond what the wording supports.
                    6. Set Obstruction_of_space = true only if the passage explicitly reports protesters blocking/occupying space; otherwise false.
                    7. Set repression = true only when the passage explicitly reports violent/coercive actions by responding actors; otherwise false.
                    8. Set protesters_violence = true only when the passage explicitly reports violent acts by protesters; otherwise false.
                    9. If multiple distinct actors or acts are mentioned, include all matching items in the arrays in the order they appear in the passage.
                    10. If the passage provides no information for a field, use these defaults:

                        * Boolean fields: false
                        * Array fields: []
                        * If responding_actor is empty, set responding_actor_class to []

                    Output format — the single JSON object must use these exact keys and types (no extra keys, no text outside the JSON):


                    {
                    "repression": boolean,
                    "repression_reports": [string or null],
                    "responding_actor": [string or null],
                    "responding_actor_class": [string or null],
                    "protesters_violence": boolean,
                    "protesters_violence_reports": [string or null],
                    "Obstruction_of_space": boolean
                    }


                    Important rules & reminders:

                    * Rely **only** on explicit content of the passage. **Do not** invent actors, numbers, motives, methods, or outcomes that are not directly stated, and include only info clearly happening during the event itself.
                    * Do **not** include any internal chain-of-thought or step-by-step reasoning in the output — your reasoning must remain internal and silent.
                    * Use quoted phrases from the passage when available; otherwise use strictly literal paraphrases limited to the passage facts.
                    * If a field is not applicable, return the exact default types as specified (no `null` for arrays; use `[]`).
                    * Output exactly one JSON object and nothing else.

                    Example

                    Input passage:
                    "اندلعت اعمال شغب في بلدة جدعا بمحافظة الكرك , حيث قام المئات من ابناء البلدة بحرق الاطارات واغلاق الطرق الرئيسية في البلدة احتجاجا على عدم فصل بلدية الجدعا عن بلدية طلال, مما اثار غضب اهالي البلدة . حيث حضرت على الفور قوات الدرك من اجل السيطرة على الوضع والحد من اعمال الشغب ."

                    Expected JSON output:
                    {
                    "repression": true,
                    "repression_reports": ["حضرت على الفور قوات الدرك من اجل السيطرة على الوضع والحد من اعمال الشغب"],
                    "responding_actor": ["قوات الدرك"],
                    "responding_actor_class": ["Police"],
                    "protesters_violence": true,
                    "protesters_violence_reports": ["قام المئات من ابناء البلدة بحرق الاطارات واغلاق الطرق الرئيسية","اندلعت اعمال شغب"],
                    "Obstruction_of_space": true
                    }

                    Final reminder: analyze the Arabic passage thoroughly, reason internally, and output **only** the single JSON object that conforms exactly to the schema and rules above.

        """,

        "response_format": "json_object",
        "temperature": 0.10,
        "top_p": 0.20
    },

}
