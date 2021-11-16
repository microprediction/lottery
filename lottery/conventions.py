from itertools import groupby
from typing import Union

NORMALIZATION_TOLERANCE = 1e-8
NEG_INF_CUTOFF_TIME = -10000000000     # Avoid numpy dependency
MAX_TAU = 1000*1000*1000               # About 300 years


def k_and_tau_to_horizon_str(k:int, tau:int):
    """  (1,0)  -> k=1&tau=0 -> (1,0)
       A convention for packing 2-tuple into something hashable and json'able
    """
    return 'k='+str(k)+'&tau='+str(tau)


def horizon_str_to_k_and_tau(h:str):
    """  k=1&tau=0 -> (1,0) """
    k = int(h.split('&')[0].split('=')[1])
    tau = int(h.split('&')[1].split('=')[1])
    return k, tau

# Hardwire some common usage patterns
ONCE_HORIZON = k_and_tau_to_horizon_str(k=1, tau=0)

ALLOWED_HORIZON_STYLES = {
          'once':[ONCE_HORIZON]    # One-off lottery, or horse race
                          }




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


def ensure_normalized_dict_weights(d:dict,tol:float=NORMALIZATION_TOLERANCE) -> dict:
    """  Normalize weights provided as dictionary """
    new_vals, new_weights = ensure_normalized_weights(values=d.keys(), weights=d.values(),tol=tol)
    return dict(zip(new_vals,new_weights))



def cutoff_time(previous_times:[int], t:int, k:Union[int,str], tau:int):
    """
        When a truth value is received at time t, but before it is
        appended to previous_times, this function defines the latest
        epoch second when forecasts will be accepted for judging the
        new data point against the (k,tau) horizon.

        In terms of "quarantine":
            The horizon k,tau>0 means "quarantine after tau seconds, plus k observation intervals after that"

        Which predictions count:
             k   tau    Task
             0   10     Predictions must arrive 10 seconds prior to the truth
             1   -10    Predictions must arrive within 10 seconds of the previous truth
             1   10     Predictions must arrive 10 seconds before the previous truth

        Typical usage:
             Task:                                                         Horizon to use
             Predict the next data point within 5 seconds of the last      k=1, tau=-5
             Provide predictions up until one second before race jump       k=1, tau=1

    :param previous_times:  times at which ground truths have arrived
    :param t:               current time - typically of an incoming observation
    :param k:
    :param tau:             in seconds
    :return:
    """
    n = len(previous_times)
    int_k = int(k)
    assert int_k>=0, 'k>=0 please'
    if int_k==0:
        return t-tau
    elif (int_k>0) and n>=int_k:
        try:
            return previous_times[-int_k]-tau
        except IndexError:
            return NEG_INF_CUTOFF_TIME
    else:
        return NEG_INF_CUTOFF_TIME


def consolidate_rewards(rewards:[(str, float)]) -> [(str,float)]:
    """ By convention rewards are presented in alphabetical order with only one entry per owner """
    rewards = sorted(rewards)
    return [(owner, sum([r[1] for r in group]) ) for owner, group in groupby(rewards, lambda x: x[0])]


def equal_rewards(r1:[(str, float)], r2:[(str, float)])->bool:
    """ True if two reward listings are equivalent """
    c1 = consolidate_rewards(r1)
    c2 = consolidate_rewards(r2)
    return c1==c2


if __name__=='__main__':
    rewards = [('bill', -1.0), ('mary', -1.5), ('bill', 1.1363636363636362), ('mary', 1.3636363636363638)]
    r = consolidate_rewards(rewards=rewards)
    from pprint import pprint
    pprint(r)