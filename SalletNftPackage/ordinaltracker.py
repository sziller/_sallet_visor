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
        
examples:
o_op_tot_rng: output side range of sats in a given output where numbering starts from the first sat in the output
o_op_crp_rng: output side range of sats in a given output, narrowed down to only sats in question (method param)
o_tx_crp_rng: output side range of sats in the transaction of the output, narrowed down to only sats in question

If interested in an entire output (which is most of the time the case) you simply do NOT define a range.
This way the function sets the < o_op_crp_rng > = < o_op_tot_rng > and considers all the sats in the output.
"""

import logging
import inspect

import bitcoinlib.transactions

from SalletBasePackage.models import UtxoId
from SalletNodePackage.BitcoinNodeObject import Node


lg = logging.getLogger(__name__)
lg.info("START: {:>85} <<<".format('ordinaltracker.py'))


class OrdinalTracker:
    """=== Class name: Track ===========================================================================================
    Class wrapped around recursive method in order to not have to roll cumulative data
    ============================================================================================== by Sziller ==="""
    def __init__(self, node: Node, init_output_id: UtxoId, o_op_crp_rng: (range, None) = None):
        self.node: Node                                         = node
        self.ordinals_collection: list[(range, None)]           = []  # cumulative data to store Ordinal-ranges
        self.init_output_id: UtxoId                             = init_output_id
        self.init_op_crp_rng: (range, None)                     = o_op_crp_rng
        
        self.depth: int                                         = 0
        
        lg.warning("=== INCOMING ====================================================================   START  =")
        lg.warning("op_id: {}".format(self.init_output_id))
        lg.warning("range: {}".format(self.init_op_crp_rng))
        if self.init_op_crp_rng:
            lg.warning("value: {}".format(len(self.init_op_crp_rng)))
        lg.warning("=== INCOMING ====================================================================   ENDED  =")
        
    def get_collection_length(self) -> int:
        """=== Method name: get_collection_length ======================================================================
        Returning the number of ordinals in the list of ranges.
        :return: int - number of ordinal numbers
        ========================================================================================== by Sziller ==="""
        return sum([len(_) for _ in self.ordinals_collection])
    
    @staticmethod
    def check_if_coinbase(tx_data_hxstr: dict):
        """=== Method name: check_if_coinbase ==========================================================================
        Under development: check if TX entered is coinbase:
        ========================================================================================== by Sziller ==="""
        hxstr_template = "01{}ffffffff".format(32 * '00')
        if hxstr_template in tx_data_hxstr[:(8 + 2 + 64 + 8 + 16)]:
            return True
        return False
    
    @staticmethod
    def range_overlap(rng_x: range, rng_y: range) -> range:
        """=== Method name: range_overlap ==============================================================================
        Method returns the longest range, being part of both input ranges.
        ATTENTION! Not for general use: for performance reasons - stepsize is assumed to be one!!!
        Only to be usd with ordinal tracker, or if you know what you are doing!
        :param rng_x: range - to be checked
        :param rng_y: range - to be checked
        :return: range - representing the overlap
        ========================================================================================== by Sziller ==="""
        ans = range(max(rng_x.start, rng_y.start), min(rng_x.stop, rng_y.stop))
        return ans if len(ans) else False
        
    def track(self):
        """=== Method name: run ========================================================================================
        Activates the recursive process
        ========================================================================================== by Sziller ==="""
        self.rec_ordinal_calc(output_id=self.init_output_id, rng=self.init_op_crp_rng)
    
    def rec_ordinal_calc(self, output_id: UtxoId, rng: (range, None)):
        """=== Method name: rec_ordinal_calc =========================================================================
        This is a function to calculate a given outputs Ordinal numbers.
        It can work recursively as the basic working principle repeats all the way to the coinbase subsiby, where
        - if arrived at - the Ordinals are calculated.
        Function however already considers Ordinal calculation specification as part of its algorithm,
        so it's not enough to simply replace fimal ordinal calc, in case spec. is changed.
        
        This function takes:
        - an output of a given TX (it's outpoint ID - TX ID + index == 36bytes in TX)
        - and the range of satoshies the user wants to calculate Ordinals for
        ...and does one of the following 2 things:
        - returns the same 2 data for the TX's relevant inputs, as was granted for IT, thus recourivelly calling itself.
        - or - if it arrives at a subsiby - originated range, it returns Ordinals.
        
        The whole repetition goes on until all sats in the entered range are being labelled with Ordinals.
        tbd...
        :param output_id: class - UtxoID - the ID defining a unique output on the Blockchain
        :param rng: an o_op_crp_rng:
        - o:    output side - of the TX
        - op:   output level - ordinals
        - crp:  cropped - the continous range of satoshies to be assigned Ordinals (blockchain lvl) to.
        - rng:  range - as it is easier to store both for performance and practical reasons.
        ============================================================================================== by Sziller ==="""
        cmn = inspect.currentframe().f_code.co_name
        lg.info("[- HINT -]: {:>5} - {:>72} {}".format(self.depth, cmn, "<<<"))
        # ---------------------------------------------------------------------------------------------------
        # - general TX data (tx)
        # ---------------------------------------------------------------------------------------------------
        # Node-independent TX query: raw ty in binary format. (hex-string)
        tx_data_raw = self.node.nodeop_getrawtransaction(tx_hash=output_id.txid, verbose=False)
        tx_data = bitcoinlib.transactions.Transaction.parse(tx_data_raw).as_dict()
        try:
            output_data = tx_data['outputs'][output_id.n]
        except IndexError:
            msg = "IndexError: TX has no outpoint defined by UtxoId!"
            lg.critical(msg)
            raise Exception(msg)
        lg.warning("processing: {}".format(output_id.txid))
        
        lg.info("==== TX data =========================================================== START ===")
        lg.info("_ IN:  {:>3} ______________________________________________________________________________"
              .format(len(tx_data["inputs"])))
        # for _ in tx_data["inputs"]:
        #     lg.debug("{}".format(_))
        lg.info("_ OUT: {:>3} ______________________________________________________________________________"
              .format(len(tx_data["outputs"])))
        # for _ in tx_data["outputs"]:
        #     lg.debug("{}".format(_))
        lg.info("==== TX data =========================================================== ENDED ===")
        lg.info("==== output data ======================================================= START ===")
        lg.info(output_data)
        lg.info("==== output data ======================================================= ENDED ===")
        # ---------------------------------------------------------------------------------------------------
        # - output side (o)
        # ---------------------------------------------------------------------------------------------------
        # preparation                                                                   START   -
        
        # total value spent in output in question: < output_value_tot >
        # output_value_tot = int(round(output_data['value'] * (10 ** 8), 8))
        output_value_tot = output_data['value']
        # reading of or setting default to < rng > - this is the < o_op_crp_rng > range of the entered output.
        rng = range(0, output_value_tot) if rng is None else rng
        lg.debug("default   : <o_tx_crp_rng> ")
        # length measured: number of satoshis in range
        output_sum = len(rng)  # the value (or number of sats) included in the range entered
        # INFO level logging of method call
        lg.info("{} > {} / {}".format(output_id.__repr__(), output_sum, output_value_tot))
        lg.info("")
        if output_sum > output_value_tot:  # or (rng.stop > output_value):
            raise Exception("Range entered is too long! rng (entered): {} - of length: {}\n"
                            "max. output_value_tot: (allowed) {}".format(rng, output_sum, output_value_tot))
        # preparation                                                                   ENDED   -

        # conversion o_op_crp_rng -> o_tx_crp_rng                                       START   -
        # calculating the place of satoshis in question inside the transaction
        o_tx_crp_rng = False
        o_val: int = 0
        for _ in range(output_id.n + 1):  # iterating through tx-outpoints till and including current one
            # add = int(round(tx_data['outputs'][_]['value'] * 10 ** 8, 8))  # CHECK !!! 8 at end?!!!
            o_tx_crp_rng = range(o_val + rng.start, o_val + rng.stop)
            add = tx_data['outputs'][_]['value']
            o_val += add
            lg.debug("value     : of output_id nr.{:>3}/{:>3} - {:>35} - {:14.8f}<<<"
                     .format(_, output_id.n, str(range(o_val - add, o_val)), add / 10**8))
        lg.warning("[- HINT -]: of output_id nr.{:>3}/{:>3} - {:>35} - {:<14} sat<<<"
                .format(output_id.n, output_id.n, str(o_tx_crp_rng), output_sum))
        # conversion o_op_crp_rng -> o_tx_crp_rng                                       ENDED   -
        
        # At this stage the range of sats is the chosen output is represented as local ordinals on tx level.
        # this tx lvl ordinal is used on the input side!

        # ---------------------------------------------------------------------------------------------------
        # - input side (i)
        # ---------------------------------------------------------------------------------------------------
        # preparation                                                                   START   -
        input_sum = 0
        inp_cum_val = 0
        input_nr = 0
        is_coinbase = self.check_if_coinbase(tx_data_hxstr=tx_data_raw)
        lg.info("Coinbase TX: {:>5}".format(str(is_coinbase)))
        # preparation                                                                   ENDED   -
        
        if is_coinbase:
            # Input side - coinbase transaction                                                 START   -
            lg.error("we reached a coinbase TX")
            # Input side - coinbase transaction                                                 ENDED   -
        else:
            # Input side - regular transaction                                                  START   -
            while input_sum < output_sum:
                # print(tx_data["inputs"])
                print("check input: {}".format(input_nr))
                act_input = tx_data["inputs"][input_nr]
                lg.info("loop      : Actual input number:{c:>3}{i:>67}{c:>3}".format(**{'c': input_nr, 'i': "<<< input"}))
                op_id = UtxoId.construct({"txid": act_input['prev_txid'], "n": act_input['output_n']})  # creating matching outputs outpoint ID
                curr_output_value = self.node.nodeop_get_tx_outpoint_value(tx_outpoint=op_id)
                lg.info("curr value: {}".format(curr_output_value))
                
                inp_cum_val += curr_output_value
                print("!!!!!!!!!!!!!!!!!!!!!!!!!!! {}".format(curr_output_value))
                
                i_tx_loc_rng = range(inp_cum_val - curr_output_value, inp_cum_val)
                print("i_tx_loc_rng: {} - {}".format(i_tx_loc_rng, len(i_tx_loc_rng)))
                print("o_tx_crp_rng: {} - {}".format(o_tx_crp_rng, len(o_tx_crp_rng)))
                i_tx_crp_rng = self.range_overlap(i_tx_loc_rng, o_tx_crp_rng)
                print(":::::::: {}".format(i_tx_crp_rng))
                if i_tx_crp_rng:
                    i_op_crp_rng = range(i_tx_crp_rng.start - input_sum, i_tx_crp_rng.stop - input_sum)
                    print("Rec. call: {} with range: {}".format(op_id.__repr__(), str(i_op_crp_rng)))
                    lg.warning("RECURSIVE call! [- HINT -]: {} with range: {}".format(op_id.__repr__(), str(i_op_crp_rng)))
                    self.depth += 1
                    # i_op_crp_rng must be reentered a lvl lower
                    self.rec_ordinal_calc(output_id=op_id, rng=i_op_crp_rng)  # wrong range - PROBABLY
                    self.depth -= 1
                    input_sum += len(i_tx_crp_rng)  ###
                print("input : {}\noutput: {}".format(input_sum, output_sum))
                input_nr += 1
            # Input side - regular transaction                                                  ENDED   -
    
    
if __name__ == "__main__":
    log_time = "test"
    rootpath_all_config = ".."
    log_filename = "{}/log/ordinaltracker-{}.log".format(rootpath_all_config, log_time)

    LOG_FORMAT = "%(asctime)s [%(levelname)8s]: %(message)s"
    LOG_LEVEL = logging.DEBUG  # NOTSET=0, DEBUG=10, INFO=20, WARN=30, ERROR=40, CRITICAL=50

    logging.basicConfig(
        filename=log_filename,
        level=LOG_LEVEL,
        format=LOG_FORMAT,
        datefmt='%y%m%d_%H:%M:%S',
        filemode="w")
    
    txid = "ef37b2b383025ddf87209dc4a64dfb48010a274eddc3f16434fe14366241e360"
    txid = "12779f6f559eb8375c81f09ef5d358cc759432a3b789b82b2a2a5508de9100dd"
    # txid = "dfec52f1557a335185af663b02b84bf517a02dece9fc1f7dd3abfae03696c094"
    # txid = "785822e4f31959ea9b0e3eca7ff9208dd45f968549baa45a66c1155efb28443f"
    # txid = "56f26b369c93ba1098afb14fdf213209018904bcef82114a8f019de069dc7a7b"
    # txid = "23539386b3d10a1134e56e85119807208b1c6e9f32953e1a47e3e536df1c21f3"
    # txid = "25aeae01d227d576a3cb6ff7d7cde42623334999a7ba6104b2dd2a3c9cf3e948" 
    index = 4
    _id_ = UtxoId.construct_from_string(str_in="{}_{}".format(txid, index))
    
    span = range(10000, 70000)
    # span = None
    main_node = Node(is_rpc=False, dotenv_path="../.env", alias="sziller.eu")
    tracker = OrdinalTracker(node=main_node, init_output_id=_id_, o_op_crp_rng=span)
    tracker.track()
    
    # tr01 = range(0, 14237000000)
    # tr02 = range(5258000100, 5258000200)
    # 
    # print(r:=OrdinalTracker.range_overlap(tr01, tr02))
    # print(r)
