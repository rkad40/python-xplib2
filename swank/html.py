class Template():
    def __init__(self):
        me = self
        me.html = []

    def write(self,text):
        me = self
        me.html.append(str(text))

    def writeln(self,text):
        me = self
        me.html.append(str(text) + "\n")

    def render(self):
        me = self
        html = ''.join(me.html)
        return(html)
