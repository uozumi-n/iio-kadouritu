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
where python >nul 2>&1
if %errorlevel% equ 0 (
    set PYTHON_CMD=python
    for /f "tokens=*" %%i in ('python --version 2^>^&1') do set PYTHON_VERSION=%%i
    echo ✅ Python が見つかりました: !PYTHON_VERSION!
) else (
    where python3 >nul 2>&1
    if %errorlevel% equ 0 (
        set PYTHON_CMD=python3
        for /f "tokens=*" %%i in ('python3 --version 2^>^&1') do set PYTHON_VERSION=%%i
        echo ✅ Python3 が見つかりました: !PYTHON_VERSION!
    ) else (
        echo ❌ エラー: Python がインストールされていません
        echo.
        echo 以下のURLからPythonをインストールしてください:
        echo https://www.python.org/downloads/
        echo.
        echo インストール時は必ず「Add Python to PATH」にチェックを入れてください
        echo.
        pause
        exit /b 1
    )
)

echo.

:: 依存パッケージのチェックとインストール
echo 📦 依存パッケージをチェック中...
%PYTHON_CMD% -c "import streamlit" >nul 2>&1
if %errorlevel% neq 0 (
    echo ⚠️  Streamlit がインストールされていません
    echo 📥 依存パッケージをインストール中... ^(初回のみ、少し時間がかかります^)
    echo.

    %PYTHON_CMD% -m pip install -r requirements.txt

    if %errorlevel% equ 0 (
        echo.
        echo ✅ インストール完了！
    ) else (
        echo.
        echo ❌ エラー: インストールに失敗しました
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
%PYTHON_CMD% -m streamlit run app.py

:: アプリ終了後
echo.
echo 👋 アプリが終了しました
echo.
pause
