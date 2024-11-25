import pandas as pd
import os
from datetime import datetime
from typing import List

class StockCategoryRSDataUpdater:
    def __init__(self, base_path: str):
        """
        初始化類別，設定基礎路徑
        Parameters:
            base_path: 主資料夾的基礎路徑 (ex: C:-Users-User-Desktop-stock)
        """

        self.base_path = base_path
        self.category_paths = {
            '100產業': os.path.join(base_path, "others", "產業別.xlsx"),
            '族群': os.path.join(base_path, "others", "族群_複製.xlsx"),
            '概念股': os.path.join(base_path, "others", "概念股_複製.xlsx"),
        }
        self.category_historical_data_paths = os.path.join(base_path, "100產業分析")
        

    def load_excel(self, file_path):
        """
        通用的 Excel 載入方法
        """
        try:
            return pd.read_excel(file_path)
        except Exception as e:
            print(f"Error loading file {file_path}: {e}")
            return None

    def update_stock_category_RS_data(self, day: datetime):
        """
        更新當日所有資料，包括產業、族群和概念股的 RS排行 和成交值排行
        """
        for category, path in self.category_paths.items():
            print(f"Updating {category} for {day}...")
            rs_file = os.path.join(self.category_historical_data_paths, f"{category}RS排行.xlsx")
            volume_file = os.path.join(self.category_historical_data_paths, f"{category}成交值排行.xlsx")
            self.update_category_data(day, category, rs_file, volume_file)

    def update_category_data(self, day: datetime, category: str, rs_file: str, volume_file: str):
        """
        更新單一類別資料（產業、族群或概念股）
        Parameters:
            day: 當天日期
            category: 類別 (industry/group/concept)
            rs_file: RS 排行檔名 (ex: C:-Users-User-Desktop-stock-100產業分析-industryRS排行.xlsx)
            volume_file: 成交值排行檔名 (ex: C:-Users-User-Desktop-stock-100產業分析-industry成交值排行.xlsx)
        """
        category_path = self.category_paths.get(category)
        if not category_path:
            print(f"Invalid category: {category}")
            return
        # 讀個股對應產業或族群或概念股的 Excel 檔案
        category_df = self.load_excel(category_path)
        # print(f'{category_path}\n: {category_df}')

        # 讀取當日選股summary
        stock_file = os.path.join(self.base_path, "全個股條件篩選", f"daily_stock_summary_{day.strftime('%Y-%m-%d')}_with_template.xlsx")
        stock_df = self.load_excel(stock_file)

        if category_df is None or stock_df is None:
            print(f"Missing required files for {category}. Skipping update.")
            return

        # 排序並篩選前 20%
        stock_rs_df = stock_df.loc[stock_df['ERS_rate_250'] > 80]
        stock_rs_ids = stock_rs_df['ID'].tolist()

        # 計算統計數據（RS）
        number_of_stocks = self._count_stocks_in_category(category_df)
        rs_data = self._map_and_calculate(category_df, stock_rs_ids, number_of_stocks)

        # 更新 RS 排行歷史資料
        self._update_history(day, rs_data, os.path.join(self.category_historical_data_paths, rs_file))

        # 計算統計數據（成交值）
        stock_volume_df = stock_df.sort_values(by='business volume(億)', ascending=False).head(340)
        stock_volume_ids = stock_volume_df['ID'].tolist()
        volume_data = self._map_and_calculate(category_df, stock_volume_ids, number_of_stocks)

        # 更新成交值排行歷史資料
        self._update_history(day, volume_data, os.path.join(self.category_historical_data_paths, volume_file))

    def _count_stocks_in_category(self, category_df: pd.DataFrame):
        """
        計算每個類別的股票數量

        Parameters:
            category_df: 個股對應產業或族群或概念股的 Excel 檔案 (ex: .../產業別.xlsx)

        Returns:
            pd.DataFrame: 包含類別名稱和股票數量的 DataFrame
        """
        counts = []
        # 計算每個類別的股票總數
        for col in category_df.columns:
            n = len(category_df.loc[category_df[col].astype(str) != '0', col])
            counts.append([col, n])
        return pd.DataFrame(counts, columns=['category', 'number'])

    def _map_and_calculate(self, category_df: pd.DataFrame, stock_ids: List[str] , number_of_stocks: pd.DataFrame):
        """
        將股票對應到類別，並計算統計數據

        Parameters:
            category_df: 個股對應產業或族群或概念股的 Excel 檔案 (ex: .../產業別.xlsx)
            stock_ids: ERS_rate_250或Volume_排行 > 80 的股票 ID 列表
            number_of_stocks: 包含類別名稱和股票數量的 DataFrame

        Returns:
            pd.DataFrame: 當日每個類別 ERS_rate_250 > 80 的股票數量百分比、總股票數量
        """
        mappings = []

        # 將股票對應到類別
        for stock_id in stock_ids:
            for col in category_df.columns:
                if stock_id.split('.')[0] in category_df[col].astype(str).values:
                    mappings.append([col, stock_id.split('.')[0], 1])
        

        # 計算每個類別 ERS_rate_250 > 80 的股票數量
        mapped_df = pd.DataFrame(mappings, columns=['category', 'ID', 'count'])
        stats = mapped_df.groupby('category').sum().sort_values(by='count', ascending=False)
        stats['all number'] = number_of_stocks.set_index('category').loc[stats.index, 'number'].values
        stats['percentage'] = (100 * stats['count'] / stats['all number']).round(1)
        return stats.transpose()

    def _update_history(self, day: datetime, daily_data: pd.DataFrame, file_path: str):
        """
        更新歷史資料

        Parameters:
            day: 當天日期
            daily_data: 當日每個類別 ERS_rate_250或Volume排行 > 80 的股票數量百分比、總股票數量
            file_path: Category ERS_rate_250或Volume > 80歷史資料檔案路徑 (ex: .../100產業分析/industryRS排行.xlsx)
        """
        history = pd.read_excel(file_path, header=0)

        if history is None:
            print(f"Creating new history file at {file_path}")
            history = pd.DataFrame()
        # 刪除空日期的行 (ex: histroy['Unamed: 0'] == 00:00:00)
        history = history.dropna(subset=['Unnamed: 0'])
        history.loc[1:, 'Unnamed: 0'] = history.loc[1:, 'Unnamed: 0'].apply(lambda x: x.split(' ')[0])
        history = history.set_index('Unnamed: 0')

        day = day.strftime('%Y-%m-%d')

        try:
            history.drop(day, inplace=True)
        except KeyError:
            pass

        daily_data = pd.DataFrame(daily_data.loc['percentage']).transpose()
        daily_data.index = [day]
        updated_history = pd.concat([history, daily_data], axis=0).sort_index(ascending=False)
        updated_history.to_excel(file_path, index=True)
