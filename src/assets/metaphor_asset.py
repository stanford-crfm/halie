import os
import csv
import random
import collections
import numpy as np
from typing import List
from pathlib import Path

from assets.base_asset import Asset
from logs.metaphor_log import MetaphorLog
from surveys.metaphor_survey import MetaphorSurvey


class MetaphorAsset(Asset):
    def __init__(self, path_raw: str, verbose: bool = False):
        super().__init__(path_raw, verbose)

    def _read_survey_responses(self, verbose: bool = False) -> List[MetaphorSurvey]:
        path_questions = os.path.join(self.path_raw, 'survey_questions.csv')
        path_responses = os.path.join(self.path_raw, 'survey_responses.csv')

        # Read survey questions to convert to codes
        question_to_code = dict()
        with open(path_questions) as f:
            reader = csv.DictReader(f)

            for row in reader:
                if row['question']:
                    question_to_code[row['question']] = row['code']

        survey_responses = []
        with open(path_responses) as f:
            reader = csv.DictReader(f)

            for row in reader:
                # Read survey response
                survey_response = dict()
                for question, value in row.items():
                    question = question.strip()
                    if question in question_to_code and value:
                        code = question_to_code[question]
                        survey_response[code] = value.strip()

                # Filter out based on session_id
                if survey_response['session_id'] in self.session_ids:
                    session_id = survey_response['session_id']
                    worker_id = survey_response['worker_id']
                    if session_id not in self.session_id_to_metadata:
                        print(session_id)
                        continue

                    metadata = self.session_id_to_metadata[session_id]
                    survey_response = MetaphorSurvey(
                        session_id=session_id,
                        worker_id=worker_id,

                        model=metadata['crfm'],
                        prompt=metadata['example'],

                        fluency=survey_response['fluency'],
                        helpfulness=survey_response['helpfulness'],
                        ease=survey_response['ease'],

                        enjoyment=survey_response['enjoyment'],
                        satisfaction=survey_response['satisfaction'],
                        ownership=survey_response['ownership'],
                        reuse=survey_response['reuse'],
                    )

                    survey_responses.append(survey_response)
        return survey_responses

    def _read_logs(self) -> List[MetaphorLog]:
        path = os.path.join(self.path_raw, 'logs')

        session_id_to_path_log = dict()
        for path in list(Path(path).rglob("*.jsonl")):
            session_id = os.path.splitext(os.path.basename(path))[0]
            session_id_to_path_log[session_id] = path

        session_id_to_worker_id = dict()
        for survey_response in self.survey_responses:
            session_id = survey_response.session_id
            worker_id = survey_response.worker_id
            session_id_to_worker_id[session_id] = worker_id

        logs = []
        for session_id in self.session_ids:
            if session_id in session_id_to_path_log:
                if session_id not in session_id_to_worker_id:
                    print(f'Cannot find {session_id}')
                    continue
                path_log = session_id_to_path_log[session_id]
                metadata = self.session_id_to_metadata[session_id]

                if 'worker_id' not in metadata:
                    metadata['worker_id'] = session_id_to_worker_id[session_id]
                log = MetaphorLog(path_log, metadata)
                logs.append(log)
        return logs

    def check_latency(self):
        print()
        print('=' * 40)
        print('[Asset] Check latency')
        print('=' * 40)

        latency = collections.defaultdict(list)
        for log in self.logs:
            model = log.model
            events = log.events

            start_index, start_timestamp = -1, -1
            end_index, end_timestamp = -1, -1
            for i, event in enumerate(events):
                if event.name == 'suggestion-get':
                    start_index = i
                    start_timestamp = event.timestamp
                elif event.name == 'suggestion-open':
                    end_index = i
                    end_timestamp = event.timestamp

                    elapsed_time = end_timestamp - start_timestamp
                    elapsed_time = round(elapsed_time / 1000 / 60, 2)  # Convert ms to min

                    if start_index < 0:
                        continue

                    if end_index - start_index > 2:
                        # print('Skip potentially invalid event sequence to compute latency:',
                        #       start_index, end_index, elapsed_time)
                        # sequence = ', '.join([e.name for e in events[start_index:end_index]])
                        continue

                    # Reset after adding it
                    latency[model].append(elapsed_time)
                    start_index, start_timestamp = -1, -1
                    end_index, end_timestamp = -1, -1

        for model, elapsed_times in latency.items():
            mean = np.mean(elapsed_times)
            sem = np.std(elapsed_times, ddof=1) / np.sqrt(np.size(elapsed_times))
            print(f'{model:20}{len(elapsed_times):5}{mean:10.2f} (± {sem:.3f})')

    def print_random_final_sentences(self):
        print()
        print('=' * 40)
        print('[Asset] Print final sentences of a randomly selected log')
        print('=' * 40)

        log = random.choice(self.logs)
        print(log.session_id)
        print(log.worker_id)

        for i, sentence in enumerate(log.final_sentences, 1):
            print(f'{i}.', sentence)
