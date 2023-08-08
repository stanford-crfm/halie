import json

from events.summarization_event import SummarizationEvent
from logs.base_log import Log
from utils.stats import apply_ops


class SummarizationLog(Log):
    def __init__(self, path_log, metadata):
        super().__init__(path_log, metadata)
        self.sequence_id = metadata['additional_data']

    def _read_events(self):
        events = []
        with open(self.path, 'r') as f:
            for line in f:
                events.append(json.loads(line))

        for i, event in enumerate(events):
            if event['eventName'] == 'system-initialize':
                break

        events = [
            SummarizationEvent(event) for event in events[i:]
            if event['eventName'] not in SummarizationEvent.unavailable_names
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
