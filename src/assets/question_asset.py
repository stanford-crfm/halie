import os
import csv
import json
from typing import List
from pathlib import Path

from assets.base_asset import Asset
from logs.question_log import QuestionLog
from surveys.question_survey import QuestionSurvey


class QuestionAsset(Asset):
    def __init__(self, path_raw: str, verbose: bool = False):
        super().__init__(path_raw, verbose)

    def _read_session_id_to_metadata(self) -> dict:
        path = os.path.join(self.path_raw, 'logs/session.txt')

        session_id_to_metadata = dict()
        with open(path, 'r') as f:
            for line in f:
                data = json.loads(line)
                session_id = data['session_id']
                if session_id in self.session_ids:
                    data['prompt'] = data['iqa_sequence_index']
                    session_id_to_metadata[session_id] = data
        return session_id_to_metadata

    def _read_survey_responses(self, verbose: bool = False) -> List[QuestionSurvey]:
        path_questions = os.path.join(self.path_raw, 'survey_questions.csv')
        path_responses = os.path.join(self.path_raw, 'survey_responses.csv')

        # Read survey questions to convert to codes
        question_to_code = dict()
        with open(path_questions) as f:
            reader = csv.DictReader(f)

            for row in reader:
                if row['question']:
                    question_to_code[row['question']] = row['code']

        # Create dictionary to remove duplicates based on session_id and worker_id
        session_id_to_survey_response = dict()
        worker_ids = set()
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
                    metadata = self.session_id_to_metadata[session_id]
                    survey_response = QuestionSurvey(
                        session_id=session_id,
                        worker_id=worker_id,

                        model=metadata['crfm'],
                        prompt=metadata['prompt'],

                        fluency=survey_response['fluency'],
                        helpfulness=survey_response['helpfulness'],
                        ease=survey_response['ease'],

                        helpfulness_freetext=survey_response['helpfulness_freetext'],
                        change_freetext=survey_response['change_freetext'],
                        adjectives=survey_response['adjectives'],
                    )
                    # Handle duplicates based on session_id by overwriting
                    if session_id in session_id_to_survey_response:
                        if verbose:
                            print(f'Duplicate survey response for {session_id}')
                            print('Existing:', session_id_to_survey_response[session_id].to_dict())
                            print('New:', survey_response.to_dict())
                            print()

                    # Handle duplicates based on worker_id by skipping
                    if worker_id in worker_ids:
                        if verbose:
                            print(f'Duplicate participation from {worker_id}')
                            print()
                        continue

                    session_id_to_survey_response[session_id] = survey_response
                    worker_ids.add(worker_id)
            survey_responses = list(session_id_to_survey_response.values())
        return survey_responses

    def _read_logs(self, do_not_allow_multiple_participation: bool = True) -> List[QuestionLog]:
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
                    if session_id not in session_id_to_worker_id:
                        continue
                    metadata['worker_id'] = session_id_to_worker_id[session_id]
                logs.append(QuestionLog(path_log, metadata))

        if do_not_allow_multiple_participation:
            worker_ids = set()  # Filter out multiple participation from same workers
            filtered_logs = []
            for log in logs:
                if log.worker_id in worker_ids:
                    continue
                filtered_logs.append(log)
                worker_ids.add(log.worker_id)
            logs = filtered_logs

        return logs
