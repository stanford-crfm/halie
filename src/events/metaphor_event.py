from typing import List

from events.base_event import Event


class MetaphorEvent(Event):
    available_names = {
        'system-initialize', 'text-insert', 'text-delete',
        'cursor-backward', 'cursor-forward', 'cursor-select',

        'suggestion-get', 'suggestion-open', 'suggestion-reopen',
        'suggestion-up', 'suggestion-down', 'suggestion-hover',
        'suggestion-select', 'suggestion-close', 'suggestion-fail',

        'sentence-add', 'sentence-delete',
    }
    available_sources = {'user', 'api'}

    def __init__(self, event: dict, metadata: dict):
        self.session_id = metadata['session_id']
        self.worker_id = metadata['worker_id']

        self.model = metadata['model']
        self.prompt = metadata['prompt']

        self.name = self._convert_name(event['eventName'])
        self.source = event['eventSource']
        self.timestamp = event['eventTimestamp']

        self.text_delta = event['textDelta']
        self.cursor_range = event['cursorRange']

        self.doc = event['currentDoc']
        self.cursor = event['currentCursor']

        self.completions = self._get_completions(event)
        self.filtered_completions = self._get_filtered_completions(event)

        assert self.name in MetaphorEvent.available_names
        assert self.source in MetaphorEvent.available_sources

    def _convert_name(self, name: str) -> str:
        # TODO Change it in the jsonl files
        if name == 'template-add':
            return 'sentence-add'
        elif name == 'template-delete':
            return 'sentence-delete'
        else:
            return name

    def _get_completions(self, event: dict) -> List[str]:
        completions = event['currentSuggestions']
        if not completions:
            return []

        completions = [completion['trimmed'] for completion in completions]
        return completions

    def _get_filtered_completions(self, event: dict) -> List[str]:
        filtered_completions = []
        if 'originalSuggestions' not in event:
            return []

        completions = event['originalSuggestions']
        if len(completions) > 0:
            filtered_completions = [completion['trimmed'] for completion in completions]
        return filtered_completions
