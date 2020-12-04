from igxl.sheets.definition import StandardTable as SheetDefinition

banner = \
r"""
###########################################################################
#  ____  _         __  __
# |  _ \(_)_ __   |  \/  | __ _ _ __
# | |_) | | '_ \  | |\/| |/ _` | '_ \
# |  __/| | | | | | |  | | (_| | |_) |
# |_|   |_|_| |_| |_|  |_|\__,_| .__/
#                              |_|
###########################################################################
"""

header = \
"""
@{SheetInfo}\t@{SheetName}
\t\t\tUSL Tag:\t${USLTag}
\tGroup Name\tPin Name\tType\tComment
"""


class Worksheet(SheetDefinition):
    def __init__(me):
        me.reset()
        me.type = 'DTPinMap'
        me.name = 'Pin Map'
        me.version = 2.1
        me.allow_refs = True
        me.banner = banner
        me.header = header
        me.columns = ['GroupName', 'PinName', 'Type', 'Comment']
        me.initialize()
