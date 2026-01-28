from . import mat, cases, eq
from . import enum_trans as enum

def trans_atom(lst):
    for v in lst:
        if isinstance(v, list):
            trans_atom(v)
    for k, v in enumerate(lst):
        if isinstance(v, str):
            mat.translate(lst,k)
            cases.translate(lst,k)

def trans_list(lst):
    eq.translate(lst)
    enum.translate(lst)
    return [trans_list(el) if isinstance(el, list) else el for el in lst]

def trans(lst):
    trans_atom(lst)
    return trans_list(lst)
