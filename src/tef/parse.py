import re

class Parse:
    re_env = re.compile(r'\\(?:begin|end)[ \t\r\n]*\{[a-zA-Z*]+\}')
    re_cmd = re.compile(r'\\[a-zA-Z]+')
    re_cmd2= re.compile(r'\\.')
    re_comment = re.compile(r'%.*')
    re_any1= re.compile(r'.', re.DOTALL)
    re_any2= re.compile(r'[^}]', re.DOTALL)
    re_list1 = [re_env, re_cmd, re_cmd2, re_comment, re_any1]
    re_list2 = [re_env, re_cmd, re_cmd2, re_comment, re_any2]

    begin_env=r'\\begin[ \t\r\n]*\{(?P<name>[a-zA-Z*]+)\}'
    end_env  =r'\\end[ \t\r\n]*\{(?P<name>[a-zA-Z*]+)\}'

    paren_dic = {re.compile(r'{') : re.compile(r'}'),
                 re.compile(re.escape('[')) : re.compile(re.escape(']')),
                 re.compile(re.escape(r'\[')) : re.compile(re.escape(r'\]')),
                 re.compile(begin_env) : re.compile(end_env)}

    def __init__(self, string):
        self.string = string
        self.pos = 0

    def token(self, brace_accept):
        re_list = self.re_list1 if brace_accept else self.re_list2
        for r in re_list:
            match = r.match(self.string, self.pos)
            if match:
                self.pos = match.end()
                self.match=match.group(0)
                return True
        return False

    def parse(self, top=None, cl_should_be=None, name=None):
        result = [top] if top else []
        brace  = (top=='{') or top is None
        while self.token(brace):
            c=self.match
            for r in self.paren_dic.keys():
                mt=r.match(c, 0)
                if mt:
                    cl=self.paren_dic[r]
                    result += self.parse(c, cl, mt.groupdict().get('name'))
                    break
            else:
                result.append(c)
                for r in self.paren_dic.values():
                    mt=r.match(c, 0)
                    if mt:
                        if cl_should_be == r and name == mt.groupdict().get('name'):
                            return [result]
        return result


def parse(utf_string):
    return Parse(utf_string).parse()
