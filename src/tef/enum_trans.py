import re
import itertools
from .utils import to_roman_lower, split_list, is_sq_list, flatten, join_flatten, ruby_style_to_i

Default_ncols=1
Default_item=[r'\rm(', 'i', ')']
Default_itemw='2em'

def counter(type, num):
    if type=='':
        return ''
    if type=='1':
        return str(num)
    if type=='i':
        return to_roman_lower(num)
    if type=='I':
        return to_roman_lower(num).upper()
    if 1<=num and num<=26:                  # type == 'a' or 'A'
        return chr(ord(type) + num -1)
    return str(num)

def escape(str):
    if re.search(r'[\[\]]', str):
        return '{'+str+'}'
    return str

def make_item(lst, num, type):
    body=lst[0]+counter(lst[1], num)+lst[2]
    return f'\\item[{escape(body)}] '

def replace(lst, num, type):
    lst[0]=item(num)
    lst[1]=' '

def skip(v):
    return isinstance(v, str) and (v=='\n' or v=='\r' or v==' ' or v=='' or v[0]=='%')

def back_search(line, end_pt):
    i=end_pt
    while skip(line[i-1]):
        i-=1
    if isinstance(line[i-1], list) and line[i-2] == r'\\':
        return i-2
    return i-1 if line[i-1]==r'\\' else i

def get_param(lst):
    return split_list(lst[1:-1], ',')+[[], [], []]

def find_counter(lst):
    for k, v in enumerate(lst):
        if v in ['1', 'i', 'I', 'a', 'A']:
            return k

def parse_ncols(lst):
    ncols=ruby_style_to_i(join_flatten(lst))
    return ncols if ncols>=1 else Default_ncols

def parse_item(lst):
    if not lst:
        return Default_item
    lst=list(flatten(lst, lambda x: x[0]!='{'))
    c=find_counter(lst)
    if c is not None:
        return [join_flatten(lst[:c]), lst[c], join_flatten(lst[c+1:])]
    str=join_flatten(lst)
    return [str, "", ""] if str else Default_item
    

def parse_itemw(lst):
    return join_flatten(lst) if lst else Default_itemw

def parse_param(prm):
    ncols = parse_ncols(prm[0])
    itemv = parse_item(prm[1])
    itemw = parse_itemw(prm[2])
    return (ncols, itemv, itemw)

def append_dollar(line, end_pt):
    pt=back_search(line, end_pt)
    line[pt]='$'+line[pt]

def translate(lst):
    if len(lst)<2 or not (lst[0] == r'\begin{enum}' and lst[-1] == r'\end{enum}'):
        return

    lst[-1]='\n' # sentinel

    items=[]
    param=[[],[],[]]
    for pt, el in enumerate(lst):
        if not items and is_sq_list(el):
            param=get_param(el)
            lst[pt]=''
        if el=='\n' and (lst[pt+1:pt+3]==['-', ' '] or lst[pt+1:pt+3] == ['*', ' '] or lst[pt+1:pt+4] == ['*', '*', ' ']):
            items.append(pt+1)

    items.append(len(lst))

    (ncols, itemv, itemw)=parse_param(param)

    for num, pt in enumerate(items[:-1]):
#        print(lst[pt:])
        if lst[pt]=='*':
            if lst[pt+1]=='*':
                lst[pt+1] = r'$\displaystyle'
                type='**'
            else:
                lst[pt+1] = '$'
                type='*'
            append_dollar(lst, items[num+1])
        else:
            lst[pt+1] = ''
            type='-'
        lst[pt]=make_item(itemv, num+1, type)

    if ncols==1:
        lst[0]=r'\begin{enumerate}'
        lst[-1]=r'\end{enumerate}'
    else:
        lst[0]=r'\begin{colenum}{%d}{%.2f}{%s}' % (ncols, 1.0/ncols, itemw)
        lst[-1]=r'\end{colenum}'
