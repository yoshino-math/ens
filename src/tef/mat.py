from itertools import cycle
import re
from .utils import is_sq_list, join_flatten, find_index, ruby_style_to_i, num_str, is_matrix

def make_matrix(v, lst, ncols=2):
    env  = "pmatrix" if v == r"\matrix" else v[1:]
    seps = cycle(["&"] * (ncols - 1) + [r"\\"])
    cnt  = join_flatten(next(seps) if x == "," else x for x in lst)
    return rf"\begin{{{env}}}{cnt}\end{{{env}}}"

def make_vector(lst):
    cnt = join_flatten( r'\\' if x==',' else x for x in lst)
    return rf'\begin{{pmatrix}}{cnt}\end{{pmatrix}}'

def make_svector(lst):
    cnt = join_flatten(r'\\' if x==',' else x for x in lst)
    return rf'\left(\!\begin{{smallmatrix}}{cnt}\end{{smallmatrix}}\!\right)'

def mk_ops(lst):
    comma_pt = find_index(lst, ',')
    colon_pt = find_index(lst, ':')
    pair = [comma_pt is None, colon_pt is None]
    if pair == [False, True]:
        i=ruby_style_to_i(join_flatten(lst[0:comma_pt]))
        j=ruby_style_to_i(join_flatten(lst[comma_pt+1:]))
        return rf'\swap{{{i-1}}}{{{j-1}}}'
    if pair == [True, False]:
        i=ruby_style_to_i(join_flatten(lst[0:colon_pt]))
        s=join_flatten(lst[colon_pt+1:])
        return rf'\mult{{{i-1}}}{{{s}}}'
    if pair == [False, False]:
        if comma_pt < colon_pt:
            i=ruby_style_to_i(join_flatten(lst[0:comma_pt]))
            j=ruby_style_to_i(join_flatten(lst[comma_pt+1:colon_pt]))
            s=join_flatten(lst[colon_pt+1:])
        return rf'\add[{s}]{{{i-1}}}{{{j-1}}}'
    return ''
    
def mk_op(v):
    if v==r'\row' or v==r'\col':
        return v+'ops'
    elif is_sq_list(v):
        return mk_ops(v[1:-1])
    return v

def make_option(lst):
    return join_flatten(mk_op(v) for v in lst)

def make_gmatrix(v, lst, ops, ncols=2):
    cmd = 'p' if v == r'\matrix' else v[1:2]
    seps = cycle(["&"] * (ncols - 1) + [r"\\"])
    cnt  = join_flatten(next(seps) if x == "," else x for x in lst)
    op=make_option(ops)
    return rf'\begin{{gmatrix}}[{cmd}]{cnt}{op}\end{{gmatrix}}'

def translate(lst,k):
    if not len(lst)>k+1:
        return
    v=lst[k]
    if v==r'\vector' and is_sq_list(lst[k+1]):
        lst[k]=make_vector(lst[k+1][1:-1])
        lst[k+1]=''
    elif v==r'\svector' and is_sq_list(lst[k+1]):
        lst[k]=make_svector(lst[k+1][1:-1])
        lst[k+1]=''
    elif is_matrix(v) and is_sq_list(lst[k+1]):
        if len(lst)>k+2 and is_sq_list(lst[k+2]):
            lst[k]=make_gmatrix(v, lst[k+1][1:-1], lst[k+2][1:-1])
            lst[k+1]=''
            lst[k+2]=''
        else:
            lst[k]=make_matrix(v, lst[k+1][1:-1])
            lst[k+1]=''
    elif len(lst)>k+2 and is_matrix(v) and num_str(lst[k+1]) and is_sq_list(lst[k+2]):
        if len(lst)>k+3 and is_sq_list(lst[k+3]):
            lst[k]=make_gmatrix(v, lst[k+2][1:-1], lst[k+3][1:-1], int(lst[k+1]))
            lst[k+1]=''
            lst[k+2]=''
            lst[k+3]=''
        else:
            lst[k]=make_matrix(v, lst[k+2][1:-1], int(lst[k+1]))
            lst[k+1]=''
            lst[k+2]=''
