#! /usr/bin/env python

from string import Template
import re

class EvalTemplate(Template):
    delimiter = '~'
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

class Flattener:
    def __init__( self, ns = "", delim=".", allow_empty_ns=False, allow_leading_delim=False ):
        self.ns = ns
        self.delim = delim
        self.allow_empty_ns = allow_empty_ns
        self.allow_leading_delim = allow_leading_delim

    def __call__( self, obj ):
        return Flattener.flatten( obj, ns=self.ns, delim=self.delim, allow_empty_ns=self.allow_empty_ns, allow_leading_delim=self.allow_leading_delim )

    def clean_key( self, key ):
        if not self.allow_leading_delim:
            key = key.lstrip(self.delim)

        if not self.allow_empty_ns:
            clean_key = key.replace( self.delim+self.delim, self.delim )
            while clean_key != key:
                key = clean_key
                clean_key = key.replace( self.delim+self.delim, self.delim )
        return key

    def get_absolute_key( self, key ):
        keys = list()
        for key in key.split(self.delim):
            if key == '..':
                keys.pop()
                continue

            if key != '.':
                keys.append( key )

        return self.construct_key( keys )


    def get_parent_key( self, key ):
        return self.construct_key( key.split(self.delim)[:-1] )


    def construct_key( self, keys ):
        if type(keys) == list:
            return self.delim.join(keys)

        return keys

    @staticmethod
    def flatten( obj, ns="", delim=".", allow_empty_ns=False, allow_leading_delim=False ):
        '''
        Flattens a nested object into a single dictionary. Keys for the resultant dictionary are created
        by concatenating all keys required to access the element5 from the top.

        dict and list ojbects are flattened. all other objects are left as is.
        '''

        ret  = dict()
        if type(obj) == dict:
            for k in obj.keys():
                nns = ns + delim + k
                ret.update( Flattener.flatten( obj[k], ns=nns, delim=delim, allow_empty_ns=allow_empty_ns, allow_leading_delim=allow_leading_delim ) )
            return ret
            
        if type(obj) == list:
            for i in range(len(obj)):
                nns = ns + delim + str(i)
                ret.update( Flattener.flatten( obj[i], ns=nns, delim=delim, allow_empty_ns=allow_empty_ns, allow_leading_delim=allow_leading_delim ) )
            return ret

        f = Flattener( ns, delim, allow_empty_ns, allow_leading_delim )
        ns = f.clean_key( ns )

        ret[ns] = obj
        
        return ret

class LatexLabels(dict):
    def parse(self,filename):
        with open(filename) as file:
            data = file.read()
        
        r  = re.compile("\\\\newlabel\{([^\}]+)\}\{\{([^\}]+)\}\{([^\}]+)\}\}")
        rr = re.compile("\\\\bgroup\s*([0-9]+)\s*\\\\egroup")
        for match in r.findall( data ):
            (label,tag,page) = match
            match = rr.search(tag)
            if match:
                tag = match.group(1)

            tag = tag.strip()

            
            self[label.replace(":","_")] = tag

