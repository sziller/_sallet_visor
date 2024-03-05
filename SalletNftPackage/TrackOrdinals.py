"""
Tracking ordinals on Bitcoin:

we use 4 different expressions to distinguish between different types of ordinal numbers:

- ch: CHain         - absolute - Ordinal numbers on-chain (this is referred to as Ordinals with capital 'O')
- bl: BLock         - relative - ordinal numbers inside a Block
- tx: Transaction   - relative - ordinal numbers inside a TX
- op: OutPut        - relative - ordinals inside a given input or output


        # example for our case:
        # (5, 6, 7, 8)
        # range(5, 9) -> range (start, stop) -> entries in it: (start, ...., last)
        # 5: start
        # 8: last
        # 9: stop
        # len = stop - start = 4 = 9 - 5
        # stop = last + 1 = 9 = 8 + 1
        # (9, 10, 11)
        # previous range's stop = subsequent range's start
"""

import bitcoinlib
import time
import logging
import inspect
from SalletBasePackage.models import UtxoId
from SalletNodePackage.BitcoinNodeObject import Node
from SalletNftPackage import ordinals_spec as orsp

# Setting up logger                                         logger                      -   START   -

LOG_FORMAT = "%(asctime)s [%(levelname)8s]: %(message)s"
LOG_LEVEL = logging.INFO  # NOTSET=0, DEBUG=10, INFO=20, WARN=30, ERROR=40, CRITICAL=50

# if conf.LOGFILE_TIMED:
#     log_time = HeFu.timestamp()
# else:
#     log_time = "CR"

# log_time = time.time()
log_time = "test"
rootpath_all_config = ".."
log_filename = "{}/log/Ordinals-{}.log".format(rootpath_all_config, log_time)

logging.basicConfig(
    filename=log_filename,
    level=LOG_LEVEL,
    format=LOG_FORMAT,
    datefmt='%y%m%d_%H:%M:%S',
    filemode="w")
# Setting up logger                                         logger                      -   ENDED   -

lg = logging.getLogger(__name__)
lg.info("START: {:>85} <<<".format('TrackOrdinals.py'))


class CalcOrdinals:
    """=== Class name: CalcOrdinals ====================================================================================
    Object calculates Ordinals of given Bitcoin Outpoint.
    ============================================================================================== by Sziller ==="""
    def __init__(self, txoutpoint: UtxoId, o_loc_ord_range: range or None = None, dotenv_path: str = "./.env"):
        # initial Transaction output to track the Ordinals of
        self.txoutpoint: UtxoId                                 = txoutpoint
        # range of sats inside tx_outpoint to be tracked
        self.o_loc_ord_range: range or None                     = o_loc_ord_range
        self.dotenv_path: str                                   = dotenv_path
        self.node: Node                                         = Node(dotenv_path=self.dotenv_path, is_rpc=True)
        self.ordinals_list: list                                = []
        self.ordinals_collection: list[range or None]           = []
        self.backtrack_roadmap: list[dict[str, range or None]]  = []  # save outpoint:range here
        self.value: int                                         = 0  # number of sat's in root output
        
    def get_collection_length(self) -> int:
        """=== Method name: get_collection_length ======================================================================
        returning the number of ordinals in the list of ranges.
        :return: int - number of ordinal numbers
        ========================================================================================== by Sziller ==="""
        return sum([len(_) for _ in self.ordinals_collection])
        
    def read_init(self):
        tx_data = self.node.nodeop_getrawtransaction(tx_hash=self.txoutpoint.txid, verbose=True)
        self.value = int(round(tx_data['vout'][self.txoutpoint.n]['value'] * 10 ** 8, 8))  # CHECK !!! 8 at end?!!! = tx_data

    def run(self):
        """=== Function name: run ======================================================================================
        initiating recursive run of Method: rec_track_ordinals()
        ========================================================================================== by Sziller ==="""
        self.read_init()
        self.backtrack_roadmap.append({"tx_op": self.txoutpoint.__repr__(), "loc_range": None})
        lg.info("prep - run: {}".format(self.backtrack_roadmap))
        self.rec_track_ordinals()
    
    def rec_track_ordinals(self):
        """=== Method name: rec_track_ordinals =========================================================================
        Recursive function to track orninal numbers of satoshies in a given Transaction.
        <CalcOrdinals> namespace stores data above recursive scope.
        :return:
        ========================================================================================== by Sziller ==="""
        cmn = inspect.currentframe().f_code.co_name  # current method name
        coinbase = False
        
        if self.get_collection_length() != self.value:
            tx_out_data = self.backtrack_roadmap[-1]
            del (self.backtrack_roadmap[-1])
            txoutpoint: UtxoId              = UtxoId.construct_from_string(tx_out_data["tx_op"])  # ID of current output
            o_loc_ord_range: range or None  = tx_out_data["loc_range"]
            lg.info("NEW OUTPOINT: {:>78} <<< new outpoint".format(txoutpoint.__repr__()))
            lg.info("range       : {}".format(o_loc_ord_range))
            # TX data read using Node object
            tx_data = self.node.nodeop_getrawtransaction(tx_hash=txoutpoint.txid, verbose=True)
            # for k, v in tx_data.items():
            #     print("{}: {}".format(k, v))
            nr_of_outputs = len(tx_data['vout'])  # reading number of outputs
            nr_of_inputs = len(tx_data['vin'])  # reading number of inputs
            lg.info("measure   : nr or  inputs:{:>3}".format(nr_of_inputs))
            lg.info("measure   : nr or outputs:{:>3}".format(nr_of_outputs))

            # calculating: current TX outpoints relative ordinals
            o_rel_ord_init: int = 0  # stop pycharm complaining
            o_value: int = 0  # stop pycharm complaining
            o_rel_ord_rear: int = 0  # last range 'ended' with this, in theory

            lg.info("USER-INPUT: output nr: {:>3}".format(txoutpoint.n))
            for _ in range(txoutpoint.n + 1):  # iterating through tx-outpoints till and including current one
                o_value = int(round(tx_data['vout'][_]['value'] * 10 ** 8, 8))  # CHECK !!! 8 at end?!!!
                o_rel_ord_init = o_rel_ord_rear  # passing prev. 'rear' entry as 'init' for current range
                o_rel_ord_rear = o_rel_ord_init + o_value  # last entry in range
                lg.info("value     : of outpoint nr.{:>3}/{:>3} - {} <<<".format(_, txoutpoint.n, o_value))
            o_rel_ord_range_uncropped = range(o_rel_ord_init, o_rel_ord_rear)
            if o_loc_ord_range is None:
                o_loc_ord_range = range(0, o_value)
            o_loc_ord_last = o_loc_ord_range[-1]  # [-1] returns the 'last' entry in a range. 'stop' is always +1
            o_rel_ord_range_cropped = range(o_rel_ord_range_uncropped[o_loc_ord_range[0]],
                                            o_rel_ord_range_uncropped[o_loc_ord_last] + 1)
            lg.info("range -rel: of outpoint nr.{:>3} - {}".format(txoutpoint.n, o_rel_ord_range_cropped))
            lg.info("range -loc: of outpoint nr.{:>3} - {}".format(txoutpoint.n, o_loc_ord_range))
            lg.info("value     : of outpoint nr.{:>3} - {}".format(txoutpoint.n, len(o_rel_ord_range_cropped)))
            lg.info("value     : of outpoint nr.{:>3} - {}".format(txoutpoint.n, len(o_loc_ord_range)))

            # necessary and sufficient to be "coinbase"

            i_rel_ord_init = 0
            i_rel_ord_last = 0
            total_inp_value = 0

            if len(tx_data['vin']) == 1 and "coinbase" in tx_data['vin'][0]:
                blockheight: int = self.node.nodeop_getblock(tx_data["blockhash"])["height"]
                subsidy: int = orsp.subsidy(blockheight)
                initial_ordinal = orsp.first_ordinal(blockheight)
                lg.warning("TX type   : Coinbase TX reached - in block:{:>8}".format(blockheight))
                lg.warning("subsidy   : {}".format(subsidy))
                if subsidy in o_loc_ord_range:
                    lg.warning("WE WILL HAVE TO DEAL WITH FEES")
                    self.ordinals_list.extend(list("fee"))
                else:
                    lg.warning("Writing ordinals")
                    lg.info("analyzing : current TX original ordinals: ")
                    self.ordinals_list.extend(
                        list(range(initial_ordinal + o_loc_ord_range[0], initial_ordinal + o_loc_ord_range[-1] + 1)))
                    nr_of_ords = len(self.ordinals_list)
                    print("ord_init: {}".format(self.ordinals_list[0]))
                    print("ord_last: {}".format(self.ordinals_list[-1]))
                    if nr_of_ords >= self.value:
                        return True
                    else:
                        self.rec_track_ordinals()
                    # return list(range(initial_ordinal, initial_ordinal + len(o_rel_ord_range_cropped)))

            else:
                for c, inp in enumerate(tx_data['vin']):
                    lg.info("loop      : Actual input number:{c:>3}{i:>67}{c:>3}".format(**{'c': c, 'i': "<<< input"}))
                    try:
                        op_id = UtxoId.construct(
                            {"txid": inp['txid'], "n": inp['vout']})  # creating matching outputs outpoint ID
                    except KeyError:
                        raise Exception("It seems we've found a COINBASE TX!")
                    outpoint = self.node.nodeop_get_tx_outpoint(
                        tx_outpoint=op_id)  # searching on-chain for matching output
                    i_rel_ord_init = i_rel_ord_last
                    i_rel_ord_last = int(i_rel_ord_init + outpoint['value'] * 10 ** 8)
                    i_rel_ord_range = range(i_rel_ord_init, i_rel_ord_last)
                    lg.info("local_input: {}".format(i_rel_ord_range))
                    lg.info("global_out: {}".format(o_rel_ord_range_cropped))
                    current_rel_range_overlap = range(max(i_rel_ord_range[0], o_rel_ord_range_cropped[0]),
                                                      min(i_rel_ord_range[-1], o_rel_ord_range_cropped[-1]) + 1)
                    total_inp_value += outpoint['value'] * 10 ** 8
                    if len(current_rel_range_overlap):
                        overlap = True
                        lg.info(
                            "overlap range: {} - {}".format(current_rel_range_overlap, len(current_rel_range_overlap)))

                        # acting recursively:
                        loc_range_overlap = self.calc_loc_range_overlap(parent_range=i_rel_ord_range,
                                                                        subset_range=current_rel_range_overlap)
                        lg.warning("overlap-loc: {}".format(loc_range_overlap))
                        self.backtrack_roadmap.append({'tx_op': op_id.__repr__(), "loc_range": loc_range_overlap})
                        print("CALLING REC")
                        print(self.backtrack_roadmap)
                        # self.rec_track_ordinals()
                    else:
                        lg.info("overlap range: -- NO OVERLAP DETECTED --")
                    # lg.info(total_inp_value)
            
            self.rec_track_ordinals()
        
        else:
            return True
        
        
        
        
        
        
        
            
    @staticmethod
    def calc_loc_range_overlap(parent_range: range, subset_range: range):
        """ADD VALIDATION!!!"""
        return range(subset_range[0] - parent_range[0], subset_range[-1] + 1 - parent_range[0])
        
        
if __name__ == "__main__":
    # tx_id = "7c22da907dbf509b5f60c8b60c8baa68423b9023b99cd5701dfb1a592ffa5741"
    # tx_id = "4bb697b2f8e6160c8ac91fcdfb9acafe3011d44e23f745c301e569a1b3b4a679"  # many outputs
    # tx_id = "d53cb2720b9b00d80aced71d2f68bce2301cab5d3e073fc86838bb62f1abdb4f"  # coinbase related - but not really
    # tx_id = "785822e4f31959ea9b0e3eca7ff9208dd45f968549baa45a66c1155efb28443f"  # tons of inputs - long calc!!!
    # tx_id = "44932e0abb2e8ee770cae42ec4f1a3dc68a4663bb8da87e56258a33b67f68f4a"  # many on both sides
    # tx_id = "21bb393e74b1828e627b985186ef9a93e39e81726613458c3a68bf956757d413"  # general tx
    # tx_id = "dfec52f1557a335185af663b02b84bf517a02dece9fc1f7dd3abfae03696c094"  # ideal for test
    # tx_id = "e44d6f3f6cd8b8beaefcc7449b88c4fe47ac67af5e899cb2c21d2de663914d69"  # ideal for test
    tx_id = "12779f6f559eb8375c81f09ef5d358cc759432a3b789b82b2a2a5508de9100dd"  #
    tx_id = "ffe43993741fa8cb6dbc94316a2f5011730e3a1bec269075a3ccbb82a098f4d0"
    tx_id = "0570eb5d0f361a9f5664c20426d5633997f00aff45dcc50c4f49bec7f99eb7ee"
    n = 2
    field = None
    # field = range(10000, 20000)
    txop = UtxoId.construct({"txid": tx_id, "n": n})
    calculator = CalcOrdinals(txoutpoint=txop, o_loc_ord_range=field, dotenv_path="../.env")
    calculator.run()
    print(len(calculator.ordinals_list))
    print("fee" in calculator.ordinals_list)
    for _ in calculator.backtrack_roadmap:
        print(_)
    # an old coinbase TX - a dead-end, as it should be!
    # 56f26b369c93ba1098afb14fdf213209018904bcef82114a8f019de069dc7a7b
    # 5029302f0c8c1c2ef856194ca8a7f78a7b6ba029b3a432466ba1d4ab2105aef5
    # 525c4eef55f597d0344345ce9439b1e7eeb72053d0682eb2c6910a4f4d695987
    # c880b2fe6c52cc806125af48ca03ad6873627c302aecf006b3c1987a1db879b1
