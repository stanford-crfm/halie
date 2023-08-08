"""
Functions to read runs of dialogue sessions saved as SQLite.

This file has dependency on the interactive-mode branch stanford-crfm/benchmarking.
"""

import os
import sys
import glob
import pandas as pd
from sqlitedict import SqliteDict

sys.path.append('/Users/minalee/Research/crfm-benchmarking/benchmarking/src')

positive_annotations = ["positive-feedback-utterances", "tangents-utterances", "dataset-specific",
                        "interesting-utterances", "active-utterances"]
negative_annotations = ["preference-utterances", "humanness-utterances", "sensibility-utterances",
                        "specificity-utterances", "negative-feedback-utterances", "making-up-utterances",
                        "consistency-utterances", "boring-utterances", "passive-utterances"
                        ]
# Map ternary questions to two binary questions
ternary_to_binary = {
    "interestingness-utterances": ["interesting-utterances", "boring-utterances"],
    "contribution-utterances": ["active-utterances", "passive-utterances"],
}


def recover_worker_id(session_id):
    session_id_to_worker_id = {
        '5eb5fedf-8f32-4c8f-8b58-dfafe0d6da9c': '5eb5fedf-8f32-4c8f-8b58-dfafe0d6da9c',
        'c18a1b4a-0cf5-4238-9e79-d12399b00d4e': 'c18a1b4a-0cf5-4238-9e79-d12399b00d4e',
        '3094228f-b905-4aa4-afa2-cc46254ed1a5': '3094228f-b905-4aa4-afa2-cc46254ed1a5',
        '4c12fbd3-483c-4786-ab3d-995ffecca755': '4c12fbd3-483c-4786-ab3d-995ffecca755',
        '9e5583e3-bd4a-41d5-b35f-a872935f5459': '9e5583e3-bd4a-41d5-b35f-a872935f5459',
        'ca9706a9-b623-4dc9-b5a2-bb855bfd52ff': 'ca9706a9-b623-4dc9-b5a2-bb855bfd52ff',
        'b66b7cdf-3c74-4fd4-8bc4-0f9c362445b5': 'b66b7cdf-3c74-4fd4-8bc4-0f9c362445b5',
        '507bf460-ba63-4e0d-8f77-2a752f1023c3': '507bf460-ba63-4e0d-8f77-2a752f1023c3',
        'cbdbeedb-cd91-445c-bef9-e1baeeae00b9': 'cbdbeedb-cd91-445c-bef9-e1baeeae00b9',
        'f7a0e9cc-b33b-4bd8-b9f8-ef3486682fb5': 'f7a0e9cc-b33b-4bd8-b9f8-ef3486682fb5',
        '80c4ae62-8c1b-483c-9d13-c33beae9a1eb': '80c4ae62-8c1b-483c-9d13-c33beae9a1eb',
        'fe1dd26e-d123-49fb-9f0e-f784d17349e1': 'fe1dd26e-d123-49fb-9f0e-f784d17349e1',
        '3ec0ca3d-0b27-4114-acbb-f8ab97de4827': '3ec0ca3d-0b27-4114-acbb-f8ab97de4827',
        'd183e6f0-7382-4066-ae0d-dd47e82d2696': 'd183e6f0-7382-4066-ae0d-dd47e82d2696',
        'f042a22a-28e2-49f8-8e8b-39e1cd0093b5': 'f042a22a-28e2-49f8-8e8b-39e1cd0093b5',
    }
    return session_id_to_worker_id[session_id]


def extract_instances(traces, run_args) -> pd.DataFrame:
    """Return a dataframe of instances from the interaction traces"""

    # References are not included
    instances_df = pd.DataFrame.from_dict(({
        'input': t.instance.input,
        'split': t.instance.split,
        'sub_split': t.instance.sub_split,
        'trace_id': tid}
        for tid, t in traces.items() if t.trace_completed)).set_index('trace_id')
    assert instances_df is not None
    return instances_df


def extract_rounds(traces, run_args) -> pd.DataFrame:
    rounds_df = pd.DataFrame([{
        'round_id': rid,
        'user_input': r.user_input.input if r.user_input else None,
        'completion': r.request_state.result.completions[0].text if r.request_state.result else None,
        'generated_toxic': r.generated_toxic,
        'timestamp': r.time,
        'trace_id': str(t._id)}
        for t in traces.values() if t.trace_completed
        for rid, r in enumerate(t.trace)]).set_index(['trace_id', 'round_id'])
    assert rounds_df is not None
    return rounds_df


def get_final_value_binary(question, round_id, selected_rounds):
    if question['tag'] in positive_annotations:
        if round_id in selected_rounds:
            return 1
        return 0
    elif question['tag'] in negative_annotations:
        if round_id in selected_rounds:
            return 0
        return 1
    return 0


def get_final_value_ternary(question, turn_annotation):
    if question in positive_annotations:
        if turn_annotation == "positive":
            return 1
        else:
            return 0
    if question in negative_annotations:
        if turn_annotation == "negative":
            return 1
        else:
            return 0


# Mapping from ternary labels to integers
ternary_map = {'positive': 1, 'neutral': 0, 'negative': -1, None: 0}


def selectedUttToRound(utt_id):
    """Convert from utterance number to round id

    Interaction round consists of two utterances (one from bot and other from human)
        - if it is bot initiated then round 0 contains bot response
        - otherwise user and bot responses are contained in round 0
    Therefore,
        - If user initiated, then utterance at index 1 is from the bot and corresponds to round 1
        - If bot initiated, then 0th utterance if from the bot and corresponds to round 0
    """
    return (utt_id + 1) // 2


def extract_survey(traces, run_args):
    rows = []
    user_initiated = run_args['user_initiated']
    for tid, trace in traces.items():
        if not trace.trace_completed:
            continue
        for survey_id, survey in enumerate(trace.surveys):
            for question in survey.data:
                # Common information to all rows
                base_cols = {'trace_id': tid,
                             'survey_id': survey_id, 'user_id': survey.user_id}
                n_rounds = len(trace.trace)

                # If the first round has no LM completion, then it is user initiated

                if question['type'] == 'freeForm':
                    rows.append({**base_cols, 'round_id': -1, 'type': 'freeForm',
                                'metric': question['tag'], 'value': question['answer'] if 'answer' in question else None})

                elif question['type'] == 'turn-ternary':
                    if user_initiated:
                        rows.append({**base_cols, 'round_id': 0, 'type': 'turn-ternary',
                                    'metric': question['tag'], 'value': None})
                        round_id = 1
                        for turn_annotation in question['turnAnnotations'][1::2]:
                            if turn_annotation is None:
                                # print(survey_id)
                                # print(survey)
                                continue
                            for binary_annotation in ternary_to_binary[question['tag']]:
                                final_value = get_final_value_ternary(
                                    binary_annotation, turn_annotation)
                                rows.append({**base_cols, 'round_id': round_id, 'type': 'final',
                                            'metric': binary_annotation, 'value': final_value})
                            rows.append({**base_cols, 'round_id': round_id, 'type': 'turn-ternary',
                                        'metric': question['tag'], 'value': ternary_map[turn_annotation]})
                            round_id += 1
                    else:
                        round_id = 0
                        for turn_annotation in question['turnAnnotations'][0::2]:
                            rows.append({**base_cols, 'round_id': round_id, 'type': 'turn-ternary',
                                        'metric': question['tag'], 'value': ternary_map[turn_annotation]})
                            for binary_annotation in ternary_to_binary[question['tag']]:
                                final_value = get_final_value_ternary(
                                    binary_annotation, turn_annotation)
                                rows.append({**base_cols, 'round_id': round_id, 'type': 'final',
                                            'metric': binary_annotation, 'value': final_value})
                            round_id += 1

                elif question['type'] == 'turn-binary':
                    # Rounds which were marked as True for the metric
                    selected_rounds = list(
                        map(selectedUttToRound, question['selectedUtterances']))
                    if user_initiated:
                        rows.append({**base_cols, 'round_id': 0, 'type': 'turn-binary',
                                    'metric': question['tag'], 'value': None})
                        round_begin_id = 1
                    else:
                        round_begin_id = 0

                    for round_id in range(round_begin_id, n_rounds):
                        final_value = get_final_value_binary(
                            question, round_id, selected_rounds)
                        rows.append({**base_cols, 'round_id': round_id, 'type': 'turn-binary',
                                    'metric': question['tag'], 'value': round_id in selected_rounds})
                        rows.append({**base_cols, 'round_id': round_id, 'type': 'final',
                                    'metric': question['tag'], 'value': final_value})

                elif question['type'] == 'likert':
                    rows.append({**base_cols, 'round_id': -1, 'type': 'likert', 'metric': question['tag'], 'value': question['options'].index(
                        question['rating']) + 1 if ('rating' in question and question['rating'] in question['options']) else None})
                    # No transformation needed for final value
                    rows.append({**base_cols, 'round_id': -1, 'type': 'final', 'metric': question['tag'], 'value': question['options'].index(
                        question['rating']) + 1 if ('rating' in question and question['rating'] in question['options']) else None})

                else:
                    raise NotImplementedError

    return pd.DataFrame.from_dict(rows)


def traces_df(run_path):
    name, args = os.path.basename(run_path).split(':')
    run_args = {arg.split('=')[0]: arg.split('=')[1]
                for arg in args.split(',')}
    run_args['scenario'] = name
    with SqliteDict(os.path.join(run_path, "interaction_traces.sqlite"), tablename="interaction_traces") as trace_db:
        traces = {k: v for k, v in trace_db.items()}
    instances_df = extract_instances(traces, run_args)
    rounds_df = extract_rounds(traces, run_args)
    survey_df = extract_survey(traces, run_args)
    joined_survey = survey_df.join(instances_df, on=['trace_id']).join(
        rounds_df, on=['trace_id', 'round_id'])
    for k, v in run_args.items():
        joined_survey[k] = v
    return joined_survey


def load_runs(path):
    run_paths = glob.glob(f'{path}/*')
    return pd.concat([traces_df(run_path) for run_path in run_paths])


def count_rounds(df):
    """
    Count number of rounds of conversation (1 round ~= 2 turns)
    """
    count_df = df.query("round_id>=0")[['trace_id', 'round_id']].drop_duplicates().groupby(["trace_id"]).count()
    count_df = count_df.rename(columns={"round_id": "n_rounds"})
    return count_df


def count_user_words(df):
    """
    Count words in user utterances
    """
    count_df = df.query("round_id>0")[["trace_id", "round_id", "user_input"]].drop_duplicates().groupby("trace_id").apply(lambda x: x["user_input"].str.split().str.len()).reset_index().set_index("trace_id")
    count_df = count_df.groupby("trace_id").sum("user_input")
    count_df = count_df.rename(columns={"user_input": "n_user_words"}).drop("level_1", axis=1)
    return count_df


def count_bot_words(df):
    """
    Count words in bot utterances
    """
    count_df = df.query("round_id>0")[["trace_id", "round_id", "completion"]].drop_duplicates().groupby("trace_id").apply(lambda x: x["completion"].str.split().str.len()).reset_index().set_index("trace_id")
    count_df = count_df.groupby("trace_id").sum("completion")
    count_df = count_df.rename(columns={"completion": "n_bot_words"}).drop("level_1", axis=1)
    return count_df


def count_avg_words(df):
    """
    Count avg # of words in user utterances
    """
    count_df = df.query("round_id>0")[["trace_id", "round_id", "user_input"]].drop_duplicates().groupby("trace_id").apply(lambda x: x["user_input"].str.split().str.len()).reset_index().set_index("trace_id")
    count_df = count_df.groupby("trace_id").mean("user_input")
    count_df = count_df.rename(columns={"user_input": "avg_user_words"}).drop("level_1", axis=1)
    return count_df


def add_counts_to_df(df):
    """
    Count turns and words in user and bot utterances and add them to dataframe
    """
    # Do counts
    round_count_df = count_rounds(df)
    user_word_df = count_user_words(df)
    bot_word_df = count_bot_words(df)
    avg_word_df = count_avg_words(df)

    # Join with original df to add values
    count_dfs = [round_count_df, user_word_df, bot_word_df, avg_word_df]
    for count_df in count_dfs:
        df = df.join(count_df, on="trace_id")

    # Return joined df
    return df


def filter_conversation_length(df, min_turns=11, min_words=250):
    """
    Filter based on the conversation length criteria in our front-end, to remove
    Conversations that contained fatal errors
    """
    # Check whether counts have already been added to df
    columns = df.columns
    count_col_names = ["avg_user_words", "n_bot_words", "n_rounds", "n_user_words"]
    for col_name in count_col_names:
        if col_name not in columns:
            df = add_counts_to_df(df)
            break

    # Cache original number of conversations
    n_before = df["trace_id"].nunique()

    # Filter based on number of words
    filter_df = df[(df["n_rounds"] >= min_turns) | (df["n_bot_words"] + df["n_user_words"] >= min_words)]
    n_after = filter_df["trace_id"].nunique()
    print("Removed {} of {} conversations for having insufficient length".format(n_before-n_after, n_before))

    return filter_df


def filter_avg_user_words(df, min_avg_words=3):
    """
    Filter conversations based on avg # of user words, to eliminate spammers
    """
    # Check whether counts have already been added to df
    columns = df.columns
    count_col_names = ["avg_user_words", "n_bot_words", "n_rounds", "n_user_words"]
    for col_name in count_col_names:
        if col_name not in columns:
            df = add_counts_to_df(df)
            break

    # Cache original number of conversations
    n_before = df["trace_id"].nunique()

    # Filter by avg user words
    filter_df = df[df["avg_user_words"] > min_avg_words]
    n_after = filter_df["trace_id"].nunique()
    print("Removed {} of {} conversations for having insufficient user words".format(n_before-n_after, n_before))

    return filter_df


def filter_spam_surveys(df):
    """ Filter surveys with all turn level annotations marked to "None of the Above" """
    binary_nota = df.query('type=="turn-binary"')[['trace_id', 'metric', 'value']]\
                 .groupby('trace_id')['value'].apply(lambda x: True not in set(x))
    ternary_nota = df.query('type=="turn-ternary"')[['trace_id', 'metric', 'value']]\
                 .groupby('trace_id')['value'].apply(lambda x: len({-1, 1} & set(x)) == 0)
    all_nota = binary_nota & ternary_nota
    print(f"For {all_nota.sum()} traces, all turn-level annotations are marked none of the above")
    print(f"Removing the following trace_ids:\n {all_nota.reset_index().query('value')['trace_id']}")

    filtered_df = df.set_index('trace_id').loc[~all_nota].reset_index()

    return filtered_df
