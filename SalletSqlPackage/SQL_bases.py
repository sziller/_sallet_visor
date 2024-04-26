"""
SQLAlchemy powered DB Bases: test, and production code.
by Sziller
"""

# imports for general Base handling START                                                   -   START   -
from sqlalchemy import Column, Integer, String, JSON
from sqlalchemy.ext.declarative import declarative_base
# imports for general Base handling ENDED                                                   -   ENDED   -

# imports for local Base handling   START                                                   -   START   -
import random as rnd
from SalletBasePackage import models
# imports for local Base handling   ENDED                                                   -   ENDED   -

Base = declarative_base()


class Utxo(Base):
    """=== Classname: Utxo(Base) =======================================================================================
    Class represents a Utxo Database Entry who's data is to be stored and processed by the DB
    ============================================================================================== by Sziller ==="""
    __tablename__ = "utxoset"
    utxo_id: str = Column("utxo_id", String, primary_key=True)
    n: int = Column("n", Integer)
    txid: str = Column("txid", String)
    value: int = Column("value", Integer)
    addresses: list = Column("addresses", JSON)
    scriptPubKey_hex: str = Column("scriptPubKey_hex", String)
    scriptPubKey_asm: str = Column("scriptPubKey_asm", String)
    reqSigs: int = Column("reqSigs", Integer)
    scriptType: str = Column("scriptType", String)

    def __init__(self,
                 txid: str,
                 n: int,
                 value: int,
                 addresses: list,
                 scriptPubKey_hex: str,
                 scriptPubKey_asm: str,
                 reqSigs: int,
                 scriptType: str,
                 **kwargs):
        self.txid: str = txid
        self.n: int = n
        self.value: int = value
        self.addresses: list = addresses
        self.scriptPubKey_hex: str = scriptPubKey_hex
        self.scriptPubKey_asm: str = scriptPubKey_asm
        self.reqSigs: int = reqSigs
        self.scriptType: str = scriptType

        self.generate_utxo_id()

    def generate_utxo_id(self):
        """Function adds a unique ID to the row"""
        data = models.UtxoId(self.txid, self.n)
        self.utxo_id = "{}".format(data)

    def return_as_dict(self):
        """=== Method name: return_as_dict =============================================================================
        Returns instance as a dictionary
        @return : dict - parameter: argument pairs in a dict
        ========================================================================================== by Sziller ==="""
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}

    @classmethod
    def construct(cls, d_in, **kwargs):
        """=== Classmethod: construct ==================================================================================
        Input necessary class parameters to instantiate object of the class!
        @param d_in: dict - format data to instantiate new object
        @return: an instance of the class
        ========================================================================================== by Sziller ==="""
        return cls(**d_in)


class MDPrvKey(Base):
    """=== Class name: MDPrvKey ========================================================================================
    Table row.
    ============================================================================================== by Sziller ==="""
    __tablename__ = "mdprvkeys"
    hxstr: str = Column("hxstr", String, primary_key=True)
    owner: str = Column("owner", String)
    kind: int = Column("kind", Integer)
    comment: str = Column("comment", String)
    root_hxstr: str = Column("root_hxstr", String)
    deriv_nr: int = Column("deriv_nr", Integer)

    def __init__(self,
                 owner: str,
                 kind: int = 0,
                 root_hxstr: str = "",
                 deriv_nr: int = 0,
                 hxstr: str = "",
                 comment: str = "some txt"):
        self.hxstr: str = hxstr
        self.owner: str = owner
        self.kind: int = kind
        self.comment: str = comment
        self.root_hxstr: str = root_hxstr
        self.deriv_nr: int = deriv_nr

        if not self.hxstr:
            self.generate_hxstr()

    def generate_hxstr(self):
        """Function adds a unique ID <hxstr> to the row"""
        self.hxstr = "{:04}".format(rnd.randint(0, 9999))

    def return_as_dict(self):
        """=== Method name: return_as_dict =============================================================================
        Returns instance as a dictionary
        @return : dict - parameter: argument pairs in a dict
        ========================================================================================== by Sziller ==="""
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}

    @classmethod
    def construct(cls, d_in):
        """=== Classmethod: construct ==================================================================================
        Input necessary class parameters to instantiate object of the class!
        @param d_in: dict - format data to instantiate new object
        @return: an instance of the class
        ========================================================================================== by Sziller ==="""
        return cls(**d_in)


class Node(Base):
    """=== Classname: Node(Base) =======================================================================================
    Class represents a Node Database Entry who's data is to be stored and processed by the DB
    ============================================================================================== by Sziller ==="""
    __tablename__ = "nodes"
    alias: str                      = Column("alias", String, primary_key=True)
    owner: str                      = Column("owner", String)
    ip: str                         = Column("ip", String)
    port: int                       = Column("port", Integer)
    features: dict                  = Column("features", JSON)
    desc: str                       = Column("desc", String)
    is_rpc: bool                    = Column("is_rpc", Integer)

    def __init__(self,
                 alias: str,
                 owner: str,
                 ip: str,
                 port: int,
                 features: dict,
                 desc: str,
                 is_rpc: int):
        self.alias: str     = alias
        self.owner: str     = owner
        self.ip: str        = ip
        self.port: int      = port
        self.features: dict = features
        self.desc: str      = desc
        self.is_rpc: int    = is_rpc

    def return_as_dict(self):
        """=== Method name: return_as_dict =============================================================================
        Returns instance as a dictionary
        @return : dict - parameter: argument pairs in a dict
        ========================================================================================== by Sziller ==="""
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}

    @classmethod
    def construct(cls, d_in):
        """=== Classmethod: construct ==================================================================================
        Input necessary class parameters to instantiate object of the class!
        @param d_in: dict - format data to instantiate new object
        @return: an instance of the class
        ========================================================================================== by Sziller ==="""
        return cls(**d_in)
    
# CLASS definitions ENDED                                                                   -   ENDED   -
