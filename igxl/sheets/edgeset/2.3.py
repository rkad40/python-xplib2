from igxl.sheets.definition import StandardTable as SheetDefinition

banner = \
r"""
###########################################################################
#  _____    _              ____       _
# | ____|__| | __ _  ___  / ___|  ___| |_ ___
# |  _| / _` |/ _` |/ _ \ \___ \ / _ \ __/ __|
# | |__| (_| | (_| |  __/  ___) |  __/ |_\__ \
# |_____\__,_|\__, |\___| |____/ \___|\__|___/
#             |___/
###########################################################################
"""

header = \
"""
@{SheetInfo}\t@{SheetName}

\tTiming Mode:\t${TimingMode}
\tTime Domain:\t${TimeDomain}\t\t\tStrobe Ref Setup Name:\t${StrobeRefSetupName}

\t\t\tData\t\tDrive\t\t\t\tCompare\t\t\t\tEdge Resolution
\tPin/Group\tEdge Set\tSrc\tFmt\tOn\tData\tReturn\tOff\tMode\tOpen\tClose\tRef Offset\tMode\tComment
"""


class Worksheet(SheetDefinition):
    def __init__(me):
        me.reset()
        me.type = 'DTEdgesetSheet'
        me.name = 'Edge Sets'
        me.version = 2.3
        me.allow_refs = True
        me.banner = banner
        me.header = header
        me.columns = ['PinGroup', 'EdgeSet', 'DataSrc', 'DataFmt', 'DriveOn',
          'DriveData', 'DriveReturn', 'DriveOff', 'CompareMode', 'CompareOpen',
          'CompareClose', 'RefOffset', 'EdgeResolutionMode', 'Comment']
        me.initialize()
