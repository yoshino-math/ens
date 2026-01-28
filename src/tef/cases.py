from .utils import is_sq_list, join_flatten, split_list_at, find_last_index, append_cr

def make_condition(lst):
    return rf'&\text{{({join_flatten(lst)})}}'

def cases_line(lst):
    pt = find_last_index(lst, is_sq_list)
    if pt:
        lst[pt]=make_condition(lst[pt][1:-1])
        return append_cr(join_flatten(lst))
    return join_flatten(lst)

def make_cases(lst):
    cnt=join_flatten(cases_line(line) for line in split_list_at(lst))
    return rf'\begin{{cases}}{cnt}\end{{cases}}'

def eqsys_line(lst):
    pt = find_last_index(lst, '=')
    if pt:
        lst[pt]='&='
        return append_cr(join_flatten(lst))
    return join_flatten(lst)

def make_eqsys(lst):
    cnt=join_flatten(eqsys_line(line) for line in split_list_at(lst))
    return rf'\begin{{cases}}{cnt}\end{{cases}}'

def translate(lst, k):
    if not len(lst)>k+2:
        return
    v=lst[k:k+2]
    if v==[':', ':'] and is_sq_list(lst[k+2]):
        lst[k]=make_cases(lst[k+2][1:-1])
        lst[k+1]=''
        lst[k+2]=''
    elif v==['*', '*'] and is_sq_list(lst[k+2]):
        lst[k]=make_eqsys(lst[k+2][1:-1])
        lst[k+1]=''
        lst[k+2]=''
