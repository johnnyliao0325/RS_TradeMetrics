import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime
import os
from typing import List
import time
from src.line_notifier import LineNotifier

class StockDataHandler:
    def __init__(self, data_dir: str, notifier: LineNotifier) -> None:
        self.data_dir = data_dir
        self.notifier = notifier
        if not os.path.exists(self.data_dir):
            os.makedirs(self.data_dir)

    def fetch_stock_data(self, symbols: List[str], start_date: datetime, end_date: datetime) -> pd.DataFrame:
        try:
            data = yf.download(symbols, start=start_date, end=end_date, group_by='ticker', auto_adjust=False)
            ## if data include 2 days, drop the first day
            if len(data) > 1:
                data = data.drop(data.index[0])
            print(data)
            return data
        except Exception as e:
            print(f"Error fetching data for {len(symbols)} symbols: {e}")
            return pd.DataFrame()

    def update_daily_data(self, symbols: List[str], rewrite = False, today = None, tomorrow = None) -> None:
        if today is None:
            today = datetime.now().date()
            tomorrow = today + pd.Timedelta(days=1)
        else:
            pass
        failed_symbols = []
        # Fetch data for all symbols at once to improve efficiency
        new_data = self.fetch_stock_data(symbols, today, tomorrow)
        if new_data.empty:
            if self.notifier is not None:
                self.notifier.send_message("Failed to fetch data for all symbols.")
            else:
                print("Failed to fetch data for all symbols.")
            failed_symbols = symbols
            self.retry_failed_symbols(failed_symbols, symbols, today, tomorrow, rewrite)
            return

        for symbol in symbols:
            if rewrite:
                self.rewrite_symbol_data(symbol, new_data, today, failed_symbols)
            else:
                self.update_symbol_data(symbol, new_data, today, failed_symbols)
        print(f"{len(failed_symbols)} failed symbols")
        # Retry failed symbols
        self.retry_failed_symbols(failed_symbols, symbols, today, tomorrow, rewrite)

    def load_existing_data(self, file_path: str) -> pd.DataFrame:
        if os.path.exists(file_path):
            return pd.read_csv(file_path, parse_dates=['Date'])
        else:
            return pd.DataFrame()

    def update_historical_data(self, symbols: List[str], start_date: datetime, end_date: datetime, rewrite = False ) -> None:
        failed_symbols = []

        # Fetch data for all symbols within the specified date range
        new_data = self.fetch_stock_data(symbols, start_date, end_date)
        if new_data.empty:
            if self.notifier is not None:
                self.notifier.send_message("Failed to fetch historical data for all symbols.")
            else:
                print("Failed to fetch historical data for all symbols.")
            return

        for symbol in symbols:
            if rewrite:
                self.rewrite_symbol_data(symbol, new_data, start_date, failed_symbols)
            else:
                self.update_symbol_data(symbol, new_data, start_date, failed_symbols)

        # Retry failed symbols
        self.retry_failed_symbols(failed_symbols, symbols, start_date, end_date, rewrite)
    def rewrite_symbol_data(self, symbol: str, new_data: pd.DataFrame, date: datetime, failed_symbols: List[str]) -> None:
        file_path = os.path.join(self.data_dir, f"{symbol}.csv")
        try:
            new_data[symbol] = new_data[symbol].dropna()
        except KeyError:
            print(f"KeyError: {symbol} data is empty.")
            failed_symbols.append(symbol)
            return

        if not os.path.exists(file_path):
            updated_data = new_data[symbol]
            updated_data = updated_data.assign(ID = symbol)
            new_data[symbol].to_csv(file_path, encoding='utf-8-sig')
            return
        existing_data = self.load_existing_data(file_path)
        # print(new_data[symbol])
        if not self.csv_format_check(existing_data):
            return
        
        if symbol in new_data.columns.get_level_values(0) and (not new_data[symbol].isna().values.any()):
            symbol_data = new_data[symbol].dropna().reset_index()
            symbol_data['ID'] = symbol

            if not existing_data.empty:
                # Merge only the OHLC data, keeping other columns in existing_data
                existing_data['Date'] = pd.to_datetime(existing_data['Date'], utc = True).dt.date
                existing_data = existing_data.set_index('Date')


                # 將日期轉換為 datetime.date 以進行比較
                symbol_data.index = pd.to_datetime(symbol_data.index).date
                date = pd.to_datetime(date).date()  # 將 date 變數也轉換為 datetime.date
                if len(symbol_data.index) > 1:
                    symbol_data['Date'] = pd.to_datetime(symbol_data['Date']).dt.date
                    symbol_data = symbol_data.set_index('Date')
                    updated_data = pd.concat([existing_data[~existing_data.index.isin(symbol_data.index)], symbol_data], axis=0)
                    # print(f"{symbol}: Muiti-historical Data rewrite successfully.")
                else:
                    # 檢查日期是否在 existing_data 中並刪除
                    # print(f"check {date} in existing data", existing_data.index[0], date)
                    if date in existing_data.index:
                        existing_data = existing_data.drop(date)
                        # print(f"repeat {date}, drop it and rewrite new data")

                    # 更新新數據
                    for column in ['Open', 'High', 'Low', 'Close', 'Adj Close', 'Volume', 'ID']:
                        existing_data.loc[date, column] = symbol_data[column].values[0]
                    # print(f"existing_data: {existing_data}, drop and rewrite new data")
                    # updated_data = pd.concat([existing_data[~existing_data.index.isin(symbol_data.index)], symbol_data], axis=0)

                    updated_data = existing_data
            else:
                updated_data = symbol_data.set_index('Date')
            updated_data = updated_data.sort_index(ascending=True)
            updated_data.to_csv(file_path, encoding='utf-8-sig')
            # print(f"{symbol}: Data rewrite successfully.")
        else:
            if symbol not in new_data.columns.get_level_values(0):
                print(f'{symbol} not in new data', sep=' | ')
            if new_data[symbol].isna().values.any():
                print(f'{symbol} data is empty.', sep=' | ')
            failed_symbols.append(symbol)
    def update_symbol_data(self, symbol: str, new_data: pd.DataFrame, date: datetime, failed_symbols: List[str]) -> None:
        file_path = os.path.join(self.data_dir, f"{symbol}.csv")

        new_data[symbol] = new_data[symbol].dropna()

        if not os.path.exists(file_path):
            updated_data = new_data[symbol]
            updated_data = updated_data.assign(ID = symbol)
            updated_data.to_csv(file_path, encoding='utf-8-sig')
            return
        existing_data = self.load_existing_data(file_path)
 
        if not self.csv_format_check(existing_data):
            return
        if symbol in new_data.columns.get_level_values(0) and not new_data[symbol].empty:
            symbol_data = new_data[symbol].dropna().reset_index()
            symbol_data['ID'] = symbol

            if not existing_data.empty:
                # Merge only the OHLC data, keeping other columns in existing_data
                existing_data['Date'] = pd.to_datetime(existing_data['Date'], utc = True).dt.date
                existing_data = existing_data.set_index('Date')


                # 將日期轉換為 datetime.date 以進行比較
                symbol_data.index = pd.to_datetime(symbol_data.index).date
                date = pd.to_datetime(date).date()  # 將 date 變數也轉換為 datetime.date
                if len(symbol_data.index) > 1:
                    symbol_data['Date'] = pd.to_datetime(symbol_data['Date']).dt.date
                    symbol_data = symbol_data.set_index('Date')
                    updated_data = pd.concat([existing_data, symbol_data[~symbol_data.index.isin(existing_data.index)]], axis=0)
                    # print(f"{symbol}: Muiti-historical Data updated successfully.")
                else:

                    # 檢查日期是否在 existing_data 中並跳過
                    if date in existing_data.index:
                        # print("repeat, pass")
                        pass
                    else:
                        # 更新新數據
                        try:
                            for column in ['Open', 'High', 'Low', 'Close', 'Adj Close', 'Volume', 'ID']:
                                existing_data.loc[date, column] = symbol_data[column].values[0]
                        except IndexError:
                            print(f"IndexError: {symbol} data is empty.")
                            failed_symbols.append(symbol)
                            return
                        # unexpected error
                        except Exception as e:
                            print(f"Error updating data for {symbol}: {e}")
                            failed_symbols.append(symbol)
                            return

                    updated_data = existing_data
            else:
                updated_data = symbol_data.set_index('Date')
            updated_data = updated_data.sort_index(ascending=True)
            updated_data.to_csv(file_path, encoding='utf-8-sig')
            # print(f"{symbol}: Data updated successfully.")
        else:
            if symbol not in new_data.columns.get_level_values(0):
                print(f'{symbol} not in new data', sep=' | ')
            if new_data[symbol].isna().values.any():
                print(f'{symbol} data is empty.', sep=' | ')
            print(f"{symbol} failed to update.")
            failed_symbols.append(symbol)
    def csv_format_check(self, existing_data: pd.DataFrame) -> bool:
        columns_check = 'Date' in existing_data.columns
        if columns_check:
            try:
                existing_data = existing_data.set_index('Date')
            except KeyError:
                return False
        index_type_check = type(existing_data.index) is pd.core.indexes.datetimes.DatetimeIndex
        # check 'Close' column can be converted to float
        try:
            close_type_check = existing_data['Close'].apply(lambda x: type(x) is float).all()
        except KeyError:
            close_type_check = False
        return all([index_type_check, close_type_check])

    def retry_failed_symbols(self, failed_symbols: List[str], symbols: List[str], start_date: datetime, end_date: datetime, rewrite = False) -> None:
        max_retries = 10
        if len(failed_symbols) == 0:
            return
        for retry in range(max_retries):
            if len(failed_symbols) == 0:
                break
            print(f"{retry+1} times retry. Start to retrying {len(failed_symbols)} failed symbols:")        
            retry_symbols = failed_symbols
            failed_symbols = []
            # split the retry_symbols into smaller chunks (2 symbols per chunk)
            for i in range(0, len(retry_symbols), 2):
                retry_symbols_chunk = retry_symbols[i:i+2]
                print(retry_symbols_chunk)
                new_data = self.fetch_stock_data(retry_symbols_chunk, start_date, end_date)
                if new_data.empty:
                    import numpy as np
                    failed_symbols.extend(np.array(retry_symbols_chunk).flatten().tolist())
                    print(f"Retry times: {retry + 1}. Failed to fetch data for {i}/{round(len(retry_symbols)/2, 0)} chumk")
                    continue
                else:
                    # print(f"Retry times: {retry + 1}. Fetch data successfully for {i}/{round(len(retry_symbols)/2, 0)} chumk")
                    print(new_data)
                for symbol in retry_symbols:
                    if rewrite:
                        self.rewrite_symbol_data(symbol, new_data, start_date, failed_symbols)
                    else:
                        self.update_symbol_data(symbol, new_data, start_date, failed_symbols)
        if failed_symbols:
            if self.notifier is not None:
                self.notifier.send_message(f"Failed to fetch data for {len(failed_symbols)}symbols after retries: {', '.join(failed_symbols)}")
            else:
                print(f"Failed to fetch data for {len(failed_symbols)}symbols after retries: {', '.join(failed_symbols)}")
    def fetch_stock_data_by_web(self, symbols: List[str], start_date: datetime, end_date: datetime) -> pd.DataFrame:
        # fetch data from yahoo finance by web
        pass


