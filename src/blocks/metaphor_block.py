import editdistance
import numpy as np
from typing import List

from blocks.base_block import EventBlock
from utils.text_utils import get_levenshtein_distance
from events.metaphor_event import MetaphorEvent
from logs.metaphor_log import MetaphorLog
from utils.metaphor_utils import get_human_eval


class MetaphorEventBlock(EventBlock):
    def __init__(self, name: str, events: List[MetaphorEvent], log: List[MetaphorLog]):
        super().__init__(name, events, log)

        self.index = int(name.split('-')[-1])  # Starts from 0
        self.norm_index = round(self.index / log.max_index, 2)

        model_completion = self._get_model_completion(events)
        self.model_completion = model_completion
        self.final_sentence = events[-1].text_delta

        self.acceptance = self._get_acceptance(events)

        apt, specific, imageable = get_human_eval(self.final_sentence)
        self.apt = apt
        self.specific = specific
        self.imageable = imageable

        if apt:
            self.overall = np.mean([apt, specific, imageable])
        else:
            self.overall = None

        self.edit_model_final_token = get_levenshtein_distance(
            self.model_completion.split(),
            self.final_sentence.split()
        )
        self.edit_model_final_char = editdistance.eval(
            self.model_completion,
            self.final_sentence
        )

    def _get_model_completion(self, events: List[MetaphorEvent]):
        model_completion = ''
        for i, event in enumerate(events):
            if event.name == 'text-insert' and event.source == 'api':
                try:
                    ops = event.text_delta['ops']
                    for op in ops:
                        if 'insert' in op:
                            model_completion = op['insert'].strip()
                            break
                except Exception as e:
                    print(e)
                    import ipdb
                    ipdb.set_trace()
                    print()
        return model_completion

    def _get_acceptance(self, events: List[MetaphorEvent]):
        open_cnt, select_cnt = 0, 0
        for i, event in enumerate(events):
            if event.name == 'suggestion-open':
                open_cnt += 1
            elif event.name == 'suggestion-select':
                select_cnt += 1
        return round((select_cnt / open_cnt) * 100) if open_cnt > 0 else None

    def to_dict(self):
        return {
            'session_id': self.session_id,
            'worker_id': self.worker_id,

            'order_id': self.index,
            'norm_order_id': self.norm_index,

            'model': self.model,
            'prompt': self.prompt,

            'elapsed_time': self.elapsed_time,
            'num_queries': self.num_queries,
            'num_events': self.num_events,

            'acceptance': self.acceptance,

            'model_completion': self.model_completion,
            'final_sentence': self.final_sentence,
            'edit_model_final_token': self.edit_model_final_token,
            'edit_model_final_char': self.edit_model_final_char,

            'apt': self.apt,
            'specific': self.specific,
            'imageable': self.imageable,
            'overall': self.overall,
        }
