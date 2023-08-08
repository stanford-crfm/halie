from typing import List

from blocks.base_block import EventBlock
from logs.summarization_log import SummarizationLog
from events.summarization_event import SummarizationEvent
from utils.text_utils import get_levenshtein_distance, normalize_text


class SummarizationEventBlock(EventBlock):
    def __init__(self, name: str, events: List[SummarizationEvent], log: SummarizationLog):
        self.name = name
        self.session_id = log.session_id
        self.worker_id = log.worker_id
        self.order_id = int(name.split('-')[-1])

        metadata = log.get_metadata()
        self.model = metadata['model']
        self.prompt = log.sequence_id

        self.elapsed_time = self._get_elapsed_time(events)  # Time for editing

        self.document = self._get_document(events)

        self.original_summary = self._get_original_summary(events)
        self.original_normalized_summary = normalize_text(self.original_summary)
        self.original_length = len(self.original_normalized_summary.split())
        consistency, coherency, relevance = self._get_original_ratings(events)
        self.original_consistency = consistency
        self.original_coherency = coherency
        self.original_relevance = relevance

        self.edited_summary = self._get_edited_summary(events)
        self.edited_normalized_summary = normalize_text(self.edited_summary)
        self.edited_length = len(self.edited_normalized_summary.split())
        consistency, coherency, relevance = self._get_edited_ratings(events)
        self.edited_consistency = consistency
        self.edited_coherency = coherency
        self.edited_relevance = relevance

        self.distance = get_levenshtein_distance(
            self.original_summary.split(),
            self.edited_summary.split()
        )

    def _get_elapsed_time(self, events: List[SummarizationEvent]) -> float:
        # Get elapsed time for editing
        start = None
        end = None
        for event in events:
            if event.name == 'summary-editing':
                start = event.timestamp
            elif event.name == 'summary-edited-rating':
                end = event.timestamp
                break
        elapsed_time = end - start
        elapsed_time = round(elapsed_time / 1000 / 60, 2)  # min
        return elapsed_time

    def _get_document(self, events: List[SummarizationEvent]) -> str:
        document_event = None
        for event in events[::-1]:
            if event.name == 'summary-add':
                document_event = event
                break

        prompt = document_event.text_delta
        document_summary_pairs = list(filter(None, prompt.split('\n***\n')))
        current_pair = document_summary_pairs[-1]

        start_index = len('Document: ')
        end_index = current_pair.index('\nSummary:')
        document = current_pair[start_index:end_index]
        return document

    def _get_original_summary(self, events: List[SummarizationEvent]) -> str:
        assert events[0].name == 'summary-original-rating'
        assert events[1].name == 'text-insert'
        return events[1].doc

    def _get_original_ratings(self, events: List[SummarizationEvent]) -> (bool, bool, bool):
        rating_events = []
        for event in events:
            rating_events.append(event.name)
            if event.name == 'summary-editing':
                break

        consistency, coherency, relevance = False, False, False
        if 'summary-consistent' in rating_events:
            consistency = True
        if 'summary-coherent' in rating_events:
            coherency = True
        if 'summary-relevant' in rating_events:
            relevance = True
        return consistency, coherency, relevance

    def _get_edited_summary(self, events: List[SummarizationEvent]) -> str:
        for event in events:
            if event.name == 'summary-edited-rating':
                return event.doc

    def _get_edited_ratings(self, events: List[SummarizationEvent]) -> (bool, bool, bool):
        rating_events = []
        for event in events:
            if event.name == 'summary-edited-rating' or len(rating_events) > 0:
                rating_events.append(event.name)

        consistency, coherency, relevance = False, False, False
        if 'summary-consistent' in rating_events:
            consistency = True
        if 'summary-coherent' in rating_events:
            coherency = True
        if 'summary-relevant' in rating_events:
            relevance = True
        return consistency, coherency, relevance
