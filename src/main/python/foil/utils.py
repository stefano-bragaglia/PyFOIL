class Tabling:
    def __init__(self, f):
        self.f = f
        self.cache = {}

    def __call__(self, *args):
        key = ()
        for arg in args:
            if type(arg) is list:
                # values = ()
                # for item in arg:
                #     val = ()
                #     if type(item) is dict:
                #         val = (*val, tuple((k, v) for k, v in item.items()))
                #     else:
                #         val = (*val, item)
                #     values = (*values, val)
                # key = (*key, values)
                key = (*key, tuple(arg))
            elif type(arg) is dict:
                key = (*key, tuple((k, v) for k, v in arg.items()))
            else:
                key = (*key, arg)

        # return copy.deepcopy(self.cache.setdefault(key, self.f(*args)))
        return self.cache.setdefault(key, self.f(*args))
