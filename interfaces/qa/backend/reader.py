import os
import csv
import json
import collections

from access_code import AccessCodeConfig


def read_log(
    log_path
):
    log = []
    if log_path.endswith('.json'):
        with open(log_path, 'r') as f:
            log = json.load(f)
    elif log_path.endswith('.jsonl'):
        with open(log_path, 'r') as f:
            for line in f:
                log.append(json.loads(line))
    else:
        print('Unknown file extension:', log_path)
    return log


def read_examples(
    example_path
):
    examples = {'na': ''}

    if not os.path.exists(example_path):
        print(f'Path does not exist: {example_path}')
        return examples

    paths = []
    for filename in os.listdir(example_path):
        if filename.endswith('txt'):
            paths.append(os.path.join(example_path, filename))

    for path in paths:
        name = os.path.basename(path)[:-4]
        with open(path, 'r') as f:
            text = f.read().replace('\\n', '\n')

        if name not in {'socialmedia', 'story'}:
            text = text + ' '

        if name in {'socialmedia'}:
            text = text + '\n'
        examples[name] = text
    return examples


def read_prompts(
    prompt_path
):
    prompts = {'na': ''}
    with open(prompt_path) as f:
        rows = csv.reader(f, delimiter="\t", quotechar='"')
        for row in rows:
            if len(row) != 3:
                continue

            prompt_code = row[1]
            prompt = row[2].replace('\\n', '\n')
            prompts[prompt_code] = prompt
    return prompts


def read_access_codes(
    data_dir,
    num_sequence,
):
    """
    Read all access codes from data_dir.

    Return a dictionary with access codes as keys and configs as values.
    """
    access_codes = dict()

    # Retrieve all file names that contain 'access_code'
    if not data_dir:
        raise RuntimeError('Need to set path to access code')

    if not os.path.exists(data_dir):
        raise RuntimeError(f'Cannot find access code at {data_dir}')

    paths = []
    for filename in os.listdir(data_dir):
        if 'access_code' in filename and filename.endswith('csv'):
            paths.append(os.path.join(data_dir, filename))

    # Read access codes with configs
    for path in paths:
        with open(path, 'r') as f:
            input_file = csv.DictReader(f)

            for row in input_file:
                if 'access_code' not in row:
                    print(f'Could not find access_code in {path}:\n{row}')
                    continue

                access_code = row['access_code']
                config = AccessCodeConfig(row, data_dir, num_sequence)
                access_codes[access_code] = config
    return access_codes


def read_access_code_history(
    session_id_history_path
):
    access_code_history = collections.defaultdict(list)
    # NOTE Appears to have memory leak
    try:
        with open(session_id_history_path, 'r') as f:
            lines = f.read().split('\n')
            for line in lines:
                if not line:  # Skip empty line at the end
                    continue
                history = json.loads(line)
                access_code = history['access_code']
                access_code_history[access_code].append(history)
    except Exception as e:
        print('Failed to read all access code history')
        print(e)

    return access_code_history


def update_session_id_history(
    session_id_history,
    session_id_history_path
):
    with open(session_id_history_path, 'r') as f:
        lines = f.read().split('\n')
        for line in lines:
            if not line:  # Skip empty line at the end
                continue
            history = json.loads(line)
            session_id = history['session_id']

            # Overwrite with the most recent history
            session_id_history[session_id] = history
    return session_id_history


def read_blocklist(
    blocklist_path
):
    blocklist = set()
    with open(blocklist_path, 'r') as f:
        lines = f.read().split('\n')
        for line in lines:
            if not line:  # Skip empty line at the end
                continue
            blocklist.add(line.strip())
    return blocklist


###############################################################################
# Interactive QA
###############################################################################

def read_iqa_questions(
    path_questions
):
    questions = []
    with open(path_questions, newline='') as csvfile:
        reader = csv.reader(csvfile)
        for row in reader:
            assert len(row) == 6
            questions.append({
                'question': row[0].strip(),
                'answer_a': row[1].strip(),
                'answer_b': row[2].strip(),
                'answer_c': row[3].strip(),
                'answer_d': row[4].strip(),
                'answer': row[5].strip(),
            })
    return questions


def read_iqa_sequences(
    path_sequences,
    num_questions_per_sequence,
):
    sequences = []
    with open(path_sequences, newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            sequence = dict()
            for i in range(num_questions_per_sequence):
                question_index = int(row[f'q_{i}'])
                assistance = row[f'lm_{i}'] == 'True'
                sequence[i] = {
                    'question_index': question_index,
                    'assistance': assistance,
                }
            sequences.append(sequence)
    return sequences


###############################################################################
# Text Summarization
###############################################################################

def read_summarization_samples(
    path_samples,
):
    samples = dict()
    with open(path_samples) as f:
        input_file = csv.DictReader(f)

        for row in input_file:
            document = row['document'].replace('\n', ' ')
            summary = row['summary']
            id = row['id']
            samples[id] = {
                'document': document,
                'summary': summary,
            }
    return samples


def read_summarization_sequences(
    path_sequences,
):
    sequences = []
    with open(path_sequences, 'r') as f:
        for line in filter(None, f.read().split('\n')):
            sequences.append(line.split(', '))
    return sequences
