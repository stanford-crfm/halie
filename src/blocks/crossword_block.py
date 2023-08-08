from typing import List

from blocks.base_block import EventBlock
from logs.crossword_log import CrosswordLog
from events.crossword_event import CrosswordEvent
from utils.query_utils import get_query_type


class CrosswordEventBlock(EventBlock):
    def __init__(self, name: str, events: List[CrosswordEvent], log: CrosswordLog):
        super().__init__(name, events, log)

        self.order_id = int(name.split('-')[-1])  # Starts from 0
        self.prompt_dataset = log.prompt_dataset

        user_query = events[0].user_query
        query_index = name.split('-')[-1]

        self.user_query = user_query
        self.completion = events[-1].completion

        all_clues = log.puzzle.get_all_clue_questions()
        self.query_type = get_query_type(user_query, all_clues)
        self.query_index = query_index

        self.clue_num = events[0].selected_clue_num
        self.clue_direction = events[0].selected_clue_direction

        self.clue_type = log.puzzle.get_clue_type(self.clue_num, self.clue_direction)

    def to_dict(self) -> dict:
        return self.__dict__
