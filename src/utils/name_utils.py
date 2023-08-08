from enum import Enum
from typing import List


class Model(Enum):
    INSTRUCT_DAVINCI = 'InstructDavinci'
    INSTRUCT_BABBAGE = 'InstructBabbage'
    DAVINCI = 'Davinci'
    JURASSIC_JUMBO = 'Jumbo'


def get_all_models() -> List[str]:
    return [
        Model.INSTRUCT_DAVINCI.value,
        Model.INSTRUCT_BABBAGE.value,
        Model.DAVINCI.value,
        Model.JURASSIC_JUMBO.value,
    ]


def convert_model_name_dialogue(name: str) -> str:
    if name == 'text-davinci-001':
        return Model.INSTRUCT_DAVINCI.value
    elif name == 'text-babbage-001':
        return Model.INSTRUCT_BABBAGE.value
    elif name == 'davinci':
        return Model.DAVINCI.value
    elif name == 'j1-jumbo':
        return Model.JURASSIC_JUMBO.value
    else:
        raise RuntimeError(f'Invalid model name: {name}')


def convert_model_name_crossword(name: str) -> str:
    if name == 'text-davinci':
        return Model.INSTRUCT_DAVINCI.value
    elif name == 'text-babbage':
        return Model.INSTRUCT_BABBAGE.value
    elif name == 'davinci':
        return Model.DAVINCI.value
    elif name == 'ai2-jumbo':
        return Model.JURASSIC_JUMBO.value
    else:
        raise RuntimeError(f'Invalid model name: {name}')


def convert_model_name_coauthor(name: str) -> str:
    if name == 'openai/text-davinci-001':
        return Model.INSTRUCT_DAVINCI.value
    elif name == 'openai/text-babbage-001':
        return Model.INSTRUCT_BABBAGE.value
    elif name == 'openai/davinci':
        return Model.DAVINCI.value
    elif name == 'ai21/j1-jumbo':
        return Model.JURASSIC_JUMBO.value
    else:
        raise RuntimeError(f'Invalid model name: {name}')


def convert_model_name_summarization(name: str) -> str:
    if name == 'openai/text-davinci-001':
        return Model.INSTRUCT_DAVINCI.value
    elif name == 'openai/text-babbage-001':
        return Model.INSTRUCT_BABBAGE.value
    elif name == 'openai/davinci':
        return Model.DAVINCI.value
    elif name == 'ai21/j1-jumbo':
        return Model.JURASSIC_JUMBO.value
    elif name == 'reference':
        return 'Reference'
    else:
        raise RuntimeError(f'Invalid model name: {name}')


def convert_gid_to_dataset(gid: int) -> str:
    if gid == 61:
        return 'NYT-1'
    elif gid == 151:
        return 'ELECT'
    elif gid == 173:
        return 'NYT-2'
    elif gid == 187:
        return 'SIT'
    elif gid == 191:
        return 'LOVE'
    else:
        raise RuntimeError(f'{gid}')
