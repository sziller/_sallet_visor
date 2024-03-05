"""Objects used in the Sallet universe"""

import inspect


class UtxoId:
    divider: str = "_"
    ccn = inspect.currentframe().f_code.co_name
    
    def __init__(self, txid: str, n: int):
        self.txid: str = txid
        self.n: int = n
    
    def __repr__(self):
        return "{}{}{}".format(self.txid, self.divider, self.n)

    @classmethod
    def construct(cls, d_in):
        """=== Classmethod: construct ==================================================================================
        Input necessary class parameters to instantiate object of the class!
        @param d_in: dict - format data to instantiate new object
        @return: an instance of the class
        ========================================================================================== by Sziller ==="""
        return cls(**d_in)

    @classmethod
    def construct_from_string(cls, str_in):
        """=== Classmethod: construct ==================================================================================
        Input necessary class parameters to instantiate object of the class!
        @param str_in: str - format data to instantiate new object
        @return: an instance of the class
        ========================================================================================== by Sziller ==="""
        utxo_id_atom_list = "{}".format(str_in).split(sep=UtxoId.divider)
        return cls(txid=utxo_id_atom_list[0], n=int(utxo_id_atom_list[1]))
    

class Utxo:
    """=== Class name: Utxo ============================================================================================
    ============================================================================================== by Sziller ==="""
    ccn = inspect.currentframe().f_code.co_name
    
    def __init__(self, utxo_id: UtxoId):
        self.utxo_id: UtxoId                    = utxo_id
        self.separator = UtxoId.divider
        utxo_id_atom_list                       = "{}".format(self.utxo_id).split(sep=self.separator)
        self.txid: str                          = utxo_id_atom_list[0]
        self.n: int                             = int(utxo_id_atom_list[1])
        self.value: float                       = 0.0
        self.scriptPubKey: ScriptPubKey or None = None

    def data(self):
        """actual dictionary to be returned"""
        return {'utxo_id':      "{}".format(self.utxo_id),
                'n':            self.n,
                'txid':         self.txid,
                'value':        self.value,
                'scriptPubKey': self.scriptPubKey}

    @classmethod
    def construct(cls, d_in):
        """=== Classmethod: construct ==================================================================================
        Input necessary class parameters to instantiate object of the class!
        @param d_in: dict - format data to instantiate new object
        @return: an instance of the class
        ========================================================================================== by Sziller ==="""
        return cls(**d_in)


class ScriptPubKey:
    """=== Class name: ScriptPubKey ====================================================================================
    ============================================================================================== by Sziller ==="""
    ccn = inspect.currentframe().f_code.co_name
    
    def __init__(self, spk_ams: str, spk_hex: str, spk_reqSigs: int, spk_type: str, spk_addresses: list):
        self.asm: str               = spk_ams
        self.hex: str               = spk_hex
        self.reqSigs: int           = spk_reqSigs
        self.type: str              = spk_type
        self.addresses: list[str]   = spk_addresses

    @classmethod
    def construct(cls, d_in):
        """=== Classmethod: construct ==================================================================================
        Input necessary class parameters to instantiate object of the class!
        @param d_in: dict - format data to instantiate new object
        @return: an instance of the class
        ========================================================================================== by Sziller ==="""
        return cls(spk_ams=d_in['ams'],
                   spk_hex=d_in['hex'],
                   spk_reqSigs=d_in['reqSigs'],
                   spk_type=d_in['type'],
                   spk_addresses=d_in['addresses'])


class PrivateKey:
    ccn = inspect.currentframe().f_code.co_name
    
    def __init__(self, owner: str, kind: int):
        self.hxstr: str     = ""
        self.owner: str     = owner
        self.kind: int      = kind
        self.comment: str   = ""


class MerkleDerived(PrivateKey):
    ccn = inspect.currentframe().f_code.co_name
    
    def __init__(self, owner, root_hxstr, kind: int = 1, deriv_nr: int = 0):
        super().__init__(owner, kind)
        self.root_hxstr: str = root_hxstr
        self.deriv_nr: int  = deriv_nr


if __name__ == "__main__":
    pass
    newkey = MerkleDerived(owner="sziller")
    """
    txid = "bbfa2e90208029653940f44299b8ce980ed228cb859c29821090af95c7fb9817"
    vout = 0
    utxo_id = UtxoId(txid=txid, vout=vout)
    utxo = Utxo(utxo_id=utxo_id)
    
    print(utxo.data())
    """
