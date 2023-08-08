import os
import pandas as pd
from argparse import ArgumentParser

from assets.summarization_asset import SummarizationAsset
from blocks.summarization_block import SummarizationEventBlock
from utils.survey_utils import save_survey_responses
from utils.events_utils import get_event_blocks_dict, save_event_blocks_dict
from utils.text_utils import normalize_text


if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument('--path_raw', type=str, default='./data/raw/summarization')
    parser.add_argument('--path_std', type=str, default='./data/std/summarization')
    parser.add_argument('--path_cache', type=str, default='./cache')
    parser.add_argument('--verbose', action='store_true')
    args = parser.parse_args()

    asset = SummarizationAsset(args.path_raw, args.verbose)
    asset.print_summary()

    save_survey_responses(
        path=os.path.join(args.path_std, 'survey_responses.csv'),
        survey_responses=asset.survey_responses,
    )

    event_blocks_dict = get_event_blocks_dict(
        asset=asset,
        event_block_name='summary',
        event_block_type=SummarizationEventBlock,
        start_event_names={'summary-original-rating'},
        start_event_sources={'api'},
        end_event_names={},
        end_event_sources={},
    )
    # Add third-party annotations to event blocks
    # Take average if there are multiple annotations per summary
    annotations = asset.annotations
    df_annotations = pd.DataFrame(annotations)[['summary', 'consistency', 'relevance', 'coherency']]
    df_annotations = df_annotations.groupby(by=['summary']).mean()  # 805

    for event_block in event_blocks_dict:
        original_summary = normalize_text(event_block['original_summary'])
        df = df_annotations.query(f'summary == "{original_summary}"')
        if len(df) == 1:  # Annotated only a subset
            event_block['original_consistency_third_party'] = round(df.iloc[0]['consistency'], 2)
            event_block['original_relevance_third_party'] = round(df.iloc[0]['relevance'], 2)
            event_block['original_coherency_third_party'] = round(df.iloc[0]['coherency'], 2)

        edited_summary = normalize_text(event_block['edited_summary'])
        df = df_annotations.query(f'summary == "{edited_summary}"')
        if len(df) == 1:  # Annotated only a subset
            event_block['edited_consistency_third_party'] = round(df.iloc[0]['consistency'], 2)
            event_block['edited_relevance_third_party'] = round(df.iloc[0]['relevance'], 2)
            event_block['edited_coherency_third_party'] = round(df.iloc[0]['coherency'], 2)

    save_event_blocks_dict(
        path=os.path.join(args.path_std, 'event_blocks.csv'),
        event_blocks_dict=event_blocks_dict,
    )
