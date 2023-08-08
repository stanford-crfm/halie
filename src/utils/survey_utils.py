import collections
import pandas as pd
from typing import List

from surveys.base_survey import Survey


def get_model_to_scores(
    asset,
    survey_question_code,
):
    session_id_to_model = dict()
    for log in asset.logs:
        session_id_to_model[log.session_id] = log.model

    survey_responses = asset.survey_responses
    model_to_scores = collections.defaultdict(list)
    if survey_question_code in survey_responses[0]:
        for survey_response in survey_responses:
            session_id = survey_response['session_id']
            model = session_id_to_model[session_id]
            score = int(survey_response[survey_question_code])
            model_to_scores[model].append(score)
    else:
        print(f'Survey question code {survey_question_code} doesn\'t exist in the asset')
        print('Select one of the followings:', ', '.join(survey_responses[0].keys()))

    return model_to_scores


def save_survey_responses(path: str, survey_responses: List[Survey], columns: List[str] = []):
    survey_responses = [survey_response.to_dict() for survey_response in survey_responses]
    df_survey_responses = pd.DataFrame(survey_responses)

    if columns:
        df_survey_responses = df_survey_responses[columns]

    df_survey_responses.to_csv(path, index=False, sep=',')
    print(f'Saved {len(df_survey_responses)} survey responses at {path}')
