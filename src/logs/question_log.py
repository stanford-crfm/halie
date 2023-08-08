import json
from typing import List

from events.question_event import QuestionEvent
from logs.base_log import Log
from utils.stats import apply_ops


class QuestionLog(Log):
    def __init__(self, path_log: str, metadata: dict):
        super().__init__(path_log, metadata)

    def _read_events(self) -> List[QuestionEvent]:
        events = []
        with open(self.path, 'r') as f:
            for line in f:
                events.append(json.loads(line))

        for i, event in enumerate(events):
            if event['eventName'] == 'system-initialize':
                break

        events = [
            QuestionEvent(event) for event in events[i:]
            if event['eventName'] not in QuestionEvent.unavailable_names
        ]

        # Add a dummy button-next event at the end
        prev_timestamp = events[-1].timestamp
        events.append(QuestionEvent({
            'eventName': 'button-next',
            'eventSource': 'user',
            'eventTimestamp': prev_timestamp,

            'textDelta': '',
            'cursorRange': -1,

            'currentDoc': '',
            'currentCursor': -1,

            'currentSuggestions': [],
        }))

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
