from weakref import *
import inspect
 
# https://pygame.org/wiki/SignalSlot

class Signal:
    def __init__(self):
        self.slots = []
 
        # for keeping references to _WeakMethod_FuncHost objects.
        # If we didn't, then the weak references would die for
        # non-method slots that we've created.
        self.funchost = []
 
    def __call__(self, *args, **kwargs):
        r = []
        for i, slot in enumerate(self.slots):
            if slot != None:
                rr = slot(*args, **kwargs)
                if not rr is None:
                  r.append( rr )
            else:
                del self.slots[i]
        return r
                
    def call(self, *args, **kwargs):
        self.__call__(*args, **kwargs)
 
    def connect(self, slot):
        self.disconnect(slot)
        if inspect.ismethod(slot):
            self.slots.append(WeakMethod(slot))
        else:
            o = _WeakMethod_FuncHost(slot)
            self.slots.append(WeakMethod(o.func))
            # we stick a copy in here just to keep the instance alive
            self.funchost.append(o)
 
    def disconnect(self, slot):
        try:
            for i, wm in enumerate(self.slots):
                if inspect.ismethod(slot):
                    if wm.f == slot.im_func and wm.c() == slot.im_self:
                        del self.slots[i]
                        return
                else:
                    if wm.c().hostedFunction == slot:
                        del self.slots[i]
                        return
        except:
            pass
 
    def disconnectAll(self):
        self.slots = []
        self.funchost = []
 
class _WeakMethod_FuncHost:
    def __init__(self, func):
        self.hostedFunction = func
    def func(self, *args, **kwargs):
        return self.hostedFunction(*args, **kwargs)
 
# this class was generously donated by a poster on ASPN (aspn.activestate.com)
class WeakMethod:
    def __init__(self, f):
        self.f = f.im_func
        self.c = ref(f.im_self)
    def __call__(self, *args, **kwargs):
        if self.c() == None : return
        return self.f(self.c(), *args, **kwargs)
