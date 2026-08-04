import os
import sys
import platform
import argparse
import subprocess
import configparser
from tef.tef import trans as tef_trans
from ens.ens_engine import trans as ens_trans
from ens.common import ENSError, detect_code

# chain.py のあるディレクトリとプロジェクトルートを特定
CHAIN_PY_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(os.path.dirname(CHAIN_PY_DIR))

# 設定の読み込み
config = configparser.ConfigParser()
config.read([
    os.path.join(CHAIN_PY_DIR, 'ens_config.ini'),
    os.path.join(PROJECT_ROOT, 'ens_config.ini'),
    os.path.join(os.getcwd(), 'ens_config.ini')
], encoding='utf-8')

PLATEX_PATH = config.get('paths', 'platex', fallback='platex')
DVIPDFMX_PATH = config.get('paths', 'dvipdfmx', fallback='dvipdfmx')
LUALATEX_PATH = config.get('paths', 'lualatex', fallback='lualatex')
STYLE_DIR = config.get('paths', 'style_dir', fallback=os.path.join(PROJECT_ROOT, 'stylefile'))
_system = platform.system()
if _system == "Darwin":
    _pdf_view_default = "open"
elif _system == "Linux":
    _pdf_view_default = "xdg-open"
else:
    _pdf_view_default = "start"
PDF_VIEW_COMMAND = config.get('commands', 'pdf_view', fallback=_pdf_view_default)

def read_file_text(path):
    """ファイルを適切なエンコーディングで読み込み、文字列として返す"""
    with open(path, 'rb') as f:
        enc = detect_code(f)
        return f.read().decode(enc)

def ens_to_tef(input_path, ruby_compat=False):
    """ENS ファイルを TEF ファイルに変換する"""
    if ens_trans is None:
        raise ImportError("Error: Could not find 'ens' package.")
    
    print(f"ens translater(2026/1/25)\n", flush=True)
    output_path = os.path.splitext(input_path)[0] + ".tef"
    try:
        content = read_file_text(input_path)
        # ens_engine.trans expects an iterable of lines
        result = ens_trans(content.splitlines(keepends=True), ruby_compat=ruby_compat)
    except ENSError as e:
        print(f"Error: {e}", flush=True)
        sys.exit(1)
    
    with open(output_path, 'w', encoding='utf-8', newline='') as f:
        f.write(result)
    
    print(f"Successfully transformed: {input_path} -> {output_path}\n", flush=True)
    return output_path

def tef_to_tex(input_path):
    """TEF ファイルを TeX ファイルに変換する"""
    if tef_trans is None:
        raise ImportError("Error: Could not find 'tef' package.")
    
    print(f"tef translater(2026/1/22)\n", flush=True)
    output_path = os.path.splitext(input_path)[0] + ".tex"
    
    try:
        content = read_file_text(input_path)
        result = tef_trans(content)
    except ENSError as e:
        print(f"Error: {e}", flush=True)
        sys.exit(1)
    
    with open(output_path, 'w', encoding='utf-8', newline='') as f:
        f.write(result)
    
    print(f"Successfully transformed: {input_path} -> {output_path}\n", flush=True)
    return output_path

def determine_latex_engine(tex_path):
    """エンコーディングを考慮して冒頭2行を読み取り、エンジンを判定する"""
    with open(tex_path, 'rb') as f:
        enc = detect_code(f)
        f.seek(0)
        # 冒頭2行を読み込む
        lines = []
        for _ in range(2):
            line = f.readline()
            if not line: break
            lines.append(line.decode(enc, errors='ignore'))
    
    is_luatex = False
    for line in lines:
        # % 以降（コメント）を除外してから ltjs を探す
        if "ltjs" in line.split('%')[0]:
            is_luatex = True
            break
    
    if is_luatex and enc != 'utf-8':
        print(f"Error: LuaLaTeX (ltjs*) detected, but file encoding is {enc}.", flush=True)
        print("LuaLaTeX requires UTF-8. Please save your file as UTF-8.", flush=True)
        sys.exit(1)
        
    return "lualatex" if is_luatex else "platex"

def tex_to_dvi(tex_path):
    """TeX ファイルを DVI ファイルに変換する"""
    print("") # LaTeX 出力の前に空行を挿入
    tex_abs = os.path.abspath(tex_path)
    tex_dir = os.path.dirname(tex_abs)
    tex_file = os.path.basename(tex_abs)
    dvi_file = os.path.splitext(tex_file)[0] + ".dvi"
    
    # スタイルファイルディレクトリの設定
    env = os.environ.copy()
    sep = os.pathsep
    env['TEXINPUTS'] = f".{sep}{STYLE_DIR}//{sep}{env.get('TEXINPUTS', '')}"
    
    print(f"Running platex: {tex_file} in {tex_dir}", flush=True)
    try:
        subprocess.run(
            [PLATEX_PATH, "-interaction=nonstopmode", tex_file],
            cwd=tex_dir,
            env=env,
            check=True
        )
        print("LaTeX compilation successful.", flush=True)
        return os.path.join(tex_dir, dvi_file)
    except subprocess.CalledProcessError as e:
        print(f"Error during LaTeX compilation (platex): {e}", flush=True)
        sys.exit(1)
    except FileNotFoundError:
        print(f"Error: platex not found at {PLATEX_PATH}", flush=True)
        sys.exit(1)

def tex_to_pdf_luatex(tex_path):
    """LuaLaTeX を呼び出し、直接 PDF を生成し、ビューアを開く"""
    print("", flush=True)
    tex_abs = os.path.abspath(tex_path)
    tex_dir = os.path.dirname(tex_abs)
    tex_file = os.path.basename(tex_abs)
    pdf_file = os.path.splitext(tex_file)[0] + ".pdf"
    
    env = os.environ.copy()
    sep = os.pathsep
    env['TEXINPUTS'] = f".{sep}{STYLE_DIR}//{sep}{env.get('TEXINPUTS', '')}"
    
    print(f"Running lualatex: {tex_file} in {tex_dir}", flush=True)
    try:
        subprocess.run(
            [LUALATEX_PATH, "-interaction=nonstopmode", tex_file],
            cwd=tex_dir,
            env=env,
            check=True
        )
        print("LuaLaTeX compilation successful.", flush=True)
        return os.path.join(tex_dir, pdf_file)
    except subprocess.CalledProcessError as e:
        print(f"Error during LuaLaTeX compilation: {e}", flush=True)
        sys.exit(1)
    except FileNotFoundError:
        print(f"Error: lualatex not found at {LUALATEX_PATH}", flush=True)
        sys.exit(1)

def dvi_to_pdf(dvi_path):
    """DVI ファイルを PDF ファイルに変換し、ビューアを開く"""
    print("") # dvipdfmx 出力の前に空行を挿入
    dvi_abs = os.path.abspath(dvi_path)
    dvi_dir = os.path.dirname(dvi_abs)
    dvi_file = os.path.basename(dvi_abs)
    pdf_file = os.path.splitext(dvi_file)[0] + ".pdf"
    
    print(f"Running dvipdfmx: {dvi_file} in {dvi_dir}", flush=True)
    try:
        subprocess.run(
            [DVIPDFMX_PATH, dvi_file],
            cwd=dvi_dir,
            check=True
        )
        print(f"PDF generation successful: {pdf_file}", flush=True)
        return os.path.join(dvi_dir, pdf_file)
    except subprocess.CalledProcessError as e:
        print(f"Error during PDF generation (dvipdfmx): {e}", flush=True)
        sys.exit(1)
    except FileNotFoundError:
        print(f"Error: dvipdfmx not found at {DVIPDFMX_PATH}", flush=True)
        sys.exit(1)

def main():
    parser = argparse.ArgumentParser(description="ENS -> TEF -> TeX -> DVI -> PDF chain processor.")
    parser.add_argument("input_file", help="Path to the input file (.ens, .tef, .tex, or .dvi)")
    parser.add_argument("--tef", action="store_true", help="Stop after .tef generation")
    parser.add_argument("--tex", action="store_true", help="Stop after .tex generation")
    parser.add_argument("--dvi", action="store_true", help="Stop after .dvi generation")
    parser.add_argument("--ruby-compat", action="store_true", help="Enable Ruby compatibility mode for ENS")

    if len(sys.argv) == 1:
        print("--- Current Configuration ---")
        print(f"  pLaTeX   : {PLATEX_PATH}")
        print(f"  LuaLaTeX : {LUALATEX_PATH}")
        print(f"  dvipdfmx : {DVIPDFMX_PATH}")
        print(f"  Style Dir: {STYLE_DIR}")
        print(f"  PDF View : {PDF_VIEW_COMMAND}")
        print(f"  ENS Path : {PROJECT_ROOT}")
        print("-----------------------------\n")
        parser.print_help()
        return

    args = parser.parse_args()

    input_path = args.input_file
    if not os.path.exists(input_path):
        print(f"Error: File not found: {input_path}", flush=True)
        sys.exit(1)

    _, ext = os.path.splitext(input_path.lower())
    
    current_file = input_path

    # フェーズ 1: ENS -> TEF
    if ext == ".ens":
        current_file = ens_to_tef(current_file, ruby_compat=args.ruby_compat)
        if args.tef: return
        ext = ".tef"

    # フェーズ 2: TEF -> TeX
    if ext == ".tef":
        current_file = tef_to_tex(current_file)
        if args.tex: return
        ext = ".tex"

    # フェーズ 3: TeX -> DVI (または LuaLaTeX による PDF 直接生成)
    if ext == ".tex":
        engine = determine_latex_engine(current_file)
        if engine == "lualatex":
            if args.dvi:
                print("Error: LuaLaTeX mode does not produce DVI files.", flush=True)
                sys.exit(1)
            current_file = tex_to_pdf_luatex(current_file)
            ext = ".pdf"
        else:
            current_file = tex_to_dvi(current_file)
            if args.dvi: return
            ext = ".dvi"

    # フェーズ 4: DVI -> PDF
    if ext == ".dvi":
        current_file = dvi_to_pdf(current_file)
        ext = ".pdf"
    
    # フェーズ 5: PDF を開く
    if ext == ".pdf":
        pdf_dir = os.path.dirname(os.path.abspath(current_file))
        pdf_file = os.path.basename(current_file)
        print(f"Opening PDF: {pdf_file}", flush=True)
        subprocess.run(f'{PDF_VIEW_COMMAND} {pdf_file}', shell=True, cwd=pdf_dir)

if __name__ == "__main__":
    main()
