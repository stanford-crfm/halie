import pandas as pd
from typing import List
from pandas import DataFrame

from logs.base_log import Log
from blocks.dialogue_block import DialogueEventBlock


class DialogueLog(Log):
    def __init__(self, session_id: str, df_run: DataFrame, metadata: dict):
        self.session_id = session_id
        self.metadata = metadata

        self.worker_id = metadata['worker_id']
        self.domain = metadata['domain']
        self.example = metadata['example']
        self.prompt = metadata['prompt']
        self.prompt_dataset = metadata['domain']
        self.mode = 'both'

        self.n = metadata['n']
        self.max_token = metadata['max_tokens']
        self.temperature = metadata['temperature']
        self.top_p = metadata['top_p']
        self.presence_penalty = metadata['presence_penalty']
        self.frequency_penalty = metadata['frequency_penalty']

        self.model = metadata['model']
        self.event_blocks = self._read_event_blocks(df_run)

    def _read_event_blocks(self, df_run: DataFrame) -> List[DialogueEventBlock]:
        event_blocks = []

        df = df_run[['round_id', 'user_input', 'completion', 'timestamp']].query('round_id > -1')
        df = df.groupby('round_id').aggregate({
            'user_input': 'first',
            'completion': 'first',
            'timestamp': 'first',
        }).reset_index()

        df['timestamp'] = pd.to_datetime(df['timestamp'])

        prev_timestamp = None
        for i, row in df.iterrows():
            round_id = row['round_id']
            if round_id == 0:
                prev_timestamp = row['timestamp']
                continue

            curr_timestamp = row['timestamp']
            elapsed_time = (curr_timestamp - prev_timestamp).seconds / 60  # min
            prev_timestamp = curr_timestamp

            event_blocks.append(DialogueEventBlock(
                name=f'turn-{round_id:02}',
                session_id=self.session_id,
                worker_id=self.worker_id,
                turn_id=round_id,
                model=self.model,
                prompt=self.prompt,
                prompt_dataset=self.prompt_dataset,
                elapsed_time=elapsed_time,
                user_input=row['user_input'],
                model_completion=row['completion'],
            ))
        return event_blocks
