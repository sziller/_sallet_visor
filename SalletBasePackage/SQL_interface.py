"""
SQLAlchemy powered DB handling test, and production code.
We hope to swap DB handling while using Alchemy from SQLite to PostgreSQL.
Present implementation servers both current SQLight and all development steps along the way.
by Sziller
"""
import os
import random as rnd
from SalletBasePackage import models

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine, MetaData, Column, Integer, String, JSON
from sqlalchemy.pool import NullPool
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv


Base = declarative_base()


def createSession(db_path: str, style: str = "SQLite", base=Base):
    """=== Function name: createSession ================================================================================
    ============================================================================================== by Sziller ==="""
    if style == "SQLite":
        engine = create_engine('sqlite:///%s' % db_path, echo=False, poolclass=NullPool)
    elif style == "PostGreSQL":
        engine = create_engine(db_path, echo=False, poolclass=NullPool)
    else:
        raise Exception("no valid dialect defined")

    base.metadata.create_all(bind=engine)  # check if always necessary!!!
    Session = sessionmaker(bind=engine)
    return Session()

# CLASS definitions ENDED                                                                   -   START   -


class Node(Base):
    """=== Classname: Utxo(Base) =======================================================================================
    Class represents scheduled task who's data is to be stored and processed by the DB
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
    
    
class Utxo(Base):
    """=== Classname: Utxo(Base) =======================================================================================
    Class represents scheduled task who's data is to be stored and processed by the DB
    ============================================================================================== by Sziller ==="""
    __tablename__ = "utxoset"
    utxo_id: str                    = Column("utxo_id", String, primary_key=True)
    n: int                          = Column("n", Integer)
    txid: str                       = Column("txid", String)
    value: int                      = Column("value", Integer)
    addresses: list                 = Column("addresses", JSON)
    scriptPubKey_hex: str           = Column("scriptPubKey_hex", String)
    scriptPubKey_asm: str           = Column("scriptPubKey_asm", String)
    reqSigs: int                    = Column("reqSigs", Integer)
    scriptType: str                 = Column("scriptType", String)

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
        self.txid: str              = txid
        self.n: int                 = n
        self.value: int             = value
        self.addresses: list        = addresses
        self.scriptPubKey_hex: str  = scriptPubKey_hex
        self.scriptPubKey_asm: str  = scriptPubKey_asm
        self.reqSigs: int           = reqSigs
        self.scriptType: str        = scriptType
        
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
        # return cls(n=d_in["n"],
        #            txid=d_in["txid"],
        #            value=d_in["value"],
        #            addresses=d_in["scriptPubKey"]["addresses"],
        #            scriptPubKey_hex=d_in["scriptPubKey"]["hex"],
        #            scriptPubKey_asm=d_in["scriptPubKey"]["asm"],
        #            reqSigs=d_in["scriptPubKey"]["reqSigs"],
        #            scriptType=d_in["scriptPubKey"]["type"])
        return cls(**d_in)


class MDPrvKey(Base):
    """=== Class name: MDPrvKey ========================================================================================
    Table row.
    ============================================================================================== by Sziller ==="""
    __tablename__ = "mdprvkeys"  # mdprvkeys
    hxstr: str                  = Column("hxstr", String, primary_key=True)
    owner: str                  = Column("owner", String)
    kind: int                   = Column("kind", Integer)
    comment: str                = Column("comment", String)
    root_hxstr: str             = Column("root_hxstr", String)
    deriv_nr: int               = Column("deriv_nr", Integer)

    def __init__(self,
                 owner: str,
                 kind: int = 0,
                 root_hxstr: str = "",
                 deriv_nr: int = 0,
                 hxstr: str = "",
                 comment: str = "some txt"):
        self.hxstr: str         = hxstr
        self.owner: str         = owner
        self.kind: int          = kind
        self.comment: str       = comment
        self.root_hxstr: str    = root_hxstr
        self.deriv_nr: int      = deriv_nr

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


# CLASS definitions ENDED                                                                   -   ENDED   -
# CLASS assignment to tables START                                                          -   START   -
load_dotenv()
OBJ_KEY = {os.getenv("DB_ID_TABLE_UTXO"):   Utxo,
           os.getenv("DB_ID_TABLE_SECRET"): MDPrvKey,
           os.getenv("DB_ID_TABLE_NODE"):   Node
           }
# CLASS assignment to tables ENDED                                                          -   ENDED   -


def ADD_rows_to_table(primary_key: str,
                      data_list: list,
                      db_table: str,
                      session_in: object):
    """
    @param primary_key: 
    @param data_list: 
    @param db_table: 
    @param session_in: 
    @return: 
    """
    
    session = session_in
    added_primary_keys = []
    global OBJ_KEY
    RowObj = OBJ_KEY[db_table]
    for data in data_list:
        # there are cases:
        # - a. when primary key exists before instance being added to DB
        # - b. primary key is generated from other incoming data on instantiation
        if primary_key in data:  # a.: works only if primary key is set and included in row to be created!
            if not session.query(RowObj).filter(getattr(RowObj, primary_key) == data[primary_key]).count():
                newrow = RowObj.construct(d_in=data)
                session.add(newrow)
                added_primary_keys.append(data[primary_key])
        else:
            # this is the general case. <data> doesn't need to include primary key:
            # we check if primary key having been generated on instantiation exists.
            newrow = RowObj.construct(d_in=data)
            if not session.query(RowObj).filter(getattr(RowObj, primary_key) == getattr(newrow, primary_key)).count():
                session.add(newrow)
    session.commit()
    return added_primary_keys


def drop_table(table_name, engine):
    """
    @param table_name: 
    @param engine: 
    @return: 
    """
    Base = declarative_base()
    metadata = MetaData()
    metadata.reflect(bind=engine)
    table = metadata.tables[table_name]
    if table is not None:
        Base.metadata.drop_all(engine, [table], checkfirst=True)


def db_delete_multiple_rows_by_filterkey(filterkey: str,
                                         filtervalue_list: list,
                                         db_table: str,
                                         session_in: object or None = None):
    """=== Function name: db_delete_multiple_docs_by_key ==============================================================
    @param filterkey: str - name of row's attribute
    @param filtervalue_list: list - list of values of rows to be deleted
    @param db_table: str - the actual DataBase name the engine uses. Different for SQLite and PostGreSQL
    @param session_in: str - to distinguish path handling, enter DB style : PostGreSQL or SQLite
    @return:
    ============================================================================================== by Sziller ==="""
    session = session_in
    global OBJ_KEY
    RowObj = OBJ_KEY[db_table]
    for filtervalue in filtervalue_list:
        session.query(RowObj).filter(getattr(RowObj, filterkey) == filtervalue).delete(synchronize_session=False)
    session.commit()


def MODIFY_multiple_rows_by_column_to_value(
        filterkey: str,
        filtervalue_list: list,
        target_key: str,
        target_value,
        db_table: str,
        db_path: str    = "",
        style: str      = "",
        session_in: object or None = None):
    """=== Function name: db_REC_modify_multiple_rows_by_column_to_value ===============================================
    USE THIS IF THE NEW VALUES THE CELLS MUST TAKE ARE IDENTICAL!!!
    This function deals with the USERs DB Table!!!
    @param filterkey: str - name of column, in which filtervalues will be looked for
    @param filtervalue_list: list - list of values of rows to be deleted
    @param target_key: str - name of the column, whose value will be modified
    @param target_value: any data to be put into multiple cell
    @param db_path: str - the actual DataBase name the engine uses. Different for SQLite and PostGreSQL
    @param db_table: str - name of the table you want to write
    @param style: str - to distinguish path handling, enter DB style : PostGreSQL or SQLite
    @param session_in: obj - a precreated session. If used, it will not be closed. If not entered, a new session is
                                                    created, which is closed at the end.
    @return:
    ============================================================================================== by Sziller ==="""
    session = session_in
    global OBJ_KEY
    RowObj = OBJ_KEY[db_table]
    for filtervalue in filtervalue_list:
        session.query(RowObj).filter(getattr(RowObj, filterkey) == filtervalue).update({target_key: target_value})
    session.commit()


def MODIFY_multiple_rows_by_column_by_dict(filterkey: str,
                                           mod_dict: dict,
                                           db_table,
                                           db_path: str = "",
                                           style: str = "",
                                           session_in: object or None = None):
    """
    
    @param filterkey: 
    @param mod_dict: 
    @param db_path: 
    @param db_table: 
    @param style: 
    @param session_in:
    @return: 
    """
    if session_in:
        session = session_in
    else:
        session = createSession(db_path=db_path, style=style)
    global OBJ_KEY
    RowObj = OBJ_KEY[db_table]
    for filtervalue, sub_dict in mod_dict.items():
        session.query(RowObj).filter(getattr(RowObj, filterkey) == filtervalue).update(sub_dict)
    session.commit()


def QUERY_entire_table(ordered_by: str,
                       db_table: str,
                       session_in: object or None = None) -> list:
    """=== Function name: QUERY_entire_table =========================================================================
    Function returns an entire DB table, defined by args.
    This function deals with the entered DB Table!!!
    @param ordered_by:
    @param db_table: str - name of the table you want to write
    @param session_in: obj - a precreated session. If used, it will not be closed. If not entered, a new session is
                                                    created, which is closed at the end.
    @return: list of rows in table requested.
    ========================================================================================== by Sziller ==="""
    session = session_in
    global OBJ_KEY
    RowObj = OBJ_KEY[db_table]
    results = session.query(RowObj).order_by(ordered_by).all()
    result_list = [_.return_as_dict() for _ in results]
    session.commit()
    return result_list


def QUERY_rows_by_column_filtervalue_list_ordered(filterkey: str,
                                                  filtervalue_list: list,
                                                  ordered_by: str,
                                                  db_table: str,
                                                  db_path: str = "",
                                                  style: str = "",
                                                  session_in: object or None = None) -> list:

    """=== Function name: QUERY_rows_by_column_filtervalue_list_ordered =============================================
    This function deals with the entered DB Table!!!
    @param filterkey:
    @param filtervalue_list:
    @param ordered_by:
    @param db_path:
    @param db_table:
    @param style:
    @param session_in:
    @return:
    ============================================================================================== by Sziller ==="""
    session = session_in
    global OBJ_KEY
    RowObj = OBJ_KEY[db_table]
    results = session.query(RowObj).filter(getattr(RowObj, filterkey).in_(tuple(filtervalue_list))).order_by(ordered_by)
    result_list = [_.return_as_dict() for _ in results]
    session.commit()
    return result_list


if __name__ == "__main__":
    pass
