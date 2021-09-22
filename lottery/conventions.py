
NORMALIZATION_TOLERANCE = 1e-8
NEG_INF_CUTOFF_TIME = -10000000000     # Avoid numpy dependency


def ensure_normalized_weights(values, weights, tol=NORMALIZATION_TOLERANCE):
    if weights is None:
        weights = [ 1 /len(values) for _ in values]
    assert len(values) == len(weights)
    if -tol < 1 - sum(weights) < tol:
        return values, weights
    else:
        sw = sum(weights)
        assert sw>0,'weights sum to zero'
        weights = [ w/sw for w in weights ]
        return values, weights


def cutoff_time(previous_times:[int], t:int, k:int, tau:int):
    """
        When a truth value is received at time t, but before it is
        appended to previous_times, this function defines the latest
        epoch second when forecasts will be accepted for judging the
        new data point against the (k,tau) horizon.

    :param previous_times:  times at which ground truths have arrived
    :param t:               current time - typically of an incoming observation
    :param k:
    :param tau:             in seconds
    :return:
    """
    n = len(previous_times)
    if k==1:
        return t-tau
    elif (k>1) and n>=k:
        try:
            return previous_times[-k]-tau
        except IndexError:
            return NEG_INF_CUTOFF_TIME
    else:
        return NEG_INF_CUTOFF_TIME