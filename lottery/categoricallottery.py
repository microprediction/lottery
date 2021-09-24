from lottery.ongoingcategoricallottery import OngoingCategoricalLottery
from lottery.conventions import MAX_TAU


class CategoricalLottery(OngoingCategoricalLottery):

    def __init__(self, state=None, meta=None,  allowed_values:[str]=None, t:int=-MAX_TAU):
        is_new = state is None
        super().__init__(state=state, meta=meta, allowed_values=allowed_values, allowed_horizons_style='tote')
        if is_new:
            super().observe(t=t,value='open')

    def observe(self, value:str, t:int, approx_max_len:int=10000):
        raise NotImplementedError('Use open, close, settle instead')

    def close(self, t:int):
        super().observe(t=t, value='close')

    def settle(self, value:str, t=MAX_TAU):
        rewards = self.payout(t=t, value=value, consolidate=True)
        super().observe(t=t, value=value)
        return rewards



if __name__=="__main__":
    from pprint import pprint
    L = CategoricalLottery(t=15)
    L.add(t=10, owner='bill', values=['1', '3', '5'], weights=[0.5, 0.25, 0.25], amount=1.0) # too early
    L.add(t=20, owner='mary', values=['1', '3', '5'], weights=[0.75, 0.25, 0.0], amount=1.0)
    L.add(t=20, owner='alice', values=['1', '3', '5'], weights=[0.65, 0.3, 0.05], amount=1.0)
    L.close(t=25)
    L.add(t=30, owner='alice', values=['1', '3', '5'], weights=[1.0, 0.0, 0.0], amount=1.0) # too late
    rewards = L.settle(value='1')
    pprint(rewards)
