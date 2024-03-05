import logging
import inspect
import random


lg = logging.getLogger(__name__)
lg.info("START: {:>85} <<<".format('mngr_minetest.py'))

def minetest(attacker_perc = 70, treshold = 6):
    counter = 0
    flow = 0

    while flow < treshold:
        counter += 1
        miner = random.randrange(0, 100)
        if miner < attacker_perc:
            flow = 0
        else:
            flow += 1
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
        data.append(minetest(attacker_perc=70, treshold=6))
    print(sum(data) / len(data))
            
        
