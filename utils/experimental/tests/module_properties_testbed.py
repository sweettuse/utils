from __future__ import annotations

from utils.experimental.module_properties import enable_module_properties
_p = 19
_l = [1]

@property
def p():
    print('in getter')
    return _p

@p.setter
def p(value):
    print('in setter')
    global _p
    _p = value

@property
def l():
    print('in getter')
    return _l

@p.setter
def l(value):
    print('in setter')
    global _l
    _l = value

if __name__ != '__main__':
    enable_module_properties()
