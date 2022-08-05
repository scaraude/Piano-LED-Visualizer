def print_10_messages(messages):
    """Print the first 10 messages of a list of messages."""
    for msg in messages[:10]:
        print(msg)
    print('...')
    for msg in messages[-10:]:
        print(msg)
    print()
    print('Total messages:', len(messages))
