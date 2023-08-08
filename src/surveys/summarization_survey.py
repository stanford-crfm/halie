from surveys.base_survey import Survey
from utils.name_utils import convert_model_name_coauthor


class SummarizationSurvey(Survey):
    def __init__(
        self, session_id: str, worker_id: str, model: str, prompt: str,
        improvement: int, edit: int, helpfulness: int, adjectives: str,
    ):
        self.session_id = session_id
        self.worker_id = worker_id

        self.model = convert_model_name_coauthor(model)
        self.prompt = prompt

        self.improvement = improvement
        self.edit = edit
        self.helpfulness = helpfulness
        self.adjectives = adjectives
