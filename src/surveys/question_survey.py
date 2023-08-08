from surveys.base_survey import Survey
from utils.name_utils import convert_model_name_coauthor


class QuestionSurvey(Survey):
    def __init__(
        self, session_id: str, worker_id: str, model: str, prompt: str,
        fluency: int, helpfulness: int, ease: int,
        helpfulness_freetext: str, change_freetext: str, adjectives: str,
    ):
        self.session_id = session_id
        self.worker_id = worker_id

        self.model = convert_model_name_coauthor(model)
        self.prompt = prompt

        self.fluency = fluency
        self.helpfulness = helpfulness
        self.ease = ease

        self.helpfulness_freetext = helpfulness_freetext
        self.change_freetext = change_freetext
        self.adjectives = adjectives
