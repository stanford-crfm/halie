from surveys.base_survey import Survey


class DialogueSurvey(Survey):
    def __init__(
        self, session_id: str, worker_id: str, turn_id: int, model: str, prompt: str,
        interestingness: int, boringness: int, preference: int, fluency: int,
        sensibility: int, specificity: int, humanness: int, quality: int,
    ):
        self.session_id = session_id
        self.worker_id = worker_id
        self.turn_id = turn_id

        self.model = model
        self.prompt = prompt

        self.interestingness = interestingness
        self.boringness = boringness
        self.preference = preference
        self.fluency = fluency
        self.sensibility = sensibility
        self.specificity = specificity
        self.humanness = humanness
        self.quality = quality
