import unittest
from unittest.mock import patch, MagicMock
from datetime import datetime
import pandas as pd
import os
import sys

# 將專案根目錄加入系統路徑，這樣可以找到 src 模組
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.stock_data_handler import StockDataHandler
from src.line_notifier import LineNotifier

class TestStockDataHandler(unittest.TestCase):
    def setUp(self):
        # Setup temporary directory for data storage
        self.temp_dir = "temp_data"
        if not os.path.exists(self.temp_dir):
            os.makedirs(self.temp_dir)

        # Setup LineNotifier mock
        self.notifier = LineNotifier(token="dummy_token")
        self.notifier.send_message = MagicMock()

        # Create instance of StockDataHandler
        self.stock_data_handler = StockDataHandler(data_dir=self.temp_dir, notifier=self.notifier)
        self.symbols = ["2330.TW", "2317.TW", "5434.TW"]

    @patch("yfinance.download")
    def test_fetch_stock_data(self, mock_download):
        # Mock yfinance download
        mock_download.return_value = pd.DataFrame({
            "Date": ["2023-11-15"],
            "Open": [100],
            "High": [110],
            "Low": [90],
            "Close": [105],
            "Volume": [1000]
        }).set_index("Date")

        start_date = datetime(2023, 11, 15)
        end_date = datetime(2023, 11, 15)
        data = self.stock_data_handler.fetch_stock_data(self.symbols, start_date, end_date)
        self.assertFalse(data.empty)
        mock_download.assert_called_once()

    @patch("yfinance.download")
    def test_update_daily_data(self, mock_download):
        # Mock yfinance download
        mock_download.return_value = pd.DataFrame({
            "Date": ["2023-11-15"],
            "Open": [100],
            "High": [110],
            "Low": [90],
            "Close": [105],
            "Volume": [1000]
        }).set_index("Date")

        self.stock_data_handler.update_daily_data(self.symbols)

        # Check if CSV files are created and contain data
        for symbol in self.symbols:
            file_path = os.path.join(self.temp_dir, f"{symbol}.csv")
            self.assertTrue(os.path.exists(file_path))
            df = pd.read_csv(file_path)
            self.assertFalse(df.empty)

    @patch("yfinance.download")
    def test_retry_failed_symbols(self, mock_download):
        # Simulate failed download initially, then success
        mock_download.side_effect = [pd.DataFrame(), pd.DataFrame({
            "Date": ["2023-11-15"],
            "Open": [100],
            "High": [110],
            "Low": [90],
            "Close": [105],
            "Volume": [1000]
        }).set_index("Date")]

        self.stock_data_handler.update_daily_data(self.symbols)

        # Verify retries happened and data was eventually downloaded
        self.assertEqual(mock_download.call_count, 2)
        for symbol in self.symbols:
            file_path = os.path.join(self.temp_dir, f"{symbol}.csv")
            self.assertTrue(os.path.exists(file_path))
            df = pd.read_csv(file_path)
            self.assertFalse(df.empty)

    def tearDown(self):
        # Clean up temporary directory
        for file in os.listdir(self.temp_dir):
            os.remove(os.path.join(self.temp_dir, file))
        os.rmdir(self.temp_dir)

if __name__ == "__main__":
    unittest.main()
