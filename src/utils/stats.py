from nltk.tokenize import word_tokenize


def get_word_count(ad, remove_punctuation=True):
    words = word_tokenize(ad.strip())
    if remove_punctuation:
        words = [word for word in words if word.isalnum()]
    return len(words)


def get_blocked_words(text, blocklist):
    words = word_tokenize(text.lower())
    blocked_words = [word for word in blocklist if word in words]
    return blocked_words


def get_ngrams(words, n):
    ngrams = []
    if n == 1:
        ngrams = words
    if n == 2:
        for i, word in enumerate(words):
            if i == len(words) - 1:
                break
            ngram = ' '.join([word, words[i + 1]])
            ngrams.append(ngram)
    return ngrams


def get_vocab_diversity(ad):
    words = word_tokenize(ad.strip())
    words = [word for word in words if word.isalnum()]

    bigrams = get_ngrams(words, 2)
    distinct_2 = len(set(bigrams)) / len(words) if len(bigrams) > 0 else 0

    return distinct_2


def get_time(events):
    # Elapsed time between system-initialize and finish
    time = int(events[-1].timestamp) - int(events[0].timestamp)
    time = round(time / 1000 / 60, 2)  # Convert from milisecond to minute
    return time


def get_time_text_change(events):
    # Elapsed time between first text-insert and last text-{insert, delete}
    start, end = 0, 0
    for i in range(len(events)):
        if events[i].name in ['text-insert', 'text-delete']:
            start = i
            break
    for i in range(len(events)-1, 0, -1):
        if events[i].name in ['text-insert', 'text-delete']:
            end = i
            break

    time = int(events[end].timestamp) - int(events[start].timestamp)
    time = round(time / 1000 / 60, 2)
    return time


def get_num_queries(events):
    count = 0
    for i in range(len(events)):
        if events[i].name in ['suggestion-get', 'button-generate']:
            count += 1
    return count


def apply_ops(doc, mask, ops, source):
    original_doc = doc
    original_mask = mask

    new_doc = ''
    new_mask = ''
    for i, op in enumerate(ops):

        # Handle retain operation
        if 'retain' in op:
            num_char = op['retain']

            retain_doc = original_doc[:num_char]
            retain_mask = original_mask[:num_char]

            original_doc = original_doc[num_char:]
            original_mask = original_mask[num_char:]

            new_doc = new_doc + retain_doc
            new_mask = new_mask + retain_mask

        # Handle insert operation
        elif 'insert' in op:
            insert_doc = op['insert']

            insert_mask = 'U' * len(insert_doc)  # User
            if source == 'api':
                insert_mask = 'A' * len(insert_doc)  # API

            if isinstance(insert_doc, dict):
                if 'image' in insert_doc:
                    print('Skipping invalid object insertion (image)')
                else:
                    print('Ignore invalid insertions:', op)
                    # Ignore other invalid insertions
                    # Debug if necessary
                    pass
            else:
                new_doc = new_doc + insert_doc
                new_mask = new_mask + insert_mask

        # Handle delete operation
        elif 'delete' in op:
            num_char = op['delete']

            if original_doc:
                original_doc = original_doc[num_char:]
                original_mask = original_mask[num_char:]
            else:
                new_doc = new_doc[:-num_char]
                new_mask = new_mask[:-num_char]

        else:
            # Ignore other operations
            # Debug if necessary
            print('Ignore other operations:', op)
            pass

    final_doc = new_doc + original_doc
    final_mask = new_mask + original_mask
    return final_doc, final_mask


def get_text_and_mask(
    events,
    event_id,
    remove_prompt=True
):
    prompt = events[0].doc.strip()

    text = prompt
    mask = 'P' * len(prompt)  # Prompt
    for event in events[:event_id]:
        if event.name in {'text-delete', 'text-insert'}:
            ops = event.text_delta['ops']
            source = event.source
            text, mask = apply_ops(text, mask, ops, source)

    if remove_prompt:
        if 'P' not in mask:
            print('=' * 80)
            print('Could not find the prompt in the final text')
            print('-' * 80)
            print('Prompt:', prompt)
            print('-' * 80)
            print('Final text:', text)
        else:
            end_index = mask.rindex('P')
            text = text[end_index + 1:]
            mask = mask[end_index + 1:]

    return text, mask
