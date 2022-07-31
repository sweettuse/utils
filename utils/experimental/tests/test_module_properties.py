from __future__ import annotations

from utils.experimental.tests import module_properties_testbed as m
print(m._p)
m.p = 42
print(m.p)
print(m._p)

m.l = [62]
m.l = [41]
m.l = [1, 19.5]
m.p = 4982
print(m.p)
print(m.p)
print(m.l)
print(m.l == m.p)
print(m.l == [1, 19.5])
