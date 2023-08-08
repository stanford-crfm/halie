import os
from argparse import ArgumentParser

from events.question_event import QuestionEvent
from assets.question_asset import QuestionAsset
from blocks.question_block import QuestionEventBlock

from utils.survey_utils import save_survey_responses
from utils.events_utils import get_event_blocks_dict, save_event_blocks_dict


if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument('--path_raw', type=str, default='./data/raw/question')
    parser.add_argument('--path_std', type=str, default='./data/std/question')
    parser.add_argument('--path_cache', type=str, default='./cache')
    parser.add_argument('--verbose', action='store_true')
    args = parser.parse_args()

    asset = QuestionAsset(args.path_raw, args.verbose)
    asset.print_summary()

    save_survey_responses(
        path=os.path.join(args.path_std, 'survey_responses.csv'),
        survey_responses=asset.survey_responses,
    )

    event_blocks_dict = get_event_blocks_dict(
        asset=asset,
        event_block_name='question',
        event_block_type=QuestionEventBlock,
        start_event_names=QuestionEvent.available_names,
        start_event_sources=QuestionEvent.available_sources,
        end_event_names={'button-next'},
        end_event_sources={'user'},
    )
    save_event_blocks_dict(
        path=os.path.join(args.path_std, 'event_blocks.csv'),
        event_blocks_dict=event_blocks_dict,
    )
