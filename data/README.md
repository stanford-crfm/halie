# Data in HALIE

Our documentation is still under construction. Please reach out to [Mina Lee](https://minalee.info/) at `minalee@stanford.edu` if you have any question or suggestion for improvement.


## Raw data
Raw data contains the raw interaction traces collected for each task, including all logged interaction traces (`logs.zip`) as well as survey questions and responses.  

## Visualizations
To facilitate easier viewing of the raw interaction data, we provide both `static` and dynamic `replay` visualizations, which are directly viewable in any browser after downlading this repository. Both static and replay visualzations are available  complete for the **Crossword puzzles** task, with further information contained in the [README](https://github.com/stanford-crfm/halie/blob/restructure/data/visualizations/crossword/README.md), and static visualizations are available for the **Question answering** task

## Standardized data

To faciliate the analysis of events between humans and LMs across hundreds of interaction sessions, we standardize the data for each task to based on the raw data we collected.
Each task has `event_blocks.csv` and `survey_responses.csv` as well as a few extra files depending on the task.

**Event blocks.** The `event_blocks.csv` file contains the event blocks (i.e., a sequence of events of our interest) that occurred during interaction. The definition of an event block varies by task. Here is how we defined event blocks for each task:

- Social dialogue: each turn is an event block (user writes one message)
- Question answering: each question and answer pair is an event block (user answers a question by querying a system zero or more times)
- Crossword puzzles: each query to the system is an event block (user queries a system once to brainstorm about a clue)
- Text summarization: each original document, machine-generated summary, and edited summary pair is an event block (user edits a machine-generated summary of a document)
- Metaphor generation: each metaphorical sentence is an event block (user writes a metaphorical sentence by querying a system zero or more times)

Our standardized data also includes some relevant statistics, such as the number of queries, the elapsed time, etc. for each event block.

For implementation details, please refer to the `*_block.py` files in `./src/blocks` for each task.

**Survey responses.** the `survey_responses.csv` file contains the survey responses collected after the task.

## Format

### Dialogue (`./assets/std/dialogue/event_blocks.csv`)
Each turn in a dialogue corresponds to a row.

| session_id | worker_id | turn_id | model | prompt | elapsed_time | user_input | model_completion | interesting | boring | preference | humanness | sensibility | specificity | commonsense | empathy | quality_overall |
| -- | -- | -- | -- | -- | -- | -- | -- | -- | -- | -- | -- | -- | -- | -- | -- | -- |
| 24d... | 650... | 1 | InstructBabbage | Robin and Tracy went to school together. Robin helped Tracy study. | 1.2 | I'm so grateful Robin helped me study! I'm not very good at math and this test was extremely important. | That's amazing! What did you learn from him? | 0 | 0 | 1 | 1 | 1 | 1 | 1 | -1 | 4 |
| 24d... | 650... | 2 | InstructBabbage | Robin and Tracy went to school together. Robin helped Tracy study. | 1.65 | I learned some mnemonic devices that helped me remember the proper order of doing things. I also learned how to double check my work. | That sounds like such an important skill to have. | 0 | 0 | 1 | 1 | 1 | 0 | 0 | -1 | 4 |

### Interactive question answering (`./assets/std/question/event_blocks.csv`)

Each question in a quiz corresponds to a row.

| session_id | worker_id | order_id | model | prompt | sequence_id | question_id | question_type | question_category | question_text | choice_a | choice_b | choice_c | choice_d | answer | answer_text | lm_used | user_queries | lm_responses | user_answer | user_correct | elapsed_time | num_queries | num_events |
| -- | -- | -- | -- | -- | -- | -- | -- | -- | -- | -- | -- | -- | -- | -- | -- | -- | -- | -- | -- | -- | -- | -- | -- |
| 000... | A2E... | 0 | InstructDavinci | na | 19 | 5 | ctrl | misc | In the phrase 'Y2K' what does 'K' stand for? | millennium | computer code | catastrophe | thousand | d | thousand | 0 |  |  | d | 1 | 0.15 | 0 | 3 |
| 000... | A2E... | 1 | InstructDavinci | na | 19 | 14 | ctrl | us_fp | "Within the United Nations, real power is located in" | the Security Council. | the Chamber of Deputies. | the Council of Ministers. | the Secretariat. | a | the Security Council. | 0 | | | a | 1 | 0.03 | 0 | 2 |

### Crossword puzzle (`./assets/std/crossword`)

**Fields in `event_blocks.csv`**

Each user query and system response in a crossword puzzle session corresponds to a row.

| session_id | worker_id | order_id | model | prompt | prompt_dataset | clue_num | clue_direction | clue_type | user_query | query_type | completion |
| -- | -- | -- | -- | -- | -- | -- | -- | -- | -- | -- | -- |
| 61_6... | 657... | 0 | InstructDavinci | 61 | NYT-1 | 1 | across | knowledge | modern persia | ['exact', 'keyword'] |  The modern Persian language... |
| 61_6... | 657... | 1 | InstructDavinci | 61 | NYT-1 | 1 | down | N/A | not give an | ['keyword'] |  inch"  This phrase... |

**Fields in `survey_responses.csv`**

* `fluency`: user's survey response to the question "How clear (or fluent) were the responses from the AI Teammate?" on 5-point Likert scale
* `helpfulness`: user's survey response to the question "Independent of its fluency, how helpful was your AI Teammate for solving the crossword puzzle?" on 5-point Likert scale
* `ease`: user's survey response to the question "How easy was it to interact with the AI Teammate?" on 5-point Likert scale
* `joy`: user's survey response to the question "How enjoyable was it to interact with the AI Teammate?" on 5-point Likert scale
  * It contains a value of `-1` if the score is unavailable (due to the late addition of the question).

| session_id | worker_id | model | prompt | prompt_dataset | fluency | helpfulness | ease | joy |
| -- | -- | -- | -- | -- | -- | -- | -- | -- |
| 151_5... | 57c... | Jumbo | 151 | ELECT | 3 | 2 | 3 | 1 |
| 151_0... | 01f... | InstructBabbage | 151 | ELECT | 3 | 1 | 5 | 2 |

### Text summarization (`./assets/std/summarization/event_blocks.csv`)

**Fields in `event_blocks.csv`**
Each document's summary in a writing session corresponds to a row.
* `elapsed_time`: time for editing a system-generated summary
* `document`: document for which a user is asked to evaluate and edit a summary
* `original_summary`: a system-generated summary
* `original_{consistency, relevance, coherency}`: user's evaluation on the system-generated summary
* `edited_summary`: a system-generated summary edited by the user
* `edited_{consistency, relevance, coherency}`: user's evaluation on the edited summary
* `distance`: edit distance between `original_summary` and `edited_summary`
* `original_{consistency, relevance, coherency}_third_party`}: third-party evaluation on the system-generated summary (available for a subset of summaries)
* `edited_{consistency, relevance, coherency}_third_party`: third-party evaluation on the system-generated summary (available for a subset of summaries)

| session_id | worker_id | order_id | model | prompt | elapsed_time | document | original_summary | original_consistency | original_relevance | original_coherency | edited_summary | edited_consistency | edited_relevance | edited_coherency | distance | original_consistency_third_party | original_relevance_third_party |  edited_consistency_third_party | edited_relevance_third_party | edited_coherency_third_party |
| -- | -- | -- | -- | -- | -- | -- | -- | -- | -- | -- | -- | -- | -- | -- | -- | -- | -- | -- | -- | -- |
| 6c4... | A2F... | 0 | Jumbo | 11 | 0.01 | The annual event... | A wakeboarding festival in Gwynedd has been cancelled. | TRUE | TRUE | TRUE | A wakeboarding festival in Gwynedd has been cancelled. | TRUE | TRUE | TRUE | 0 | | | | | | |  
| 6c4... | A2F... | 1 | Jumbo | 11 | 0.78 | About 120 cannabis... | Two men have been arrested after police discovered cannabis plants in Coleraine. | TRUE | TRUE | FALSE | Police discovered 120 cannabis plants in Coleraine worth an estimated £60,000 after two men have been arrested. | TRUE | TRUE | TRUE | 17 | | | | | | |  


**Fields in `survey_responses.csv`**
* `improvement`: user's survey response to the question "The AI assistant improved as I edited more summaries. (1: strongly disagree / 5: strongly agree)" on 5-point Likert scale
* `edit`: user's survey response to the question "How much did you have to edit the generated summaries? (1: nothing at all / 5: almost every word)" on 5-point Likert scale
* `helpfulness`: user's survey response to the question "How helpful was having access to the AI assistant as an automated summarization tool? (1: not helpful at all / 5: extremely helpful)" on 5-point Likert scale

| session_id | worker_id | model | prompt | prompt_dataset | fluency | helpfulness | ease | joy |
| -- | -- | -- | -- | -- | -- | -- | -- | -- |
| 151_5... | 57c... | Jumbo | 151 | ELECT | 3 | 2 | 3 | 1 |
| 151_0... | 01f... | InstructBabbage | 151 | ELECT | 3 | 1 | 5 | 2 |


### Metaphor generation (`./assets/std/metaphor/event_blocks.csv`)

Each metaphorical sentence in a writing session corresponds to a row.

| session_id | worker_id | order_id | norm_order_id | model | prompt | elapsed_time | num_queries | num_events | user_query | model_sent | final_sent | edit_model_final | apt | specific | imageable |
| -- | -- | -- | -- | -- | -- | -- | -- | -- | -- | -- | -- | -- | -- | -- | -- |
| 3f3... | Nelson Liu | 0 | 0.0 | Davinci | first | 0.93 | 1 | 54 |  |  | I'm improving step by step. | 27 | 0.5 | 0.0 | 0.5 |
| 3f3... | Nelson Liu | 1 | 0.06 | Davinci | first | 1.05 | 1 | 52 | | That was a step back. | That was a step back. | 0 | 0.0 | 0.0 | 0.0
