from typing import Union
from lottery.conventions import ensure_normalized_weights, cutoff_time, consolidate_rewards


class CategoricalLottery:

    # Assumptions:
    #    - There is no ordinal relationship between discrete outcomes
    #    - There are many possible outcomes

    def __init__(self):
        self.bets = dict()          #  bets[horizon][value] holds (time,owner,amount) triples
        self.bet_totals = dict()    #  bet_totals[horizon][owner] holds (time,amount) triples
        self.forecasts = dict()     #  forecasts[horizon][owner] holds (value,weight,amount) triples
        self.value_history = list() #  chronological observations of truths received
        self.time_history = list()  #  chronological times of truths received
        self.last_bet_time = dict()

    def register_forecast(self, k:int, t:int, tau:int, owner :str, values :[Union[str, int]], weights :[float] =None, amount=1.0)-> int:
        """  Update predictions for horizon (k,tau) from one supplier
        :param t            Current time
        :param tau          Horizon in seconds
        :param epoch_time:  Time bet is placed
        :param owner:       Identifier
        :param values:      Names for possible outcomes (such as horse names)
        :param weights:
        :return:  1 if successful, 0 otherwise
        """
        assert k>=1, 'no prizes for predicting the previous value k>=1 please'
        assert (k>1) or (tau>0), 'maybe not a good choice for (k,tau)'
        values, weights = ensure_normalized_weights(values=values, weights=weights)
        horizon = (k, tau)
        if horizon not in self.last_bet_time:
             self.last_bet_time[horizon] = dict()
        ignore =  (owner in self.last_bet_time[horizon]) and (t <= self.last_bet_time[horizon][owner])
        if ignore:
            return 0   # Not happy with out of order updates or more than one per second
        self.last_bet_time[horizon][owner] = t

        # Update individual opinions
        if horizon not in self.forecasts:
            self.forecasts[horizon] = dict()
        self.forecasts[horizon][owner] = {'money':sorted([(v,w*amount) for v,w in zip(values,weights)]),
                                          'probability':sorted(list(zip(values,weights)))}

        # Update amount invested by horizon
        if horizon not in self.bet_totals:
            self.bet_totals[horizon] = dict()
        if owner not in self.bet_totals[horizon]:
            self.bet_totals[horizon][owner] = list()
        self.bet_totals[horizon][owner].append((t, amount))

        # Update amount invested on individual outcomes
        #   bets[horizon][value] holds a list of (time, owner, amount) triples
        if horizon not in self.bets:
            self.bets[horizon] = dict()
        for v,w in zip(values,weights):
            a = amount*w
            if v not in self.bets[horizon]:
                self.bets[horizon][v] = list()
            self.bets[horizon][v].append((t, owner, a))
        return 1

    def calculate_rewards(self, k:int, t:int, tau:int, value: Union[int, str], consolidate=False):
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
        horizon = (k, tau)
        t_cutoff = cutoff_time(previous_times=self.time_history,t=t,k=k,tau=tau)

        if (t_cutoff>=t) or (horizon not in self.bets) or (value not in self.bets[horizon]):
            return []   # (2a) If there are no quarantined bets or nobody got it right, no rewards
                        #      Carryover logic could potentially be applied here instead.
        else:
            # (2b) Tabulate amounts bet on winning value in the most recent valid submissions for (k,tau)
            matching_correct_value = self.bets[horizon][value]
            matching_and_quarantined = [ (t_,o_,a_) for (t_,o_,a_) in matching_correct_value if (t_<= t_cutoff) ]
            quarantined_owners = list(set([ o_ for (t_,o_,a_) in matching_and_quarantined ]))
            latest_time_owner_pairs = [ ( max( [ t_ for (t_,a_) in self.bet_totals[horizon][o_] if t_<t_cutoff ] ), o_ ) for o_ in quarantined_owners]
            winners = [ (o_,a_) for (t_,o_,a_) in matching_and_quarantined if (t_,o_) in latest_time_owner_pairs ]
            total_winner_money = sum( [a_ for (o_,a_) in winners ])

            # (3) Tabulate total amount invested in the most recent valid submissions for (k,tau)
            all_owners = list(self.bet_totals[horizon].keys())
            all_recent = [  _max_or_none_triple( [ (t_,o_,a_) for (t_,a_) in self.bet_totals[horizon][o_] if (t_<= t_cutoff) ] ) for o_ in all_owners ]
            all_totals = [ (o_,a_) for (t_,o_,a_) in all_recent if t_ is not None ]
            total_money = sum( [ a_ for (o_,a_) in all_totals ] )

            # (4) Winners split the pot
            winner_rewards = [ (o_,a_*total_money/total_winner_money) for (o_,a_) in winners ]
            participation_rewards = [ (o_,-a_) for (o_,a_) in all_totals ]
            net_rewards = participation_rewards + winner_rewards  # no real need to consolidate yet
            return consolidate_rewards(net_rewards) if consolidate else net_rewards

    def append_to_history(self, value:Union[str,int], t:int, approx_max_len:int=10000):
        """ Add arriving data point to history, occasionally trimming
        :param value:  Observed truth
        :param t:      Rounded epoch second
        :return:
        """
        assert len(self.value_history)==len(self.time_history),'history out of sync'
        self.value_history.append(value)
        self.time_history.append(t)
        if len(self.time_history) > 1.1*approx_max_len:
            self.time_history = self.time_history[-approx_max_len:]
            self.value_history = self.value_history[-approx_max_len:]
        return len(self.time_history)



if __name__=="__main__":
    L = CategoricalLottery()
    import random
    ys = [ random.choice([1,1,2,3]) for _ in range(10)]
    ts = [ i*100 for i in range(10)]
    tau = 10
    k = 2
    for t,y in zip(ts,ys):
        L.append_to_history(value=y, t=t)
        rewards = L.calculate_rewards(k=k, t=t, tau=tau, value=y)
        print(rewards)
        L.register_forecast(t=t + 20, owner='bill', tau=tau, k=k, values=[y, y + 1, y + 1], weights=[0.5, 0.25, 0.25], amount=1.0)
        L.register_forecast(t=t + 20, owner='mary', tau=tau, k=k, values=[1, 2, 3], weights=[0.4, 0.4, 0.2], amount=1.5)






