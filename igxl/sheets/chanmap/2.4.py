from igxl.sheets.definition import StandardTable as SheetDefinition

banner = \
r"""
###########################################################################
#   ____ _                   __  __
#  / ___| |__   __ _ _ __   |  \/  | __ _ _ __
# | |   | '_ \ / _` | '_ \  | |\/| |/ _` | '_ \
# | |___| | | | (_| | | | | | |  | | (_| | |_) |
#  \____|_| |_|\__,_|_| |_| |_|  |_|\__,_| .__/
#                                        |_|
###########################################################################
"""

header = \
"""
@SheetInfo\t@SheetName

\tDIB ID:\t$DIBID\t\tView Mode:\t$ViewMode\t\tSite Replication:\t$SiteReplication\tUSL Tag:\t$USLTag

\tDevice Under Test\t\tTester Channel
\tPin Name\tPackage Pin\tType\t@Sites\tComment
"""


class Worksheet(SheetDefinition):
    def __init__(me):
        me.reset()
        me.type = 'DTChanMap'
        me.name = 'Channel Map'
        me.version = 2.4
        me.allow_refs = True
        me.banner = banner
        me.header = header
        me.columns = ['PinName', 'PackagePin', 'Type', '@Sites', 'Comment']
        me.initialize()
