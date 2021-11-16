from lottery.ongoingcategoricallottery import OngoingCategoricalLottery
from lottery.conventions import  horizon_str_to_k_and_tau
from pprint import pprint

# A micro-manager pattern:
#
#     - Get predictions of which algorithms will perform best
#     - Select and run those algorithms, stacking as we go
#     - See which actually performs, and reward


def _predictions_inner(d1, d2):
    """
    :param d1: dict of model k-step ahead prediction lists
    :param d2: dict of weights
    :return:
    """
    the_sum = None
    for k1,v1 in d1.items():
        if k1 in d2:
            if the_sum is None:
                the_sum = [ v1i*d2[k1] for v1i in v1 ]
            else:
                the_sum = [ si + v1i*d2[k1] for si,v1i in zip(the_sum,v1) ]
    return the_sum


if __name__=='__main__':
     try:
         from timemachines.skaters.localskaters import local_skater_from_name, LOCAL_SKATERS
         import numpy as np
     except ImportError:
         raise ImportError('for this example pip install timemachines')

     try:
         from momentum import var_init, var_update
         import numpy as np
     except ImportError:
         raise ImportError('for this example pip install momentum')

     allowed_values = [ f.__name__ for f in LOCAL_SKATERS ]
     HORIZON = 'k=2&tau=10'
     k, tau = horizon_str_to_k_and_tau(HORIZON)
     allowed_horizons = [HORIZON]
     ocl = OngoingCategoricalLottery(allowed_values=allowed_values, allowed_horizons=allowed_horizons)

     n_obs = 500
     ys = list(np.cumsum(np.random.randn(n_obs,1)))
     ts = list(range(n_obs))

     # Get the ball rolling by establishing one data point (this requirement may be removed)
     ocl.observe(t=-1,value='balanced_ema_ensemble')

     # Everyone has an opinion...
     ocl.add(t=0, owner='bill', values=['balanced_ema_ensemble','slowly_moving_average'], weights=[0.75,0.25] )
     ocl.add(t=0, owner='mary', values=['thinking_fast_and_slow','sluggish_moving_average'], weights=[0.55, 0.45])

     state_storage = dict( [ (name, dict()) for name in allowed_values ])
     stats_storage = dict( [ (name, var_init() ) for name in allowed_values ])


     for T in [100,200,300,400,500]:

         # Get suggestions and weights ... this needs to be a method!
         suggestion_weights = ocl.suggest(t=T+100, k=k, tau=tau)
         suggestions = list(suggestion_weights.keys())
         skaters = [ local_skater_from_name(name) for name in suggestions ]

         # Run the suggested models for a while, and ensemble
         y_cons = list()
         for y, t in zip(ys[T:T + 100], ts[T:T + 100]):
             y_hats = dict()
             for name, s in state_storage.items():
                 if name in suggestions:
                     f = local_skater_from_name(name)
                     y_hat = ys[0]
                     stats_storage[name] = var_update(stats_storage[name], y - y_hat)
                     y_hats[name],x_std, state_storage[name] = f(y=y,t=t,k=1,s=state_storage[name])

             y_consensus_hat = _predictions_inner(y_hats, suggestion_weights)
             y_cons.append(y_consensus_hat)

         # See which one had the least error, declare a winner, and reward
         winner = sorted( [(stats_storage[name]['std'],name) for name in suggestions ] )[0][1]
         ocl.observe(t=T, value=winner)
         reward = ocl.payout(t=T+1, value=winner, consolidate=True)
         pprint(reward)

         # Meanwhile, everyone is adjusting their opinions
         ocl.add(t=T, owner='bill', values=['balanced_ema_ensemble'])
         ocl.add(t=T, owner='mary', values=['thinking_fast_and_slow', 'sluggish_moving_average','precision_ema_ensemble'], weights=[0.55, 0.40,0.05])
















