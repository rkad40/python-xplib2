from igxl.sheets.definition import StandardTable as SheetDefinition

banner = \
r"""
###########################################################################
#      _       _       _     _     _
#     | | ___ | |__   | |   (_)___| |_
#  _  | |/ _ \| '_ \  | |   | / __| __|
# | |_| | (_) | |_) | | |___| \__ \ |_
#  \___/ \___/|_.__/  |_____|_|___/\__|
#
###########################################################################
"""

header = \
"""
@{SheetInfo}\t@{SheetName}

\t\tSheet Parameters
\tJob Name\tPin Map\tTest Instances\tFlow Table\tAC Specs\tDC Specs\tPattern Sets\tPattern Groups\tBin Table\tCharacterization\tTest Procedures\tMixed Signal Timing\tWave Definitions\tPsets\tSignals\tPort Map\tFractional Bus\tConcurrent Sequence\tComment
"""


class Worksheet(SheetDefinition):
    def __init__(me):
        me.reset()
        me.type = 'DTJobListSheet'
        me.name = 'Job List'
        me.version = 2.5
        me.allow_refs = True
        me.banner = banner
        me.header = header
        me.columns = \
        [
            'JobName', 'PinMap', 'TestInstances', 'FlowTable', 'ACSpecs',
            'DCSpecs', 'PatternSets', 'PatternGroups', 'BinTable', 'Characterization',
            'TestProcedures', 'MixedSignalTiming', 'WaveDefinitions', 'Psets',
            'Signals', 'PortMap', 'FractionalBus', 'ConcurrentSequence', 'Comment'
        ]
        me.initialize()
