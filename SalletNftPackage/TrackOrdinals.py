"""
Tracking ordinals on Bitcoin:

we use 3 different expressions to distinguish between different types of ordinals:
- abs: absolute - the ordinal numbers on-chain
- rel: relative - ordinal numbers inside a TX
- loc: rel.local ordinals inside a given input or output
"""

import bitcoinlib
import time
import logging
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
    def __init__(self, txoutpoint: UtxoId, o_loc_ord_range: range or None = None):
        pass
        self.txoutpoint: UtxoId or None     = txoutpoint  # initial Transaction output to track the Ordinals of
        self.o_loc_ord_range: range or None = o_loc_ord_range  # range of sats inside tx_outpoint to be tracked
        self.node = Node(dotenv_path="../.env")

    def run(self):
        """=== Function name: run ======================================================================================
        initiating recursive run of Method: rec_track_ordinals()
        ========================================================================================== by Sziller ==="""
        self.rec_track_ordinals(txoutpoint=self.txoutpoint, o_loc_ord_range=None)
    
    def rec_track_ordinals(self, txoutpoint: UtxoId, o_loc_ord_range: range or None = None):
        """
        
        :return:
        """
        tx_data = self.node.nodeop_getrawtransaction(tx_hash=txoutpoint.txid, verbose=True)
        nr_of_outputs = len(tx_data['vout'])
        nr_of_inputs = len(tx_data['vin'])
        lg.info("measure   : nr or  inputs:{:>3}".format(nr_of_inputs))
        lg.info("measure   : nr or outputs:{:>3}".format(nr_of_outputs))
        for k, v in tx_data.items():
            print("{}: {}".format(k, v))
        # TX data read
        if len(tx_data['vin']) == 1 and "coinbase" in tx_data['vin'][0]:
            lg.warning("coinbase  : WE have a Coinbase TX on our hand!")
            blockheight = self.node.nodeop_getblock(tx_data["blockhash"])["height"]
            lg.warning(blockheight)
            lg.warning("subsidy   : {}".format(orsp.subsidy(blockheight)))
            
            
        
        # example for our case:
        # (5, 6, 7, 8)
        # range(5, 9) -> range (init, stop) -> (init, ...., last)
        # 5: init
        # 8: last
        # 9: stop
        # len = stop - init = 4 = 9 - 5
        # stop = last + 1 = 9 = 8 + 1
        # (9, 10, 11)
        # previous range's stop = subsequent range's init
        
        o_rel_ord_init = 0  # stop pycharm complaining
        o_value = 0  # stop pycharm complaining
        o_rel_ord_rear = 0  # last range 'ended' with this, in theory
        
        lg.info("USER-INPUT: output nr: {:>3}".format(txoutpoint.n))
        for _ in range(txoutpoint.n + 1):  # iterating through tx-outpoints till and including current one
            try:
                o_value = int(round(tx_data['vout'][_]['value'] * 10 ** 8, 8))  # CHECK !!! 8 at end?!!!
            except IndexError:
                raise Exception("TX does not have that many outputs!!!")
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
        i_rel_ord_init = 0
        i_rel_ord_last = 0
        total_inp_value = 0
        for c, inp in enumerate(tx_data['vin']):
            lg.info("loop      : Actual input number:{c:>3}{i:>67}{c:>3}".format(**{'c': c, 'i': "<<< input"}))
            try:
                op_id = UtxoId.construct({"txid": inp['txid'], "n": inp['vout']})  # creating matching outputs outpoint ID
            except KeyError:
                raise Exception("It seems we've found a COINBASE TX!")
            outpoint = self.node.nodeop_get_tx_outpoint(tx_outpoint=op_id)  # searching on-chain for matching output
            i_rel_ord_init = i_rel_ord_last
            i_rel_ord_last = int(i_rel_ord_init + outpoint['value'] * 10**8)
            i_rel_ord_range = range(i_rel_ord_init, i_rel_ord_last)
            lg.info("local_input: {}".format(i_rel_ord_range))
            lg.info("global_out: {}".format(o_rel_ord_range_cropped))
            current_rel_range_overlap = range(max(i_rel_ord_range[0],   o_rel_ord_range_cropped[0]),
                                              min(i_rel_ord_range[-1], o_rel_ord_range_cropped[-1]) + 1)
            total_inp_value += outpoint['value'] * 10**8
            if len(current_rel_range_overlap):
                lg.info("overlap range: {} - {}".format(current_rel_range_overlap, len(current_rel_range_overlap)))
                
                # acting recursively:
                loc_range_overlap = self.calc_loc_range_overlap(parent_range=i_rel_ord_range, subset_range=current_rel_range_overlap)
                lg.warning("overlap-loc: {}".format(loc_range_overlap))
                self.rec_track_ordinals(txoutpoint=op_id, o_loc_ord_range=loc_range_overlap)
            else:
                lg.info("overlap range: -- NO OVERLAP DETECTED --")
            # lg.info(total_inp_value)
        
        print(total_inp_value)
        # outpoint_data = tx_data['vout'][txoutpoint.n]
        
        # print(outpoint_data)
        #for inp in tx_data['vin']:
            
    @staticmethod
    def calc_loc_range_overlap(parent_range: range, subset_range: range):
        """ADD VALIDATION!!!"""
        return range(subset_range[0] - parent_range[0], subset_range[-1] + 1 - parent_range[0])
        
if __name__ == "__main__":
    # tx_id = "7c22da907dbf509b5f60c8b60c8baa68423b9023b99cd5701dfb1a592ffa5741"
    # tx_id = "4bb697b2f8e6160c8ac91fcdfb9acafe3011d44e23f745c301e569a1b3b4a679"  # many outputs
    # tx_id = "d53cb2720b9b00d80aced71d2f68bce2301cab5d3e073fc86838bb62f1abdb4f"  # coinbase related
    # tx_id = "785822e4f31959ea9b0e3eca7ff9208dd45f968549baa45a66c1155efb28443f"  # tons of inputs - long calc!!!
    # tx_id = "44932e0abb2e8ee770cae42ec4f1a3dc68a4663bb8da87e56258a33b67f68f4a"  # many on both sides
    # tx_id = "21bb393e74b1828e627b985186ef9a93e39e81726613458c3a68bf956757d413"  # general tx
    # tx_id = "dfec52f1557a335185af663b02b84bf517a02dece9fc1f7dd3abfae03696c094"  # ideal for test
    # tx_id = "e44d6f3f6cd8b8beaefcc7449b88c4fe47ac67af5e899cb2c21d2de663914d69"  # ideal for test
    tx_id = "12779f6f559eb8375c81f09ef5d358cc759432a3b789b82b2a2a5508de9100dd"  #
    tx_id = "ffe43993741fa8cb6dbc94316a2f5011730e3a1bec269075a3ccbb82a098f4d0"
    n = 0
    field = None
    # field = range(10000, 20000)
    txop = UtxoId.construct({"txid": tx_id, "n": n})
    calculator = CalcOrdinals(txoutpoint=txop, o_loc_ord_range=field)
    calculator.run()

    # an old coinbase TX - a dead-end, as it should be!
    # 56f26b369c93ba1098afb14fdf213209018904bcef82114a8f019de069dc7a7b
    # 5029302f0c8c1c2ef856194ca8a7f78a7b6ba029b3a432466ba1d4ab2105aef5
    # 525c4eef55f597d0344345ce9439b1e7eeb72053d0682eb2c6910a4f4d695987
    
