from lottery.ongoingcategoricallottery import OngoingCategoricalLottery
from typing import Union
from lottery.rewardutil import consolidate_rewards
import time


class CategoricalLotteryDict(dict):

    def __init__(self, lotteries=None):
        if lotteries is None:
            super().__init__()

    def add(self, key, state=None, meta=None,
                       allowed_values:[str]=None,
                       allowed_horizons:[str]=None,
                       allowed_horizon_style:str=None):
        self[key] = OngoingCategoricalLottery(state=state, meta=meta)



class AggregatingCategoricalLotteryDict(CategoricalLotteryDict):

    # Merely a dict containing lotteries with hidden cumulative reward state

    def __init__(self):
        super().__init__()
        self.state = {'rewards':[]}

    def add_rewards(self, new_rewards:[(str,float)]):
        self.state['rewards'] = consolidate_rewards(self.state['rewards'] + new_rewards)





if __name__=='__main__':
    game = AggregatingCategoricalLotteryDict()
    game.add(key='question one')
    game.add(key='question two')
    from pprint import pprint
    pprint(game)

    L = OngoingCategoricalLottery()
    import random
    ys = [random.choice([1, 1, 2, 3]) for _ in range(10)]
    ts = [i * 100 for i in range(10)]
    tau = 10
    k = 2
    for t, y in zip(ts, ys):
        L = random.choice([game['question one'],game['question two']])
        L.observe(value=y, t=t)
        rewards = L.payout(k=k, t=t, tau=tau, value=y)
        print(rewards)
        L.add(t=t + 20, owner='bill', tau=tau, k=k, values=[y, y + 1, y + 1], weights=[0.5, 0.25, 0.25],
              amount=1.0)
        L.add(t=t + 20, owner='mary', tau=tau, k=k, values=[1, 2, 3], weights=[0.4, 0.4, 0.2], amount=1.5)
        game.add_rewards(rewards)


    pprint(game)
    del game['question one']

