"""Quick app to read TX data
by Sziller"""
from SalletNodePackage import BitcoinNodeObject as BNOb
from DataVisualizer.data2str import rdf


def app_node_tx_request():
    """=== App name: app_tx_request ====================================================================================
    Quick script to receive a Transactions dictionary representation.
    This app contacts your own node.
    
    Use: from the termial 
    ============================================================================================== by Sziller ==="""
    node = BNOb.Node(is_rpc=True)
    tx_hash = str(input("Enter tx ID: "))
    
    tx_data = node.nodeop_getrawtransaction(tx_hash=tx_hash, verbose=True)
    data_as_displayed = rdf(data=tx_data)
    print(data_as_displayed)


if __name__ == "__main__":
    app_node_tx_request()
