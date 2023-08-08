from typing import List

from events.base_event import Event


class QuestionEvent(Event):
    available_names = {
        'system-initialize', 'text-insert', 'text-delete',
        'cursor-backward', 'cursor-forward', 'cursor-select',

        'suggestion-get', 'suggestion-shown', 'suggestion-fail',
        'button-generate', 'button-next',
        'button-answer-a', 'button-answer-b', 'button-answer-c', 'button-answer-d',

        'window-blur', 'window-focus',
    }
    available_sources = {'user', 'api'}
    unavailable_names = {'suggestion-up', 'suggestion-down', 'suggestion-close'}  # Ignore

    def __init__(self, event: dict):
        self.name = event['eventName']
        self.source = event['eventSource']
        self.timestamp = event['eventTimestamp']

        self.text_delta = event['textDelta']
        self.cursor_range = event['cursorRange']

        self.doc = event['currentDoc']
        self.cursor = event['currentCursor']

        self.completions = self._get_completions(event)
        self.filtered_completions = self._get_filtered_completions(event)

        assert self.name in QuestionEvent.available_names
        assert self.source in QuestionEvent.available_sources

    def _get_completions(self, event: dict) -> List[str]:
        completion = ''
        completions = event['currentSuggestions']
        if completions:
            assert len(completions) == 1
            completion = completions[0]['trimmed']
        return [completion]

    def _get_filtered_completions(self, event: dict) -> List[str]:
        filtered_completion = ''
        if self.name != 'suggestion-fail':
            return ['']

        completions = event['originalSuggestions']
        assert len(completions) == 1
        filtered_completion = completions[0]['trimmed']
        return [filtered_completion]
