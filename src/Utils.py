#! /usr/bin/env python

from string import Template

class EvalTemplate(Template):
    idpattern = "[^{}]+"

    def substitute(self,mapping,**kws):
        original_template = self.template
        last_template = self.template
        self.template = super(EvalTemplate,self).substitute(mapping,**kws)
        while self.template != last_template:
            last_template = self.template
            self.template = super(EvalTemplate,self).substitute(mapping,**kws)

        ret = self.template
        self.teplate = original_template
        
        return ret


class InterpEvalError(KeyError):
    pass

class EvalTemplateDict(dict):
    """A dictionary that be used to add support for evaluating
       expresions with the string.Transform class"""

    def __init__(self, *args, **kwargs):
        self.store = dict()
        self.update(dict(*args, **kwargs))

    def __getitem__(self, key):
        try:
            return dict.__getitem__(self,key)
        except KeyError:
            try:
                return eval(self.__keytransform__(key),self)
            except Exception, e:
                raise InterpEvalError(key,e)

        return self.store[self.__keytransform__(key)]

    def __setitem__(self, key, value):
        self.store[self.__keytransform__(key)] = value

    def __delitem__(self, key):
        del self.store[self.__keytransform__(key)]

    def __iter__(self):
        return iter(self.store)

    def __len__(self):
        return len(self.store)

    def __keytransform__(self, key):
        
        return key

