import talib
import numpy as np
import pandas as pd
import os

class IndicatorCalculator:
    def __init__(self, data_dir: str) -> None:
        self.data_directory = data_dir
        if not os.path.exists(self.data_directory):
            raise FileNotFoundError(f"Data directory {self.data_directory} not found.")

    def calculate_indicators(self, stock_symbol: str, existing_data: pd.DataFrame, allstock_info: pd.DataFrame, comparestock: pd.DataFrame) -> pd.DataFrame:
        if existing_data.empty:
            print(f"No data found for {stock_symbol} to calculate indicators.")
            return stock_symbol
        if not self.csv_format_check(existing_data):
            print(f"Data format for {stock_symbol} is incorrect.")
            return stock_symbol
        # Check if there are enough data points to calculate indicators
        min_data_points = 250  # The highest period needed for calculations
        existing_data = existing_data.dropna(subset=['Adj Close'])
        if len(existing_data.index.values) < min_data_points:
            print(f"Not enough data to calculate indicators for {stock_symbol}. Minimum {min_data_points} data points required.")
            return stock_symbol
        
        # Drop rows with column 'Adj Close' is NaN values
        # 產業別
        if stock_symbol not in ['^TWII', '0050.TW', '^TWOII']:
                existing_data['產業別'] = allstock_info.loc[existing_data['ID'].values[0].split('.')[0], '產業別']
        # Moving Averages
        existing_data['5MA'] = talib.SMA(existing_data["Adj Close"], 5)
        existing_data['10MA'] = talib.SMA(existing_data["Adj Close"], 10)
        existing_data['20MA'] = talib.SMA(existing_data["Adj Close"], 20)
        existing_data['50MA'] = talib.SMA(existing_data["Adj Close"], 50)
        existing_data['100MA'] = talib.SMA(existing_data["Adj Close"], 100)
        existing_data['150MA'] = talib.SMA(existing_data["Adj Close"], 150)
        existing_data['200MA'] = talib.SMA(existing_data["Adj Close"], 200)


        # Rate of Change Percentage
        existing_data['200MA_ROCP'] = talib.ROCP(existing_data["200MA"], timeperiod=1) * 100
        existing_data['200MA_ROCP_20MA'] = talib.SMA(existing_data["200MA_ROCP"], 20)
        existing_data['200MA_ROCP_60MA'] = talib.SMA(existing_data["200MA_ROCP"], 60)

        # High/Low Max/Min
        existing_data['5Max'] = talib.MAX(existing_data['High'], 5)
        existing_data['250Max'] = talib.MAX(existing_data['High'], 250)
        existing_data['5Min'] = talib.MIN(existing_data['Low'], 5)
        existing_data['250Min'] = talib.MIN(existing_data['Low'], 250)

        # Volume Moving Averages
        existing_data['Volume_5MA'] = talib.SMA(existing_data['Volume'], 5)
        existing_data['Volume_10MA'] = talib.SMA(existing_data['Volume'], 10)
        existing_data['Volume_20MA'] = talib.SMA(existing_data['Volume'], 20)
        existing_data['Volume_50MA'] = talib.SMA(existing_data['Volume'], 50)
        existing_data['Volume_10_Max'] = talib.MAX(existing_data['Volume'], 10)
        existing_data['Volume_20_Max'] = talib.MAX(existing_data['Volume'], 20)
        existing_data['Volume_50_Max'] = talib.MAX(existing_data['Volume'], 50)

        # Rate of Change (ROCP)
        existing_data['ROCP'] = talib.ROCP(existing_data["Adj Close"], timeperiod=1) * 100
        existing_data['OBV'] = talib.OBV(existing_data["Adj Close"], existing_data["Volume"])

        # Average True Range (ATR)
        existing_data['ATR_250'] = talib.ATR(existing_data['High'], existing_data['Low'], existing_data['Adj Close'], timeperiod=250)
        existing_data['ATR_50'] = talib.ATR(existing_data['High'], existing_data['Low'], existing_data['Adj Close'], timeperiod=50)
        existing_data['ATR_20'] = talib.ATR(existing_data['High'], existing_data['Low'], existing_data['Adj Close'], timeperiod=20)

        # Standard Deviation
        existing_data['STD_7'] = 100 * talib.STDDEV(existing_data["Adj Close"], timeperiod=7) / talib.EMA(existing_data["Adj Close"], 7)
        existing_data['STD_20'] = 100 * talib.STDDEV(existing_data["Adj Close"], timeperiod=20) / talib.EMA(existing_data["Adj Close"], 20)
        existing_data['STD_50'] = 100 * talib.STDDEV(existing_data["Adj Close"], timeperiod=50) / talib.EMA(existing_data["Adj Close"], 50)
        existing_data['STD_7_7MA'] = talib.SMA(existing_data['STD_7'], 7)

        # MACD
        existing_data['MACD'], existing_data['MACD_signal'], existing_data['MACD_hist'] = talib.MACD(existing_data["Adj Close"], fastperiod=12, slowperiod=26, signalperiod=9)

        # RSI
        existing_data['RSI'] = talib.RSI(existing_data["Adj Close"], timeperiod=14)

        # Stochastic Oscillator (KD)
        existing_data['slowk'], existing_data['slowd'] = talib.STOCH(existing_data['High'], existing_data['Low'], existing_data['Adj Close'],
                                                                     fastk_period=9, slowk_period=3, slowk_matype=0,
                                                                     slowd_period=3, slowd_matype=0)
    
        # RS value
        if stock_symbol not in ['^TWII', '0050.TW', '^TWOII']:
            comparestock_index = comparestock.index.map(lambda x: (x+pd.Timedelta(days=0)).strftime('%Y-%m-%d'))
            existing_data_index = existing_data.index.map(lambda x: x.strftime('%Y-%m-%d'))
            match_index = []
            for i in range(len(existing_data_index)):
                if existing_data_index[i] in comparestock_index:
                    match_index.append(i)
            match_index = existing_data.index[match_index]
            
            # 獲取 existing_data 和 comparestock 之間的日期交集

            if existing_data.index.duplicated().any():
                print("existing_data has duplicated index values.")
                return stock_symbol
            if len(match_index) > 0:
                pass
            else:
                print("No matching dates found between existing_data and comparestock.")
                return stock_symbol
            existing_data['RS value'] = 0
            existing_data['RS 250MA'] = 0
            existing_data['RS 50MA'] = 0
            existing_data['RS 20MA'] = 0
            existing_data['RS 250EMA'] = 0
            existing_data['RS 50EMA'] = 0
            existing_data['RS 20EMA'] = 0
            # print('existing data index -1', existing_data.index[-1], 'compar data index -1', comparestock.index[-1], 'match index -1', match_index[-1])
            # print(f'existing data index -1 type: {type(existing_data.index[-1])}, compar data index -1 type: {type(comparestock.index[-1])}, match index -1 type: {type(match_index[-1])}')
            # print(f'existing data match_index -1 ROCP: {existing_data.loc[match_index[-1], "ROCP"]}, comparestock match_index -1 ROCP: {comparestock.loc[match_index[-1], "ROCP"]}')
            if pd.isna(comparestock.loc[match_index[-1], "ROCP"]):
                print(f"comparestock.loc[match_index[-1], 'ROCP'] is NaN, {stock_symbol} failed to calculate RS value.")
                return stock_symbol
            try:
                existing_data.loc[match_index, 'RS value'] = list(map(lambda stock,compare: stock-compare, existing_data.loc[match_index, 'ROCP'], comparestock.loc[match_index, 'ROCP']))
                existing_data = existing_data.fillna(0)
                existing_data['RS 250MA'] = np.array(talib.SMA(existing_data['RS value'], 250))*100
                existing_data['RS 50MA'] = np.array(talib.SMA(existing_data['RS value'], 50))*100
                existing_data['RS 20MA'] = np.array(talib.SMA(existing_data['RS value'], 20))*100
                existing_data['RS 250EMA'] = np.array(talib.EMA(existing_data['RS value'], 250))*100
                existing_data['RS 50EMA'] = np.array(talib.EMA(existing_data['RS value'], 50))*100
                existing_data['RS 20EMA'] = np.array(talib.EMA(existing_data['RS value'], 20))*100
            except KeyError:
                print(f"KeyError: 'ROCP' column not found, {stock_symbol} failed to calculate RS value.")
                return stock_symbol
            except Exception as e:
                print(f"unexpected Error: {e}, {stock_symbol} failed to calculate RS value.")
                return stock_symbol
        else:
            existing_data.loc[:, 'RS value'] = 0
            existing_data.loc[:, 'RS 250MA'] = 0
            existing_data.loc[:, 'RS 50MA'] = 0
            existing_data.loc[:, 'RS 20MA'] = 0
            existing_data.loc[:, 'RS 250EMA'] = 0
            existing_data.loc[:, 'RS 50EMA'] = 0
            existing_data.loc[:, 'RS 20EMA'] = 0


        
        # Save updated DataFrame
        csv_file_path = os.path.join(self.data_directory, f"{stock_symbol}.csv")
        existing_data.to_csv(csv_file_path, encoding='utf-8-sig')
        print(f"Indicators for {stock_symbol} have been calculated and saved successfully.")

        return None

    def csv_format_check(self, existing_data: pd.DataFrame) -> bool:
            columns_check = 'Date' in existing_data.columns
            if columns_check:
                try:
                    existing_data = existing_data.set_index('Date')
                except KeyError:
                    print(f"KeyError: 'Date' column not found.")
                    return False
            index_type_check = type(existing_data.index) is pd.core.indexes.datetimes.DatetimeIndex
            # check 'Close' column can be converted to float
            try:
                close_type_check = existing_data['Close'].apply(lambda x: type(x) is float).all()
            except KeyError:
                print(f"KeyError: 'Close' column not found.")
                close_type_check = False
            # print(f"columns_check: {columns_check}, index_type_check: {index_type_check}, close_type_check: {close_type_check}")
            return all([index_type_check, close_type_check])