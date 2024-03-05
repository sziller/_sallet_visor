"""
All classes and functions to perform the backwards, ordinals tracking
by Sziller ==="""

import logging


def is_tx_coinbase(tx_hxstr: str) -> bool:
    """=== Function name: is_tx_coinbase ===============================================================================
    Basic, one purpose parser.
    Function takes in a raw TX hexadecimal format, and checks (accordnig to hardcoded rules)
    if TX is Coinbase or not.
    Purpose: to avoid using any parsers (due to representation ambuguity)
    ============================================================================================== by Sziller ==="""
    hxstr_template = "01{}ffffffff".format(32 * '00')
    if hxstr_template in tx_hxstr[:(8+2+64+8+16)]:
        return True
    return False


if __name__ == "__main__":
    
    log_time = ""
    rootpath_all_config = "."
    log_filename = "{}/LOG.log".format(rootpath_all_config, log_time)
    LOG_FORMAT = "%(asctime)s [%(levelname)8s]: %(message)s"
    LOG_LEVEL = logging.INFO  # NOTSET=0, DEBUG=10, INFO=20, WARN=30, ERROR=40, CRITICAL=50

    rootpath_all_config = "."
    logging.basicConfig(
        filename=log_filename,
        level=LOG_LEVEL,
        format=LOG_FORMAT,
        datefmt='%y%m%d %H:%M:%S',
        # filemode="a",
        filemode="a"
    )

    lg = logging.getLogger()
    tx_hxstr_01 = ("01000000010000000000000000000000000000000000000000000000000000000000000000ffffffff"
                   "3e"
                     "09"
                       "4269744d696e746572"
                     "04"
                       "ca660200"
                     "01"
                       "0d"
                     "2c"
                       "fabe6d6df87bf0f20512226194f6272556bba709ab3f485418597ad77c36c91d3aee00750100000000000000"
                   "ffffffff"
                   "01"
                   "887c072a01000000"
                   "19"
                     "76a9"
                     "14"
                       "5c0e4a6830ff6ea9aea773d75bc207299cd50b7488ac"
                   "00000000")
    print(is_tx_coinbase(tx_hxstr=tx_hxstr_01))
