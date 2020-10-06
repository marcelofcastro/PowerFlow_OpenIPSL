import logging
from _pydecimal import Decimal, ROUND_DOWN


def to_number(s):
    """
    Convert a string to a number. If unsuccessful, return the de-blanked string.
    """
    ret = s

    # remove single quotes
    if "'" in ret:
        ret = ret.strip("'").strip()

    # try converting to booleans / None
    if ret == 'True':
        return True
    elif ret == 'False':
        return False
    elif ret == 'None':
        return None

    # try converting to float or int
    try:
        ret = int(ret)
    except ValueError:
        try:
            ret = float(ret)
        except ValueError:
            pass

    return ret