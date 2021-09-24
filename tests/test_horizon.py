from lottery.conventions import k_and_tau_to_h, horizon_from_int, MAX_TAU


def test_horizon():
    for tau in [-MAX_TAU+1, 153, 1, 0, -3, MAX_TAU-1]:
        for k in [141,0,1,4]:
            h = k_and_tau_to_h(k=k, tau=tau)
            k_back, tau_back = horizon_from_int(h)
            assert k==k_back
            assert tau==tau_back


if __name__=='__main__':
    test_horizon()