import os
from argparse import ArgumentParser

from events.metaphor_event import MetaphorEvent
from blocks.metaphor_block import MetaphorEventBlock
from assets.metaphor_asset import MetaphorAsset

from utils.events_utils import get_event_blocks_dict, save_event_blocks_dict
from utils.survey_utils import save_survey_responses


if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument('--path_raw', type=str, default='./data/raw/metaphor')
    parser.add_argument('--path_std', type=str, default='./data/std/metaphor')
    parser.add_argument('--path_cache', type=str, default='./cache')
    parser.add_argument('--verbose', action='store_true')
    args = parser.parse_args()

    asset = MetaphorAsset(args.path_raw)
    asset.print_summary()

    # asset.check_latency()
    # asset.print_random_event_sequence()

    save_survey_responses(
        path=os.path.join(args.path_std, 'survey_responses.csv'),
        survey_responses=asset.survey_responses,
        columns=[
            'session_id', 'worker_id', 'model', 'prompt',
            'fluency', 'helpfulness', 'ease', 'enjoyment', 'satisfaction', 'ownership', 'reuse'
        ],
    )

    event_blocks_dict = get_event_blocks_dict(
        asset=asset,
        event_block_name='sentence',
        event_block_type=MetaphorEventBlock,
        start_event_names=MetaphorEvent.available_names,
        start_event_sources=MetaphorEvent.available_sources,
        end_event_names={'sentence-add'},
        end_event_sources={'user'},
    )
    save_event_blocks_dict(
        path=os.path.join(args.path_std, 'event_blocks.csv'),
        event_blocks_dict=event_blocks_dict
    )
