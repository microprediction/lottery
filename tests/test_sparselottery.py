from lottery.categorical import SparseCategoricalLottery
import random


def test_sparse():
    L = SparseCategoricalLottery()
    ys = [random.choice([1, 1, 2, 3]) for _ in range(10)]
    ts = [i * 100 for i in range(10)]
    tau = 10
    k = 2
    for t, y in zip(ts, ys):
        L.register_truth(value=y, t=t)
        rewards = L.calculate_rewards(k=k, t=t, tau=tau, value=y)
        print(rewards)
        L.register_forecast(t=t + 20, owner='bill', tau=tau, k=k, values=[y, y + 1, y + 1], weights=[0.5, 0.25, 0.25],
                            amount=1.0)
        L.register_forecast(t=t + 20, owner='mary', tau=tau, k=k, values=[1, 2, 3], weights=[0.4, 0.4, 0.2], amount=1.5)
