from lottery.conventions import k_and_tau_to_horizon_str, horizon_str_to_k_and_tau, MAX_TAU


def test_horizon():
    for tau in [-MAX_TAU+1, 153, 1, 0, -3, MAX_TAU-1]:
        for k in [141,0,1,4]:
            h = k_and_tau_to_horizon_str(k=k, tau=tau)
            k_back, tau_back = horizon_str_to_k_and_tau(h)
            assert k==k_back
            assert tau==tau_back


if __name__=='__main__':
    test_horizon()