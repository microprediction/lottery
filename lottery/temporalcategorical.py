from typing import Union, List
from lottery.conventions import ensure_normalized_weights, cutoff_time, consolidate_rewards, horizon_to_str
import json


class TemporalCategoricalLottery(dict):

    def __init__(self, state = None, meta=None, allowed_values=None):
        """   Implements rolling lotteries for various horizons
        :param meta:
        :param state:         See below
        :param meta_kwargs:   Alternative way to pass
        """

        # state:
        #    [bets][horizon][value] holds (time,owner,amount) triples
        #    [bet_totals][horizon][owner] holds (time,amount) triples
        #    [forecasts][horizon][owner] holds (value,weight,amount) triples

        # Shove optional arguments into meta
        meta = dict() if meta is None else meta
        if allowed_values is not None:
            meta['allowed_values'] = allowed_values

        if state is None:
            state = dict(bets=dict(),
                         bet_totals=dict(),
                         forecasts=dict(),
                         value_history=list(),
                         time_history = list(),
                         last_bet_time=dict())
        super().__init__(meta=meta,state=state)

    @staticmethod
    def from_json(s:str):
        # Just use regular json.dumps() to serialize
        return TemporalCategoricalLottery(**json.loads(s))

    def add(self, k:int, t:int, tau:int, owner :str, values :[str], weights :[float] =None, amount=1.0)-> int:
        """  Update predictions for horizon (k,tau) from one supplier
        :param t            Current time
        :param tau          Horizon in seconds
        :param epoch_time:  Time bet is placed
        :param owner:       Identifier
        :param values:      Names for possible outcomes (such as horse names)
        :param weights:
        :return:  1 if successful, 0 otherwise
        """
        assert k>=0, 'no prizes for predicting the previous value k>=1 please'
        assert (k>0) or (tau>=0), 'maybe not a good choice for (k,tau)'
        values, weights = ensure_normalized_weights(values=values, weights=weights)
        horizon = horizon_to_str(k=k, tau=tau)
        if horizon not in self['state']['last_bet_time']:
             self['state']['last_bet_time'][horizon] = dict()
        ignore =  (owner in self['state']['last_bet_time'][horizon]) and (t <= self['state']['last_bet_time'][horizon][owner])
        if ignore:
            return 0   # Not happy with out of order updates or more than one per second
        self['state']['last_bet_time'][horizon][owner] = t

        # Update individual opinions
        if horizon not in self['state']['forecasts']:
            self['state']['forecasts'][horizon] = dict()
        self['state']['forecasts'][horizon][owner] = {'money':sorted( [ [v,w*amount] for v,w in zip(values,weights)] ),
                                                      'probability':sorted([[v,w] for v,w in zip(values,weights) ])
                                                      }

        # Update amount invested by horizon
        if horizon not in self['state']['bet_totals']:
            self['state']['bet_totals'][horizon] = dict()
        if owner not in self['state']['bet_totals'][horizon]:
            self['state']['bet_totals'][horizon][owner] = list()
        self['state']['bet_totals'][horizon][owner].append([t, amount])

        # Update amount invested on individual outcomes
        #   bets[horizon][value] holds a list of (time, owner, amount) triples
        if horizon not in self['state']['bets']:
            self['state']['bets'][horizon] = dict()
        for v,w in zip(values,weights):
            a = amount*w
            if v not in self['state']['bets'][horizon]:
                self['state']['bets'][horizon][v] = list()
            self['state']['bets'][horizon][v].append([t, owner, a])
        return 1

    def payout(self, k:int, t:int, tau:int, value: str, consolidate=False):
        """
            Calculates the hypothetical reward when a new categorical truth arrives
            at time t pertaining to the forecasting horizon (k,tau)

        :param k:       Quarantine steps
        :param t:       Current rounded time in epoch seconds
        :param tau:     Quarantine time
        :param value:   Observed truth
        :return:  rewards list [ (owner, reward) ]
        """
        def _max_or_none_triple(l):
            try:
                return max(l)
            except ValueError:
                return (None, None, None)

        # (1) Find the last epoch second we accept forecasts from
        h = horizon_to_str(k=k, tau=tau)
        try:
            t_cutoff = cutoff_time(previous_times=self['state']['time_history'],t=t,k=k,tau=tau)
        except:
            pass

        if (t_cutoff>=t) or (h not in self['state']['bets']) or (value not in self['state']['bets'][h]):
            return []   # (2a) If there are no quarantined bets or nobody got it right, no rewards
                        #      Carryover logic could potentially be applied here instead.
        else:
            # (2b) Tabulate amounts bet on winning value in the most recent valid submissions for (k,tau)
            matching_correct_value = self['state']['bets'][h][value]
            matching_and_quarantined = [ (t_,o_,a_) for (t_,o_,a_) in matching_correct_value if (t_<= t_cutoff) ]
            quarantined_owners = list(set([ o_ for (t_,o_,a_) in matching_and_quarantined ]))
            latest_time_owner_pairs = [ ( max( [ t_ for (t_,a_) in self['state']['bet_totals'][h][o_] if t_<t_cutoff ] ), o_ ) for o_ in quarantined_owners]
            winners = [ (o_,a_) for (t_,o_,a_) in matching_and_quarantined if (t_,o_) in latest_time_owner_pairs ]
            total_winner_money = sum( [a_ for (o_,a_) in winners ])

            # (3) Tabulate total amount invested in the most recent valid submissions for (k,tau)
            all_owners = list(self['state']['bet_totals'][h].keys())
            all_recent = [  _max_or_none_triple( [ (t_,o_,a_) for (t_,a_) in self['state']['bet_totals'][h][o_] if (t_<= t_cutoff) ] ) for o_ in all_owners ]
            all_totals = [ (o_,a_) for (t_,o_,a_) in all_recent if t_ is not None ]
            total_money = sum( [ a_ for (o_,a_) in all_totals ] )

            # (4) Winners split the pot
            winner_rewards = [ (o_,a_*total_money/total_winner_money) for (o_,a_) in winners ]
            participation_rewards = [ (o_,-a_) for (o_,a_) in all_totals ]
            net_rewards = participation_rewards + winner_rewards  # no real need to consolidate yet
            return consolidate_rewards(net_rewards) if consolidate else net_rewards

    def observe(self, value:str, t:int, approx_max_len:int=10000):
        """ Add arriving data point to history
        :param value:  Observed truth
        :param t:      Rounded epoch second
        :return:
        """
        assert len(self['state']['value_history'])==len(self['state']['time_history']),'history out of sync'
        self['state']['value_history'].append(value)
        self['state']['time_history'].append(t)
        if len(self['state']['time_history']) > 1.1*approx_max_len:
            self['state']['time_history']  = self['state']['time_history'][-approx_max_len:]
            self['state']['value_history'] = self['state']['value_history'][-approx_max_len:]
        return len(self['state']['time_history'])


if __name__=="__main__":
    L = TemporalCategoricalLottery(allowed_values=list(range(12)))
    import random
    ys = [ random.choice([1,1,2,3]) for _ in range(10)]
    ts = [ i*100 for i in range(10)]
    tau = 10
    k = 2
    for t,y in zip(ts,ys):
        L.observe(value=y, t=t)
        rewards = L.payout(k=k, t=t, tau=tau, value=y)
        print(rewards)
        L.add(t=t + 20, owner='bill', tau=tau, k=k, values=[y, y + 1, y + 1], weights=[0.5, 0.25, 0.25], amount=1.0)
        L.add(t=t + 20, owner='mary', tau=tau, k=k, values=[1, 2, 3], weights=[0.4, 0.4, 0.2], amount=1.5)

    pass

    # Serialize and de-serialize
    import json
    G = TemporalCategoricalLottery(**json.loads(json.dumps(L)))
    pass





