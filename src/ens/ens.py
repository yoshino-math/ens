import sys
import io
from .ens_engine import trans
from .common import ENSError, detect_code

def error(msg):
    print(f'ENS Error: {msg}')
    exit(1)


def wrap_text_stream(binary_stream):
    """
    適切なエンコーディングの TextIOWrapper を生成して返す。
    """
    enc = detect_code(binary_stream)
    return io.TextIOWrapper(binary_stream, encoding=enc, newline='')

def main_trans(file, ruby_compat=False):
    with open(file, "rb") as f_bin:
        try:
            result = trans(wrap_text_stream(f_bin), ruby_compat=ruby_compat)
        except ENSError as e:
            error(e)
        return result

def main():
    args = sys.argv[1:]
    ruby_compat = False
    if "--ruby-compat" in args:
        ruby_compat = True
        args.remove("--ruby-compat")

    if not args:
        print(f"Usage: ens [--ruby-compat] <filename>")
        exit(1)
    target_file = args[0]
    print(main_trans(target_file, ruby_compat=ruby_compat), end='')

if __name__ == "__main__":
    main()
