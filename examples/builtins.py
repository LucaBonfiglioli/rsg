from rsg.core import RsgBase

rsg = RsgBase(min_depth=1, max_depth=4, min_breadth=1, max_breadth=3)
print(next(rsg))
