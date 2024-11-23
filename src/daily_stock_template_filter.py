import pandas as pd
import os
from datetime import datetime

class DailyStockTemplateFilter:
    def __init__(self, allstock: pd.DataFrame, allstock_info: pd.DataFrame, yesterday_allstock: pd.DataFrame = None):
        self.allstock = allstock
        self.allstock_info = allstock_info
        self.yesterday_allstock = yesterday_allstock
        if self.yesterday_allstock is not None:
            self.yesterday_allstock.set_index('ID', inplace=True)
        else:
            raise ValueError("Yesterday's stock data not exist.")

    def add_basic_stock_info(self):
        """
        Step 1: Add basic stock information like name and business volume.
        """
        intersect_index = []
        intersect_stock_ID = []
        for i, index in enumerate(self.allstock.index.values):
            index = str(index)
            if index.split('.')[0] in self.allstock_info.index:
                intersect_index.append(self.allstock.index.values[i])
                intersect_stock_ID.append(index.split('.')[0])

        self.allstock.loc[intersect_index, 'Name'] = self.allstock_info.loc[intersect_stock_ID, '有價證券名稱'].values
        self.allstock['business volume 50MA(百萬)'] = (self.allstock['Volume_50MA'] * self.allstock['Adj Close']) / 1_000_000
        self.allstock['business volume(億)'] = (self.allstock['Volume'] * self.allstock['Adj Close']) / 100_000_000
        self.allstock['year high sort'] = ((self.allstock['250Max'] - self.allstock['Adj Close']).abs() / self.allstock['250Max']) < 0.25
        self.allstock['year low sort'] = (self.allstock['Adj Close'] - self.allstock['250Min']) / self.allstock['250Min'] > 0.25

    def calculate_ma_strategies(self):
        """
        Step 2: Calculate moving average (MA) strategies.
        """
        ma_conditions = {
            'Price>20MA': self.allstock['Adj Close'] > self.allstock['20MA'],
            'Price>50MA': self.allstock['Adj Close'] > self.allstock['50MA'],
            'Price>150MA': self.allstock['Adj Close'] > self.allstock['150MA'],
            'Price>200MA': self.allstock['Adj Close'] > self.allstock['200MA'],
            # '200MA trending up 60d': self.allstock['200MA ROCP 60MA'] > 0,
            '50MA>150MA': self.allstock['50MA'] > self.allstock['150MA'],
            '50MA>200MA': self.allstock['50MA'] > self.allstock['200MA'],
            '150MA>200MA': self.allstock['150MA'] > self.allstock['200MA'],
            'price>95%50MA': self.allstock['Adj Close'] / self.allstock['50MA'] > 0.95,
            'price>110%50MA': self.allstock['Adj Close'] / self.allstock['50MA'] > 1.1,
        }
        for key, condition in ma_conditions.items():
            self.allstock[key] = condition

    def calculate_volume_strategies(self):
        """
        Step 3: Calculate volume-based strategies.
        """
        volume_conditions = {
            'Volume 50MA>150k': self.allstock['Volume_50MA'] > 150_000,
            'Volume 50MA>250k': self.allstock['Volume_50MA'] > 250_000,
            'business volume 50MA(百萬)>200': self.allstock['business volume 50MA(百萬)'] > 200,
        }
        for key, condition in volume_conditions.items():
            self.allstock[key] = condition

    def calculate_rs_strategies(self):
        """
        Step 4: Calculate RS and ERS strategies.
        """
        rs_conditions = {
            'RS 250rate>55': self.allstock['RS_rate_250'] > 55,
            'RS 250rate>80': self.allstock['RS_rate_250'] < 80,
            'RS 250rate<75': self.allstock['RS_rate_250'] < 75,
            
            'RS EMA250rate>60': self.allstock['ERS_rate_250'] > 60,
            'RS EMA250rate>75': self.allstock['ERS_rate_250'] > 75,
            'RS EMA250rate>80': self.allstock['ERS_rate_250'] > 80,
            'RS EMA250rate>85': self.allstock['ERS_rate_250'] > 85,
            'RS EMA250rate<80': self.allstock['ERS_rate_250'] < 80,
            'RS EMA50rate>75': self.allstock['ERS_rate_50'] > 75,
            'RS EMA50rate<95': self.allstock['ERS_rate_50'] < 95,
            'RS 20rate>80': self.allstock['RS_rate_20'] > 80,
            'RS EMA20rate>50': self.allstock['ERS_rate_20'] > 50,
            'RS EMA20rate>80': self.allstock['ERS_rate_20'] > 80,
            'RS EMA20rate<99': self.allstock['ERS_rate_20'] < 99,
        }
        for key, condition in rs_conditions.items():
            self.allstock[key] = condition

    def calculate_rs_diff_strategies(self):
        """
        Step 5: Calculate RS difference strategies.
        """
        if self.yesterday_allstock is not None:
            rs_diff_conditions = {
                'RS EMA20 diff': self.allstock['ERS_rate_20'] - self.yesterday_allstock['ERS_rate_20'],
                'RS EMA20 20MAX diff': self.allstock['ERS_rate_20'] - self.allstock['RS 20EMA 20MAX'],
            }
            for key, value in rs_diff_conditions.items():
                self.allstock[key] = value

            diff_conditions = {
                'RS EMA20diff < -5': self.allstock['RS EMA20 diff'] < -5,
                'RS EMA20diff < -8': self.allstock['RS EMA20 diff'] < -8,
                'RS EMA20diff < -11': self.allstock['RS EMA20 diff'] < -11,
                'RS EMA20 20MAX diff < -5': self.allstock['RS EMA20 20MAX diff'] < -5,
                'RS EMA20 20MAX diff < -10': self.allstock['RS EMA20 20MAX diff'] < -10,
                'RS EMA20 20MAX diff < -20': self.allstock['RS EMA20 20MAX diff'] < -20,
            }
            for key, condition in diff_conditions.items():
                self.allstock[key] = condition
        else:
            self.allstock[['RS EMA20 diff', 'RS EMA20 20MAX diff']] = 0
            self.allstock[['RS EMA20diff < -5', 'RS EMA20diff < -8', 'RS EMA20diff < -11',
                           'RS EMA20 20MAX diff < -5', 'RS EMA20 20MAX diff < -10',
                           'RS EMA20 20MAX diff < -20']] = False

    def calculate_atr_strategies(self):
        """
        Step 6: Calculate ATR-based strategies.
        """
        atr_conditions = {
            'ATR250/price': self.allstock['ATR_250'] / self.allstock['Adj Close'],
            'ATR50/price': self.allstock['ATR_50'] / self.allstock['Adj Close'],
            'ATR20/price': self.allstock['ATR_20'] / self.allstock['Adj Close'],
        }
        for key, value in atr_conditions.items():
            self.allstock[key] = value

        atr_conditions_binary = {
            'ATR250/price<0.03': self.allstock['ATR250/price'] < 0.03,
            'ATR250/price<0.5': self.allstock['ATR250/price'] < 0.15,
            'ATR50/price<0.03': self.allstock['ATR50/price'] < 0.03,
            'ATR20/price<0.03': self.allstock['ATR20/price'] < 0.03,
        }
        for key, condition in atr_conditions_binary.items():
            self.allstock[key] = condition
    def calculate_rs_maxmin_strategies(self):
        maxmin_binary = {
            'RS 250EMA 50MIN > 50': self.allstock['RS 250EMA 50MIN'] > 50,
            'RS 250EMA 50MIN > 30': self.allstock['RS 250EMA 50MIN'] > 30,
            'RS 50EMA 20MIN >30': self.allstock['RS 50EMA 20MIN'] > 30,
            'RS 50EMA 20MIN >65': self.allstock['RS 50EMA 20MIN'] > 65,
        }
        for key, condition in maxmin_binary.items():
            self.allstock[key] = condition

    def apply_templates(self):
        """
        Step 7: Apply all templates for final stock filtering.
        """
        self.allstock['T5'] = self.allstock[['RS 20rate>80', 'RS 250rate>55', 'RS 250rate<75', 'year low sort', 'year high sort', 'Volume 50MA>150k']].all(axis=1)
        self.allstock['T5-2'] = self.allstock[['RS EMA20rate>80', 'RS EMA250rate>60', 'RS EMA250rate<80', 'year low sort', 'year high sort', 'Volume 50MA>150k']].all(axis=1)
        self.allstock['T6'] = self.allstock[['RS EMA250rate>85', 'RS 250EMA 50MIN > 50', 'RS EMA50rate>75', 'Volume 50MA>250k']].all(axis=1)# , 'RS EMA50rate<95', 'RS 50EMA 20MIN >30'
        self.allstock['T11'] = self.allstock[['RS EMA250rate>75', 'RS 50EMA 20MIN >65', 'RS 250EMA 50MIN > 30', 'RS 20EMA is 10MAX', 'Volume 50MA>250k', 'price>95%50MA']].all(axis=1)
        self.allstock['T21'] = self.allstock[['RS EMA20rate>50', 'RS EMA250rate>85', 'RS EMA20 20MAX diff < -5', 'price>110%50MA', 'Volume 50MA>250k']].all(axis=1)
        self.allstock['TM'] = self.allstock[['Price>150MA', 'Price>200MA', 'year high sort', 'year low sort', 'RS 250rate>80', 'Volume 50MA>150k']].all(axis=1)#, '200MA trending up 60d'
        
        # 保留前 50 名T6
        t6_symbols = self.allstock[self.allstock['T6']].nlargest(50, 'ERS_rate_250').index
        self.allstock['T6'] = self.allstock.index.isin(t6_symbols)  

    def save_to_excel(self, output_directory: str, today: datetime):
        """
        Save the filtered stock data to a CSV file.
        """
        output_directory = os.path.join(output_directory, f"daily_stock_summary_{today}_with_template.xlsx")
        self.allstock.to_excel(output_directory, index=True)

    def run(self, output_directory: str, today: datetime):
        """
        Main method to run all the template filters.
        """
        print('Running Template Filter...')
        self.add_basic_stock_info()
        self.calculate_ma_strategies()
        self.calculate_volume_strategies()
        self.calculate_rs_strategies()
        self.calculate_rs_diff_strategies()
        self.calculate_atr_strategies()
        self.calculate_rs_maxmin_strategies()
        self.apply_templates()
        self.save_to_excel(output_directory, today)
        print('Template Filter DONE.')
        return self.allstock

# 使用示例
# template_filter = DailyStockTemplateFilter(allstock, allstock_info, yesterday_allstock)
# filtered_stock = template_filter.run()
