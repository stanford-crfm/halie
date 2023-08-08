from events.base_event import Event


class CrosswordEvent(Event):
    available_names = {
        'give-up', 'solved', 'cell-update', 'new-clue-selected',
        'suggestion-get', 'suggestion-shown',
        'window-blur', 'window-focus', 'reset', 'reset-clock',
    }
    available_sources = {'user', 'api'}

    def __init__(self, event: dict):
        name, source = self._get_name_source(event['event-type'])
        self.name = name
        self.source = source
        self.timestamp = event['timestamp']

        self.user_query = event['lm-query']
        self.completion = event['lm-response']

        self.selected_clue_num = int(event['selected-clue-number'].strip())
        self.selected_clue_direction = event['selected-clue-direction'].strip().lower()
        self.user_grid = event['crossword-state']

        self.cell_row = event['cell-row']
        self.cell_col = event['cell-col']
        self.cell_value = event['cell-value']

        assert self.name in CrosswordEvent.available_names
        assert self.source in CrosswordEvent.available_sources

    def _get_name_source(self, event_type: str) -> (str, str):
        if event_type == 'GiveUp':
            name = 'give-up'
            source = 'user'
        elif event_type == 'Solved':
            name = 'solved'
            source = 'user'
        elif event_type == 'CellUpdate':
            name = 'cell-update'
            source = 'user'
        elif event_type == 'NewClueSelected':
            name = 'new-clue-selected'
            source = 'user'
        elif event_type == 'Ask':
            name = 'suggestion-get'
            source = 'user'
        elif event_type == 'Model Answer':
            name = 'suggestion-shown'
            source = 'api'
        elif event_type == 'GameInFocus':
            name = 'window-focus'
            source = 'api'
        elif event_type == 'GameBlurred':
            name = 'window-blur'
            source = 'api'
        elif event_type == 'Reset':
            name = 'reset'
            source = 'api'
        elif event_type == 'ResetClock':
            name = 'reset-clock'
            source = 'api'
        else:
            raise RuntimeError(f'Undefined event type: {event_type}')
        return name, source
