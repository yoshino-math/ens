from .parse import parse
from .trans import trans as trans_lst
from .utils import join_flatten


def trans(utf_string):
    return join_flatten(trans_lst(parse(utf_string)))



def main():
    str=r"""
\[ ::[
f(x)=\matrix[1,2,3,4] [$x>0$]
] \]
"""
    print(trans(str))


if __name__ == "__main__":
    main()


