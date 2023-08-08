class Survey():
    def __init__(
        self, session_id: str, worker_id: str, model: str, prompt: str,
    ):
        self.session_id = session_id
        self.worker_id = worker_id

        self.model = model
        self.prompt = prompt

    def to_dict(self) -> dict:
        return self.__dict__
