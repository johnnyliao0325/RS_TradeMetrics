import pandas as pd
import os


class StockDataUpdater:
    def __init__(self, base_path):
        """
        初始化類別，設定基礎路徑
        :param base_path: 資料根目錄
        """
        self.base_path = base_path
        self.category_paths = {
            'industry': os.path.join(base_path, "others", "產業別.xlsx"),
            'group': os.path.join(base_path, "others", "族群_複製.xlsx"),
            'concept': os.path.join(base_path, "others", "概念股_複製.xlsx"),
        }
        self.summary_path = os.path.join(base_path, "Stock_RS_rate_analysis", "100產業分析")

    def load_excel(self, file_path):
        """
        通用的 Excel 載入方法
        """
        try:
            return pd.read_excel(file_path)
        except Exception as e:
            print(f"Error loading file {file_path}: {e}")
            return None

    def update_daily_summary(self, day):
        """
        更新當日所有資料，包括產業、族群和概念股的 RS 和成交值排行
        """
        for category, path in self.category_paths.items():
            print(f"Updating {category} for {day}...")
            rs_file = f"{category}RS排行.xlsx"
            volume_file = f"{category}成交值排行.xlsx"
            self.update_category_data(day, category, rs_file, volume_file)

    def update_category_data(self, day, category, rs_file, volume_file):
        """
        更新單一類別資料（產業、族群或概念股）
        :param day: 當天日期
        :param category: 類別（industry/group/concept）
        :param rs_file: RS 排行檔名
        :param volume_file: 成交值排行檔名
        """
        category_path = self.category_paths.get(category)
        if not category_path:
            print(f"Invalid category: {category}")
            return

        category_df = self.load_excel(category_path)
        stock_file = os.path.join(self.base_path, "Stock_Data_Collector", "全個股條件篩選", f"{day}選股.xlsx")
        stock_df = self.load_excel(stock_file)

        if category_df is None or stock_df is None:
            print(f"Missing required files for {category}. Skipping update.")
            return

        # 排序並篩選前 20%
        stock_df = stock_df.sort_values(by='ES250rate', ascending=False).head(340)
        stock_ids = stock_df['ID'].astype(str)

        # 計算統計數據（RS）
        number_of_stocks = self._count_stocks_in_category(category_df)
        rs_data = self._map_and_calculate(category_df, stock_ids, number_of_stocks)

        # 更新 RS 排行歷史資料
        self._update_history(day, rs_data, os.path.join(self.summary_path, rs_file))

        # 計算統計數據（成交值）
        stock_df = stock_df.sort_values(by='busness volume(億)', ascending=False).head(340)
        volume_data = self._map_and_calculate(category_df, stock_ids, number_of_stocks)

        # 更新成交值排行歷史資料
        self._update_history(day, volume_data, os.path.join(self.summary_path, volume_file))

    def _count_stocks_in_category(self, category_df):
        """
        計算每個類別的股票數量
        """
        counts = []
        for col in category_df.columns:
            n = len(category_df.loc[category_df[col] != '0', col])
            counts.append([col, n])
        return pd.DataFrame(counts, columns=['category', 'number'])

    def _map_and_calculate(self, category_df, stock_ids, number_of_stocks):
        """
        將股票對應到類別，並計算統計數據
        """
        mappings = []
        for stock_id in stock_ids:
            for col in category_df.columns:
                if stock_id in category_df[col].values:
                    mappings.append([col, stock_id, 1])

        mapped_df = pd.DataFrame(mappings, columns=['category', 'ID', 'count'])
        stats = mapped_df.groupby('category').sum().sort_values(by='count', ascending=False)
        stats['all number'] = number_of_stocks.set_index('category').loc[stats.index, 'number'].values
        stats['percentage'] = (100 * stats['count'] / stats['all number']).round(1)
        return stats.transpose()

    def _update_history(self, day, daily_data, file_path):
        """
        更新歷史資料
        """
        history = self.load_excel(file_path)
        if history is None:
            print(f"Creating new history file at {file_path}")
            history = pd.DataFrame()

        try:
            history.drop(day, inplace=True)
        except KeyError:
            pass

        daily_data = pd.DataFrame(daily_data.loc['percentage']).transpose()
        daily_data.index = [day]
        updated_history = pd.concat([history, daily_data], axis=0).sort_index(ascending=False)
        updated_history.to_excel(file_path, index=True)
        print(f"Updated history: {file_path}")
