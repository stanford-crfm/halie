import os
import json
import uuid
import collections
from pathlib import Path
from datetime import date, datetime
from time import time, ctime

from reader import update_session_id_history


def get_uuid():
    return uuid.uuid4().hex


def print_verbose(title, arg_dict, verbose, force=False):
    if verbose or force:
        print('=' * 40)
        print(title)
        print('=' * 40)
        for key, value in arg_dict.items():
            print(f'{key}: {value}')
            print('-' * 40)
        print('\n')


def print_current_sessions(sessions, message=''):
    if message:
        print(f'\n{message}\n')

    current_timestamp = time()
    print('=' * 40)
    print(f'Most recent sessions ({ctime(current_timestamp)})')
    print('=' * 40)
    for session_id, session in sessions.items():
        start_timestamp = session['start_timestamp']
        elapsed_from_start = current_timestamp - start_timestamp  # Elapsed time in seconds
        elapsed_from_start = round(elapsed_from_start / 60, 2)  # Elapsed time in minutes

        last_query_timestamp = session['last_query_timestamp']
        elapsed_from_last_query = current_timestamp - last_query_timestamp
        elapsed_from_last_query = round(elapsed_from_last_query / 60, 2)

        active = ' * ' if elapsed_from_last_query < 15 else ''

        if elapsed_from_start < 60:
            elapsed_from_start = f'{str(elapsed_from_start)} min'
            elapsed_from_last_query = f'{str(elapsed_from_last_query)} min'
            print(f'{session_id}\t{elapsed_from_start:20}{elapsed_from_last_query:20}{active}')
    print('')


def retrieve_log_paths(all_log_dir):
    log_paths = dict()
    log_mtimes = dict()

    json_paths = list(Path(all_log_dir).rglob("*.json"))
    jsonl_paths = list(Path(all_log_dir).rglob("*.jsonl"))

    # Prioritize jsonl version
    for path in jsonl_paths:
        path = str(path)
        session_id = os.path.splitext(os.path.basename(path))[0]
        mtime = os.path.getmtime(path)

        if session_id in log_mtimes:
            # If multiple, select the most recent version
            if log_mtimes[session_id] < mtime:
                log_paths[session_id] = path
                log_mtimes[session_id] = mtime
        else:
            log_paths[session_id] = path
            log_mtimes[session_id] = mtime

    for path in json_paths:
        path = str(path)
        session_id = os.path.splitext(os.path.basename(path))[0]
        if session_id not in log_paths:
            log_paths[session_id] = path
    return log_paths


def append_session_to_file(session, session_id_history_path):
    try:
        with open(session_id_history_path, 'a') as f:
            json.dump(session, f)
            f.write('\n')
    except Exception as e:
        print('Failed to write access code history')
        print(e)


def save_log_to_json(path, log):
    with open(path, 'w') as f:  # Overwrite existing file
        json.dump(log, f)


def save_log_to_jsonl(path, log):
    with open(path, 'w') as f:  # Overwrite existing file
        for entry in log:
            json.dump(entry, f)
            f.write('\n')


def compute_stats(log):
    event_names = []
    for event in log:
        event_name = event['eventName']
        if not event_name:
            print(event)
        else:
            event_names.append(event_name)

    event_counter = collections.Counter(event_names)
    stats = {
        'eventCounter': dict(event_counter),
    }
    return stats


def apply_ops(doc, mask, ops, source):
    original_doc = doc
    original_mask = mask

    new_doc = ''
    new_mask = ''
    for i, op in enumerate(ops):

        # Handle retain operation
        if 'retain' in op:
            num_char = op['retain']

            retain_doc = original_doc[:num_char]
            retain_mask = original_mask[:num_char]

            original_doc = original_doc[num_char:]
            original_mask = original_mask[num_char:]

            new_doc = new_doc + retain_doc
            new_mask = new_mask + retain_mask

        # Handle insert operation
        elif 'insert' in op:
            insert_doc = op['insert']

            insert_mask = 'U' * len(insert_doc)  # User
            if source == 'api':
                insert_mask = 'A' * len(insert_doc)  # API

            if isinstance(insert_doc, dict):
                if 'image' in insert_doc:
                    print('Skipping invalid object insertion (image)')
                else:
                    print('Ignore invalid insertions:', op)
                    # Ignore other invalid insertions
                    # Debug if necessary
                    pass
            else:
                new_doc = new_doc + insert_doc
                new_mask = new_mask + insert_mask

        # Handle delete operation
        elif 'delete' in op:
            num_char = op['delete']

            if original_doc:
                original_doc = original_doc[num_char:]
                original_mask = original_mask[num_char:]
            else:
                new_doc = new_doc[:-num_char]
                new_mask = new_mask[:-num_char]

        else:
            # Ignore other operations
            # Debug if necessary
            print('Ignore other operations:', op)
            pass

    final_doc = new_doc + original_doc
    final_mask = new_mask + original_mask
    return final_doc, final_mask


def get_text_and_mask(events, event_id, remove_prompt=True):
    prompt = events[0]['currentDoc'].strip()

    text = prompt
    mask = 'P' * len(prompt)  # Prompt
    for event in events[:event_id]:
        if 'ops' not in event['textDelta']:
            continue
        ops = event['textDelta']['ops']
        source = event['eventSource']
        text, mask = apply_ops(text, mask, ops, source)

    if remove_prompt:
        if 'P' not in mask:
            print('=' * 80)
            print('Could not find the prompt in the final text')
            print('-' * 80)
            print('Prompt:', prompt)
            print('-' * 80)
            print('Final text:', text)
        else:
            end_index = mask.rindex('P')
            text = text[end_index + 1:]
            mask = mask[end_index + 1:]

    return text, mask


def get_last_text_from_log(log):
    for i, event in enumerate(log):
        if event['eventName'] == 'system-initialize':
            break
    log = log[i:]

    text, _ = get_text_and_mask(log, len(log), remove_prompt=False)
    return text


def get_config_for_log(
    session_id,
    session_id_history,
    session_id_history_path
):
    session_id_history = update_session_id_history(
        session_id_history,
        session_id_history_path
    )
    if session_id not in session_id_history:
        print(f'Could not find session history for session ID: {session_id}')
        return ''
    config = session_id_history[session_id]
    return config


def is_expired(
    access_code,
    start_date,
    end_date,
    expire_after,  # hours
    access_code_history,
):
    current = date.today()
    start = date(int(start_date[:4]), int(start_date[4:6]), int(start_date[6:]))
    end = date(int(end_date[:4]), int(end_date[4:6]), int(end_date[6:]))

    # Check start and end date
    if not (start <= current and current <= end):
        print(f'Expired due to date: {start} <= {current} <= {end}')
        return True

    # Check whether access code has been used
    if access_code not in access_code_history:
        return False

    if int(expire_after) < 0:  # Access code that never expires
        return False

    # If used, check if it has passed expiration date
    timestamp = access_code_history[access_code][-1]['start_timestamp']

    current = datetime.now()
    latest = datetime.fromtimestamp(timestamp)
    expiration = latest.replace(hour=latest.hour + int(expire_after))

    if not (current < expiration):
        print(f'Expired due to time: {current} < {expiration}')
        return True

    return False


def convert_iqa_sequence_to_data(
    sequence,
    questions,
    num_questions_per_sequence,
):
    data = []
    for i in range(num_questions_per_sequence):
        question_index = sequence[i]['question_index']
        assistance = sequence[i]['assistance']

        question = questions[question_index]

        data.append({
            'question': question['question'],
            'answer_a': question['answer_a'],
            'answer_b': question['answer_b'],
            'answer_c': question['answer_c'],
            'answer_d': question['answer_d'],
            'answer': question['answer'],
            'assistance': assistance,
        })
    return data


def convert_summarization_sequence_to_data(
    summarization_sequence,
    summarization_samples,
):
    data = []
    for id in summarization_sequence:
        sample = summarization_samples[id]
        data.append({
            'document': sample['document'],
            'summary': sample['summary'],
            'id': id,
        })
    return data
