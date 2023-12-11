import os
import copy
import random

# https://beta.openai.com/docs/engines/gpt-3
OPENAI_MODELS = [
    'ada', 'babbage', 'curie', 'davinci',
    'text-ada-001', 'text-babbage-001', 'text-curie-001', 'text-davinci-001',
    'text-davinci-002',
]

# https://crfm-models.stanford.edu/static/help.html#query
CRFM_MODELS = [
    'crfm/random',
    'openai/ada', 'openai/babbage', 'openai/curie', 'openai/davinci',
    'openai/text-ada-001', 'openai/text-babbage-001', 'openai/text-curie-001',
    'openai/text-davinci-001', 'openai/text-davinci-002',
    'ai21/j1-large', 'ai21/j1-grande', 'ai21/j1-jumbo',
    'huggingface/gpt2', 'huggingface/gptj_6b',
    'anthropic/stanford-online-helpful-v4-s3',
    'microsoft/TNLGv2_530B',
]

CRFM_RANDOM_MODELS = [
    'openai/davinci',
    'openai/text-davinci-001',
    'ai21/j1-jumbo',
    'openai/text-babbage-001'
]


class AccessCodeConfig:
    def __init__(self, row, data_dir, num_sequence):
        """
        Default values for admin
        """
        self.domain = 'interactiveqa'
        self.example = 'na'
        self.prompt = 'na'

        self.start_date = '20200101'
        self.end_date = '20250101'
        self.expire_after = '-1'  # Never expire

        self.session_length = 0  # Second

        self.n = 1
        self.max_tokens = 100
        self.temperature = 0.5
        self.top_p = 1
        self.presence_penalty = 0
        self.frequency_penalty = 0
        self.stop = []

        self.engine = 'davinci'
        self.model = ''
        self.crfm = ''
        self.crfm_base = ''
        self.condition = 'human'

        self.data_dir = data_dir
        self.num_sequence = num_sequence

        self.additional_data = None  # To be processed separately based on domain

        # Domain specific fields
        self.page = ''
        self.iqa_sequence_index = 1
        self.summarization_sequence_index = -1

        self.update(row)

    def convert_to_dict(self):
        return {
            'domain': self.domain,
            'example': self.example,
            'prompt': self.prompt,

            'start_date': self.start_date,
            'end_date': self.end_date,
            'expire_after': self.expire_after,

            'session_length': self.session_length,

            'n': self.n,
            'max_tokens': self.max_tokens,
            'temperature': self.temperature,
            'top_p': self.top_p,
            'presence_penalty': self.presence_penalty,
            'frequency_penalty': self.frequency_penalty,
            'stop': self.stop,

            'engine': self.engine,
            'model': self.model,
            'crfm': self.crfm,
            'crfm_base': self.crfm_base,
            'condition': self.condition,

            # Domain specific fields
            'additional_data': self.additional_data,
            'page': self.page,
            'iqa_sequence_index': self.iqa_sequence_index,
            'summarization_sequence_index': self.summarization_sequence_index,
        }

    def update(self, row):
        if 'domain' in row:
            self.domain = row['domain']
        if 'example' in row:
            self.example = row['example']
        if 'prompt' in row:
            self.prompt = row['prompt']

        if 'start_date' in row:
            self.start_date = row['start_date']
        if 'end_date' in row:
            self.end_date = row['end_date']
        if 'expire_after' in row:
            self.expire_after = row['expire_after']

        if 'session_length' in row:
            self.session_length = int(row['session_length'])

        if 'n' in row:
            self.n = int(row['n'])
        if 'max_tokens' in row:
            self.max_tokens = int(row['max_tokens'])
        if 'temperature' in row:
            self.temperature = float(row['temperature'])
        if 'top_p' in row:
            self.top_p = float(row['top_p'])
        if 'presence_penalty' in row:
            self.presence_penalty = float(row['presence_penalty'])
        if 'frequency_penalty' in row:
            self.frequency_penalty = float(row['frequency_penalty'])
        if 'stop' in row:
            self.stop = [
                token.replace('\\n', '\n')
                for token in row['stop'].split('|')
            ]

        if 'engine' in row:
            if row['engine'] in OPENAI_MODELS:
                self.engine = row['engine']
            elif row['engine'] in CRFM_MODELS:
                self.engine = ''
                self.crfm = row['engine']
            elif 'ft-academics-stanford' in row['engine']:  # Fine-tuned GPT-3
                self.engine = ''
                self.model = row['engine']
            else:
                self.engine = 'davinci'
                print(f'Error reading access code with engine: {row["engine"]}')
                print('Default back to davinci')

        if 'condition' in row:
            self.condition = row['condition']

        if 'additional_data' in row and row['additional_data'] != 'na':
            self.additional_data = row['additional_data']

            # Populate domain specific fields
            if self.domain == 'copywriting':
                self.process_additional_data_for_copywriting()
            elif self.domain == 'interactiveqa':
                self.process_additional_data_for_interactiveqa()
            elif self.domain == 'summarization':
                self.process_additional_data_for_summarization()
            elif self.domain == 'story':
                self.crfm_base = self.additional_data

    def assign_random_values(self):
        """
        Call this function before creating a new session so that for each
            session, a new value is assigned.
        """
        if self.crfm == 'crfm/random':
            random_models = copy.deepcopy(CRFM_RANDOM_MODELS)
            random_models.remove(self.crfm_base)
            self.crfm = random.choice(random_models)

        if self.domain == 'interactiveqa' and self.additional_data == 'random':
            self.iqa_sequence_index = random.randint(0, self.num_sequence - 1)

    def process_additional_data_for_copywriting(self):
        path = os.path.join(self.data_dir, self.additional_data)
        with open(path, 'r') as f:
            page = f.read()
            self.page = page

    def process_additional_data_for_interactiveqa(self):
        self.iqa_sequence_index = self.additional_data

    def process_additional_data_for_summarization(self):
        self.summarization_sequence_index = self.additional_data
