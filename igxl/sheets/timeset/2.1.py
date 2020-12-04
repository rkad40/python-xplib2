from igxl.sheets.definition import StandardTable as SheetDefinition

banner = \
r"""
###########################################################################
#  _____ _                  ____       _
# |_   _(_)_ __ ___   ___  / ___|  ___| |_ ___
#   | | | | '_ ` _ \ / _ \ \___ \ / _ \ __/ __|
#   | | | | | | | | |  __/  ___) |  __/ |_\__ \
#   |_| |_|_| |_| |_|\___| |____/ \___|\__|___/
#
###########################################################################
"""

header = \
"""
@{SheetInfo}\t@{SheetName}

\tTiming Mode:\t${TimingMode}\t\tMaster Timeset Name:\t${MasterTimesetName}
\tTime Domain:\t${TimeDomain}

\t\tCycle\tPin/Group
\tTime Set\tPeriod\tName\tClock Period\tSetup\tEdge Set\tComment
"""


class Worksheet(SheetDefinition):
    def __init__(me):
        me.reset()
        me.type = 'DTTimesetSheet'
        me.name = 'Time Sets'
        me.version = 2.1
        me.allow_refs = True
        me.banner = banner
        me.header = header
        me.columns = ['TimeSet', 'CyclePeriod', 'PinGroup', 'PinGroupClockPeriod', 
          'PinGroupSetup', 'EdgeSet', 'Comment']
        me.initialize()
