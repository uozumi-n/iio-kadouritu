@echo off
chcp 65001 > nul
setlocal enabledelayedexpansion

:: 店舗予約データ集計アプリ起動スクリプト (Windows用)
:: このファイルをダブルクリックするだけでアプリが起動します

cls
echo ==========================================
echo   店舗予約データ集計アプリ v3.0
echo ==========================================
echo.

:: スクリプトのディレクトリに移動
cd /d "%~dp0"

echo 📂 現在のディレクトリ: %CD%
echo.

:: Pythonのバージョン確認
echo 🔍 Python のバージョンを確認中...

set PYTHON_CMD=
set PYTHON_VERSION=

:: まずpythonコマンドを確認
where python >nul 2>&1
if !errorlevel! equ 0 (
    set PYTHON_CMD=python
    for /f "tokens=*" %%i in ('python --version 2^>^&1') do set PYTHON_VERSION=%%i
    echo ✅ Python が見つかりました: !PYTHON_VERSION!
    goto :python_found
)

:: 次にpython3コマンドを確認
where python3 >nul 2>&1
if !errorlevel! equ 0 (
    set PYTHON_CMD=python3
    for /f "tokens=*" %%i in ('python3 --version 2^>^&1') do set PYTHON_VERSION=%%i
    echo ✅ Python3 が見つかりました: !PYTHON_VERSION!
    goto :python_found
)

:: よくあるインストールパスを直接確認
set "COMMON_PATHS=%LOCALAPPDATA%\Programs\Python\Python312\python.exe;%LOCALAPPDATA%\Programs\Python\Python311\python.exe;%LOCALAPPDATA%\Programs\Python\Python310\python.exe;%LOCALAPPDATA%\Programs\Python\Python39\python.exe;C:\Python312\python.exe;C:\Python311\python.exe;C:\Python310\python.exe;C:\Python39\python.exe"

for %%p in ("%COMMON_PATHS:;=" "%") do (
    if exist %%~p (
        set "PYTHON_CMD=%%~p"
        for /f "tokens=*" %%i in ('"%%~p" --version 2^>^&1') do set PYTHON_VERSION=%%i
        echo ✅ Python が見つかりました: !PYTHON_VERSION!
        echo    場所: %%~p
        goto :python_found
    )
)

:: Pythonが見つからなかった場合
echo ❌ エラー: Python がインストールされていません
echo.
echo 以下のURLからPythonをインストールしてください:
echo https://www.python.org/downloads/
echo.
echo インストール時は必ず「Add Python to PATH」にチェックを入れてください
echo.
echo ※ 管理者権限で実行している場合は、通常モードで再実行してみてください
echo.
pause
exit /b 1

:python_found

echo.

:: 依存パッケージのチェックとインストール
echo 📦 依存パッケージをチェック中...
"!PYTHON_CMD!" -c "import streamlit" >nul 2>&1
if !errorlevel! neq 0 (
    echo ⚠️  Streamlit がインストールされていません
    echo 📥 依存パッケージをインストール中... ^(初回のみ、少し時間がかかります^)
    echo.

    "!PYTHON_CMD!" -m pip install -r requirements.txt
    set INSTALL_RESULT=!errorlevel!

    if !INSTALL_RESULT! equ 0 (
        echo.
        echo ✅ インストール完了！
    ) else (
        echo.
        echo ❌ エラー: インストールに失敗しました
        echo    エラーコード: !INSTALL_RESULT!
        pause
        exit /b 1
    )
) else (
    echo ✅ 依存パッケージは既にインストールされています
)

echo.
echo ==========================================
echo 🚀 アプリを起動しています...
echo ==========================================
echo.
echo 💡 ブラウザが自動的に開きます
echo    開かない場合は以下のURLにアクセスしてください:
echo    http://localhost:8501
echo.
echo ⚠️  アプリを終了するには:
echo    このウィンドウを閉じてください
echo.
echo ==========================================
echo.

:: Streamlitアプリを起動
"!PYTHON_CMD!" -m streamlit run app.py

:: アプリ終了後
echo.
echo 👋 アプリが終了しました
echo.
pause
