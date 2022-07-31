from __future__ import annotations

from proto import module

from utils.experimental.tests import module_properties_testbed 
testbed = module_properties_testbed
print(id(testbed))
import sys
m = sys.modules['utils.experimental.tests.module_properties_testbed']
print(m._p)
m.p = 42
print(m.p)
print(m._p)
# print(sys.modules)
from utils.experimental.tests import module_properties_testbed


print(testbed.p)
testbed.p = 9000
print(testbed.p)
print(testbed._p == testbed.p)
print(m._p)

print('============')
print(m.l)
m.l = [62]
m.l = [41]
m.l = 19.5
print(m.l)
