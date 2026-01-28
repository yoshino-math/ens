import re
import io
import sys
from .ens_proc import find_processor
from .common import ENSError
 
DocumentClass_03=r'\documentclass[a4j, twoside]{jsarticle}'
DocumentClass_04=r'\documentclass[a4paper, twoside]{ltjsarticle}'
UsepackageENS = r'\usepackage{ens}'
BeginDocument = r'\begin{document} \mainheader'

class LineIterator:
    def __init__(self, input_data, ruby_compat):
        self.it = iter(input_data)
        self.out= []
        self.ruby_compat=ruby_compat

    def __iter__(self):
        return self

    def __next__(self):
        line = next(self.it)
        if self.ruby_compat:
            if line.endswith('\r\n'):
                return line[:-2]
            return line[:-1]
        return line.rstrip('\r\n')

    def skip_until(self, pattern, err_msg='Not found'):
        while True:
            line = next(self, None)
            if line is None:
                raise ENSError(err_msg)

            if re.match(pattern, line):
                return

            if re.match(r'^\s*$', line):
                self.out.append(line)
            elif line.startswith('#'):
                self.out.append('%' + line[1:])
            else:
                raise ENSError(err_msg)

def make_head(string):
    if string is None:
        raise ENSError("There are no kamoku or date")

    parts = string.split(' ')
    if len(parts) < 3:
        raise ENSError("There are no date")
    
    kamoku, zenkou, date, *kai = parts

    try:
        y_s, m_s, d_s = (date.split('/', 2)+[''])[:3]
        year, month = int(y_s), int(m_s)
    except ValueError:
        raise ENSError(f"Invalid date format: {date}")

    nendo = year - (1 if month <= 3 else 0)
    if "追試" in kai and month == 4:
        nendo -= 1

    return (
        rf"\def\kamoku{{{kamoku}}} \def\zenkou{{{zenkou}}} \def\year{{{year}}} "
        rf"\def\nendo{{{nendo}}}\def\date{{\year/{m_s}/{d_s}}} "
        rf"\def\kai{{{' '.join(kai)}}}"
    )

def header(it):
    line = next(it, None)
    if line is None:
        raise ENSError('No line found')
    mt=re.match(r'^ens_ver:\s*(.*?)\s*$', line)
    if not mt:
        raise ENSError('This is not ens file')

    ver=mt.group(1)
    print(f"ENS Engine: Processing as version {ver}", file=sys.stderr, flush=True)

    if ver == "0.3":
        doc_class = DocumentClass_03
    elif ver == "0.4":
        doc_class = DocumentClass_04
    else:
        raise ENSError('ens_ver must be 0.3 or 0.4')

    it.out.append(doc_class)
    it.out.append(make_head(next(it, None)))

def layout(it):
    it.skip_until(r'^--layout', err_msg="No layout")
    it.out.append("% Layout")

    layout_rules = [
        (r'^高:\s*(.*?)\s*$', r'\setlength\textheight{%s}'),
        (r'^幅:\s*(.*?)\s*$', r'\setlength\textwidth{%s}'),
        (r'^ヘッダ上余白:\s*(.*?)\s*$', r'\setlength\topmargin{%s}'),
        (r'^ヘッダ右余白:\s*(.*?)\s*$', r'\newlength{\headerright}\setlength{\headerright}{%s}'),
        (r'^フッタ下余白:\s*(.*?)\s*$', r'\newlength{\footerbottom}\setlength{\footerbottom}{%s}'),
        (r'^(.*)$', r'%%%s'),
    ]

    while True:
        line = next(it, None)
        if line is None: break
        if line.startswith('--'):
            it.out.append(UsepackageENS)
            break

        for pattern, template in layout_rules:
            if m := re.match(pattern, line):
                it.out.append(template % m.group(1))
                break

def preamble(it):
    it.skip_until(r'^--preamble', err_msg="No preamble")
    it.out.append("% Preamble")
    
    while True:
        line = next(it, None)
        if line is None: break
        if line.startswith('--'):
            break
        it.out.append(line)
        
    it.out.append(BeginDocument)

def trans(input_data, ruby_compat=False):
    it=LineIterator(input_data, ruby_compat=ruby_compat)

    header(it)
    layout(it)
    preamble(it)

    for line in it:
        if line == "":
            it.out.append("")
            continue

        proc = find_processor(line)
        it.out.append(proc.head(line))
        
        while (content := next(it, "")) != "":
            it.out.append(proc.wrap_line(content) if hasattr(proc, 'wrap_line') else content)
        
        it.out.append(proc.tail())

    it.out.append(r"\end{document}")
    return '\n'.join(it.out)



