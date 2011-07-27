from __future__ import division

import math

dist_cpm = {
    10: 1.0,
    20: 1.0,
    30: 1.0,
    40: 1.0,
    50: 1.0,
    60: 1.0,
    70: 1.0,
    80: 1.0,
    90: 1.0,
    100: 1.0,
    102: 1.0,
    104: 1.0,
    106: 1.0,
    108: 1.0,
    110: 1.0,
    112: 1.0,
    114: 0.999267399267,
    116: 0.997557997558,
    118: 0.997557997558,
    120: 0.995604395604,
    122: 0.995115995116,
    124: 0.989010989011,
    126: 0.981196581197,
    128: 0.97094017094,
    130: 0.950427350427,
    131: 0.937484737485,
    132: 0.926251526252,
    133: 0.90695970696,
    134: 0.889865689866,
    135: 0.863003663004,
    136: 0.828815628816,
    137: 0.809523809524,
    138: 0.770695970696,
    139: 0.729914529915,
    140: 0.678632478632,
    141: 0.637606837607,
    142: 0.579975579976,
    143: 0.533821733822,
    144: 0.467643467643,
    145: 0.402686202686,
    146: 0.356776556777,
    147: 0.291330891331,
    148: 0.242735042735,
    149: 0.190476190476,
    150: 0.150183150183,
    152: 0.0830280830281,
    154: 0.0442002442002,
    156: 0.0168498168498,
    158: 0.00732600732601,
    160: 0.0026862026862,
    162: 0.0002442002442,
    164: 0.0,
    166: 0.0,
    168: 0.0,
    170: 0.0,
    180: 0.0}

def dist2prr(dist):
    try:
        return dist_cpm[dist]
    except:
        (dist1, dist2) = find_closest_value(dist)
        return interpolate_prr(dist, dist1, dist2)

def find_closest_value(dist2):
    smaller_closest = None
    bigger_closest = None
    smaller_delta = float("inf")
    bigger_delta = float("inf")
    for dist in dist_cpm:
        if dist2 > dist:
            if (dist2 - dist) < bigger_delta:
                bigger_closest = dist
                bigger_delta = dist2 - dist
        elif dist2 < dist:
            if (dist - dist2) < smaller_delta:
                smaller_closest = dist
                smaller_delta = dist - dist2
        else:
            smaller_closest = dist2
            bigger_closest = dist2
            smaller_delta = 0
            bigger_delta = 0
            return (smaller_closest, bigger_closest)
    return (smaller_closest, bigger_closest)

def interpolate_prr(dist_orig, dist1, dist2):
    if dist1 == None:
        return 0.0
    elif dist2 == None:
        return 1.0
    else:
        prr1 = dist_cpm[dist1]
        prr2 = dist_cpm[dist2]
        return prr1*math.fabs(dist1-dist_orig)/math.fabs(dist2-dist1)+prr2*math.fabs(dist2-dist_orig)/math.fabs(dist2-dist1)

def get_prr_0_95_dist():
    return 130

def get_prr_0_5_dist():
    return 143

def get_prr_0_05_dist():
    return 158
