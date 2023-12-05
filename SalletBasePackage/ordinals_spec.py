
# subsidy of block at given height
def subsidy(height):
    return 50 * 100_000_000 >> height // 210_000

# first ordinal of subsidy of block at given height
def first_ordinal(height):
    start = 0
    for height in range(height):
        start += subsidy(height)
    return start

# assign ordinals in given block
def assign_ordinals(block):
    first = first_ordinal(block.height)
    last = first + subsidy(block.height)
    coinbase_ordinals = list(range(first, last))

    for transaction in block.transactions[1:]:
        ordinals = []
        for input in transaction.inputs:
            ordinals.extend(input.ordinals)

        for output in transaction.outputs:
            output.ordinals = ordinals[:output.value]
            del ordinals[:output.value]

        coinbase_ordinals.extend(ordinals)

    for output in block.transaction[0].outputs:
        output.ordinals = coinbase_ordinals[:output.value]
        del coinbase_ordinals[:output.value]
