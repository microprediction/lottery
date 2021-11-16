from lottery.conventions import ensure_normalized_weights, cutoff_time, consolidate_rewards, k_and_tau_to_horizon_str,\
    horizon_str_to_k_and_tau, ALLOWED_HORIZON_STYLES, NEG_INF_CUTOFF_TIME, ensure_normalized_dict_weights

# An ongoing categorical lottery is an object to which:
#
#      - Predictions can be added at any time with .add()
#      - Observations of ground truths can be added at any time with .observe()
#      - Hypothetical rewards can be computed, based on quarantine/horizon conventions,
#        that would be paid if a ground truth were to arrive, with .payout()
#
# This object maintains the history of observations and breakdown of predictions currently pending, but
# it does not serve as a bank to track rewards. The payout() is idempotent (pure).


class OngoingCategoricalLottery(dict):

    def __init__(self, state = None, meta=None,
                 allowed_values:[str]=None,
                 allowed_horizons:[str]=None,
                 allowed_horizons_style:str=None):
        """   Implements rolling lotteries for various horizons
        :param meta:
        :param state:                     See below
        :param allowed_values:            Enumeration of outcomes (usually mutually exclusive)
        :param allowed_horizons           Enumeration of horizons for which we agree to accept forecasts
        :param allowed_horizons_style     Alternative way to specify a list of allowed horizons for common patterns
                                          allowed_horizon_style='tote' uses k=1&tau=0
        """

        # state includes ...
        #    [bets][horizon][value] holds (time,owner,amount) lists
        #    [bet_totals][horizon][owner] holds (time,amount) lists
        #    [forecasts][horizon][owner] holds (value,weight,amount) lists
        # We use lists rather than triples for JSON compat, despite lower performance

        # Shove optional arguments into meta
        meta = dict() if meta is None else meta
        if allowed_values is not None:
            meta['allowed_values'] = allowed_values
        if allowed_horizons is not None:
            meta['allowed_horizons'] = allowed_horizons
        if allowed_horizons_style is not None:
            meta['allowed_horizons'] = ALLOWED_HORIZON_STYLES[allowed_horizons_style]

        if meta.get('allowed_horizons') is not None:
            for h in meta['allowed_horizons']:
                k, tau = horizon_str_to_k_and_tau(h) # Checks validity

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
        return OngoingCategoricalLottery(**json.loads(s))

    def implied_k_tau(self):
        assert 'allowed_horizons' in self['meta'], ' Must specify k, tau'
        assert len(self['meta']['allowed_horizons']) == 1, ' Must specify k, tau since horizon is ambiguous '
        return horizon_str_to_k_and_tau(self.get('meta').get('allowed_horizons')[0])

    def all_added_values(self):
        """ List of all values submitted anyone """
        all_values = set()
        for hz in self['state']['bets']:
            for v in self['state']['bets'][hz].keys():
                all_values.add(v)
        return list(all_values)


    def add(self, t:int, owner :str, values :[str], weights :[float] =None, amount=1.0, k:int=None, tau:int=None)-> int:
        """  Update predictions for horizon (k,tau) from one supplier
        :param t            Current time
        :param tau          Horizon in seconds
        :param owner:       Identifier
        :param values:      Names for possible outcomes (such as horse names)
        :param weights:
        :return:  1 if successful, 0 otherwise
        """
        open_time = self['state']['time_history'][0]
        if t < open_time:
              return 0  # Too early
        else:
            if (k is None) or (tau is None):
                k, tau = self.implied_k_tau()

            assert k>=0, 'no prizes for predicting the previous value k>=1 please'
            assert (k>0) or (tau>=0), 'maybe not a good choice for (k,tau)'
            values, weights = ensure_normalized_weights(values=values, weights=weights)
            horizon = k_and_tau_to_horizon_str(k=k, tau=tau)
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


    def set_k_tau_horizon_cutoff(self, t:int, k:int=None, tau:int=None):
        if (k is None) or (tau is None):
            k, tau = self.implied_k_tau()
        h = k_and_tau_to_horizon_str(k=k, tau=tau)
        try:
            t_cutoff = cutoff_time(previous_times=self['state']['time_history'], t=t, k=k, tau=tau)
        except:
            t_cutoff = None
        return k, tau, h, t_cutoff


    def payout(self,  t:int, value: str, consolidate=False, k:int=None, tau:int=None):
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

        k, tau, h, t_cutoff = self.set_k_tau_horizon_cutoff(t=t, k=k,tau=tau)

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

    def suggest(self, t:int=None, k:int=None, tau:int=None )->dict:
        """
            :param  t   -  Future time

            Returns { suggestions: weights }

        """
        _, _, h, t_cutoff = self.set_k_tau_horizon_cutoff(t=t, k=k, tau=tau)
        suggestions = self.all_added_values()
        peanut_gallery = self['state']['bets'][h]
        suggestion_weights = dict([(nm, 0) for nm in suggestions])
        for name in suggestions:
            for n_, bts in peanut_gallery.items():
                if name == n_:
                    for bt in bts:
                        if bt[0] > t_cutoff:
                            suggestion_weights[name] += bt[2]
        suggestion_weights = ensure_normalized_dict_weights(suggestion_weights)
        return suggestion_weights








