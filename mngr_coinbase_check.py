from SalletNodePackage import BitcoinNodeObject as BNOb
import logging
import config as conf

def coinbase_rawtx(height: int) -> str:
    """=== Function name: coinbase_rawtx ===============================================================================
    Reads the Coinbase-transaction hexstring of the Block, defined by its sequence nr (height)
    :param height:
    ============================================================================================== by Sziller ==="""
    node = BNOb.Node(is_rpc=True)
    bl_hash = node.nodeop_getblockhash(sequence_nr=height)
    bl_data = node.nodeop_getblock(block_hash=bl_hash)
    coinbase_id = bl_data['tx'][0]
    hexstr = node.nodeop_getrawtransaction(coinbase_id, False)
    return hexstr


def task_bc_crawl(start: int, end: int):
    """=== Task name: task_bc_crawl ====================================================================================
    ============================================================================================== by Sziller ==="""
    for _ in range(start, end):
        if _ % 500 == 0:
            lg.info("just passed: {:>6}".format(_))
        hxstr = coinbase_rawtx(_)
        print("{:>6} / {:>6}".format(_, end))
        if '0000000000000000000000000000000000000000000000000000000000000000ffffffff' not in hxstr:
            lg.error("{:>6}: {}".format(_, hxstr))
        else:
            lg.debug("{:>6}: {}".format(_, hxstr))


if __name__ == "__main__":
    log_time = ""
    rootpath_all_config = "."
    log_filename = "{}/LOG_bc_crawl.log".format(rootpath_all_config, log_time)
    LOG_FORMAT = "%(asctime)s [%(levelname)8s]: %(message)s"
    LOG_LEVEL = logging.INFO  # NOTSET=0, DEBUG=10, INFO=20, WARN=30, ERROR=40, CRITICAL=50

    rootpath_all_config = "."
    logging.basicConfig(
        filename=log_filename,
        level=LOG_LEVEL,
        format=LOG_FORMAT,
        datefmt='%y%m%d %H:%M:%S',
        # filemode="w",
        filemode="a"
    )
    lg = logging.getLogger()
    
    st = int(input("starting height: ")) # 410_001  # innen újra
    end = int(input("finishing height: ")) # 600_000
    task_bc_crawl(start=st, end = end)

    # already checked:
    # 300_000 - 336_000
    # 400_000 - end
