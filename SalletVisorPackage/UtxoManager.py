"""
Sallet univers' utxo manager
by Sziller
"""

import os
import yaml
import logging
import inspect
from dotenv import load_dotenv
from SalletBasePackage import SQL_interface as sqla, models
from SalletBasePackage import units
from SalletNodePackage import BitcoinNodeObject as BtcNode


# Setting up logger                                         logger                      -   START   -
lg = logging.getLogger()
# Setting up logger                                         logger                      -   ENDED   -

lg.info("START     : {:>85} <<<".format('UtxoManager.py'))


class UTXOManager:
    """=== Classname: UTXOManager ======================================================================================
    Object manages custom made wallet's utxo related tasks, processes.
    Possible usecases and data sources:
    - utxo_set.yaml - a human readable, manually filled in list of UTXO data
    ============================================================================================== by Sziller ==="""
    # Current Class Name
    ccn = inspect.currentframe().f_code.co_name  # current class name
    
    def __init__(self, node: BtcNode or None = None, root_path="./", dotenv_name=".env", session_in=False):
        lg.info("__init__  : {:>60}".format(self.ccn))
        self.node: (BtcNode, None)          = node
        self.root_path: str                 = root_path
        self.dotenv_path: str               = self.root_path + dotenv_name
        load_dotenv(dotenv_path=self.dotenv_path)
        self.unit_used: str                 = os.getenv("UNIT_USE")
        if not session_in:
            self.session                    = sqla.createSession(db_path=self.root_path + os.getenv("DB_PATH_UTXO"),
                                                                 style=os.getenv("DB_STYLE_UTXO"),
                                                                 tables=[sqla.Utxo.__table__])
        else:
            self.session                    = session_in
        self.utxo_obj_dict: dict            = {}  # dict of all utxo objects
        self.path_map: dict     = {"utxo_set": "UTXO_SET_YAML_PATH",
                                   "utxo_set_flat": "UTXO_SET_FLAT_YAML_PATH",
                                   "utxo_id_set": "UTXO_ID_SET_YAML_PATH"}
    
    def __repr__(self):
        """=== Redefined built-in method ===============================================================================
        Defining the appearance of the Instance
        ========================================================================================== by Sziller ==="""
        return "UTXOManager() - Node{}".format(self.node.__repr__())
    
    # ---------------------------------------------------------------------------------------------------
    # - Collection of DATA handling tasks - complex methods                             -   START       -
    # ---------------------------------------------------------------------------------------------------
    
    # UTXO reading methods                                                                          -   START   -
    # Depending on where actual UTXO data is stored, use these methods to read it, and convert it to internal dataset
    # Different sources may be one of the following:
    # - yaml file containing full UTXO data
    # - yaml file containing utxo ID's
    # - sqlite db containing fill UTXO data
    
    def task_update_int_utxo_set_by_utxo_id_set_yaml(self, unit_src: str = "btc") -> dict:
        """=== Method name: task_update_internal_utxo_set_by_utxo_id_set_yaml ==========================================
        Method reads a yaml file containing a list of Utxo_id's in string format and updates (or createds) the set of
        Utxo-s by reading the NODE defined:
        Step 1. importing list of stings
        Step reseting self.utxo_obj_dict
        Step 3. loop:
                1. turning strings into UtxoId instances
                2. searching Node for matching Utxo-s
                3. isntantiating Utxo (using looked-up data)
                4. adding to self.utxo_obj_dict
        (divider has to match with what is defined in the UtxoId class.)
        :param unit_src: str - name ot the unit used in the soure data
        ========================================================================================== by Sziller ==="""
        cmn = inspect.currentframe().f_code.co_name  # current method name
        if self.node:
            yaml_read_in_utxo_id_set = self.read_yaml(mode="utxo_id_set")
            self.utxo_obj_dict: dict = {}
            for _ in yaml_read_in_utxo_id_set:
                utxo_id_obj = models.UtxoId.construct_from_string(_)
                tx = self.node.nodeop_getrawtransaction(tx_hash=utxo_id_obj.txid, verbose=True)
                # Mind if Node under your control answers different syntax dictionary
                utxo_data = tx['vout'][utxo_id_obj.n]
                utxo_data["value"] = int(units.bitcoin_unit_converter(
                    value=utxo_data["value"],
                    unit_in=unit_src,
                    unit_out=self.unit_used))
                self.utxo_obj_dict[utxo_id_obj.__repr__()] = (
                    models.Utxo.construct(utxo_id_obj=utxo_id_obj, **utxo_data))
            return self.utxo_obj_dict
        else:
            msg = "not found : Node not defined! - says {}.{}".format(self.ccn, cmn)
            lg.critical(msg)
            raise Exception(msg)
    
    def task_update_int_utxo_set_by_utxo_set_yaml(self, unit_src: str) -> dict:
        """=== Method name: task_update_internal_utxo_set_by_utxo_set_yaml =============================================
        Method reads a yaml file containing a list of Utxo data in string format and updates (or createds) the set of
        Utxo-s:
        Step 1. importing list of stings
        Step reseting self.utxo_obj_dict
        Step 3. loop:
                1. turning strings into Utxo data dictionaries
                2. isntantiating Utxo (using data read)
                3. adding to self.utxo_obj_dict
        :param unit_src: str - name ot the unit used in the soure data
        ========================================================================================== by Sziller ==="""
        cmn = inspect.currentframe().f_code.co_name  # current method name
        yaml_read_in_utxo_set = self.read_yaml(mode="utxo_set")
        self.utxo_obj_dict: dict = {}
        for _ in yaml_read_in_utxo_set:
            _["value"] = units.bitcoin_unit_converter(value=_["value"], unit_in=unit_src, unit_out=self.unit_used)
            utxo_id_obj = models.UtxoId.construct_from_string(_['utxo_id'])
            self.utxo_obj_dict[utxo_id_obj.__repr__()] = models.Utxo.construct(utxo_id_obj=utxo_id_obj, **_)
        return self.utxo_obj_dict
        
    def task_update_int_utxo_set_by_db(self, unit_src: str) -> dict:
        """=== Method name: task_update_internal_utxo_set_by_db ========================================================
        Method reads a Sqlite DB file containing Utxo data and updates (or createds) the set of Utxo-s:
        Step 1. importing DB data
        Step reseting self.utxo_obj_dict
        Step 3. loop:
                1. turning lines into Utxo data dictionaries
                2. isntantiating Utxo (using data read)
                3. adding to self.utxo_obj_dict
        :param unit_src: str - name ot the unit used in the soure data
        ========================================================================================== by Sziller ==="""
        cmn = inspect.currentframe().f_code.co_name  # current method name
        utxo_set_data = self.read_db()
        self.utxo_obj_dict: dict = {}
        for _ in utxo_set_data:
            utxo_id_obj = models.UtxoId.construct_from_string(_['utxo_id'])
            _['utxo_id'] = utxo_id_obj
            _["value"] = units.bitcoin_unit_converter(value=_["value"], unit_in=unit_src, unit_out=self.unit_used)
            self.utxo_obj_dict[utxo_id_obj.__repr__()] = models.Utxo.construct_from_flat_inputdict(
                utxo_id_obj=utxo_id_obj, **_)
        return self.utxo_obj_dict

    # UTXO reading methods                                                                          -   ENDED   -

    # UTXO writing methods                                                                          -   START   -
    
    def task_export_int_utxo_to_db(self, unit_trg: str, export_session=None):
        """=== Method name: task_export_int_utxo_to_db =================================================================
        ========================================================================================== by Sziller ==="""
        cmn = inspect.currentframe().f_code.co_name  # current method name
        dict_for_export = []
        for obj in self.utxo_obj_dict.values():
            _ = obj.return_db_inputdict()
            _["value"] = units.bitcoin_unit_converter(value=_["value"], unit_in=self.unit_used, unit_out=unit_trg)
            dict_for_export.append(_)
        
        sqla.ADD_rows_to_table(primary_key="utxo_id",
                               data_list=dict_for_export,
                               db_table="utxoset",
                               session_in=export_session)
    
    def task_export_int_utxo_to_yaml(self, unit_trg: str, mode: str = "utxo_set", fullfilename: str = "./utxo-set.yaml"):
        """=== Method name: write_yaml =================================================================================
        Method writes data to yaml file.
        ========================================================================================== by Sziller ==="""
        cmn = inspect.currentframe().f_code.co_name  # current class name

        if mode in list(self.path_map.keys()):
            yaml_path = self.root_path + os.getenv(self.path_map[mode])
            yaml_path = "./TEST_yaml.yaml"
            if mode == "utxo_set_flat":
                data_to_dump = [_.return_db_inputdict() for _ in self.utxo_obj_dict.values()]  # compressed as in DB
            elif mode == "utxo_set":
                data_to_dump = [_.data() for _ in self.utxo_obj_dict.values()]  # uncompressed as on Node
            elif mode == "utxo_id_set":
                data_to_dump = [_ for _ in self.utxo_obj_dict.keys()]  # ID's only in list (TX-outpoints)
            else:
                msg = "<mode> = '{}' not implemented yet! - says {}.{}".format(mode, self.ccn, cmn)
                lg.critical(msg)
                raise Exception(msg)
            for _ in data_to_dump:
                _["value"] = units.bitcoin_unit_converter(value=_["value"], unit_in=self.unit_used, unit_out=unit_trg)
            with open(yaml_path, 'w') as outfile:
                yaml.dump(data_to_dump, outfile, default_flow_style=False)
        else:
            msg = "<mode> = '{}' unrecognized! - says {}.{}".format(mode, self.ccn, cmn)
            lg.critical(msg)
            raise Exception(msg)
    # UTXO writing methods                                                                          -   ENDED   -

    # ---------------------------------------------------------------------------------------------------
    # - Collection of DATA handling tasks - complex methods                             -   ENDED       -
    # ---------------------------------------------------------------------------------------------------

    # ---------------------------------------------------------------------------------------------------
    # - Collection of DATA handling scripts - simple methods                            -   START       -
    # ---------------------------------------------------------------------------------------------------
    
    def read_yaml(self, mode: str = "utxo") -> list:
        """=== Method name: read_yaml ==================================================================================
        Method reads in data from yaml file and returns it. We do not store Data read from yaml as there can be many
        different information forms stored, e.g:
        - set of utxo_id's (transaction outpoints)
        - set of utxo's
        ========================================================================================== by Sziller ==="""
        cmn = inspect.currentframe().f_code.co_name  # current method name

        if mode in list(self.path_map.keys()):
            yaml_path = self.root_path + os.getenv(self.path_map[mode])
            with open(yaml_path, 'r') as stream:
                try:
                    lg.info("read in   : {}-set from {}\n - says {}".format(mode, yaml_path, self.ccn))
                    return yaml.safe_load(stream)
                except yaml.YAMLError as exc:
                    msg = "read in   : failed from {}\n - says {}".format(yaml_path, self.ccn)
                    lg.critical(exc)
                    lg.critical(msg)
                    raise Exception(msg)
        else:
            msg = "<mode> = '{}' unrecognized! - says {}.{}".format(mode, self.ccn, cmn)
            lg.critical(msg)
            raise Exception(msg)

    def read_db(self):
        """=== Method name: read_db ====================================================================================
        Method reads in UTXO set from yaml file.
        ========================================================================================== by Sziller ==="""
        return sqla.QUERY_entire_table(ordered_by="addresses",
                                       db_table=os.getenv("DB_ID_TABLE_UTXO"),
                                       session_in=self.session)
    
    # ---------------------------------------------------------------------------------------------------
    # - Collection of DATA handling scripts - simple methods                            -   ENDED       -
    # ---------------------------------------------------------------------------------------------------
    
    def return_utxo_id_string_set(self) -> set:
        """=== Method name: return_utxo_id_string_set ==================================================================
        Get the set of utxo ID's in for of strings (with dividers)
        :return: set - of uxto_id's
        ========================================================================================== by Sziller ==="""
        return {k for k in self.utxo_obj_dict.keys()}
    
    def return_utxo_id_obj_list(self) -> list:
        """=== Method name: return_utxo_id_obj_list ====================================================================
        Get the list of utxo_id objects
        :return: list - of uxto_id objects
        ========================================================================================== by Sziller ==="""
        return [k.utxo_id for k in self.utxo_obj_dict.values()]
        
    def return_total_balance(self):
        """=== Method name: return_total_balance =======================================================================
        Method calculates the balance of all UTXO-s in the stored utxo set
        ========================================================================================== by Sziller ==="""
        value_in_btc = sum([_.value for _ in self.utxo_obj_dict.values()])
        return units.bitcoin_unit_converter(value=value_in_btc, unit_in="btc", unit_out=os.getenv("UNIT_BASE"))
 
    def return_address_set(self) -> set:
        """=== Method name: return_address_set =========================================================================
        Method calculates the balance of all UTXO-s in the stored utxo set
        ========================================================================================== by Sziller ==="""
        address_list = []
        for obj in self.utxo_obj_dict.values():
            address_list += obj.scriptPubKey.addresses
        return set(address_list)
            
    def return_balance_by_addresslist(self, addresses: set or None = None) -> dict:
        """=== Method name: return_balance_by_address ==================================================================
        ATTENTION, only working with single address UTXO's properly.
        When used with addresses = None, the entire utxo set is considered
        ========================================================================================== by Sziller ==="""
        if addresses is None:
            addresses = self.return_address_set()
        detailed_balance = {_: 0 for _ in addresses}
        for address in addresses:
            for utxo_obj in self.utxo_obj_dict.values():
                if address in utxo_obj.scriptPubKey.addresses:
                    detailed_balance[address] += utxo_obj.value
        return {k: round(v, 8) for k, v in detailed_balance.items()}


if __name__ == "__main__":
    # NOTSET=0, DEBUG=10, INFO=20, WARN=30, ERROR=40, CRITICAL=50
    logging.basicConfig(filename="../log/UtxoManager.log", level=logging.NOTSET, filemode="w",
                        format="%(asctime)s [%(levelname)8s]: %(message)s", datefmt='%y%m%d %H:%M:%S')
    lg.warning("START: {:>85} <<<".format('__name__ == "__main__" namespace: UtxoManager.py'))
    node = BtcNode.Node(alias="sziller", is_rpc=True)
    mngr = UTXOManager(node=node, dotenv_name=".env", root_path="../")
    
    # -------------------------------------------------------------------------------------------------------
    # - Testing: UTXOManager                                                                    -   START   -
    # -------------------------------------------------------------------------------------------------------
    
    mngr.task_update_int_utxo_set_by_db(unit_src="btc")
    lg.info(mngr.return_balance_by_addresslist(addresses=
                                               # {'1Ett9x7n37pth8yXZ2RW3EfprrWe6MPqsj'}
                                               None))
    lg.info(mngr.return_total_balance())

    # summarize(UTXO)

    # uncomment:
    # from btc_sziller_Class_package import BaseClasses as BC
    #
    # counter_spec = 0
    # counter_all = 0
    # act_addr = "19zohsYZfQX6TG9FjCeD8FW21q3yHj6KWA"
    # for _ in UTXO:
    #     counter_all += 1
    #     if _['address'] == act_addr: counter_spec += 1
    #
    # amount_list_spec = [_["sat_value"] for _ in UTXO if _["address"] == act_addr]
    # amount_list_all = [_["sat_value"] for _ in UTXO]
    # amount_spec = sum(amount_list_spec)
    # amount_all = sum(amount_list_all)
    # print("Nr of UTXO for address {:>40} - {}".format(act_addr, counter_spec))
    # print("Nr of UTXO in set      {:>40} - {}".format(" ", counter_all))
    # print("Balance of address     {:>40} - {}".format(act_addr, int(BC.bitcoin_unit_converter(value=amount_spec, unit_in='btc', unit_out="sat"))))
    # print("Balance of UTXOset     {:>40} - {}".format(" ", int(BC.bitcoin_unit_converter(value=amount_all, unit_in='btc', unit_out="sat"))))
