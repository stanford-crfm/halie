import os
import math
import pandas as pd
from typing import List
from pandas import DataFrame

from assets.base_asset import Asset
from logs.dialogue_log import DialogueLog
from surveys.dialogue_survey import DialogueSurvey
from utils.name_utils import convert_model_name_dialogue
from utils.dialogue_utils import filter_spam_surveys, filter_avg_user_words, filter_conversation_length, recover_worker_id


class DialogueAsset(Asset):
    def __init__(self, path_raw: str, verbose: bool = False):
        self.path_raw = path_raw
        self._unzip_logs()
        self.runs = self._read_runs()

        self.session_ids = self._get_session_ids()
        self.session_id_to_metadata = self._get_session_id_to_metadata()
        self.blocklist = []  # TODO
        self.logs = self._convert_runs_to_logs(verbose)
        self.survey_responses = self._get_survey_responses()

        # Filter out session with missing metrics in survey
        session_ids_with_missing_metrics = [
            '8844876d-81f4-438c-b4ab-5008444d2170',
            '3ec0ca3d-0b27-4114-acbb-f8ab97de4827',
            '9e5583e3-bd4a-41d5-b35f-a872935f5459',
            '6aaf9bbc-51f1-434e-ba95-e8088580b4f8',
            'f08fbbde-4310-4b81-8b6d-2b39f482a280',
            'b42bb6e3-6ce8-4ff3-a347-70209acc41e2',
            '3094228f-b905-4aa4-afa2-cc46254ed1a5',
            'b66b7cdf-3c74-4fd4-8bc4-0f9c362445b5',
            'c18a1b4a-0cf5-4238-9e79-d12399b00d4e',
            'f042a22a-28e2-49f8-8e8b-39e1cd0093b5',
            'b04e7253-6c17-4b74-b9ab-e4e64db6f507',
            '3527b38c-36bb-4faa-9819-b5dfe8de69f4',
            '792133dd-dd5b-46eb-9aa4-ae6a8d2f7c88',
            '52065c44-35cb-48a2-8496-21587ea79edf',
            '9ace537c-ff89-4911-8495-40bf5294bb09',
            '9efa158f-77f0-4f63-af41-4bec91c8b15d',
            '54fd92ba-f343-4496-b0b8-d3792b230926',
            'd183e6f0-7382-4066-ae0d-dd47e82d2696',
            'b873deb9-f65b-4093-90d6-65ef2461ea0c',
            '80c4ae62-8c1b-483c-9d13-c33beae9a1eb',
            '1085f517-a093-4a24-bd9b-ae15cc6d5cb1',
            'cbdbeedb-cd91-445c-bef9-e1baeeae00b9',
            'ca9706a9-b623-4dc9-b5a2-bb855bfd52ff',
            'ee43d454-9a72-4b9d-b269-7f089454f85c',
            'fe1dd26e-d123-49fb-9f0e-f784d17349e1',
            '507bf460-ba63-4e0d-8f77-2a752f1023c3',
            '5eb5fedf-8f32-4c8f-8b58-dfafe0d6da9c',
            '06d0a7f6-d7ab-4088-a1e6-73ed8e0a60a3',
            'f7a0e9cc-b33b-4bd8-b9f8-ef3486682fb5',
            '4c12fbd3-483c-4786-ab3d-995ffecca755',
            'c0c1580b-0a6a-4298-94e8-e78a0b016442'
        ]
        self.session_ids = self.session_ids - set(session_ids_with_missing_metrics)
        print(f'Filtered {len(session_ids_with_missing_metrics)} sessions with missing metrics')

        self.session_id_to_metadata = {
            session_id: metadata
            for session_id, metadata in self.session_id_to_metadata.items()
            if session_id in self.session_ids
        }
        self.logs = [log for log in self.logs if log.session_id in self.session_ids]
        self.survey_responses = [survey for survey in self.survey_responses if survey.session_id in self.session_ids]

    def _unzip_logs(self):
        path_dir = os.path.join(self.path_raw, 'runs')
        path_zip = os.path.join(self.path_raw, 'logs.zip')
        if not os.path.exists(path_dir):
            os.system(f'unzip {path_zip} -d {self.path_raw}')

    def _read_runs(self) -> DataFrame:
        # Read logs from csv if available
        path = os.path.join(self.path_raw, 'runs.csv')
        if os.path.exists(path):
            df_runs = pd.read_csv(path)
        else:
            """
            Dependency on crfm-benchmarking

            source ~/Research/crfm-benchmarking/benchmarking/venv/bin/activate
            export PYTHONPATH=~/Research/crfm-benchmarking/benchmarking/src
            """
            from utils.dialogue_utils import load_runs
            path = os.path.join(self.path_raw, 'runs')
            df_runs = load_runs(path)

            df_runs = filter_spam_surveys(df_runs)
            df_runs = filter_avg_user_words(df_runs)
            df_runs = filter_conversation_length(df_runs)

            # Save as csv to remove dependency
            path = os.path.join(self.path_raw, 'runs.csv')
            df_runs.to_csv(path, index=False, sep=',')
        return df_runs

    def _get_session_ids(self) -> List[str]:
        session_ids = set(self.runs['trace_id'].to_list())
        print(f'Read {len(session_ids)} sessions')
        return session_ids

    def _get_session_id_to_metadata(self) -> dict:
        session_id_to_metadata = dict()
        for session_id in self.session_ids:
            df = self.runs.query(f'trace_id == "{session_id}"')

            worker_id = df.iloc[0]['user_id']
            domain = df.iloc[0]['scenario']
            if domain == 'commonsense_dialogues':
                domain = 'commonsense_dialogue'
            elif domain == 'empatheticdialogues':
                domain = 'empathetic_dialogue'

            model = convert_model_name_dialogue(df.iloc[0]['model'])
            metadata = {
                'worker_id': worker_id,
                'domain': domain,
                'example': 'dialogue',  # TODO
                'prompt': df.iloc[0]['input'],
                'mode': 'both',

                'n': 1,
                'max_tokens': 50,
                'temperature': 0.9,
                'top_p': 1,
                'presence_penalty': 0,
                'frequency_penalty': 0,

                'model': model,
            }

            session_id_to_metadata[session_id] = metadata

        return session_id_to_metadata

    def _convert_runs_to_logs(self, verbose: bool = False, do_not_allow_multiple_participation: bool = True) -> List[DialogueLog]:
        logs = []
        worker_ids = set()

        for session_id in self.session_ids:
            df_run = self.runs.query(f'trace_id == "{session_id}"')
            metadata = self.session_id_to_metadata[session_id]
            worker_id = metadata['worker_id']

            if do_not_allow_multiple_participation:
                if worker_id in worker_ids:
                    if worker_id == '1':
                        # Manually assign worker ID
                        worker_id = recover_worker_id(session_id)
                        metadata['worker_id'] = worker_id
                    else:
                        print(f'Duplicate participation from {worker_id}')
                        continue

            logs.append(DialogueLog(session_id, df_run, metadata))
            worker_ids.add(worker_id)

        return logs

    def _get_survey_responses(self) -> List[DialogueSurvey]:
        survey_responses = []
        session_ids_with_missing_metrics = set()

        for session_id in self.session_ids:
            df = self.runs.query(f'trace_id == "{session_id}" & type == "final"')
            metadata = self.session_id_to_metadata[session_id]
            worker_id = metadata['worker_id']

            turn_ids = list(range(df['round_id'].min(), df['round_id'].max() + 1))
            turn_ids.remove(0)
            for turn_id in turn_ids:
                df_turn = df.query(f'round_id == {turn_id}')

                metrics = [
                    'interesting-utterances', 'boring-utterances',
                    'preference-utterances', 'humanness-utterances', 'sensibility-utterances',
                    'specificity-utterances', 'dataset-specific', 'quality-overall'
                ]
                metric_to_value = dict()

                for metric in metrics:
                    df_turn_metric = df_turn.query(f'metric == "{metric}"')
                    if len(df_turn_metric) == 1:
                        if math.isnan(df_turn_metric['value']):
                            metric_to_value[metric] = None
                        else:
                            metric_to_value[metric] = int(df_turn_metric['value'])
                    elif len(df_turn_metric) == 0:
                        metric_to_value[metric] = None
                    else:
                        import ipdb
                        ipdb.set_trace()
                        print(df_turn_metric)

                # if not metric_to_value['sensibility-utterances'] and not metric_to_value['quality-overall']:
                #     session_ids_with_missing_metrics.add(session_id)

                survey_responses.append(DialogueSurvey(
                    session_id=session_id,
                    worker_id=worker_id,
                    turn_id=turn_id,

                    model=metadata['model'],
                    prompt=metadata['prompt'],

                    interestingness=metric_to_value['interesting-utterances'],
                    boringness=metric_to_value['boring-utterances'],
                    preference=metric_to_value['preference-utterances'],
                    fluency=metric_to_value['humanness-utterances'],
                    sensibility=metric_to_value['sensibility-utterances'],
                    specificity=metric_to_value['specificity-utterances'],
                    humanness=metric_to_value['dataset-specific'],
                    quality=metric_to_value['quality-overall'],
                ))
        print(f'Found {len(session_ids_with_missing_metrics)} sessions with missing metrics')
        return survey_responses
