import rich
from rsg.core import RsgInt, Rsg, RsgList

rsg = RsgInt()
rich.print(next(rsg))

rsg = RsgList(min_breadth=1, max_breadth=10, min_depth=0, max_depth=4)
rich.print(next(rsg))

rsg = Rsg()
rich.print(next(rsg))
