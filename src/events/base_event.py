class Event:
    available_names = set()
    available_sources = set()
    unavailable_names = set()
    unavailable_sources = set()

    def __init__(self):
        self.name = ''
        self.source = ''
        self.timestamp = ''

    def _get_completions(self):
        pass

    def _get_filtered_completions(self):
        pass
