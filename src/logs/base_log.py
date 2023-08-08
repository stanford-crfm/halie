import os
import json
from typing import List

from events.base_event import Event
from utils.stats import (
    get_time, get_time_text_change, get_num_queries,
    get_text_and_mask, get_word_count, apply_ops
)
from utils.name_utils import convert_model_name_coauthor


class Log:
    def __init__(self, path_log: str, metadata: dict):
        self.path = path_log

        self.session_id = os.path.splitext(os.path.basename(path_log))[0]
        assert self.session_id == metadata['verification_code']

        self.worker_id = metadata['worker_id']
        self.domain = metadata['domain']
        self.example = metadata['example']
        self.prompt = metadata['prompt']
        self.mode = metadata['condition']

        self.n = metadata['n']
        self.max_token = metadata['max_tokens']
        self.temperature = metadata['temperature']
        self.top_p = metadata['top_p']
        self.presence_penalty = metadata['presence_penalty']
        self.frequency_penalty = metadata['frequency_penalty']

        self.question_sequence_id = -1
        self.summarization_sequence_id = -1
        if 'iqa_sequence_index' in metadata:
            self.question_sequence_id = int(metadata['iqa_sequence_index'])
        if 'summarization_sequence_index' in metadata:
            self.summarization_sequence_id = int(metadata['summarization_sequence_index'])
        metadata['question_sequence_id'] = self.question_sequence_id
        metadata['summarization_sequence_id'] = self.summarization_sequence_id

        self.model = self._read_model(metadata)
        metadata['model'] = self.model
        self.metadata = metadata

        self.events = self._read_events()
        self.stats = self._get_basic_stats()

    def _read_model(self, metadata: dict) -> str:
        model = 'unknown'
        if metadata['model']:
            model = metadata['model']
        elif metadata['engine']:
            model = metadata['engine']
        elif metadata['crfm']:
            model = metadata['crfm']
        model = convert_model_name_coauthor(model)
        return model

    def _read_events(self) -> List[Event]:
        events = []
        with open(self.path, 'r') as f:
            for line in f:
                events.append(json.loads(line))

        for i, event in enumerate(events):
            if event['eventName'] == 'system-initialize':
                break

        events = [Event(event) for event in events[i:]]

        # Populate doc and mask
        prompt = events[0].doc.strip()

        text = prompt
        mask = 'P' * len(prompt)  # Prompt
        for event in events:
            if event.name in {'text-delete', 'text-insert'}:
                ops = event.text_delta['ops']
                source = event.source
                text, mask = apply_ops(text, mask, ops, source)

            event.doc = text
            event.mask = mask

        return events

    def _get_basic_stats(self) -> dict:
        time = get_time(self.events)
        time_text_change = get_time_text_change(self.events)
        num_queries = get_num_queries(self.events)
        final_text, _ = get_text_and_mask(
            self.events,
            len(self.events),
            remove_prompt=False
        )
        word_count = get_word_count(final_text)

        return {
            'session_id': self.session_id,
            'time': float(time),
            'time_text_change': float(time_text_change),
            'num_queries': int(num_queries),
            'final_text': final_text,
            'word_count': int(word_count),
        }

    def get_metadata(self) -> dict:
        return self.__dict__

    def print_events(self, show_source: bool = False, show_index: bool = False):
        events = self.events
        texts = []

        for i, event in enumerate(events):
            text = ''
            if show_index:
                text += f'{i}. '
            text += event.name
            if show_source:
                text += f' ({event.source})'

            texts.append(text)
        print(', '.join(texts))
