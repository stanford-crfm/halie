from typing import List

from logs.base_log import Log
from events.base_event import Event


class EventBlock:
    def __init__(self, name: str, events: List[Event], log: Log):
        self.name = name

        metadata = log.get_metadata()
        self.session_id = metadata['session_id']
        self.worker_id = metadata['worker_id']

        self.model = metadata['model']
        self.prompt = metadata['prompt']

        self.elapsed_time = self._get_elapsed_time(events)
        self.num_queries = self._get_num_queries(events)
        self.num_events = len(events)

    def _get_elapsed_time(self, events: List[Event]) -> float:
        start = events[0].timestamp
        end = events[-1].timestamp

        elapsed_time = end - start
        elapsed_time = round(elapsed_time / 1000 / 60, 2)  # min
        return elapsed_time

    def _get_num_queries(self, events: List[Event]) -> int:
        num_queries = 0
        for event in events:
            if event.name in {'suggestion-get', 'button-generate'}:
                num_queries += 1
        return num_queries

    def to_dict(self) -> dict:
        return self.__dict__
