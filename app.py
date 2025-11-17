import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import io

# ページ設定
st.set_page_config(
    page_title="店舗予約データ集計アプリ",
    page_icon="📊",
    layout="wide"
)

# タイトル
st.title("📊 店舗予約データ集計アプリ")
st.markdown("---")

# ファイルアップロード
st.header("1️⃣ CSVファイルをアップロード")
uploaded_file = st.file_uploader(
    "CSVファイルをドラッグ&ドロップまたは選択してください",
    type=['csv'],
    help="予約データのCSVファイルを選択してください"
)

if uploaded_file is not None:
    try:
        # CSVファイルを読み込み
        df = pd.read_csv(uploaded_file)

        # データプレビュー
        st.success(f"✅ ファイル読み込み完了！（{len(df)}件のデータ）")

        with st.expander("📋 データプレビュー（最初の10行）", expanded=True):
            st.dataframe(df.head(10), use_container_width=True)

        # 日時データの処理
        # 「2025-11-16, 23:15」形式をパース
        df['開始日時'] = pd.to_datetime(df['開始日時'], format='%Y-%m-%d, %H:%M', errors='coerce')
        df['終了日時'] = pd.to_datetime(df['終了日時'], format='%Y-%m-%d, %H:%M', errors='coerce')

        # 欠損値を除外
        df = df.dropna(subset=['開始日時', '終了日時'])

        # 期間データを取得
        min_date = df['開始日時'].min().date()
        max_date = df['開始日時'].max().date()

        st.markdown("---")
        st.header("2️⃣ 集計条件を選択")

        # 集計条件の設定
        col1, col2 = st.columns(2)

        with col1:
            st.subheader("📅 期間選択")
            start_date = st.date_input(
                "開始日",
                value=min_date,
                min_value=min_date,
                max_value=max_date
            )
            end_date = st.date_input(
                "終了日",
                value=max_date,
                min_value=min_date,
                max_value=max_date
            )

            if start_date > end_date:
                st.error("⚠️ 開始日は終了日より前に設定してください")

        with col2:
            st.subheader("🏪 店舗選択")

            # 全店舗リストを取得
            all_stores = sorted(df['店名'].unique().tolist())

            # 全選択ボタン
            if st.button("✅ 全店舗を選択"):
                st.session_state.selected_stores = all_stores

            # チェックボックスで店舗選択
            if 'selected_stores' not in st.session_state:
                st.session_state.selected_stores = all_stores

            selected_stores = st.multiselect(
                "店舗を選択（複数選択可）",
                options=all_stores,
                default=st.session_state.selected_stores,
                key='store_selector'
            )

        # 集計単位選択
        st.subheader("📊 集計単位")
        aggregation_unit = st.radio(
            "集計単位を選択",
            options=['月次', '日別'],
            horizontal=True
        )

        st.markdown("---")

        # 集計実行ボタン
        if st.button("🚀 集計実行", type="primary", use_container_width=True):
            if not selected_stores:
                st.error("⚠️ 店舗を選択してください")
            elif start_date > end_date:
                st.error("⚠️ 期間を正しく設定してください")
            else:
                # データフィルタリング
                filtered_df = df[
                    (df['開始日時'].dt.date >= start_date) &
                    (df['開始日時'].dt.date <= end_date) &
                    (df['店名'].isin(selected_stores))
                ].copy()

                if len(filtered_df) == 0:
                    st.warning("⚠️ 指定した条件に該当するデータがありません")
                else:
                    # 利用時間を計算（時間単位）
                    filtered_df['利用時間'] = (
                        filtered_df['終了日時'] - filtered_df['開始日時']
                    ).dt.total_seconds() / 3600

                    # 集計期間列を追加
                    if aggregation_unit == '月次':
                        filtered_df['期間'] = filtered_df['開始日時'].dt.strftime('%Y-%m')
                    else:  # 日別
                        filtered_df['期間'] = filtered_df['開始日時'].dt.strftime('%Y-%m-%d')

                    # Summary重複を除外してグループ化
                    # 同じ期間、店名、Summaryの組み合わせで重複を除外
                    unique_df = filtered_df.drop_duplicates(subset=['期間', '店名', 'Summary'])

                    # 集計
                    result = unique_df.groupby(['期間', '店名']).agg(
                        利用件数合計=('Summary', 'count'),
                        合計時間=('利用時間', 'sum')
                    ).reset_index()

                    # 合計時間を小数点第1位まで丸める
                    result['合計時間'] = result['合計時間'].round(1)

                    # 結果を表示
                    st.header("3️⃣ 集計結果")
                    st.success(f"✅ 集計完了！（{len(result)}件）")

                    # 結果テーブル表示
                    st.dataframe(
                        result,
                        use_container_width=True,
                        hide_index=True
                    )

                    # 統計情報
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.metric("総利用件数", f"{result['利用件数合計'].sum():,}件")
                    with col2:
                        st.metric("総利用時間", f"{result['合計時間'].sum():.1f}時間")
                    with col3:
                        st.metric("対象店舗数", f"{len(selected_stores)}店舗")

                    # CSVダウンロードボタン
                    st.markdown("---")

                    # CSVに変換
                    csv_buffer = io.StringIO()
                    result.to_csv(csv_buffer, index=False, encoding='utf-8-sig')
                    csv_data = csv_buffer.getvalue()

                    # ダウンロードボタン
                    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                    filename = f"reservation_summary_{timestamp}.csv"

                    st.download_button(
                        label="📥 CSVダウンロード",
                        data=csv_data,
                        file_name=filename,
                        mime='text/csv',
                        use_container_width=True
                    )

    except Exception as e:
        st.error(f"❌ エラーが発生しました: {str(e)}")
        st.info("CSVファイルの形式を確認してください")

else:
    st.info("👆 CSVファイルをアップロードしてください")

    # 使い方の説明
    with st.expander("📖 使い方"):
        st.markdown("""
        ### CSVファイルの形式
        以下の列を含むCSVファイルをアップロードしてください：

        - ID
        - Type
        - Resource Calendar Interface ID
        - Reservation Content ID
        - 開始日時（形式: `2025-11-16, 23:15`）
        - 終了日時（形式: `2025-11-16, 23:15`）
        - Summary
        - 店名
        - リソース名
        - タイプ
        - カテゴリ
        - 人数制限

        ### 機能
        1. **期間選択**: カレンダーから集計期間を指定
        2. **店舗選択**: 複数店舗を選択可能
        3. **集計単位**: 月次または日別で集計
        4. **重複除外**: Summary列の重複を除外してカウント
        5. **CSVダウンロード**: 集計結果をCSVファイルでダウンロード
        """)

# フッター
st.markdown("---")
st.markdown(
    "<div style='text-align: center; color: gray;'>店舗予約データ集計アプリ v1.0</div>",
    unsafe_allow_html=True
)
