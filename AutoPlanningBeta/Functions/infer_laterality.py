
try:
    from connect import *
except: 
    pass

def infer_laterality(coords, rt_lim = -2.0, lt_lim = 2.0):
    print('a')
    x = coords['x']
    if x < rt_lim:
        return 'RIGHT'
    elif x > lt_lim:
        return 'LEFT'
    else:
        return 'MEDIAL'

    