from blocks.base_block import EventBlock
from utils.text_utils import count_num_words


class DialogueEventBlock(EventBlock):
    def __init__(
        self, name: str, session_id: str, worker_id: str, turn_id: int,
        model: str, prompt: str, prompt_dataset: str, elapsed_time: float,
        user_input: str, model_completion: str,
    ):
        self.name = name

        self.session_id = session_id
        self.worker_id = worker_id
        self.turn_id = turn_id

        self.model = model
        self.prompt = prompt
        self.prompt_dataset = prompt_dataset

        self.elapsed_time = elapsed_time
        self.user_input = user_input
        self.user_num_words = count_num_words(user_input)
        self.model_completion = model_completion
        self.model_num_words = count_num_words(model_completion)
