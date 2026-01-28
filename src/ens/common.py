class ENSError(Exception):
    """ENS プロジェクト全般で使われる基盤の例外クラス"""
    pass

def detect_code(binary_stream):
    """
    バイナリモードのストリームを覗き見して、適切なエンコーディング名を返す。
    判別不能時は ENSError を発生させる。
    """
    preview = binary_stream.peek(2048)
    for enc in ["utf-8", "cp932", "euc-jp"]:
        try:
            preview.decode(enc)
            return enc
        except UnicodeDecodeError as e:
            # エラーの終了位置がバッファの末尾と一致している場合、
            # 覗き見バッファの境界でマルチバイト文字が切れただけと判断できる。
            if e.end == len(preview):
                return enc
            continue
        except UnicodeError:
            continue
    
    raise ENSError("Unsupported file encoding. (Tried UTF-8, CP932, EUC-JP)")
