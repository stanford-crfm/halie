import os
import json
import collections
from typing import List

from logs.base_log import Log
from events.crossword_event import CrosswordEvent
from utils.name_utils import convert_model_name_crossword, convert_gid_to_dataset
from utils.crossword_utils import Puzzle


class CrosswordLog(Log):
    gid_to_puzzle = dict()

    def __init__(self, path_log: str, path_puzzles: str):
        self.path = path_log
        self.session_id = os.path.splitext(os.path.basename(path_log))[0]
        self.session_id = '_'.join(self.session_id.split('_')[:-2])  # Remove the suffix "_ID_log"

        metadata = self._read_metadata()
        self.metadata = metadata

        self.gid = metadata['gid']
        self.puzzle = self._read_puzzle(self.gid, path_puzzles)

        self.worker_id = metadata['worker_id']
        self.domain = metadata['domain']
        self.example = metadata['example']
        self.prompt = self.gid  # Game ID
        self.prompt_dataset = convert_gid_to_dataset(self.gid)
        self.mode = metadata['mode']

        self.n = metadata['n']
        self.max_token = metadata['max_token']
        self.temperature = metadata['temperature']
        self.top_p = metadata['top_p']
        self.presence_penalty = metadata['presence_penalty']
        self.frequency_penalty = metadata['frequency_penalty']

        self.question_sequence_id = -1  # N/A
        self.summarization_sequence_id = -1  # N/A

        self.model = self._read_model(metadata)
        self.events = self._read_events()
        self.stats = self._get_basic_stats()

        self.letter_accuracy = self._get_accuracy(accuracy='letter')
        self.clue_accuracy = self._get_accuracy(accuracy='clue')

    def _read_puzzle(self, gid: str, path_puzzles: str):
        if gid not in CrosswordLog.gid_to_puzzle:
            puzzle = Puzzle(gid, path_dir=path_puzzles)
            CrosswordLog.gid_to_puzzle[gid] = puzzle
        else:
            puzzle = CrosswordLog.gid_to_puzzle[gid]
        return puzzle

    def _read_metadata(self) -> dict:
        metadata = None

        with open(self.path, 'r') as f:
            data = json.load(f)
            for event in data:
                metadata = {
                    'worker_id': event['username'],
                    'domain': 'crossword',
                    'example': 'na',
                    'prompt': 'na',
                    'mode': 'both',

                    # TODO: Check with Megha
                    'n': 1,
                    'max_token': 30,
                    'temperature': 0.9,
                    'top_p': 1,
                    'presence_penalty': 0,
                    'frequency_penalty': 0,

                    'model': event['model'],
                    'gid': event['gid'],
                }
                break
        return metadata

    def _read_model(self, metadata: dict) -> str:
        model = metadata['model']
        model = convert_model_name_crossword(model)
        return model

    def _read_events(self) -> List[CrosswordEvent]:
        events = []
        with open(self.path, 'r') as f:
            data = json.load(f)
            for event in data:
                events.append(CrosswordEvent(event))
        return events

    def _get_basic_stats(self) -> dict:  # TODO
        return {
            'session_id': self.session_id,
            'time': -1,
            'time_text_change': -1,
            'num_queries': 0,
            'final_text': 0,
            'word_count': 0,
        }

    def _get_last_crossword_state(self):
        curr_time = 0
        counter = 0
        while curr_time <= 31:
            if(counter >= len(self.events)):
                break
            curr_time = self.events[counter].timestamp
            counter += 1
        return self.events[counter-1].user_grid

    def _get_accuracy(self, accuracy: str):
        user_grid = self._get_last_crossword_state()
        # Letter Accuracy
        if(accuracy == "letter"):
            return self.puzzle.grade_puzzle_letter(user_grid)
        # Clue Accuracy
        elif(accuracy == "clue"):
            return self.puzzle.grade_puzzle_clue(user_grid)
        else:
            raise RuntimeError()
