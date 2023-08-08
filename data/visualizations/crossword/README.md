# Crossword Task Visualizations

We provide both `static` visualizations and dynamic `replays` as `.html` files that can be rendered directly in any browser after downloading. 

Visualizations in `replays` provide a dynamic way of viewing an *entire* intraction trace: given a user log, `CellUpdate` (user updating crossword grid cell), `Ask` (user querying the LM), and `ModelAnswer` (LM response to query) events are shown in temporal sequence, allowing viewers to see how language model interaction influences task performance. 

An example dynamic replay is below: 


<kbd><img src="https://www.dropbox.com/scl/fi/mphxekbsdns7udow9y3y6/replay-movie-small.gif?rlkey=08ml4w3lzoigbkhp0z5099mgl&raw=1" width="800"></kbd>


For longer interactions, it may be easier to view `static` visualizations, which render the final state in the browser, showing the entire dialogue history with an LM and the final crossword puzzle state. 

## Data Structure

Visualizations have the following filename structure:
- Static: `static/game_{PUZZLE ID}_user_{USER ID}_model_{MODEL}.html`
- Replays: `replays/game_{PUZZLE ID}_user_{USER ID}_model_{MODEL}_replay.html`

So, `replays/game_191_user_2c3c84df1b7610fa6d5c5089107f6112_model_text-davinci_replay.html` correponds to the dynamic replay visualization for puzzle `191` and user `2c3c84df1b7610fa6d5c5089107f6112`, who was allowed to interact with the language model `text-davinci`.

Visualizations  cover 343 logs across the 4 different language models use in HALIE (text-davinci-001, text-babbage-001, davinci, and ai21-jumbo), and 5 different crossword puzzles as follows: 

| Puzzle ID | Puzzle Name | 
| ------------- | ------------- | 
| 61 | NYT-1  |
|151 | NYT-2  |
| 173 | ELECT |
| 187 | SIT|
| 191 | LOVE|


All user ID's are anonymized, and we remove any personal identifiable information (PII) from the released data.
