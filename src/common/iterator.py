# 21/06/2024$ -----------------------------------------------------------------------------------------------------
#  created by: felix 
#              felix.eickeler@obermeyer-group.com    
# ----------------------------------------------------------------------------------------------------------------
#

def safe_next(gen, no_throw=False):
    try:
        return next(gen)
    except StopIteration:
        if no_throw:
            return None
        else:
            raise


def safe_send(gen, value, no_throw=False):
    try:
        return gen.send(value)
    except StopIteration:
        if no_throw:
            return None
        else:
            raise