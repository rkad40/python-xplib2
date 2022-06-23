class Objectify(object):
    r"""
    Create a class-like object of a variable.

    ## Arguments
    - `data`: data to objectify
    - `key`: it the top level object is a list, specify the top level attribute (default = 'data')
    
    ## Returns
    Variable pointer to the class-like object.
    """
    def __init__(self, data, key='data'):
        t = type(data)
        if t == dict:
            for a, b in data.items():
                if isinstance(b, (list, tuple)):
                    setattr(self, a, [Objectify(x, key=a) if isinstance(x, dict) else x for x in b])
                else:
                    setattr(self, a, Objectify(b, key=a) if isinstance(b, dict) else b)
        elif t in (list, tuple):
            if not hasattr(self, key):
                setattr(self, key, [])
            l = getattr(self, key)
            for item in data:
                l.append(Objectify(item))

class __object():
    def __init__(self, obj, *keys):
        self._obj = obj
        self._keys = keys
    @property
    def val(self):
        o = self._obj
        for key in self._keys:
            o = o[key]
        return o
    @val.setter
    def val(self, val):
        o = self._obj
        for i in range(0, len(self._keys) - 1):
            key = self._keys[i]
            o = o[key]
        o[self._keys[-1]] = val
    
def x(obj, *keys):
    return __object(obj, *keys)

            