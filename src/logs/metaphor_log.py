import json
from typing import List

from events.metaphor_event import MetaphorEvent
from logs.base_log import Log
from utils.stats import apply_ops


class MetaphorLog(Log):
    def __init__(self, path_log: str, metadata: dict):
        super().__init__(path_log, metadata)
        self.prompt = metadata['example']

        max_index, final_sentences = self._get_final_sentences()
        self.max_index = max_index
        self.final_sentences = final_sentences

    def _read_events(self) -> List[MetaphorEvent]:
        events = []
        with open(self.path, 'r') as f:
            for line in f:
                events.append(json.loads(line))

        for i, event in enumerate(events):
            if event['eventName'] == 'system-initialize':
                break

        events = [
            MetaphorEvent(event, self.metadata) for event in events[i:]
            if event['eventName'] not in MetaphorEvent.unavailable_names
        ]

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

    def _get_final_sentences(self) -> List[str]:
        max_index = 0
        sentences = []
        for event in self.events:
            if event.name in {'template-add', 'sentence-add'}:
                sentence = event.text_delta.strip()
                if sentence:
                    max_index += 1
                    sentences.append(sentence)
            if event.name in {'template-delete', 'sentence-delete'}:
                sentence = event.text_delta.strip()
                sentences.remove(sentence)
        return max_index, sentences
