import os
import pandas as pd
from argparse import ArgumentParser

from assets.crossword_asset import CrosswordAsset
from blocks.crossword_block import CrosswordEventBlock
from utils.events_utils import get_event_blocks_dict, save_event_blocks_dict
from utils.survey_utils import save_survey_responses

if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument('--path_raw', type=str, default='./data/raw/crossword')
    parser.add_argument('--path_std', type=str, default='./data/std/crossword')
    parser.add_argument('--path_cache', type=str, default='./cache')
    parser.add_argument('--verbose', action='store_true')
    args = parser.parse_args()

    asset = CrosswordAsset(args.path_raw, args.verbose)
    asset.print_summary()

    event_blocks_dict = get_event_blocks_dict(
        asset=asset,
        event_block_name='crossword',
        event_block_type=CrosswordEventBlock,
        start_event_names={'suggestion-get'},
        start_event_sources={'user'},
        end_event_names={'suggestion-shown'},
        end_event_sources={'api'},
    )
    save_event_blocks_dict(
        path=os.path.join(args.path_std, 'event_blocks.csv'),
        event_blocks_dict=event_blocks_dict,
    )

    survey_responses = asset.survey_responses
    save_survey_responses(
        path=os.path.join(args.path_std, 'survey_responses.csv'),
        survey_responses=survey_responses,
    )

    accuracies = []
    for log in asset.logs:
        accuracies.append({
            'session_id': log.session_id,
            'worker_id': log.worker_id,
            'model': log.model,
            'prompt': log.prompt,
            'prompt_dataset': log.prompt_dataset,
            'letter_accuracy': log.letter_accuracy,
            'clue_accuracy': log.clue_accuracy,
        })

    path = os.path.join(args.path_std, 'accuracies.csv')
    pd.DataFrame(accuracies).to_csv(path, index=False, sep=',')
    print(f'Saved {len(accuracies)} accuracies at {path}')
