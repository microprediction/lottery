from lottery.conventions import ensure_normalized_weights, NORMALIZATION_TOLERANCE


def test_normalization_1():
    values = ['dot',1,'cat']
    weights = [3,4,5]
    nv, nw = ensure_normalized_weights(values=values, weights=weights)
    assert -NORMALIZATION_TOLERANCE<1-sum(nw)<NORMALIZATION_TOLERANCE


def test_normalization_2():
    values = ['dot',1,'cat']
    weights = [0.3,0.3,0.3]
    nv, nw = ensure_normalized_weights(values=values, weights=weights, tol=0.2)
    assert nw[0]==weights[0]
