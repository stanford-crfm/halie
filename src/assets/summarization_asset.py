import os
import pandas as pd
from typing import List
from pathlib import Path

from assets.base_asset import Asset
from logs.summarization_log import SummarizationLog
from surveys.summarization_survey import SummarizationSurvey
from utils.name_utils import convert_model_name_summarization
from utils.text_utils import normalize_text


class SummarizationAsset(Asset):
    def __init__(self, path_raw, verbose: bool = False):
        self.path_raw = path_raw
        self._unzip_logs()

        self.session_ids = self._read_session_ids()
        self.session_id_to_metadata = self._read_session_id_to_metadata()
        self.blocklist = []  # Did not use blocklist
        self.survey_responses = self._read_survey_responses()
        self.annotations = self._read_third_party_annotations()
        self.logs = self._read_logs()

    def _read_session_ids(self) -> List[str]:
        path = os.path.join(self.path_raw, 'mturk')
        dfs = []
        for file in os.listdir(path):
            if file.endswith('.csv'):
                df = pd.read_csv(os.path.join(path, file))
                dfs.append(df)
        mturk = pd.concat(dfs)

        session_ids = list(set(mturk["Answer.verification-code"]))
        return session_ids

    def _read_survey_responses(self) -> List[SummarizationSurvey]:
        path = os.path.join(self.path_raw, 'mturk')
        dfs = []
        for file in os.listdir(path):
            if file.endswith('.csv'):
                df = pd.read_csv(os.path.join(path, file))
                dfs.append(df)
        df_mturk = pd.concat(dfs)

        survey_responses = []
        for index, row in df_mturk.iterrows():
            for i in range(1, 6):
                if row[f'Answer.assistant_improvement.{i}']:
                    improvement = i
                if row[f'Answer.edit_amount.{i}']:
                    edit = i
                if row[f'Answer.helpfulness.{i}']:
                    helpfulness = i

            survey_responses.append(SummarizationSurvey(
                session_id=row['Answer.verification-code'],
                worker_id=row['WorkerId'],

                model=row['Input.engine'],
                prompt=row['Input.additional_data'],

                improvement=improvement,
                edit=edit,
                helpfulness=helpfulness,

                adjectives=row['Answer.model-adjectives'],
            ))
        return survey_responses

    def _read_logs(self) -> List[SummarizationLog]:
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
                logs.append(SummarizationLog(path_log, metadata))
        return logs

    def _read_third_party_annotations(self) -> List[dict]:
        path = os.path.join(self.path_raw, 'eval')
        dfs = []
        for file in os.listdir(path):
            if file.endswith('.csv'):
                df = pd.read_csv(os.path.join(path, file))
                dfs.append(df)
        df_annotations = pd.concat(dfs)

        annotations = []
        annotators = set()
        for index, row in df_annotations.iterrows():
            for i in range(1, 6):
                if row[f'Answer.coherence.cohere_{i}']:
                    coherency = i
                if row[f'Answer.relevance.rel_{i}']:
                    relevance = i
            consistency = 1 if row['Answer.consistency.consistent'] else 0

            annotations.append({
                'article': row['Input.source_article'],
                'summary': normalize_text(row['Input.output_text']),
                'source': row['Input.output_type'],  # reference, initial_output, reference_output
                'model': convert_model_name_summarization(row['Input.model']),

                'consistency': consistency,
                'relevance': relevance,
                'coherency': coherency,
            })
            annotators.add(row['WorkerId'])
        print(f'The number of unique annotators for third-party evaluation: {len(annotators)}')
        print(f'The total number of annotations for third-party evaluation: {len(annotations)}')
        return annotations
