import os
from argparse import ArgumentParser

from assets.dialogue_asset import DialogueAsset
from utils.events_utils import save_event_blocks_dict
from utils.survey_utils import save_survey_responses


if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument('--path_raw', type=str, default='./data/raw/dialogue')
    parser.add_argument('--path_std', type=str, default='./data/std/dialogue')
    parser.add_argument('--path_cache', type=str, default='./cache')
    parser.add_argument('--verbose', action='store_true')
    args = parser.parse_args()

    asset = DialogueAsset(args.path_raw, args.verbose)
    asset.print_summary()

    save_survey_responses(
        path=os.path.join(args.path_std, 'survey_responses.csv'),
        survey_responses=asset.survey_responses,
    )

    # Save standardized event blocks
    event_blocks_dict = []
    for log in asset.logs:
        for event_block in log.event_blocks:
            event_blocks_dict.append(event_block.to_dict())

    save_event_blocks_dict(
        path=os.path.join(args.path_std, 'event_blocks.csv'),
        event_blocks_dict=event_blocks_dict,
    )
