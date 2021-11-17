try:
    from momentum import var_init, var_update
    using_momentum = True
except ImportError:
    using_momentum = False