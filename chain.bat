@echo off
setlocal

:: --- 設定エリア ---
:: pythonの実行ファイルを設定してください. (ver3.8以上)
set PYTHON=python

:: ensを置いた場所を設定してください. (chain.batと同じ場所なら, %~dp0としてください)
set ENS_PATH=%~dp0
rem set ENS_PATH=c:/path/to/ens
:: ------------------

:: Python の検索パス (PYTHONPATH) に、ENS のソースコードが入っている src フォルダを追加します。
set PYTHONPATH=%ENS_PATH%src;%PYTHONPATH%

:: ens パッケージの chain モジュールを実行します。
"%PYTHON%" -m ens.chain %*
if %ERRORLEVEL% neq 0 exit /b %ERRORLEVEL%

endlocal
