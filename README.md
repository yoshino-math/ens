# ENS (Educational Notation System) セットアップガイド

このツールは、独自の簡潔な記法（`.ens`）や中間形式（`.tef`）から LaTeX を経由して PDF を生成するシステムです。

## 1. 準備するもの
- **Python 3.8 以上**
- **TeX 環境**（`platex`/`lualatex` が使える状態）

## 2. インストール
配布された ZIP ファイルを好きな場所に展開してください。
**`pip install` 等のインストール作業は不要です。**

## 3. 使い方（基本）
ファイルを引数に渡して実行します。

- **ENS ファイルから PDF を生成する**

  Windows:
  ```batch
  chain.bat sample.ens
  ```
  macOS:
  ```sh
  chmod +x chain.sh  # 初回のみ
  ./chain.sh sample.ens
  ```

- **TEF ファイルから PDF を生成する**

  Windows:
  ```batch
  chain.bat sample.tef
  ```
  macOS:
  ```sh
  ./chain.sh sample.tef
  ```

  ※ その他、`.tex` や `.dvi` ファイルを渡して、その後の工程（PDF化など）だけを行うことも可能です。

## 4. 便利なオプション
特定の段階で処理を止めたい場合に使用します。
- `--tef`: `.tef` ファイルへの変換（ENSのみ）までで止める
- `--tex`: `.tex` ファイルの生成（TEF変換）までで止める
- `--dvi`: `.dvi` ファイルの生成（LaTeXコンパイル）までで止める

使用例：

Windows:
```batch
chain.bat sample.ens --tef
```
macOS:
```sh
./chain.sh sample.ens --tef
```

## 5. 設定の変更 (`ens_config.ini`)
フォルダ直下の `ens_config.ini` を編集することで、以下のカスタマイズが可能です。
- **TeX パス**: 自動で見つからない（PATHが通っていない）場合は、フルパスを指定してください。
- **PDF ビューア**: PDF 生成後に自動で開くコマンドを変更できます。OS に応じて自動選択されます（Windows: `start`、macOS: `open`）。特定のアプリを指定したい場合のみ設定してください。
- **スタイルファイル**: 標準以外のパスにあるスタイルファイルを使用したい場合に指定できます。

## 6. 動作確認とヘルプ
引数なしで実行すると、「現在の設定状況」と「詳しい使いかた（ヘルプ）」が表示されます。

Windows:
```batch
chain.bat
```
macOS:
```sh
./chain.sh
```
もし「コマンドが見つからない」等のエラーが出る場合は、表示される各コンパイラのパスが正しいか確認してください。

---
## 開発・配布上の注意
このパッケージは、展開したフォルダの `src/` を直接参照する「ポータブル構成」になっています。
`src/` フォルダを移動したり名前を変えたりすると動作しなくなりますのでご注意ください。
