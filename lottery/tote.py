from lottery.temporalcategorical import TemporalCategoricalLottery
from typing import Union


class TypedTote(TypedTemporalCategoricalLottery):

    # A short lived temporal lottery with only recorded truths:  'opened', 'closed' and then the winning value
    # Here k=1 and tau=0, forcing predictions to be lodged before the close of the race

    def __init__(self, closing_time_estimate: int=None,
                 values:[Union[str,int]]=None,
                 meta: dict = None,**kwargs):
        meta = dict() if meta is None else meta
        meta.update({'values': values, 'closing_time_estimate': closing_time_estimate})
        super().__init__()
        self.k = 1
        self.tau = 0
        self.CLOSED = 0 if self.value_type==int else 'closed'
        self.OPENED = 1 if self.value_type==int else 'opened'

    def add(self, t:int, owner:str, values: [Union[str, int]], weights: [float] = None, amount=1.0):
        """ A flexi-bet """
        return super().add(k=self.k, t=t, tau=self.tau, owner=owner, values=values, weights=weights, amount=amount)

    def open(self,t:int):
        super().observe(value=self.OPENED, t=t)

    def close(self,t:int):
        super().observe(value=self.CLOSED, t=t)

    def observe(self):
        raise NotImplementedError('For the Tote class, only use open(), close() and settle()')

    def payout(self, t:int, value:Union[str, int]):
        """ Calculate hypothetical rewards, were value to arrive at time t """
        return super().payout(k=self.k, tau=self.tau, t=t, value=value)


class EnumeratedTote(TypedTote,EnumeratedValuesMixin):

    def __init__(self, values, **kwargs):
        value_type = EnumeratedValuesMixin.infer_value_type(values)
        super().__init__(value_type=value_type,**kwargs)
        self.values = values  # List of allowed values


if __name__=='__main__':
    tote = EnumeratedTote(values=[1,2,3])
    import json
    tote1 = json.loads( json.dumps(tote, default=vars) )
    pass