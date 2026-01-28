import re

def flatten(lst, predicate=lambda x: True):
    """
    item がリストであり、かつ predicate(item) が True を返す場合のみ再帰的に平坦化する。
    それ以外（リストでないか、条件を満たさないリストの場合）はそのまま返す。
    """
    for item in lst:
        if isinstance(item, list) and predicate(item):
            yield from flatten(item, predicate)
        else:
            yield item

def join_flatten(lst, predicate=lambda x: True):
    """
    多重リストを平坦化し、空文字で結合した文字列を返す。
    """
    return "".join(flatten(lst, predicate))

def to_roman_lower(n):
    """
    数値を小文字のローマ数字に変換する (1-20まで対応)。
    範囲外の場合は数値を文字列として返す。
    """
    romans = [
        "", "i", "ii", "iii", "iv", "v", "vi", "vii", "viii", "ix", "x",
        "xi", "xii", "xiii", "xiv", "xv", "xvi", "xvii", "xviii", "xix", "xx"
    ]
    if 1 <= n <= 20:
        return romans[n]
    return str(n)

def split_list_at(lst, delimiter='\n'):
    """
    リストを指定されたデリミタで分割する。
    デリミタが見つかった箇所で区切り、デリミタ自体は分割されたチャンクの末尾に含める。
    Rubyの slice_after(delimiter) に相当。
    """
    result = []
    current = []
    for item in lst:
        current.append(item)
        if item == delimiter:
            result.append(current)
            current = []
    if current:
        result.append(current)
    return result

def split_list(lst, delimiter='\n'):
    """
    リストを指定されたデリミタで分割する。
    文字列の split() と同様に、デリミタ自体は破棄し、その前後で分割する。
    連続するデリミタや、先頭・末尾のデリミタに対しても空リストを生成する。
    """
    result = []
    current = []
    for item in lst:
        if item == delimiter:
            result.append(current)
            current = []
        else:
            current.append(item)
    result.append(current)
    return result

def is_sq_list(lst):
    return isinstance(lst, list) and lst[0]=='[' and lst[-1]==']'

def ruby_style_to_i(s):
    """
    Rubyの String#to_i の挙動をシミュレートする。
    先頭の空白を無視し、最初に見つかった数字の塊（符号付き）を整数として返す。
    数値として解釈できない場合は 0 を返す。

    注意: Rubyの to_i はASCII空白のみを飛ばすが、この関数は lstrip() を使用するため、
    全角スペースなどの Unicode 空白文字も読み飛ばす仕様としている。
    """
    s = str(s).lstrip()
    match = re.match(r'^([+-]?\d+)', s)
    if match:
        val_str = match.group(1)
        # Python 3.10.7以降、セキュリティ（DoS対策）のため、
        # 文字列から整数への変換にはデフォルトで4300桁の制限がある。
        # これを超えると ValueError になるため、事前に長さをチェックして回避する。
        if len(val_str) > 4300:
            return 0
        return int(val_str)
    return 0

def find_index(lst, predicate):
    """
    リストの中で条件（predicate）に合う最初の要素のインデックスを返す。
    predicate が関数の場合はその戻り値で、値（文字列等）の場合は内容の一致で判定する。
    見つからない場合は None を返す。
    """
    if not callable(predicate):
        target = predicate
        predicate = lambda x: x == target
    return next((i for i, x in enumerate(lst) if predicate(x)), None)

def find_last_index(lst, predicate):
    """
    リストの中で条件（predicate）に合う最後の要素のインデックスを返す。
    predicate が関数の場合はその戻り値で、値（文字列等）の場合は内容の一致で判定する。
    非破壊的に後ろから探索を行い、見つからない場合は None を返す。
    """
    if not callable(predicate):
        target = predicate
        predicate = lambda x: x == target
    n = len(lst)
    return next((n - 1 - i for i, x in enumerate(reversed(lst)) if predicate(x)), None)

def append_cr(text):
    """
    文字列の末尾に LaTeX の改行命令 \\\\ を追加する。
    末尾に改行コード（\\n, \\r, \\r\\n）がある場合は、その直前に挿入する。
    Ruby の str.sub(/$/, "\\\\\\\\") と同等の挙動。
    """
    return re.sub(r'(\r?\n?)$', r'\\\\\1', text, count=1)

def num_str(v):
    return isinstance(v, str) and re.match(r'[123456789]', v)

def is_matrix(v):
    return re.match(r'\\[bpvs]?matrix', v)
