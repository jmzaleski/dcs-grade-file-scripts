
#lifted from https://github.com/bewest/argparse

class _AttributeHolder(object):
    """Abstract base class that provides __repr__.

    The __repr__ method returns a string in the format::
        ClassName(attr=name, attr=name, ...)
    The attributes are determined either by a class-level attribute,
    '_kwarg_names', or by inspecting the instance __dict__.
    """

    def __repr__(self):
        type_name = type(self).__name__
        arg_strings = []
        for arg in self._get_args():
            arg_strings.append(repr(arg))
        for name, value in self._get_kwargs():
            arg_strings.append('%s=%r' % (name, value))
        return '%s(%s)' % (type_name, ', '.join(arg_strings))

    def _get_kwargs(self):
        return sorted(self.__dict__.items())

    def _get_args(self):
        return []

class Namespace(_AttributeHolder):
    """Simple object for storing attributes.

    Implements equality by attribute names and values, and provides a simple
    string representation.
    """

    def __init__(self, **kwargs):
        for name in kwargs:
            setattr(self, name, kwargs[name])

    def set_from_dict(self,dict):
        for k in dict:
            assert type(k) is str
            setattr(self,k,dict[k])

    def init_names(self,list):
        for k in list:
            assert type(k) is str
            setattr(self,k,None)
        return self

    def set(self,name,val):
        setattr(self,name,val)
    __hash__ = None

    def __eq__(self, other):
        return vars(self) == vars(other)

    def __ne__(self, other):
        return not (self == other)

    def __contains__(self, key):
        return key in self.__dict__

    def key_generator(self):
        for key, value in self._get_kwargs():
            yield key

    def value_generator(self):
        for key, value in self._get_kwargs():
            yield value

    def generator(self):
        for key, value in self._get_kwargs():
            yield key, value

    #does it look like i don't know what i'm doing??
    def __iter__(self):
        return self._get_kwargs().__iter__

    def __next__(self):
        for k,v in self.generator():
            yield k,v

if __name__ == '__main__':
    ns = Namespace()
    setattr(ns, "i", 42)
    setattr(ns, "s", "forty-two")
    setattr(ns, "d", 42.0)
    print(ns)
    print(ns.i)
    print(ns.s)
    print(ns.d)
    print('d' in ns)
    print( Namespace(i=-42,s="forty-below",d=-42.0))
    print(ns._get_kwargs())

    for key in ns.key_generator():
        print(key)

    for val in ns.value_generator():
        print(val)
    for key,val in ns.generator():
        print(key, val)

    # print("iter")
    # for x in ns:
    #     print(x)
    # print("fancy")

    ns2 = Namespace()
    ns2.set_from_dict({"ii":42,'dd':42.0})
    print(ns2)
