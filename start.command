#!/bin/bash

# 店舗予約データ集計アプリ起動スクリプト
# このファイルをダブルクリックするだけでアプリが起動します

echo "=========================================="
echo "  店舗予約データ集計アプリ v2.2"
echo "=========================================="
echo ""

# スクリプトのディレクトリに移動
cd "$(dirname "$0")"

echo "📂 現在のディレクトリ: $(pwd)"
echo ""

# Pythonのバージョン確認
echo "🔍 Python のバージョンを確認中..."
if command -v python3 &> /dev/null; then
    PYTHON_CMD=python3
    echo "✅ Python3 が見つかりました: $(python3 --version)"
elif command -v python &> /dev/null; then
    PYTHON_CMD=python
    echo "✅ Python が見つかりました: $(python --version)"
else
    echo "❌ エラー: Python がインストールされていません"
    echo ""
    echo "以下のURLからPythonをインストールしてください:"
    echo "https://www.python.org/downloads/"
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

    if command -v pip3 &> /dev/null; then
        pip3 install -r requirements.txt
    elif command -v pip &> /dev/null; then
        pip install -r requirements.txt
    else
        echo "❌ エラー: pip が見つかりません"
        read -p "Enterキーを押して終了..."
        exit 1
    fi

    if [ $? -eq 0 ]; then
        echo ""
        echo "✅ インストール完了！"
    else
        echo ""
        echo "❌ エラー: インストールに失敗しました"
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

# Streamlitアプリを起動
streamlit run app.py

# アプリ終了後
echo ""
echo "👋 アプリが終了しました"
echo ""
read -p "Enterキーを押してウィンドウを閉じる..."
