from lottery.ongoingcategoricallottery import OngoingCategoricalLottery
from lottery.rewardutil import equal_rewards
from lottery.conventions import consolidate_rewards
from pprint import pprint
import json


def test_categorical_deterministic_case_a():

    # Fix data
    ys = [3, 2, 1, 1, 1, 1, 1, 1, 1, 3]
    anticipated_rewards = [[], [], [('bill', -1.0), ('mary', -1.5), ('mary', 2.5)],
                           [('bill', -1.0), ('mary', -1.5), ('mary', 2.5)],
                           [('bill', -1.0), ('mary', -1.5), ('bill', 1.1363636363636362), ('mary', 1.3636363636363638)],
                           [('bill', -1.0), ('mary', -1.5), ('bill', 1.1363636363636362), ('mary', 1.3636363636363638)],
                           [('bill', -1.0), ('mary', -1.5), ('bill', 1.1363636363636362), ('mary', 1.3636363636363638)],
                           [('bill', -1.0), ('mary', -1.5), ('bill', 1.1363636363636362), ('mary', 1.3636363636363638)],
                           [('bill', -1.0), ('mary', -1.5), ('bill', 1.1363636363636362), ('mary', 1.3636363636363638)],
                           [('bill', -1.0), ('mary', -1.5), ('mary', 2.5)]]

    L = OngoingCategoricalLottery()
    #print(ys)
    ts = [i * 100 for i in range(10)]
    tau = 10
    k = 2
    all_r = list()
    for t, y, r_anticipated in zip(ts, ys, anticipated_rewards):
        L.observe(value=y, t=t)
        r_actual = L.payout(k=k, t=t, tau=tau, value=y)
        all_r.append(r_actual)
        if not equal_rewards(r_anticipated,r_actual):
            print('Deterministic reward test failed ... strange! ')
            c_anticipated = consolidate_rewards(r_anticipated)
            c_actual = consolidate_rewards(r_actual)
            print('anticipated rewards:')
            pprint(c_anticipated)
            print('actual rewards:')
            pprint(c_actual)
            raise Exception('Deterministic reward test failed ... strange!')

        L.add( t=t + 20, owner='bill', tau=tau, k=k, values=[y, y + 1, y + 1], weights=[0.5, 0.25, 0.25], amount=1.0)
        L.add( t=t + 20, owner='mary', tau=tau, k=k, values=[1, 2, 3], weights=[0.4, 0.4, 0.2], amount=1.5)
    #print(all_r)


def test_categorical_deterministic_case_b():

    # Fix data
    ys = [3, 2, 1, 1, 1, 1, 1, 1, 1, 3]
    anticipated_rewards = [[], [], [('bill', -1.0), ('mary', -1.5), ('mary', 2.5)],
                           [('bill', -1.0), ('mary', -1.5), ('bill', 1.5625), ('mary', 0.9375000000000001)],
                           [('bill', -1.0), ('mary', -1.5), ('bill', 1.3888888888888888), ('bill', 0.6944444444444444), ('mary', 0.41666666666666674)],
                           [('bill', -1.0), ('mary', -1.5), ('bill', 1.3888888888888888), ('bill', 0.6944444444444444), ('mary', 0.41666666666666674)],
                           [('bill', -1.0), ('mary', -1.5), ('bill', 1.3888888888888888), ('bill', 0.6944444444444444), ('mary', 0.41666666666666674)],
                           [('bill', -1.0), ('mary', -1.5), ('bill', 1.3888888888888888), ('bill', 0.6944444444444444), ('mary', 0.41666666666666674)],
                           [('bill', -1.0), ('mary', -1.5), ('bill', 1.3888888888888888), ('bill', 0.6944444444444444), ('mary', 0.41666666666666674)],
                           [('bill', -1.0), ('mary', -1.5), ('mary', 2.5)]]

    L = OngoingCategoricalLottery()
    #print(ys)
    ts = [i * 100 for i in range(10)]
    tau = 10
    k = 2
    all_r = list()
    for t, y, r_anticipated in zip(ts, ys, anticipated_rewards):
        L.observe(value=y, t=t)
        r_actual = L.payout(k=k, t=t, tau=tau, value=y)
        all_r.append(r_actual)
        if not equal_rewards(r_anticipated,r_actual):
            print('Deterministic reward test failed ... strange! ')
            c_anticipated = consolidate_rewards(r_anticipated)
            c_actual = consolidate_rewards(r_actual)
            print('anticipated rewards:')
            pprint(c_anticipated)
            print('actual rewards:')
            pprint(c_actual)
            raise Exception('Deterministic reward test failed ... strange!')

        L.add( t=t + 20, owner='bill', tau=tau, k=k, values=[y, y - 1, y], weights=[0.5, 0.25, 0.25], amount=1.0)
        L.add( t=t + 20, owner='mary', tau=tau, k=k, values=[1, 2, 3, 4], weights=[0.4, 0.4, 0.1, 0.5], amount=1.5)
        L.add( t=t + 21, owner='mary', tau=tau, k=k, values=[1, 2, 3, 4], weights=[0.1, 0.1, 0.1, 0.7], amount=1.5)



def test_categorical_deterministic_case_b_serialization():

    # Fix data
    ys = [3, 2, 1, 1, 1, 1, 1, 1, 1, 3]
    anticipated_rewards = [[], [], [('bill', -1.0), ('mary', -1.5), ('mary', 2.5)],
                           [('bill', -1.0), ('mary', -1.5), ('bill', 1.5625), ('mary', 0.9375000000000001)],
                           [('bill', -1.0), ('mary', -1.5), ('bill', 1.3888888888888888), ('bill', 0.6944444444444444), ('mary', 0.41666666666666674)],
                           [('bill', -1.0), ('mary', -1.5), ('bill', 1.3888888888888888), ('bill', 0.6944444444444444), ('mary', 0.41666666666666674)],
                           [('bill', -1.0), ('mary', -1.5), ('bill', 1.3888888888888888), ('bill', 0.6944444444444444), ('mary', 0.41666666666666674)],
                           [('bill', -1.0), ('mary', -1.5), ('bill', 1.3888888888888888), ('bill', 0.6944444444444444), ('mary', 0.41666666666666674)],
                           [('bill', -1.0), ('mary', -1.5), ('bill', 1.3888888888888888), ('bill', 0.6944444444444444), ('mary', 0.41666666666666674)],
                           [('bill', -1.0), ('mary', -1.5), ('mary', 2.5)]]

    L = OngoingCategoricalLottery()
    #print(ys)
    ts = [i * 100 for i in range(10)]
    tau = 10
    k = 2
    all_r = list()
    for t, y, r_anticipated in zip(ts, ys, anticipated_rewards):
        L.observe(value=str(y), t=t)
        r_actual = L.payout(k=k, t=t, tau=tau, value=str(y))
        all_r.append(r_actual)
        if not equal_rewards(r_anticipated,r_actual):
            print('Deterministic reward test failed ... strange! ')
            c_anticipated = consolidate_rewards(r_anticipated)
            c_actual = consolidate_rewards(r_actual)
            print('anticipated rewards:')
            pprint(c_anticipated)
            print('actual rewards:')
            pprint(c_actual)
            raise Exception('Deterministic reward test failed ... strange!')

        L.add( t=t + 20, owner='bill', tau=tau, k=k, values=[str(y), str(y - 1), str(y)], weights=[0.5, 0.25, 0.25], amount=1.0)
        L.add( t=t + 20, owner='mary', tau=tau, k=k, values=['1', '2', '3', '4'], weights=[0.4, 0.4, 0.1, 0.5], amount=1.5)
        L.add( t=t + 21, owner='mary', tau=tau, k=k, values=['1', '2', '3', '4'], weights=[0.1, 0.1, 0.1, 0.7], amount=1.5)

        json_str = json.dumps(L)
        G = OngoingCategoricalLottery.from_json(json_str)

        if G['state']!=L['state']:
            for k_,v_ in G['state'].items():
                v1 = L['state'][k_]
                if v1!=v_:
                    print(v1)
                    print(v_)
        pass





if __name__=='__main__':
    test_categorical_deterministic_case_b_serialization()