from typing import List

from blocks.base_block import EventBlock
from logs.question_log import QuestionLog
from events.question_event import QuestionEvent
from utils.question_utils import attention_check, category_map, sequences, questions, get_prompt_type


class QuestionEventBlock(EventBlock):
    def __init__(self, name: str, events: List[QuestionEvent], log: List[QuestionLog]):
        super().__init__(name, events, log)

        self.order = int(name.split('-')[-1])  # Starts from 0

        self.sequence_id = log.question_sequence_id
        self.question_id = -1
        self.question_type = ''  # attn, ctrl, lm
        self.category = ''  # misc, global_facts, us_fp, nutrition, college_chem, attention

        self.question_text = ''
        self.choice_a = ''
        self.choice_b = ''
        self.choice_c = ''
        self.choice_d = ''
        self.answer = ''  # a, b, c, d
        self.answer_text = ''
        self._get_question_metadata()

        self.lm_used = self._get_lm_used(events)  # 1 for used, 0 otherwise
        self.user_queries, self.lm_responses = self._get_user_query_lm_response(events)
        self.user_query_types = self._get_user_query_types()
        self.user_answer = self._get_user_answer(events)  # a, b, c, d

        self.user_correct = self._get_user_correct()  # 1 for correct, 0 otherwise

    def _get_question_metadata(self):
        sequence_id = int(self.sequence_id)
        sequence = sequences.iloc[sequence_id]

        question_id = sequence[self.order]

        is_control = not sequence[self.order + 11]
        is_attention = question_id in attention_check

        if is_attention:
            question_type = 'attn'
        elif is_control:
            question_type = 'ctrl'
        else:
            question_type = 'lm'

        category = category_map[question_id]
        question = questions.iloc[question_id]

        self.sequence_id = sequence_id
        self.question_id = question_id
        self.question_type = question_type
        self.category = category

        self.question_text = question['question']
        self.choice_a = question['a']
        self.choice_b = question['b']
        self.choice_c = question['c']
        self.choice_d = question['d']
        self.answer = question['answer'].strip().lower()
        self.answer_text = question[self.answer]

    def _get_lm_used(self, events: List[QuestionEvent]) -> int:
        for event in events:
            if event.name == 'button-generate':
                return 1
        return 0

    def _get_user_query_lm_response(self, events: List[QuestionEvent]) -> (List[str], List[str]):
        # Get a list of user queries and generated responses
        user_queries, lm_responses = [], []
        for i, event in enumerate(events):
            if event.name == 'suggestion-shown':
                text = event.text_delta  # e.g. '<b>In which war was "The Star Spangled Banner" written?</b>\n\nThe War of 1812.'
                start = '<b>'
                end = '</b>'
                end_index = text.index(end)
                user_query = text[len(start):end_index].strip()
                lm_response = text[end_index + len(end):].strip()
                user_queries.append(user_query)
                lm_responses.append(lm_response)
        return user_queries, lm_responses

    def _get_user_query_types(self):
        user_query_types = []
        for user_query in self.user_queries:
            types = get_prompt_type(
                user_query, self.question_text,
                [self.choice_a, self.choice_b, self.choice_c, self.choice_d]
            )
            user_query_types.append(';'.join(types))
        return user_query_types

    def _get_user_answer(self, events: List[QuestionEvent]) -> str:
        answer = 'N/A'
        for event in events:
            if 'button-answer' in event.name:
                answer = event.name.split('-')[-1].lower()
        if answer == 'N/A':
            print('User did not answer the question')
        return answer

    def _get_user_correct(self) -> int:
        if self.user_answer == self.answer:
            return 1
        else:
            return 0

    def to_dict(self) -> dict:
        return {
            'session_id': self.session_id,
            'worker_id': self.worker_id,
            'order_id': self.order,  # Start from 1

            'model': self.model,
            'prompt': self.prompt,

            'sequence_id': self.sequence_id,
            'question_id': self.question_id,
            'question_type': self.question_type,
            'question_category': self.category,

            'question_text': self.question_text,
            'choice_a': self.choice_a,
            'choice_b': self.choice_b,
            'choice_c': self.choice_c,
            'choice_d': self.choice_d,
            'answer': self.answer,
            'answer_text': self.answer_text,

            'lm_used': self.lm_used,
            'user_queries': self.user_queries,
            'user_query_types': self.user_query_types,
            'lm_responses': self.lm_responses,
            'user_answer': self.user_answer,

            'user_correct': self.user_correct,

            'elapsed_time': self.elapsed_time,
            'num_queries': self.num_queries,
            'num_events': self.num_events,
        }
