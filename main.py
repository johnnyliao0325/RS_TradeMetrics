import os
from datetime import datetime
import pandas as pd
from src.stock_data_handler import StockDataHandler
from src.line_notifier import LineNotifier
from src.indicator_calculator import IndicatorCalculator
from src.daily_stock_summary import DailyStockSummaryGenerator
from src.rs_rate_calculator import RSRateCalculator
from src.rs_max_calculator import RSRateMaxMinUpdater
from src.daily_stock_template_filter import DailyStockTemplateFilter
from src.rs_rate_manager import RSRateManager
from src.daily_stock_category_RS_data_updator import StockCategoryRSDataUpdater
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
    def __init__(self, base_dir, data_dir: str, output_dir: str, line_token: str, ):
        self.data_dir = data_dir
        self.output_dir = output_dir
        # self.notifier = LineNotifier(token=line_token)
        self.notifier = None
        self.stock_handler = StockDataHandler(data_dir=self.data_dir, notifier=self.notifier)
        self.indicator_calculator = IndicatorCalculator(data_dir=self.data_dir)
        self.summary_generator = DailyStockSummaryGenerator(data_dir=self.data_dir, output_directory=self.output_dir)
        self.rs_rate_calculator = RSRateCalculator(data_dir=self.data_dir, output_directory=self.output_dir)
        self.rs_max_min_calculator = RSRateMaxMinUpdater(data_dir=self.data_dir, output_directory=output_dir, n_values=[20, 50, 250], n_day_sort=[10, 20, 50, 250])
        self.rs_rate_manager = RSRateManager(data_dir=self.data_dir, output_directory=self.output_dir, n_values=[20, 50, 250], n_day_sort=[10, 20, 50, 250])
        self.stock_category_rs_data_updater = StockCategoryRSDataUpdater(base_path=base_dir)
    def update_data(self, symbols: list, rewrite: bool = True, today = None, tomorrow = None):
        """Step 1: 更新每日資料"""
        split_symbols = [symbols[i:i + 10] for i in range(0, len(symbols), 10)]
        for symbol_batch in split_symbols:
            self.stock_handler.update_daily_data(symbol_batch, rewrite=rewrite, today=today, tomorrow=tomorrow)

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
            if self.notifier is not None:
                self.notifier.send_message(f"以下股票的技術指標更新失敗：{failed_symbols}")
            else:
                print(f"以下股票的技術指標更新失敗：{failed_symbols}")

    def generate_summary(self, symbols: list, date: datetime):
        """Step 3: 生成每日摘要"""
        self.summary_generator.generate_daily_summary(symbols, date)

    def calculate_rs_rate(self, date: str, n_values: list = [20, 50, 250]):
        """Step 4: 計算 RS rate"""
        self.rs_rate_calculator.update_daily_rs_rate(date, n_values)

    def calculate_rs_rate_max_min(self, symbols: list, today: datetime):
        """Step 5: 計算 RS rate 最大值和最小值"""
        self.rs_max_min_calculator.update_rs_rate_max_min(symbols=symbols, today=today)
    


    def update_rs_rate_info(self, today: datetime, symbols: list):
        """Step 6: 更新 RS rate 資訊 (包括 RS rate 和 RS rate 最大值和最小值)"""
        print(f'today type: {type(today)}')
        self.rs_rate_manager.update_daily_rs_rate_and_max_min(today, symbols)



    def filter_stock(self, output_directory: str, today: datetime, allstock_info: pd.DataFrame, mark: str = ''):
        """Step 6: 篩選股票"""
        allstock_path = os.path.join(output_directory, f"daily_stock_summary_{today}_with_rs_rate_and_maxmin.xlsx")
        allstock = pd.read_excel(allstock_path, index_col="ID")
        for y_i in range(20):
            yesterday = today - pd.Timedelta(days=y_i+1)
            yesterday = yesterday.strftime("%Y-%m-%d")
            print(f"Checking {yesterday}...")
            yesterday_allstock_path = os.path.join(output_directory, f"daily_stock_summary_{yesterday}_with_rs_rate_and_maxmin.xlsx")
            if os.path.exists(yesterday_allstock_path):
                yesterday_allstock = pd.read_excel(yesterday_allstock_path)
                break

        filterer = DailyStockTemplateFilter(allstock=allstock, allstock_info=allstock_info, yesterday_allstock=yesterday_allstock)
        daily_stock_template = filterer.run(output_directory=output_directory, today=today, mark=mark)

    def update_category_rs_data(self, today: datetime):
        """Step 7: 更新類股 RS 資料"""
        self.stock_category_rs_data_updater.update_stock_category_RS_data(today)


def main():
    ## 定義要更新的股票代號
    

    ## 設置資料目錄和 Line Notifier
    base_dir = CONFIG.get("base_dir")
    data_dir = CONFIG.get("data_dir")
    output_directory = CONFIG.get("output_directory")
    line_token = CONFIG.get("line_token")

    symbols = CONFIG.get("specific_symbols_list")
    allstock_info = CONFIG.get("allstock_info")



    # if CONFIG.get("specific_symbols_list") is not None:
    #     symbols = CONFIG.get("specific_symbols_list")
    #     _, allstock_info = get_allstock_info()
    #     if symbols[0] != '^TWII':
    #         symbols.insert(0, '^TWII')
    # else:
    #     symbols, allstock_info = get_allstock_info()
    #     symbols = symbols.tolist()

    ## 定義起始日期
    delay_days = CONFIG.get("delay_days")
    today = datetime.now().date() - pd.Timedelta(days=delay_days)
    tomorrow = today + pd.Timedelta(days=1)
    prev_day = today - pd.Timedelta(days=6532)


    ## 初始化 DailyStockTasks
    tasks = DailyStockTasks(base_dir=base_dir, data_dir=data_dir, output_dir=output_directory, line_token=line_token)

    
    print(f'執行{today}資料, 隔日日期為{tomorrow}, 從{prev_day}開始執行')
    print(type(today))


    ## 記錄執行時間
    spend_time = {}

    ## print要執行的任務
    do_task_text = f"{today.strftime('%Y-%m-%d')} 開始執行任務：\n"
    print("開始執行任務：\n")
    tasks_number = 1
    for task, do_task in DO_TASKS.items():
        if do_task:
            do_task_text += f"{tasks_number}：{task}\n"
            print(f"{tasks_number}：{task}\n")
            tasks_number += 1
    if tasks.notifier is not None:
        tasks.notifier.send_message(do_task_text)
    else:
        print(do_task_text)

    ## Step 1: 更新每日數據
    if DO_TASKS.get('update_data'):
        start_time = datetime.now()
        tasks.update_data(symbols=symbols, rewrite=True, today=today, tomorrow=tomorrow)
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





    ## Step 4: 計算 RS rate、RS rate 最大值和最小值
    if DO_TASKS.get('calculate_rs_rate_and_max_min'):
        start_time = datetime.now()
        tasks.update_rs_rate_info(symbols=symbols, today=today)
        spend_time['calculate_rs_rate_max_min'] = datetime.now() - start_time





    ## Step 4: 計算 RS rate
    if DO_TASKS.get('calculate_rs_rate'):
        start_time = datetime.now()
        tasks.calculate_rs_rate(date=today.strftime("%Y-%m-%d"))
        spend_time['calculate_rs_rate'] = datetime.now() - start_time

    ## Step 5: 計算 RS rate 最大值和最小值
    if DO_TASKS.get('calculate_rs_rate_max_min'):
        start_time = datetime.now()
        tasks.calculate_rs_rate_max_min(symbols=symbols, today=today)
        spend_time['calculate_rs_rate_max_min'] = datetime.now() - start_time

    if DO_TASKS.get('filter_stock'):
        start_time = datetime.now()
        tasks.filter_stock(output_directory=output_directory, today=today, allstock_info=allstock_info, mark=CONFIG.get("filter_stock_mark"))
        spend_time['filter_stock'] = datetime.now() - start_time

    if DO_TASKS.get('update_category_rs_data'):
        start_time = datetime.now()
        tasks.update_category_rs_data(today=today)
        spend_time['update_category_rs_data'] = datetime.now() - start_time

    ## 通知執行時間
    message_text = "程式執行時間：\n"
    total_time = 0
    for task, time in spend_time.items():
        time = round(time.total_seconds(), 1)
        message_text += f"{task}: {time} 秒\n"
        total_time += time
    message_text += f"總計: {round(total_time, 1)} 秒"

    if spend_time:
        if tasks.notifier is not None:
            tasks.notifier.send_message(message_text)
        else:
            print(message_text)


if __name__ == "__main__":
    symbols, allstock_info = get_allstock_info()
    symbols = symbols.tolist()
    for i in [0]: # 0, 1, 2, 3, 4, 5, 6, 7, 8, 9
        try:
            
            DO_TASKS = {
            'update_data': True,
            'calculate_indicators': True,
            'generate_summary': True,
            'calculate_rs_rate_and_max_min': True,
            'calculate_rs_rate': False,
            'calculate_rs_rate_max_min': False,
            'filter_stock': True,
            'update_category_rs_data': True
        }
            CONFIG = {
            "delay_days": i,
            "base_dir": "C:/Users/User/Desktop/stock",
            "data_dir": os.path.join(os.getcwd(), "data_test"),
            "output_directory": "C:/Users/User/Desktop/stock/全個股條件篩選",
            "line_token": 'u7bfH6ad2gDcHvvPrtHR9sjJ8AYmQ7tNl0VBf7piO4q',
            "specific_symbols_list": symbols, # symbols or ['2330.TW', '2317.TW']
            "allstock_info": allstock_info,
            "filter_stock_mark": ""
        }
            main()
        except Exception as e:
            print(e)
            continue