#!/bin/bash

# 店舗予約データ集計アプリ起動スクリプト
# このファイルをダブルクリックするだけでアプリが起動します

echo "=========================================="
echo "  店舗予約データ集計アプリ v3.1"
echo "=========================================="
echo ""

# スクリプトのディレクトリに移動
cd "$(dirname "$0")"

echo "📂 現在のディレクトリ: $(pwd)"
echo ""

# ===========================================
# Mac特有のPATH問題を解決
# ダブルクリック起動時は .zshrc/.bash_profile が読み込まれないため
# 一般的なPythonインストール先を手動でPATHに追加
# ===========================================

# Homebrew (Apple Silicon)
if [ -d "/opt/homebrew/bin" ]; then
    export PATH="/opt/homebrew/bin:$PATH"
fi

# Homebrew (Intel Mac)
if [ -d "/usr/local/bin" ]; then
    export PATH="/usr/local/bin:$PATH"
fi

# Python.org公式インストーラのデフォルトパス
if [ -d "/Library/Frameworks/Python.framework/Versions/Current/bin" ]; then
    export PATH="/Library/Frameworks/Python.framework/Versions/Current/bin:$PATH"
fi

# pyenv
if [ -d "$HOME/.pyenv/shims" ]; then
    export PATH="$HOME/.pyenv/shims:$PATH"
fi

# ユーザーローカルのpip
if [ -d "$HOME/Library/Python/3.9/bin" ]; then
    export PATH="$HOME/Library/Python/3.9/bin:$PATH"
fi
if [ -d "$HOME/Library/Python/3.10/bin" ]; then
    export PATH="$HOME/Library/Python/3.10/bin:$PATH"
fi
if [ -d "$HOME/Library/Python/3.11/bin" ]; then
    export PATH="$HOME/Library/Python/3.11/bin:$PATH"
fi
if [ -d "$HOME/Library/Python/3.12/bin" ]; then
    export PATH="$HOME/Library/Python/3.12/bin:$PATH"
fi

# Pythonのバージョン確認
echo "🔍 Python のバージョンを確認中..."
PYTHON_CMD=""

# python3を優先して探す
if command -v python3 &> /dev/null; then
    PYTHON_CMD=python3
    echo "✅ Python3 が見つかりました: $(python3 --version)"
elif command -v python &> /dev/null; then
    # pythonがPython 3かどうか確認
    PYTHON_VERSION=$(python --version 2>&1)
    if [[ "$PYTHON_VERSION" == *"Python 3"* ]]; then
        PYTHON_CMD=python
        echo "✅ Python が見つかりました: $PYTHON_VERSION"
    fi
fi

if [ -z "$PYTHON_CMD" ]; then
    echo "❌ エラー: Python 3 がインストールされていません"
    echo ""
    echo "=========================================="
    echo "📥 Pythonのインストール方法"
    echo "=========================================="
    echo ""
    echo "以下のURLからPythonをダウンロードしてインストールしてください:"
    echo ""
    echo "  https://www.python.org/downloads/"
    echo ""
    echo "1. 上記URLにアクセス"
    echo "2. 「Download Python 3.x.x」ボタンをクリック"
    echo "3. ダウンロードした .pkg ファイルをダブルクリック"
    echo "4. 画面の指示に従ってインストール"
    echo "5. インストール完了後、このアプリを再度起動"
    echo ""
    echo "=========================================="
    echo ""
    read -p "Enterキーを押して終了..."
    exit 1
fi

echo ""

# 依存パッケージのチェックとインストール
echo "📦 依存パッケージをチェック中..."
if ! $PYTHON_CMD -c "import streamlit" &> /dev/null; then
    echo "⚠️  Streamlit がインストールされていません"
    echo "📥 依存パッケージをインストール中... (初回のみ、少し時間がかかります)"
    echo ""

    # python -m pip を使用してPATH問題を回避
    $PYTHON_CMD -m pip install -r requirements.txt

    if [ $? -eq 0 ]; then
        echo ""
        echo "✅ インストール完了！"
    else
        echo ""
        echo "❌ エラー: インストールに失敗しました"
        echo ""
        echo "以下を試してください:"
        echo "1. インターネット接続を確認"
        echo "2. Pythonを再インストール"
        echo ""
        read -p "Enterキーを押して終了..."
        exit 1
    fi
else
    echo "✅ 依存パッケージは既にインストールされています"
fi

echo ""
echo "=========================================="
echo "🚀 アプリを起動しています..."
echo "=========================================="
echo ""
echo "💡 ブラウザが自動的に開きます"
echo "   開かない場合は以下のURLにアクセスしてください:"
echo "   http://localhost:8501"
echo ""
echo "⚠️  アプリを終了するには:"
echo "   このターミナルウィンドウで Control+C を押すか"
echo "   ターミナルを閉じてください"
echo ""
echo "=========================================="
echo ""

# Streamlitアプリを起動 (python -m streamlit を使用してPATH問題を回避)
$PYTHON_CMD -m streamlit run app.py

# アプリ終了後
echo ""
echo "👋 アプリが終了しました"
echo ""
read -p "Enterキーを押してウィンドウを閉じる..."
