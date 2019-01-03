import math


def max_gain(pos: int, neg: int) -> float:
    if pos == 0:
        if neg == 0:
            return math.nan

        return 0

    return pos * entropy(pos, neg)


def gain(pos: int, neg: int, pos_i: int, neg_i: int) -> float:
    return min(pos, pos_i) * (entropy(pos, neg) - entropy(pos_i, neg_i))


def entropy(pos: int, neg: int) -> float:  # yet to cover pos,  yet to cover neg
    if pos == 0:
        if neg == 0:
            return math.nan

        return math.inf

    return -math.log2(pos / (pos + neg))


if __name__ == '__main__':
    e2 = entropy(18, 54)
    e3 = entropy(10, 0)
