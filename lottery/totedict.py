from lottery.tote import Tote, EnumeratedTote
from typing import Union
from lottery.rewardutil import consolidate_rewards
import time


class ToteDict(dict):

    def __init__(self, tote_type=Tote):
        super().__init__()
        self.tote_type = tote_type
        self.state = {'rewards': []}

    def __setitem__(self, key, item):
        self.__dict__[key] = item

    def __getitem__(self, key):
        return self.__dict__[key]

    def __repr__(self):
        return repr(self.__dict__)

    def __len__(self):
        return len(self.__dict__)

    def __delitem__(self, key):
        del self.__dict__[key]

    def clear(self):
        return self.__dict__.clear()

    def copy(self):
        return self.__dict__.copy()

    def has_key(self, k):
        return k in self.__dict__

    def update(self, *args, **kwargs):
        return self.__dict__.update(*args, **kwargs)

    def keys(self):
        return self.__dict__.keys()

    def values(self):
        return self.__dict__.values()

    def items(self):
        return self.__dict__.items()

    def pop(self, *args):
        return self.__dict__.pop(*args)

    def __contains__(self, item):
        return item in self.__dict__

    def __iter__(self):
        return iter(self.__dict__)

    def add(self, key:str,
            values:[Union[str,int]]=None,
            meta: dict = None):
        item = self.tote_type(values=values, meta=meta)
        self.__setitem__(key=key, item=item)

    def add_rewards(self, new_rewards: [(str, float)]):
        self.state['rewards'] = consolidate_rewards(self.state['rewards'] + new_rewards)





if __name__=='__main__':
    tote = AggregatingToteDict()
    tote.add(key='race one',closing_time_estimate=100, values=[1,2,3])
    from pprint import pprint
    pprint(game)

    L = TemporalCategoricalLottery()
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

