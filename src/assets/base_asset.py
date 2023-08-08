import os
import csv
import json
import random
import collections
import pandas as pd
from pathlib import Path

from logs.base_log import Log
from utils.name_utils import convert_model_name_coauthor


class Asset:
    def __init__(self, path: str, verbose: bool = False):
        self.path_raw = path
        self._unzip_logs()
        self.session_ids = self._read_session_ids()
        self.session_id_to_metadata = self._read_session_id_to_metadata()
        self.blocklist = self._read_blocklist()
        self.survey_responses = self._read_survey_responses(verbose)
        self.logs = self._read_logs()

    def _unzip_logs(self):
        # Unzip logs if necessary
        path_dir = os.path.join(self.path_raw, 'logs')
        path_zip = os.path.join(self.path_raw, 'logs.zip')
        if not os.path.exists(path_dir):
            os.system(f'unzip {path_zip} -d {self.path_raw}')

    def _read_session_ids(self):
        path = os.path.join(self.path_raw, 'session_ids.txt')

        session_ids = []
        with open(path, 'r') as f:
            session_ids = list(filter(None, f.read().split('\n')))
        return session_ids

    def _read_session_id_to_metadata(self):
        path = os.path.join(self.path_raw, 'logs/session.txt')

        session_id_to_metadata = dict()
        with open(path, 'r') as f:
            for line in f:
                data = json.loads(line)
                session_id = data['session_id']
                if session_id in self.session_ids:
                    session_id_to_metadata[session_id] = data
        return session_id_to_metadata

    def _read_blocklist(self):
        path = os.path.join(self.path_raw, 'blocklist.txt')

        blocklist = []
        if not os.path.exists(path):
            print('Could not find blocklist for this asset')
            return blocklist

        with open(path, 'r') as f:
            blocklist = list(filter(None, f.read().split('\n')))
        return blocklist

    def _read_survey_responses(self, verbose: bool = False):
        path_questions = os.path.join(self.path_raw, 'survey_questions.csv')
        path_responses = os.path.join(self.path_raw, 'survey_responses.csv')

        question_to_code = dict()
        with open(path_questions) as f:
            reader = csv.DictReader(f)

            for row in reader:
                if row['question']:
                    question_to_code[row['question']] = row['code']

        # Create dictionary to remove duplicates based on session_id
        session_id_to_survey_response = dict()
        with open(path_responses) as f:
            reader = csv.DictReader(f)

            for row in reader:
                survey_response = dict()
                for question, value in row.items():
                    question = question.strip()
                    if question in question_to_code and value:
                        code = question_to_code[question]
                        survey_response[code] = value.strip()
                if survey_response['session_id'] in self.session_ids:
                    session_id = survey_response['session_id']
                    if session_id in session_id_to_survey_response:
                        if verbose:
                            print(f'Duplicate survey response for {session_id}')
                            print('Existing:', session_id_to_survey_response[session_id])
                            print('New:', survey_response)
                            print()
                    metadata = self.session_id_to_metadata[session_id]
                    survey_response['model'] = convert_model_name_coauthor(metadata['crfm'])
                    survey_response['prompt'] = metadata['prompt']
                    session_id_to_survey_response[session_id] = survey_response

        survey_responses = list(session_id_to_survey_response.values())
        return survey_responses

    def _read_logs(self):
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
                path_log = session_id_to_path_log[session_id]
                metadata = self.session_id_to_metadata[session_id]
                if 'worker_id' not in metadata:
                    metadata['worker_id'] = session_id_to_worker_id[session_id]
                logs.append(Log(path_log, metadata))
        return logs

    def get_events_dict(self):
        events = []
        for log in self.logs:
            for event in log.events:
                events.append(event.to_dict())
        return events

    def get_dataframe(self):
        session_metadata = []
        for log in self.logs:
            metadata = log.get_metadata()
            session_metadata.append({
                'worker_id': metadata['worker_id'],
                'session_id': metadata['session_id'],
                'model': metadata['model'],
                'mode': metadata['mode'],
            })
        df_session_metadata = pd.DataFrame(session_metadata)

        session_stats = []
        for log in self.logs:
            session_stats.append(log.stats)
        df_session_stats = pd.DataFrame(session_stats)

        df_survey_responses = pd.DataFrame(self.survey_responses)
        columns = ['ease', 'satisfaction', 'confidence', 'ownership']
        for column in columns:
            if column in df_survey_responses:
                df_survey_responses[column] = df_survey_responses[column].apply(pd.to_numeric)

        df_processed = pd.merge(
            df_survey_responses,
            df_session_stats,
            on='session_id',
        )

        df_processed = pd.merge(
            df_processed,
            df_session_metadata,
            on=['session_id', 'worker_id']
        )
        return df_processed

    def print_summary(self):
        print()
        print('=' * 40)
        print('[Asset] Data overview')
        print('=' * 40)

        print(f'Path: {self.path_raw}')
        print(f'Sessions: {len(self.session_ids)}')
        print(f'Metadata: {len(self.session_id_to_metadata)}')
        print(f'Survey responses: {len(self.survey_responses)}')
        print(f'Logs: {len(self.logs)}\n')

        print('Number of unique workers:', len({log.worker_id for log in self.logs}))
        print('Number of sessions per model')
        sessions_per_model = collections.defaultdict(list)
        for log in self.logs:
            sessions_per_model[log.model].append(log)
        for model in ['InstructDavinci', 'InstructBabbage', 'Davinci', 'Jumbo']:
            sessions = sessions_per_model[model]
            print(f'\t{model:20}{len(sessions)}')

    def print_random_event_sequence(
        self,
        num_sample=1,
        show_source=False,
    ):
        print()
        print('=' * 40)
        print('[Asset] Print event sequence of a randomly selected log')
        print('=' * 40)

        logs = random.sample(self.logs, num_sample)
        for log in logs:
            print(log.session_id)
            log.print_events(show_source)
            print()
