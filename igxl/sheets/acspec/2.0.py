from igxl.sheets.definition import Spec2Table as SheetDefinition

banner = \
r"""
###########################################################################
#     _    ____   ____
#    / \  / ___| / ___| _ __   ___  ___ ___
#   / _ \| |     \___ \| '_ \ / _ \/ __/ __|
#  / ___ \ |___   ___) | |_) |  __/ (__\__ \
# /_/   \_\____| |____/| .__/ \___|\___|___/
#                      |_|
###########################################################################
"""

header = \
"""
@SheetInfo\t@SheetName

\t\t\tSelector\t\t@Categories
\tSymbol\tValue\tName\tVal\t@Selectors\tComment
"""


class Worksheet(SheetDefinition):
    def __init__(me):
        me.reset()
        me.type = 'DTACSpecSheet'
        me.name = 'AC Specs'
        me.version = 2.0
        me.allow_refs = False
        me.banner = banner
        me.header = header
        me.columns = ['Symbol', 'Value', 'SelectorName', 'SelectorVal', '@Columns', 'Comment']
        me.initialize()
