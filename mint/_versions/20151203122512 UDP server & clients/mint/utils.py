import sys

def put(*args):
    sys.stdout.write(put_format(*args) + '\n')

def put_format(*args):
    fmt = args[0]
    if isinstance(fmt, str) and '{' in fmt:
        s = fmt.format(*args[1:])
    else:
        s = ' '.join(map(str, args))
    return s

def new_name(obj, reset=True):
    cls = type(obj)
    if not hasattr(cls, 'n_instances'):
        cls.n_instances = 0
    n = cls.n_instances
    cls.n_instances += 1
    return '{} {}'.format(cls.__name__, n)

class bunch(dict):

    def __init__(self, **kwargs):
        super(bunch, self).__init__(kwargs)
        self.__dict__.update(kwargs)

class each(object):

    def __init__(self, *args):
        if len(args) == 0:
            raise TypeError('each() expects at least 1 argument')
        elif len(args) == 1:
            arg = args[0]
            if hasattr(arg, '__call__'):
                f = arg
                return vectorized(f)
            else:
                iterable = arg
        else:
            iterable = args
        self.__iterable = iterable

    def __getattribute__(self, key):
        if key == '_each__iterable':
            return object.__getattribute__(self, key)
        else:
            return each(list(getattr(t, key) for t in self.__iterable))

    # >>> each(a).foo = 656
    def __setattr__(self, k, v):
        if k == '_each__iterable':
            super(each, self).__setattr__(k, v)
        else:
            for t in self.__iterable:
                setattr(t, k, v)
            return self

    # >>> each(a).f(ARGS)
    # >>> each(funcs)(ARGS)
    def __call__(self, *args, **kwargs):
        return [f(*args, **kwargs) for f in self.__iterable]

    # >>> list(each(a).foo)
    def __iter__(self):
        return iter(self.__iterable)

    def __repr__(self):
        return '<each of {}>'.format(self.__iterable)

def vectorized(f):
    raise NotImplementedError('vectorized function is not implemented yet')

if __name__ == '__main__':
    import doctest
    doctest.testmod()
