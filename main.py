# import os
# from datetime import datetime
# from src.stock_data_handler import StockDataHandler
# from src.line_notifier import LineNotifier
# from src.indicator_calculator import IndicatorCalculator
# from src.daily_stock_summary import DailyStockSummaryGenerator
# from src.rs_rate_calculator import RSRateCalculator
# import requests
# import pandas as pd
# import warnings
# warnings.filterwarnings("ignore")
# def get_allstock_info():
#     url = "https://isin.twse.com.tw/isin/class_main.jsp?owncode=&stockname=&isincode=&market=1&issuetype=1&industry_code=&Page=1&chklike=Y"
#     response = requests.get(url)
#     listed = pd.read_html(response.text)[0]
#     listed.columns = listed.iloc[0,:]
#     listed = listed[["有價證券代號","有價證券名稱","市場別","產業別","公開發行/上市(櫃)/發行日"]]
#     listed = listed.iloc[1:]

#     # ============上櫃股票df============
#     urlTWO = "https://isin.twse.com.tw/isin/class_main.jsp?owncode=&stockname=&isincode=&market=2&issuetype=&industry_code=&Page=1&chklike=Y"
#     response = requests.get(urlTWO)
#     listedTWO = pd.read_html(response.text)[0]
#     listedTWO.columns = listedTWO.iloc[0,:]
#     listedTWO = listedTWO.loc[listedTWO['有價證券別'] == '股票']
#     listedTWO = listedTWO[["有價證券代號","有價證券名稱","市場別","產業別","公開發行/上市(櫃)/發行日"]]

#     # ============上市股票代號+.TW============
#     stock_1 = listed["有價證券代號"]
#     stock_num = stock_1.apply(lambda x: str(x) + ".TW")
#     stock_num.loc[len(stock_num)+1] = '0050.TW'
#     stock_num.loc[len(stock_num)+1] = '^TWII'

#     # ============上櫃股票代號+.TWO============
#     stock_2 = listedTWO["有價證券代號"]
#     stock_num2 = stock_2.apply(lambda x: str(x) + ".TWO")
#     stock_num2.loc[len(stock_num2)+1] = 'IX0043.TWO'


#     # ============concate全部股票代號============
#     stock_num = pd.concat([stock_num, stock_num2], ignore_index=True) 
#     stock_num = stock_num.sort_values(ascending=False).reset_index(drop = True)
#     allstock_info = pd.concat([listed, listedTWO], ignore_index=True)
#     allstock_info.columns = ["ID","有價證券名稱","市場別","產業別","公開發行/上市(櫃)/發行日"]
#     allstock_info.set_index('ID', inplace = True)
#     return stock_num, allstock_info
# def main():
#     # 定義要更新的股票代號
#     spend_time = {'update_daily_data': 0, 'calculate_indicators': 0, 'generate_daily_summary': 0, 'calculate_rs_rate': 0}
#     symbols, allstock_info = get_allstock_info()
#     # 設置資料目錄
#     data_dir = os.path.join(os.getcwd(), "data_test")

#     # 設置 Line Notifier（可以替換成你的實際 Token）
#     line_token = 'u7bfH6ad2gDcHvvPrtHR9sjJ8AYmQ7tNl0VBf7piO4q'
#     notifier = LineNotifier(token=line_token)

#     # 建立 StockDataHandler 和 IndicatorCalculator
#     stock_handler = StockDataHandler(data_dir=data_dir, notifier=notifier)
#     calculator = IndicatorCalculator(data_dir=data_dir)

#     # 進行每日數據更新
#     delay = 0
#     today = datetime.now().date() - pd.Timedelta(days=delay)
#     prev_day = today + pd.Timedelta(days=-6532)
#     tomorrow = today + pd.Timedelta(days=1)
#     print(today)
#     print(prev_day)
#     print(tomorrow)

#     n = 10
#     symbols = symbols.tolist()
#     # symbols = ['9949.TWO', '1102.TW']


#     ## update data

#     program_start_time = datetime.now()
#     split_symbols = [symbols[i:i + n] for i in range(0, len(symbols), n)]
#     for symbol in split_symbols: # 分割成n個一組
#         # stock_handler.update_historical_data(symbol, prev_day, today, rewrite=False)
#         stock_handler.update_daily_data(symbol, rewrite=True)
#     program_end_time = datetime.now()
#     spend_time['update_daily_data'] = program_end_time - program_start_time
    

#     ## update indicators

#     program_start_time = datetime.now()
#     comparestock_path = os.path.join(data_dir, '^TWII.csv')
#     comparestock = None
#     indicator_failed_update_symbols = []
#     # symbols = ['1563.TW']
#     for i, symbol in enumerate(symbols):
#         csv_file_path = os.path.join(data_dir, f"{symbol}.csv")
#         if os.path.exists(csv_file_path):
#             existing_data = pd.read_csv(csv_file_path, index_col="Date", parse_dates=["Date"])
#             failed_symbol = calculator.calculate_indicators(symbol, existing_data, allstock_info, comparestock)
#             if failed_symbol:
#                 indicator_failed_update_symbols.append(failed_symbol)
#         if symbol == '^TWII':
#             comparestock = pd.read_csv(comparestock_path, index_col="Date", parse_dates=["Date"])
#     program_end_time = datetime.now()
#     spend_time['calculate_indicators'] = program_end_time - program_start_time
#     # # 通知使用者
#     if indicator_failed_update_symbols:
#         notifier.send_message(f"以下股票的技術指標更新失敗：{indicator_failed_update_symbols}")

#     ## generate daily summary

#     program_start_time = datetime.now()
#     output_directory = "C:/Users/User/Desktop/stock/全個股條件篩選"
#     summary_generator = DailyStockSummaryGenerator(data_dir, output_directory)
#     summary_generator.generate_daily_summary(symbols, today)
#     program_end_time = datetime.now()
#     spend_time['generate_daily_summary'] = program_end_time - program_start_time

#     ## calculate rs rate

#     program_start_time = datetime.now()
#     rs_calculator = RSRateCalculator(data_dir=data_dir, output_directory=output_directory)
#     rs_calculator.update_daily_rs_rate(today.strftime("%Y-%m-%d"), [20, 50, 250])
#     program_end_time = datetime.now()
#     spend_time['calculate_rs_rate'] = program_end_time - program_start_time

#     if spend_time:
#         notifier.send_message(f"程式執行時間：\n{spend_time}")

#     ## calculate rs rate max 


# if __name__ == "__main__":
#     main()
    
import os
from datetime import datetime
import pandas as pd
from src.stock_data_handler import StockDataHandler
from src.line_notifier import LineNotifier
from src.indicator_calculator import IndicatorCalculator
from src.daily_stock_summary import DailyStockSummaryGenerator
from src.rs_rate_calculator import RSRateCalculator
from src.rs_max_calculator import RSRateMaxMinUpdater
import requests
import warnings

warnings.filterwarnings("ignore")


def get_allstock_info():
    # 獲取所有股票的信息，包括上市和上櫃股票
    url = "https://isin.twse.com.tw/isin/class_main.jsp?owncode=&stockname=&isincode=&market=1&issuetype=1&industry_code=&Page=1&chklike=Y"
    response = requests.get(url)
    listed = pd.read_html(response.text)[0]
    listed.columns = listed.iloc[0, :]
    listed = listed[["有價證券代號", "有價證券名稱", "市場別", "產業別", "公開發行/上市(櫃)/發行日"]]
    listed = listed.iloc[1:]

    # 上櫃股票
    urlTWO = "https://isin.twse.com.tw/isin/class_main.jsp?owncode=&stockname=&isincode=&market=2&issuetype=&industry_code=&Page=1&chklike=Y"
    response = requests.get(urlTWO)
    listedTWO = pd.read_html(response.text)[0]
    listedTWO.columns = listedTWO.iloc[0, :]
    listedTWO = listedTWO.loc[listedTWO['有價證券別'] == '股票']
    listedTWO = listedTWO[["有價證券代號", "有價證券名稱", "市場別", "產業別", "公開發行/上市(櫃)/發行日"]]

    # 上市和上櫃股票代號處理
    stock_num = pd.concat([listed["有價證券代號"].apply(lambda x: str(x) + ".TW"),
                           listedTWO["有價證券代號"].apply(lambda x: str(x) + ".TWO")], ignore_index=True)
    stock_num.loc[len(stock_num) + 1] = '0050.TW'
    stock_num.loc[len(stock_num) + 1] = '^TWII'
    stock_num = stock_num.sort_values(ascending=False).reset_index(drop=True)

    # 合併所有股票信息
    allstock_info = pd.concat([listed, listedTWO], ignore_index=True)
    allstock_info.columns = ["ID", "有價證券名稱", "市場別", "產業別", "公開發行/上市(櫃)/發行日"]
    allstock_info.set_index('ID', inplace=True)
    return stock_num, allstock_info


class DailyStockTasks:
    def __init__(self, data_dir: str, output_dir: str, line_token: str):
        self.data_dir = data_dir
        self.output_dir = output_dir
        self.notifier = LineNotifier(token=line_token)
        self.stock_handler = StockDataHandler(data_dir=self.data_dir, notifier=self.notifier)
        self.indicator_calculator = IndicatorCalculator(data_dir=self.data_dir)
        self.summary_generator = DailyStockSummaryGenerator(data_dir=self.data_dir, output_directory=self.output_dir)
        self.rs_rate_calculator = RSRateCalculator(data_dir=self.data_dir, output_directory=self.output_dir)
        self.rs_max_min_calculator = RSRateMaxMinUpdater(data_dir=self.data_dir, n_values=[20, 50, 250], n_day_sort=[10, 20, 50, 250])
    def update_data(self, symbols: list, rewrite: bool = True):
        """Step 1: 更新每日資料"""
        split_symbols = [symbols[i:i + 10] for i in range(0, len(symbols), 10)]
        for symbol_batch in split_symbols:
            self.stock_handler.update_daily_data(symbol_batch, rewrite=rewrite)

    def update_data_for_historical(self, symbols: list, prev_day: datetime, today: datetime, rewrite: bool = True):
        """Step 1: 更新每日資料"""
        split_symbols = [symbols[i:i + 10] for i in range(0, len(symbols), 10)]
        for symbol_batch in split_symbols:
            self.stock_handler.update_historical_data(symbol_batch, prev_day, today, rewrite=rewrite)

    def update_indicators(self, symbols: list, allstock_info: pd.DataFrame):
        """Step 2: 更新技術指標"""
        comparestock_path = os.path.join(self.data_dir, '^TWII.csv')
        comparestock = None
        failed_symbols = []
        for symbol in symbols:
            csv_file_path = os.path.join(self.data_dir, f"{symbol}.csv")
            if os.path.exists(csv_file_path):
                existing_data = pd.read_csv(csv_file_path, index_col="Date", parse_dates=["Date"])
                failed_symbol = self.indicator_calculator.calculate_indicators(symbol, existing_data, allstock_info, comparestock)
                if failed_symbol:
                    failed_symbols.append(failed_symbol)
            if symbol == '^TWII':
                comparestock = pd.read_csv(comparestock_path, index_col="Date", parse_dates=["Date"])
        if failed_symbols:
            self.notifier.send_message(f"以下股票的技術指標更新失敗：{failed_symbols}")

    def generate_summary(self, symbols: list, date: datetime):
        """Step 3: 生成每日摘要"""
        self.summary_generator.generate_daily_summary(symbols, date)

    def calculate_rs_rate(self, date: str, n_values: list = [20, 50, 250]):
        """Step 4: 計算 RS rate"""
        self.rs_rate_calculator.update_daily_rs_rate(date, n_values)

    def calculate_rs_rate_max_min(self, symbols: list):
        """Step 5: 計算 RS rate 最大值和最小值"""
        self.rs_max_min_calculator.update_rs_rate_max_min(symbols=symbols)



def main():
    ## 定義要更新的股票代號
    

    ## 設置資料目錄和 Line Notifier
    data_dir = CONFIG.get("data_dir")
    output_directory = CONFIG.get("output_directory")
    line_token = CONFIG.get("line_token")
    if CONFIG.get("specific_symbols_list"):
        symbols = CONFIG.get("specific_symbols_list")
    else:
        symbols, allstock_info = get_allstock_info()
        

    ## 初始化 DailyStockTasks
    tasks = DailyStockTasks(data_dir=data_dir, output_dir=output_directory, line_token=line_token)

    ## 定義起始日期
    delay_days = CONFIG.get("delay_days")
    today = datetime.now().date() - pd.Timedelta(days=delay_days)
    tomorrow = today + pd.Timedelta(days=1)
    prev_day = today - pd.Timedelta(days=6532)

    print(f'執行{today}資料, 隔日日期為{tomorrow}, 從{prev_day}開始執行')


    ## 記錄執行時間
    spend_time = {}

    ## print要執行的任務
    for task, do_task in DO_TASKS.items():
        if do_task:
            print(f"執行任務：{task}")

    ## Step 1: 更新每日數據
    if DO_TASKS.get('update_data'):
        start_time = datetime.now()
        tasks.update_data(symbols=symbols, rewrite=True)
        # tasks.update_data_for_historical(symbols=symbols, prev_day=prev_day, today=today, rewrite=True)
        spend_time['update_daily_data'] = datetime.now() - start_time

    ## Step 2: 更新技術指標
    if DO_TASKS.get('calculate_indicators'):
        start_time = datetime.now()
        tasks.update_indicators(symbols=symbols, allstock_info=allstock_info)
        spend_time['calculate_indicators'] = datetime.now() - start_time

    ## Step 3: 生成每日摘要
    if DO_TASKS.get('generate_summary'):
        start_time = datetime.now()
        tasks.generate_summary(symbols=symbols, date=today)
        spend_time['generate_daily_summary'] = datetime.now() - start_time

    ## Step 4: 計算 RS rate
    if DO_TASKS.get('calculate_rs_rate'):
        start_time = datetime.now()
        tasks.calculate_rs_rate(date=today.strftime("%Y-%m-%d"))
        spend_time['calculate_rs_rate'] = datetime.now() - start_time

    ## Step 5: 計算 RS rate 最大值和最小值
    if DO_TASKS.get('calculate_rs_rate_max_min'):
        start_time = datetime.now()
        tasks.calculate_rs_rate_max_min(symbols=symbols)
        spend_time['calculate_rs_rate_max_min'] = datetime.now() - start_time

    ## 通知執行時間
    if spend_time:
        tasks.notifier.send_message(f"程式執行時間：\n{spend_time}")


if __name__ == "__main__":
    DO_TASKS = {
    'update_daily_data': True,
    'calculate_indicators': True,
    'generate_summary': True,
    'calculate_rs_rate': True,
    'calculate_rs_rate_max_min': True
}
    CONFIG = {
    "delay_days": 0,
    "data_dir": os.path.join(os.getcwd(), "data_test"),
    "output_directory": "C:/Users/User/Desktop/stock/全個股條件篩選",
    "line_token": 'u7bfH6ad2gDcHvvPrtHR9sjJ8AYmQ7tNl0VBf7piO4q',
    "specific_symbols_list": None # None or ['2330.TW', '2317.TW']
}
    main()