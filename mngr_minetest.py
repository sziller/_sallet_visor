import logging
import inspect
import random


lg = logging.getLogger(__name__)
lg.info("START: {:>85} <<<".format('mngr_minetest.py'))


def minetest(attacker_perc=50, threshold=6) -> int:
    """=== Function name: minetest =====================================================================================
    Routine to simulate minority or overpowering attacks on the network.
    :param attacker_perc: int - percentage of malevolent group compared to entire network
    :param threshold: int - suggested number of blocks after which a reorg will fail
    :return integer - number of blocks after which honest miners reached the threshold
    ============================================================================================== by Sziller ==="""
    counter = 0
    flow = 0

    while flow < threshold:
        counter += 1
        miner = random.randrange(0, 100)
        if miner < attacker_perc:  # if malevolent miner is successful
            flow = 0
        else:  # if honest miner is successful
            flow += 1
    lg.info(counter)
    return counter


if __name__ == "__main__":
    # NOTSET=0, DEBUG=10, INFO=20, WARN=30, ERROR=40, CRITICAL=50
    logging.basicConfig(filename="./log/mngr_minetest.log", level=logging.NOTSET, filemode="w",
                        format="%(asctime)s [%(levelname)8s]: %(message)s", datefmt='%y%m%d %H:%M:%S')
    lg.warning("START: {:>85} <<<".format('__name__ == "__main__" namespace: mngr_minetest.py'))
    
    lg.warning("========================================================================================")
    lg.warning("=== mine test                                                                        ===")
    lg.warning("========================================================================================")
    
    data = []
    for _ in range(1000):
        data.append(minetest(attacker_perc=51, threshold=10))
    print(sum(data) / len(data))
            
        
