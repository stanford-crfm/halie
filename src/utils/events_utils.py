import pandas as pd


def get_event_indices(
    events,
    event_names,
    event_sources,
):
    """
    Get indices for events with specified names and sources
    """
    event_indices = []
    for i, event in enumerate(events):
        if event.name not in event_names:
            continue

        if event.source not in event_sources:
            continue
        event_indices.append(i)
    return event_indices


def get_event_blocks_dict(
    asset,
    event_block_name,
    event_block_type,
    start_event_names,
    start_event_sources,
    end_event_names,
    end_event_sources,
):
    event_blocks = []
    for log in asset.logs:
        events = log.events

        start_event_indices = get_event_indices(
            events,
            start_event_names,
            start_event_sources,
        )
        if not end_event_names:
            end_event_indices = []
            for index in start_event_indices[1:]:
                end_event_indices.append(index - 1)
            end_event_indices.append(len(events) - 1)
        else:
            end_event_indices = get_event_indices(
                events,
                end_event_names,
                end_event_sources,
            )
        event_block_index = 0

        while start_event_indices and end_event_indices:
            start_index = start_event_indices[0]

            # End each block with end_event
            end_index = end_event_indices[0] + 1
            if end_index > len(events):
                break

            if start_index < end_index:
                event_block = event_block_type(
                    name=f'{event_block_name}-{event_block_index:02}',
                    events=events[start_index:end_index],
                    log=log,
                )

                event_blocks.append(event_block)
                event_block_index += 1

                end_event_indices.pop(0)

                while start_event_indices[0] < end_index:
                    start_event_indices.pop(0)
                    if not start_event_indices:
                        break
            else:
                while start_index >= end_index:
                    end_event_indices.pop(0)
                    if not end_event_indices:
                        break
                    end_index = end_event_indices[0] + 1

    event_blocks_dict = []
    for event_block in event_blocks:
        event_blocks_dict.append(event_block.to_dict())

    return event_blocks_dict


def save_event_blocks_dict(path, event_blocks_dict, columns=[]):
    df_event_blocks = pd.DataFrame(event_blocks_dict)

    if columns:
        df_event_blocks = df_event_blocks[columns]

    df_event_blocks.to_csv(path, index=False, sep=',')
    print(f'Saved {len(event_blocks_dict)} event blocks at {path}')


def save_events_dict(path, events_dict, columns=[]):
    df_events = pd.DataFrame(events_dict)

    if columns:
        df_events = df_events[columns]

    df_events.to_csv(path, index=False, sep=',')
    print(f'Saved {len(events_dict)} events at {path}')
