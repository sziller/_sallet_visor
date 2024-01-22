def assign_ordinals_recursive(block, interesting_satoshis, tracked_satoshis=None):
    """
    Assign ordinals recursively for interesting satoshis in the given block.

    :param block: Block object
    :param interesting_satoshis: Set of satoshis to track
    :param tracked_satoshis: Set of satoshis already tracked (for recursion)
    :return: None
    """
    if tracked_satoshis is None:
        tracked_satoshis = set()

    # Calculate the first ordinal for the current block
    first = first_ordinal(block.height)
    last = first + subsidy(block.height)
    coinbase_ordinals = list(range(first, last))

    # Process coinbase transaction
    for output in block.transactions[0].outputs:
        output.ordinals = coinbase_ordinals[:output.value]
        del coinbase_ordinals[:output.value]
        tracked_satoshis.update(output.ordinals)

    # Process non-coinbase transactions
    for transaction in block.transactions[1:]:
        ordinals = []
        for inp in transaction.inputs:
            ordinals.extend(inp.ordinals)

        for output in transaction.outputs:
            output.ordinals = ordinals[:output.value]
            del ordinals[:output.value]
            tracked_satoshis.update(output.ordinals)

    # Recursive call for subsequent blocks
    for output in block.transactions[0].outputs:
        for satoshi in output.ordinals:
            if satoshi in interesting_satoshis and satoshi not in tracked_satoshis:
                # Process the interesting satoshi (e.g., store in a database)
                print(f"Processing interesting satoshi: {satoshi}")
                tracked_satoshis.add(satoshi)

    for subsequent_block in block.subsequent_blocks:
        assign_ordinals_recursive(subsequent_block, interesting_satoshis, tracked_satoshis)


# Example usage:
genesis_block = get_genesis_block()  # Replace with the actual method to get the genesis block
interesting_satoshis = {1, 5, 10}  # Replace with the satoshi numbers you're interested in
assign_ordinals_recursive(genesis_block, interesting_satoshis)
