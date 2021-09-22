from lottery.conventions import consolidate_rewards


def equal_rewards(r1:[(str, float)], r2:[(str, float)])->bool:
    """ True if two reward listings are equivalent """
    c1 = consolidate_rewards(r1)
    c2 = consolidate_rewards(r2)
    return c1==c2