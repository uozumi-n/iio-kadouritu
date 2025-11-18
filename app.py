import streamlit as st
import pandas as pd
from datetime import datetime, timedelta, time
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

        # 人数制限フィルタリング
        st.subheader("👥 人数制限フィルタリング（オプション）")
        use_capacity_filter = st.checkbox(
            "人数制限で絞り込む",
            value=False,
            help="人数制限の条件に合うデータのみを集計対象にします"
        )

        capacity_min = None
        capacity_max = None

        if use_capacity_filter:
            # データから人数制限の範囲を取得
            all_capacities = df['人数制限'].dropna().unique()
            if len(all_capacities) > 0:
                min_cap = int(df['人数制限'].min())
                max_cap = int(df['人数制限'].max())

                col_cap1, col_cap2 = st.columns(2)
                with col_cap1:
                    capacity_min = st.number_input(
                        "最小人数",
                        min_value=min_cap,
                        max_value=max_cap,
                        value=min_cap,
                        step=1,
                        help="この人数以上の予約を集計対象にします"
                    )
                with col_cap2:
                    capacity_max = st.number_input(
                        "最大人数",
                        min_value=min_cap,
                        max_value=max_cap,
                        value=max_cap,
                        step=1,
                        help="この人数以下の予約を集計対象にします"
                    )

                if capacity_min > capacity_max:
                    st.error("⚠️ 最小人数は最大人数以下に設定してください")
                else:
                    st.info(f"👥 人数制限: {capacity_min}人〜{capacity_max}人の予約を集計")
            else:
                st.warning("⚠️ データに人数制限の情報が含まれていません")

        # 時間帯指定
        st.subheader("⏰ 集計時間帯の指定（オプション）")
        use_time_filter = st.checkbox(
            "時間帯を指定する（例：10時〜19時の稼働率を計算する場合）",
            value=False
        )

        time_start = None
        time_end = None
        operating_hours = None

        if use_time_filter:
            col_time1, col_time2 = st.columns(2)
            with col_time1:
                time_start = st.time_input(
                    "開始時刻",
                    value=time(10, 0),
                    help="集計対象とする開始時刻"
                )
            with col_time2:
                time_end = st.time_input(
                    "終了時刻",
                    value=time(19, 0),
                    help="集計対象とする終了時刻"
                )

            if time_start and time_end:
                # 営業時間数を計算
                start_minutes = time_start.hour * 60 + time_start.minute
                end_minutes = time_end.hour * 60 + time_end.minute
                operating_hours = (end_minutes - start_minutes) / 60

                if operating_hours <= 0:
                    st.error("⚠️ 終了時刻は開始時刻より後に設定してください")
                else:
                    st.info(f"📊 指定時間帯: {time_start.strftime('%H:%M')}〜{time_end.strftime('%H:%M')} （{operating_hours:.1f}時間）")

        # 店舗別リソース数設定
        st.subheader("🔧 店舗別リソース数設定（稼働率計算用・オプション）")
        use_utilization = st.checkbox(
            "リソース数を入力して稼働率を計算する",
            value=False,
            help="各店舗のリソース数（会議室数など）を入力すると稼働率が計算されます"
        )

        store_resources = {}
        if use_utilization:
            st.markdown("各店舗のリソース数を入力してください：")

            # 選択された店舗ごとにリソース数を入力
            cols_per_row = 3
            store_cols = st.columns(cols_per_row)

            for idx, store in enumerate(selected_stores):
                col_idx = idx % cols_per_row
                with store_cols[col_idx]:
                    resource_count = st.number_input(
                        f"{store}",
                        min_value=1,
                        max_value=100,
                        value=1,
                        step=1,
                        key=f"resource_{store}"
                    )
                    store_resources[store] = resource_count

            if use_time_filter and operating_hours and operating_hours > 0:
                st.info(f"💡 稼働率 = 実際の利用時間 ÷ (リソース数 × {operating_hours:.1f}時間 × 期間の日数) × 100%")
            else:
                st.info("💡 稼働率 = 実際の利用時間 ÷ (リソース数 × 24時間 × 期間の日数) × 100%")

        st.markdown("---")

        # 集計実行ボタン
        if st.button("🚀 集計実行", type="primary", use_container_width=True):
            if not selected_stores:
                st.error("⚠️ 店舗を選択してください")
            elif start_date > end_date:
                st.error("⚠️ 期間を正しく設定してください")
            elif use_time_filter and operating_hours and operating_hours <= 0:
                st.error("⚠️ 時間帯を正しく設定してください")
            elif use_capacity_filter and capacity_min is not None and capacity_max is not None and capacity_min > capacity_max:
                st.error("⚠️ 人数制限の範囲を正しく設定してください")
            else:
                # データフィルタリング
                filtered_df = df[
                    (df['開始日時'].dt.date >= start_date) &
                    (df['開始日時'].dt.date <= end_date) &
                    (df['店名'].isin(selected_stores))
                ].copy()

                # 人数制限でフィルタリング
                if use_capacity_filter and capacity_min is not None and capacity_max is not None:
                    filtered_df = filtered_df[
                        (filtered_df['人数制限'] >= capacity_min) &
                        (filtered_df['人数制限'] <= capacity_max)
                    ].copy()

                if len(filtered_df) == 0:
                    st.warning("⚠️ 指定した条件に該当するデータがありません")
                else:
                    # 時間帯フィルタリングと利用時間計算
                    if use_time_filter and time_start and time_end:
                        # 開始時刻と終了時刻を抽出
                        filtered_df['開始時刻'] = filtered_df['開始日時'].dt.time
                        filtered_df['終了時刻'] = filtered_df['終了日時'].dt.time

                        # 時間帯と重複する予約のみを抽出
                        # 予約が時間帯と少しでも重なっている場合を含む
                        mask = (
                            (filtered_df['開始時刻'] < time_end) &
                            (filtered_df['終了時刻'] > time_start)
                        )
                        filtered_df = filtered_df[mask].copy()

                        if len(filtered_df) == 0:
                            st.warning(f"⚠️ 指定した時間帯（{time_start.strftime('%H:%M')}〜{time_end.strftime('%H:%M')}）に該当するデータがありません")
                            st.stop()

                        # 指定時間帯との重複部分のみを計算
                        def calculate_overlap_hours(row):
                            # 予約の開始・終了時刻をdatetimeに変換
                            reservation_start = row['開始日時']
                            reservation_end = row['終了日時']

                            # 指定時間帯の開始・終了をdatetimeに変換（同じ日付で）
                            date = reservation_start.date()
                            filter_start = datetime.combine(date, time_start)
                            filter_end = datetime.combine(date, time_end)

                            # 予約が日をまたぐ場合の処理
                            if reservation_end.date() != date:
                                # 終了日の時間帯も考慮
                                filter_end_next = datetime.combine(reservation_end.date(), time_end)

                                # 1日目の重複計算
                                actual_start = max(reservation_start, filter_start)
                                actual_end = min(reservation_end, datetime.combine(date, time(23, 59, 59)))
                                hours_day1 = max(0, (actual_end - actual_start).total_seconds() / 3600)

                                # 2日目の重複計算
                                filter_start_next = datetime.combine(reservation_end.date(), time_start)
                                actual_start_day2 = max(reservation_start, filter_start_next)
                                actual_end_day2 = min(reservation_end, filter_end_next)
                                hours_day2 = max(0, (actual_end_day2 - actual_start_day2).total_seconds() / 3600)

                                return hours_day1 + hours_day2
                            else:
                                # 同じ日の場合：重複部分を計算
                                actual_start = max(reservation_start, filter_start)
                                actual_end = min(reservation_end, filter_end)

                                # 重複がある場合のみ時間を計算
                                if actual_start < actual_end:
                                    return (actual_end - actual_start).total_seconds() / 3600
                                else:
                                    return 0

                        # 各行に対して重複時間を計算
                        filtered_df['利用時間'] = filtered_df.apply(calculate_overlap_hours, axis=1)

                    else:
                        # 時間帯指定なしの場合：全時間を計算
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
                        合計時間_時間=('利用時間', 'sum')
                    ).reset_index()

                    # 列名を変更（時間単位を明確に）
                    result.rename(columns={'合計時間_時間': '合計時間（時間）'}, inplace=True)

                    # 合計時間を小数点第1位まで丸める
                    result['合計時間（時間）'] = result['合計時間（時間）'].round(1)

                    # 稼働率を計算
                    if use_utilization and store_resources:
                        # 期間の日数を計算
                        if aggregation_unit == '月次':
                            # 月次の場合、各月の日数を計算
                            def get_days_in_period(period_str):
                                year, month = period_str.split('-')
                                year, month = int(year), int(month)
                                # 翌月の1日の前日 = その月の最終日
                                if month == 12:
                                    next_month = datetime(year + 1, 1, 1)
                                else:
                                    next_month = datetime(year, month + 1, 1)
                                last_day = next_month - timedelta(days=1)
                                return last_day.day
                        else:
                            # 日別の場合は1日
                            def get_days_in_period(period_str):
                                return 1

                        # 稼働率列を追加
                        result['稼働率（%）'] = 0.0

                        for idx, row in result.iterrows():
                            store = row['店名']
                            period = row['期間']
                            actual_hours = row['合計時間（時間）']

                            if store in store_resources:
                                resource_count = store_resources[store]
                                days_in_period = get_days_in_period(period)

                                # 分母を計算
                                if use_time_filter and operating_hours and operating_hours > 0:
                                    # 時間帯指定がある場合
                                    total_capacity = resource_count * operating_hours * days_in_period
                                else:
                                    # 時間帯指定がない場合（24時間）
                                    total_capacity = resource_count * 24 * days_in_period

                                # 稼働率を計算
                                if total_capacity > 0:
                                    utilization_rate = (actual_hours / total_capacity) * 100
                                    result.at[idx, '稼働率（%）'] = round(utilization_rate, 1)

                    # 結果を表示
                    st.header("3️⃣ 集計結果")
                    st.success(f"✅ 集計完了！（{len(result)}件）")

                    # フィルタ条件の情報を表示
                    filter_info = []
                    if use_time_filter and time_start and time_end:
                        filter_info.append(f"⏰ 集計時間帯: {time_start.strftime('%H:%M')}〜{time_end.strftime('%H:%M')}")
                    if use_capacity_filter and capacity_min is not None and capacity_max is not None:
                        filter_info.append(f"👥 人数制限: {capacity_min}人〜{capacity_max}人")

                    if filter_info:
                        st.info(" / ".join(filter_info))

                    # 結果テーブル表示
                    st.dataframe(
                        result,
                        use_container_width=True,
                        hide_index=True
                    )

                    # 統計情報
                    if use_utilization and '稼働率（%）' in result.columns:
                        col1, col2, col3, col4 = st.columns(4)
                    else:
                        col1, col2, col3 = st.columns(3)

                    with col1:
                        st.metric("総利用件数", f"{result['利用件数合計'].sum():,}件")
                    with col2:
                        st.metric("総利用時間", f"{result['合計時間（時間）'].sum():.1f}時間")
                    with col3:
                        st.metric("対象店舗数", f"{len(selected_stores)}店舗")

                    if use_utilization and '稼働率（%）' in result.columns:
                        with col4:
                            avg_utilization = result['稼働率（%）'].mean()
                            st.metric("平均稼働率", f"{avg_utilization:.1f}%")

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

        ### 主な機能
        1. **期間選択**: カレンダーから集計期間を指定
        2. **店舗選択**: 複数店舗を選択可能
        3. **集計単位**: 月次または日別で集計
        4. **人数制限フィルタリング（オプション）**: 人数制限で絞り込み
           - 例：10人〜30人の会議室のみを集計対象にする
        5. **時間帯指定（オプション）**: 営業時間帯を指定して集計（例：10時〜19時）
           - 予約と時間帯の重複部分のみを集計します
           - 例：予約が9時〜11時、時間帯が10時〜19時の場合 → 10時〜11時の1時間を集計
        6. **稼働率計算（オプション）**: 店舗別リソース数を入力して稼働率を算出
        7. **重複除外**: Summary列の重複を除外してカウント
        8. **CSVダウンロード**: 集計結果をCSVファイルでダウンロード

        ### 稼働率について
        稼働率は以下の計算式で算出されます：

        **稼働率 = 実際の利用時間 ÷ (リソース数 × 営業時間 × 期間の日数) × 100%**

        - **時間帯指定なし**: 24時間で計算
        - **時間帯指定あり**: 指定した時間帯（例：10時〜19時 = 9時間）で計算

        例）月次集計、東京店、リソース数3、営業時間9時間、30日間の場合：
        - 分母 = 3 × 9 × 30 = 810時間
        - 実際の利用時間が100時間なら、稼働率 = 100 ÷ 810 × 100 = 12.3%
        """)

# フッター
st.markdown("---")
st.markdown(
    "<div style='text-align: center; color: gray;'>店舗予約データ集計アプリ v2.2</div>",
    unsafe_allow_html=True
)
