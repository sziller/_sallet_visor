
# subsidy of block at given height
def subsidy(height: int) -> int:
    """=== Function name: subsidy ======================================================================================
    Calculating the number of satoshis created (granted to the miner as fee) in a given block (defined by height).
    
    // is division's integer part and is higher in hierarchy than >> (thus no parenthesis needed)
    >> is bitshifting (basically division by 2) as many times as shown after symbol.
    (16 >> 3 meany dividing 16 by (2*2*2))
    16 >> 3 == 16 / 2**3 = 2
    
    height // 210000 returns an integer. The number of halvings since initialization of the network
    0 - 209_999         it returns 0, so initial fee is not bitshifted
    210_000 - 419_999   it returns 1, so fee is bitshifted once, meaning it is divided by two

    :param height: integer - sequence number of given block
    :return: integer - nr. of sats awarded as fee in given block
    ========================================================================= by Casey - explained by Sziller ==="""
    return 50 * 100_000_000 >> height // 210_000  # 50: original fee, 100_000_000 to convert fee to satoshis


# first ordinal of subsidy of block at given height
def first_ordinal(height):
    """=== Function name: first_ordinal ================================================================================
    Counting all the issued satoshis up until given block.
    Basically adding-up all subsidies till the height entered.
    0-49, 50-99, 100-149...
    height 3 means, we add up the subsidies of each block (_) before entered height.
    the number of sats up to a sat equals the ordinal of that sat.
    ========================================================================= by Casey - explained by Sziller ==="""
    start = 0
    for _ in range(height):  # 0 <= _ < height - never reaching height entered: so all sats BEFORE current height added.
        start += subsidy(_)
    return start


# assign ordinals in given block
def assign_ordinals(block):
    """=== Function name: assign_ordinals ==============================================================================
    Logic, as explained by Casey:
    We mark each tx's outputs enclosed in brackets:
    [a b] [c] [d e f] -> [a b c d] [e] ... f will be used as miner fee
    Explained:
    TX n
    Inputs:                         Outputs:
    [a b]                           [a b c d]
    [c]             --->            [e]
    [d e f]                         ... ---> f will be used as miner fee
    
    In a coinbase it is like:
    Inputs: (no actual inputs)      Outputs:
    subs.(min)                      [subs.(min) -- x-1]
    subs.(max-1)                    [x -- y-1]
    [f0]                            [y -- subs.(max-1), subs.(max) - fx]
    [f1]                            [f rest]
    [f2]
    So outputs ordinals of 'a' to 'f' are inherited from input sordinals 'a' to 'f'
    :param block: 
    :return: 
    ========================================================================= by Casey - explained by Sziller ==="""
    first = first_ordinal(block.height)     # getting ordinal of 1st coinbase sat - the way block is ever represented
    last = first + subsidy(block.height)    # getting ordinal of last sat created in coinbase (as fee)
    coinbase_ordinals = list(range(first, last))  # setting up a range of all sat's newly issued in 'block's coinbase
    
    # as an interim result: <coinbase_ordinals> include n piece of ordinal numbers, in sequence. n = subsidy
    
    # the TX-by-TX process assumes all TXs' inputs each having an 'ordinal-registry', and creates one for the outputs'.
    for transaction in block.transactions[1:]:  # looping through all TX's in block, starting at 1 - omitting coinbase
        ordinals = []  # an empty list of ordinals for present TX is created
        for inp in transaction.inputs:  # for each input in present TX
            ordinals.extend(inp.ordinals)  # the list of said inputs ordinal's is added to the <ordinals> list
        
        # While processing a given block, for each non-coinbase transaction...
        # ...as an interim result: we have all incoming ordinals in the conventional sequence accounted for.
        # they are all stored in <ordinals>. e.g.: [41, 201, 100, 101, 102, 20, 21, 225, 226, 55, 56]
        # this is a sequence of all INCOMING ordinals, which will be re-distributed by the following code section:
        
        for output in transaction.outputs:  # we now loop through same TX's outputs
            # defining present outputs ordinals: putting in as many of the
            # leading ordinal numbers into current ordinals, as sats there
            # are in the output
            output.ordinals = ordinals[:output.value]
            del ordinals[:output.value]  # deleting just assigned ordinals from 'still available' set.

        coinbase_ordinals.extend(ordinals)  # present TX's not spent sats (ord-by-ord) are attached to coinbase ords.

    for output in block.transaction[0].outputs:
        output.ordinals = coinbase_ordinals[:output.value]
        del coinbase_ordinals[:output.value]


if __name__ == "__main__":
    print(subsidy(420_001))
    print(first_ordinal(420_001))
