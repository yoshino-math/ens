import re

class Toi:
    RE = r'^=='
    @staticmethod
    def head(line):
        m = re.match(r'^==(x)?', line)
        op = '' if m.group(1) is None else m.group(1)
        return rf"\begin{{toi}}{{{op}}}"
    @staticmethod
    def tail():
        return r"\end{toi}"

class Memo:
    RE = r'^\*\*.*\*\*'
    @staticmethod
    def head(line):
        m = re.match(r'^\*\*\s*(.*?)\s*\*\*\s*(.*?)\s*$', line)
        return rf"\begin{{memo}}{{{m.group(1)}}}{{{m.group(2)}}}"
    @staticmethod
    def tail():
        return r"\end{memo}"

class Comment:
    RE = r'^%'
    @staticmethod
    def head(line):
        return "%" + line
    @staticmethod
    def tail():
        return ""
    @staticmethod
    def wrap_line(line):
        return "% " + line

class Df:
    RE = r'^\+\+'
    @staticmethod
    def head(line):
        return ""
    @staticmethod
    def tail():
        return ""

class Newpage:
    RE = r'^:newpage'
    @staticmethod
    def head(line):
        return r"\newpage"
    @staticmethod
    def tail():
        return ""

class Report:
    RE = r'^:report'
    @staticmethod
    def head(line):
        return r"\vfill\report"
    @staticmethod
    def tail():
        return ""

class Other:
    RE = r'^.*'
    @staticmethod
    def head(line):
        return line
    @staticmethod
    def tail():
        return ""

ProcList = [Toi, Memo, Comment, Df, Newpage, Report, Other]

def find_processor(line):
    for proc in ProcList:
        if re.match(proc.RE, line):
            return proc
