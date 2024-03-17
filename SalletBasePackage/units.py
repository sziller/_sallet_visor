"""Simple function to convert between different well-known bitcoin units
by Sziller"""

import logging
import inspect

# Setting up logger                                         logger                      -   START   -
lg = logging.getLogger()
# Setting up logger                                         logger                      -   ENDED   -

lg.info("START     : {:>85} <<<".format('units.py'))


def bitcoin_unit_converter(value: float, unit_in: str, unit_out: str) -> float:
    """ Function name: bitcoin_unit_converter ==========================================================================
    FUNCTION NAME: bitcoin_unit_converter
    Script converts between different units of the Bitcoin system.
    It uses most of the wide-spread naming conventions of Bitcoin.
    Curently using 5 basic units:
    - BTC   - bitcoin                           :   0
    - mBTC  - milibitcoin,                      :   3
    - μBTC  - microbitcoin, µ sign: Alt + 0180  :   6
    - satoshi                                   :   8
    - millisatoshi                              :  11

    convert_table inside script contains the associations btw. aliasses and powers.
    For a better overlook, programm codes the units using the powers of ten.
    Script recognises 5 different units as of now:
    bitcoin     :1
    millie      :1000
    bit         :1000000
    satoshi     :100000000      (currently the smallest unit, in which tx-s can be settled)
    millisatoshi:100000000000   (currently used on the 2nd layer lightning network, cannot be settled)

    :param unit_in: the unit you want to convert from, the base unit of the conversion.
    :param unit_out: the unit you want to convert to, the target unit of the conversion.
    :param value: numerical value of the base unit.
    :return: float - numerical value of the target unit.
    ============================================================================================== by Sziller ==="""
    ccn = inspect.currentframe().f_code.co_name  # current class name
    convert_table = {'btc': 0, 'bitcoin': 0, 'bitcoins': 0, 'Bitcoin': 0, 'Bitcoins': 0,
                     'BTC': 0, 'BITCOIN': 0, 'BITCOINS': 0,
                     'coin': 0, 'coins': 0, 'COIN': 0, 'COINS': 0,

                     'mbtc': 3, 'mili': 3, 'millibitcoin': 3, 'millibitcoins': 3, 'milli-bitcoin': 3,
                     'milli-bitcoins': 3, 'millibit': 3, 'millibits': 3, 'millie': 3, 'millies': 3, 'm': 3, 'milli': 3,
                     'mBTC': 3, 'MILI': 3, 'MILLIBITCOIN': 3, 'MILLIBITCOINS': 3, 'MILLI-BITCOIN': 3,
                     'MILLI-BITCOINS': 3, 'MILLIBIT': 3, 'MILLIBITS': 3, 'MILLIE': 3, 'MILLIES': 3,

                     'µbtc': 6, 'bit': 6, 'bits': 6, 'microbitcoin': 6, 'microbitcoins': 6,
                     'micro-bitcoin': 6, 'micro-bitcoins': 6, 'micro': 6, 'micros': 6, 'µ': 6,
                     'µBTC': 6, 'BIT': 6, 'BITS': 6, 'MICROBITCOIN': 6, 'MICROBITCOINS': 6,
                     'MICRO-BITCOIN': 6, 'MICRO-BITCOINS': 6, 'MICRO': 6, 'MICROS': 6,

                     'satoshi': 8, 'satoshis': 8, 'sat': 8, 'sats': 8, 's': 8,
                     'SATOSHI': 8, 'SATOSHIS': 8, 'SAT': 8, 'SATS': 8,

                     'msatoshi': 11, 'msatoshis': 11, 'msat': 11, 'msats': 11, 'ms': 11,
                     'MSATOSHI': 11, 'MSATOSHIS': 11, 'MSAT': 11, 'MSATS': 11,

                     'millisatoshi': 11, 'millisatoshis': 11, 'millisat': 11, 'millisats': 11,
                     'MILLISATOSHI': 11, 'MILLISATOSHIS': 11, 'MILLISAT': 11, 'MILLISATS': 11
                     }

    name_table = {0: 'bitcoin', 3: "millie", 6: "bit", 8: "satoshi", 11: "millisatoshi"}

    if unit_in in convert_table.keys() and unit_out in convert_table.keys():
        if isinstance(unit_in, str):
            unit_in = convert_table[unit_in]
        if isinstance(unit_out, str):
            unit_out = convert_table[unit_out]

        convert_power = unit_in - unit_out
        calculated = float(value / (10 ** convert_power))
        round_to = 8 - unit_out  # calculating nr of decimal places to round to
        returned = round(calculated, round_to)  # returned value rounded so system rounding errors do not show
        if round_to <= 0: returned = int(returned)  # sats and millisats should be returned as integers
        return returned
    else:
        msg = "Entered unit name not recognised! - says {}() at units.py".format(ccn)
        lg.critical(msg)
        raise Exception(msg)

        
    
