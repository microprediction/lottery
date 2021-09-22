from lottery.categoricallottery import CategoricalLottery
from lottery.rewardutil import equal_rewards
import random




def test_sparse_deterministic():

    # Fix data
    ys = [3, 2, 1, 1, 1, 1, 1, 1, 1, 3]
    anticipated_rewards = [[],
                           [],
                           [('bill', -1.0), ('mary', -1.5), ('mary', 2.5)],
                           [('bill', -1.0), ('mary', -1.5), ('mary', 2.5)],
                           [('bill', -1.0), ('mary', -1.5), ('bill', 1.1363636363636362), ('mary', 1.3636363636363638)],
                           [('bill', -1.0), ('mary', -1.5), ('bill', 1.1363636363636362), ('mary', 1.3636363636363638)],
                           [('bill', -1.0), ('mary', -1.5), ('bill', 1.1363636363636362), ('mary', 1.3636363636363638)],
                           [('bill', -1.0), ('mary', -1.5), ('bill', 1.1363636363636362), ('mary', 1.3636363636363638)],
                           [('bill', -1.0), ('mary', -1.5), ('bill', 1.1363636363636362), ('mary', 1.3636363636363638)],
                           [('bill', -1.0), ('mary', -1.5), ('mary', 2.5)]]

    L = CategoricalLottery()
    print(ys)
    ts = [i * 100 for i in range(10)]
    tau = 10
    k = 2
    for t, y, r_anticipated in zip(ts, ys, anticipated_rewards):
        L.append_to_history(value=y, t=t)
        r_actual = L.calculate_rewards(k=k, t=t, tau=tau, value=y)
        if not equal_rewards(r_anticipated,r_actual):
            from lottery.conventions import consolidate_rewards
            print('Deterministic reward test failed ... strange! ')
            c_anticipated = consolidate_rewards(r_anticipated)
            c_actual = consolidate_rewards(r_actual)
            from pprint import pprint
            print('anticipated rewards:')
            pprint(c_anticipated)
            print('actual rewards:')
            pprint(c_actual)
            raise Exception('Deterministic reward test failed ... strange!')

        L.register_forecast(t=t + 20, owner='bill', tau=tau, k=k, values=[y, y + 1, y + 1], weights=[0.5, 0.25, 0.25], amount=1.0)
        L.register_forecast(t=t + 20, owner='mary', tau=tau, k=k, values=[1, 2, 3], weights=[0.4, 0.4, 0.2], amount=1.5)


if __name__=='__main__':
    test_sparse_deterministic()