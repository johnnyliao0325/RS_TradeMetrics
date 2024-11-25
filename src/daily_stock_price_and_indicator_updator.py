import yfinance as yf
import pandas as pd
import talib
import numpy as np
import os
from datetime import datetime
from typing import List
from src.line_notifier import LineNotifier

class StockDataHandlerWithIndicators:
    def __init__(self, data_dir: str, notifier: LineNotifier) -> None:
        self.data_dir = data_dir
        self.notifier = notifier
        if not os.path.exists(self.data_dir):
            os.makedirs(self.data_dir)

    def update_and_calculate_indicators(self, symbols: List[str], start_date: datetime, end_date: datetime, rewrite=False) -> None:
        today = datetime.now().date()
        tomorrow = today + pd.Timedelta(days=1)
        failed_symbols = []

        # Fetch new data for all symbols
        new_data = self._fetch_stock_data(symbols, start_date, end_date)
        if new_data.empty:
            self.notifier.send_message("Failed to fetch data for all symbols.")
            failed_symbols = symbols
            self._retry_failed_symbols(failed_symbols, symbols, start_date, end_date, rewrite)
            return

        # Process each symbol
        for symbol in symbols:
            try:
                # Read the existing data from CSV
                file_path = os.path.join(self.data_dir, f"{symbol}.csv")
                existing_data = self._load_existing_data(file_path)

                # Update the stock data
                updated_data = self._update_stock_data(symbol, new_data, existing_data, today, rewrite)

                # Calculate indicators
                updated_data = self._calculate_indicators(symbol, updated_data)

                # Write the updated data back to CSV
                updated_data.to_csv(file_path, encoding='utf-8-sig')
                print(f"{symbol}: Data updated and indicators calculated successfully.")

            except Exception as e:
                print(f"Failed to process {symbol}: {e}")
                failed_symbols.append(symbol)

        # Retry failed symbols if necessary
        self._retry_failed_symbols(failed_symbols, symbols, start_date, end_date, rewrite)

    def _fetch_stock_data(self, symbols: List[str], start_date: datetime, end_date: datetime) -> pd.DataFrame:
        try:
            data = yf.download(symbols, start=start_date, end=end_date, group_by='ticker')
            return data
        except Exception as e:
            print(f"Error fetching data for {symbols}: {e}")
            return pd.DataFrame()

    def _load_existing_data(self, file_path: str) -> pd.DataFrame:
        if os.path.exists(file_path):
            return pd.read_csv(file_path, parse_dates=['Date'])
        else:
            return pd.DataFrame()

    def _update_stock_data(self, symbol: str, new_data: pd.DataFrame, existing_data: pd.DataFrame, date: datetime, rewrite: bool) -> pd.DataFrame:
        if symbol not in new_data.columns.get_level_values(0):
            raise ValueError(f"{symbol} not found in new data.")

        # Drop NA values from the new data
        new_data[symbol] = new_data[symbol].dropna()

        if rewrite or existing_data.empty:
            updated_data = new_data[symbol].reset_index()
            updated_data['ID'] = symbol
            return updated_data.set_index('Date')

        # Merge new data with existing data
        existing_data = existing_data.set_index('Date')
        new_symbol_data = new_data[symbol].reset_index()
        new_symbol_data['ID'] = symbol
        new_symbol_data = new_symbol_data.set_index('Date')

        updated_data = pd.concat([existing_data, new_symbol_data[~new_symbol_data.index.isin(existing_data.index)]], axis=0)
        return updated_data.sort_index(ascending=True)

    def _calculate_indicators(self, stock_symbol: str, data: pd.DataFrame) -> pd.DataFrame:
        if data.empty:
            raise ValueError(f"No data found for {stock_symbol} to calculate indicators.")

        # Drop rows where 'Adj Close' is NaN
        data = data.dropna(subset=['Adj Close'])

        # Calculate indicators using talib
        data['5MA'] = talib.SMA(data["Adj Close"], 5)
        data['10MA'] = talib.SMA(data["Adj Close"], 10)
        data['20MA'] = talib.SMA(data["Adj Close"], 20)
        data['50MA'] = talib.SMA(data["Adj Close"], 50)
        data['100MA'] = talib.SMA(data["Adj Close"], 100)
        data['150MA'] = talib.SMA(data["Adj Close"], 150)
        data['200MA'] = talib.SMA(data["Adj Close"], 200)

        # More indicators can be added similarly
        return data

    def _retry_failed_symbols(self, failed_symbols: List[str], symbols: List[str], start_date: datetime, end_date: datetime, rewrite=False) -> None:
        max_retries = 3
        for retry in range(max_retries):
            if not failed_symbols:
                break
            print(f"Retrying failed symbols: Attempt {retry + 1}")
            retry_symbols = failed_symbols
            failed_symbols = []

            # Re-fetch data for failed symbols
            new_data = self._fetch_stock_data(retry_symbols, start_date, end_date)
            if new_data.empty:
                failed_symbols = retry_symbols
                continue

            # Retry updating and calculating indicators
            for symbol in retry_symbols:
                try:
                    file_path = os.path.join(self.data_dir, f"{symbol}.csv")
                    existing_data = self._load_existing_data(file_path)
                    updated_data = self._update_stock_data(symbol, new_data, existing_data, start_date, rewrite)
                    updated_data = self._calculate_indicators(symbol, updated_data)
                    updated_data.to_csv(file_path, encoding='utf-8-sig')
                    print(f"{symbol}: Data reprocessed successfully on retry.")
                except Exception as e:
                    print(f"Retry failed for {symbol}: {e}")
                    failed_symbols.append(symbol)

        if failed_symbols:
            self.notifier.send_message(f"Failed to fetch data for symbols after retries: {', '.join(failed_symbols)}")

