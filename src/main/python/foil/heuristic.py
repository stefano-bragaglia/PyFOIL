import math


def max_gain(pos: int, neg: int) -> float:
    if pos == 0:
        if neg == 0:
            return math.nan

        return 0

    return pos * entropy(pos, neg)


def gain(pos: int, neg: int, pos_i: int, neg_i: int) -> float:
    common = min(pos, pos_i)
    if common == 0:
        return 0

    return common * (entropy(pos, neg) - entropy(pos_i, neg_i))


def entropy(pos: int, neg: int) -> float:  # yet to cover pos,  yet to cover neg
    if pos == 0:
        if neg == 0:
            return math.nan

        return math.inf

    return -math.log2(pos / (pos + neg))
