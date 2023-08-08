import os
import math
import json
from typing import List
from pathlib import Path

from assets.base_asset import Asset
from logs.crossword_log import CrosswordLog
from surveys.crossword_survey import CrosswordSurvey
from utils.name_utils import convert_gid_to_dataset


class CrosswordAsset(Asset):
    """
    Asset for crossword puzzle.
    """

    def __init__(self, path_raw: str, verbose: bool = False):
        self.path_raw = path_raw
        self._unzip_logs()
        
        self.session_ids = self._read_session_ids()
        self.blocklist = self._read_blocklist()
        self.logs = self._read_logs()
        self.survey_responses = self._read_survey_responses(verbose)
        self.session_id_to_metadata = {log.session_id: log.metadata for log in self.logs}

        session_ids_from_logs = {log.session_id for log in self.logs}
        session_ids_from_surveys = {survey_response.session_id for survey_response in self.survey_responses}

        print('Missing survey response for the following session_id')
        print(session_ids_from_logs - session_ids_from_surveys)

    def _read_session_ids(self) -> List[str]:
        path = os.path.join(self.path_raw, 'session_ids.txt')

        session_ids = []
        with open(path, 'r') as f:
            session_ids = list(filter(None, f.read().split('\n')))

        session_ids = ['_'.join(session_id.split('_')[:3]) for session_id in session_ids]

        # Manually remove 61_02fe4addc3d80015a47dc2539391ba93_text-babbage_285_log
        session_ids.remove('61_02fe4addc3d80015a47dc2539391ba93_text-babbage')
        return session_ids

    def _read_survey_responses(self, verbose: bool = False) -> List[CrosswordSurvey]:
        path = os.path.join(self.path_raw, 'survey_responses.json')

        survey_responses = []
        with open(path, 'r') as f:
            data = json.load(f)
            for survey_response in data:
                gid = survey_response['gid']
                worker_id = survey_response['username']
                model = survey_response['model']
                session_id = f'{gid}_{worker_id}_{model}'

                if session_id not in self.session_ids:
                    if verbose:
                        print(f'Exclude survey response for {session_id}')
                    continue

                joy = survey_response['joy']
                if math.isnan(joy):
                    joy = -1  # From old surveys without the question about joy

                survey_responses.append(CrosswordSurvey(
                    session_id=session_id,
                    worker_id=worker_id,

                    model=model,
                    prompt=gid,
                    prompt_dataset=convert_gid_to_dataset(gid),

                    fluency=int(survey_response['fluency']),
                    helpfulness=int(survey_response['helpfulness']),
                    ease=int(survey_response['ease']),
                    joy=int(joy),

                    helpfulness_freetext=survey_response['helpfulness_freetext'],
                    change_freetext=survey_response['time_freetext'],
                    adjectives=survey_response['adjectives'],
                ))
        return survey_responses

    def _read_logs(self) -> List[CrosswordLog]:
        path_logs = os.path.join(self.path_raw, 'logs')
        path_puzzles = os.path.join(self.path_raw, 'puzzles')

        session_id_to_path_log = dict()
        for path in list(Path(path_logs).rglob("*.json")):
            session_id = os.path.splitext(os.path.basename(path))[0]
            session_id = '_'.join(session_id.split('_')[:3])
            session_id_to_path_log[session_id] = path

        logs = []
        for session_id in self.session_ids:
            if session_id in session_id_to_path_log:
                path_log = session_id_to_path_log[session_id]
                logs.append(CrosswordLog(path_log, path_puzzles))
        return logs
