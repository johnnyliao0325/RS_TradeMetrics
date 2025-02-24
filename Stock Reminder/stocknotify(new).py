import requests
import numpy as np
import time
import datetime
import sys
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager
import time
from random import randint
import pandas as pd
import openpyxl
from tqdm import trange
import yfinance as yf
from playsound import playsound
from stock_reminder_package.stock_reminder_utils import *
sys.path.append('C:/Users/User/Desktop/StockInfoHub')
from Shared_Modules.shared_functions import *
from Shared_Modules.shared_variables import *
import warnings
warnings.filterwarnings('ignore')

# 定義檢查 Breakout 的函數
def check_breakout(current_price, last_price, breakout_prices, breakout_notes):
    alerts = ['突破買']
    alert_or_not = None
    if breakout_prices is not None and breakout_notes is not None:
        for price, note in zip(breakout_prices, breakout_notes):
            if last_price <= price <= current_price:
                price_diff_percentage = (current_price - price) / price
                alerts.append(f'Trigger Price: {price}📈\nCurrent Price: {current_price}\nPrice Diff: {price_diff_percentage:.2%}\nNote: {note}\n')
                alert_or_not = '📈'
                
    return alerts, alert_or_not

# 定義檢查 Profit 的函數
def check_profit(current_price, last_price, profit_prices, profit_notes):
    alerts = ['停利']
    alert_or_not = None
    if profit_prices is not None and profit_notes is not None:
        for price, note in zip(profit_prices, profit_notes):
            if current_price >= price:
                price_diff_percentage = (current_price - price) / price
                alerts.append(f'Trigger Price: {price}💰\nCurrent Price: {current_price}\nPrice Diff: {price_diff_percentage:.2%}\nNote: {note}\n')
                alert_or_not = '💰'
    return alerts, alert_or_not

# 定義檢查 Pullback 的函數
def check_pullback(current_price, last_price, pullback_prices, pullback_notes):
    alerts = ['拉回買']
    alert_or_not = None
    if pullback_prices is not None and pullback_notes is not None:
        for price, note in zip(pullback_prices, pullback_notes):
            if last_price >= price >= current_price:
                price_diff_percentage = (current_price - price) / price
                alerts.append(f'Trigger Price: {price}📉📈\nCurrent Price: {current_price}\nPrice Diff: {price_diff_percentage:.2%}\nNote: {note}\n')
                alert_or_not = '📉📈'
    return alerts, alert_or_not

# 定義檢查 Sell 的函數
def check_sell(current_price, last_price, sell_prices, sell_notes):
    alerts = ['停損']
    alert_or_not = None
    if sell_prices is not None and sell_notes is not None:
        for price, note in zip(sell_prices, sell_notes):
            if current_price <= price:
                price_diff_percentage = (current_price - price) / price
                alerts.append(f'Trigger Price: {price}🚨\nCurrent Price: {current_price}\nPrice Diff: {price_diff_percentage:.2%}\nNote: {note}\n')
                alert_or_not = '🚨'
    return alerts, alert_or_not

# 字體顏色
class bcolors:
    OK = '\033[92m' #GREEN
    WARNING = '\033[93m' #YELLOW
    FAIL = '\033[91m' #RED
    RESET = '\033[0m' #RESET COLOR
# LINE Notify 權杖
token = 'F7cbo3hpi6SKYA8KCXXERUSOroaJTZOyO9QaCetMDOU'
notify_ornot = True # True : 發送訊息
program_test = False # True : 測試模式
program_start = False # True : 不用等開盤
# 假日不執行
n_day_ago = -0
day = datetime.datetime.strptime(str(datetime.date.today() - datetime.timedelta(days=n_day_ago)) , '%Y-%m-%d' )
if str(day).split(' ')[0] in HOLIDAY:
    print(f'Today is holiday : {day}')
    line_notify(f'{day}放假不執行stocknotify.py', TOKEN_FOR_NOTIFY, notify_ornot)
    sys.exit()



# 自動下載ChromeDriver
# print(ChromeDriverManager().install())
chrome_path = r'C:\Program Files\Google\Chrome\Application\chrome.exe'
# service = ChromeService(executable_path=ChromeDriverManager(path=chrome_path).install())
service = ChromeService(executable_path=ChromeDriverManager().install())
# 關閉通知提醒
chrome_options = webdriver.ChromeOptions()
prefs = {"profile.default_content_setting_values.notifications" : 2}
chrome_options.add_experimental_option("prefs",prefs)
# 開啟瀏覽器
driver = webdriver.Chrome(service=service, options=chrome_options)


print(f'{bcolors.OK}reset   reset   reset   reset{bcolors.RESET}')
# 讀取 Excel 檔案
notify_info = pd.read_excel('notify info.xlsx').astype(str)

# 曝險大小，同時持有總資金幾%部位
risk = 70

start_notify = '\n【Stock Notify Start】\n'
start_notify +=f'\nrisk : {risk}%\n'
now_position = sum([float(row['Position']) for index, row in notify_info.iterrows() if row['Status'] == '持有'])
start_notify += f'\nNow Position : {round(now_position*100/6, 2)}%\n\n'
start_notify += 'ID | Status | Score | Temp\n'

for index, row in notify_info.iterrows():
    row_score = round((float(row['Technical']) + float(row['Shareholder']) + float(row['Fundamental'])/3)*10/15, 1)
    start_notify += f'\n{row["stockID"]} | {row["Status"]} | {row_score} | {row["Template"]}'

line_notify(start_notify, TOKEN_FOR_NOTIFY, notify_ornot)



theurl = []



# for _ in range(10):
while True:
    notify_info = pd.read_excel('notify info.xlsx').astype(str)
    notify_info = notify_info[notify_info['Status'] != '觀察']
    for id in notify_info['stockID']:
        # 去到你想要的網頁
        url = 'https://tw.stock.yahoo.com/quote/' + id.split("_")[0].split('.')[0]
        theurl.append(url)
        print(url)
    # 假設 stock_price_info 是最新的收盤價和成交量的 DataFrame
    stock_price_info = pd.DataFrame({
        'close price': np.zeros(len(notify_info['stockID']), dtype=int),
        'volume': np.zeros(len(notify_info['stockID']), dtype=int)
    }, index=notify_info['stockID'])

    # 假設 last_stock_price_info 是上次的收盤價資訊
    last_stock_price_info = pd.DataFrame({
        'close price': np.zeros(len(notify_info['stockID']), dtype=int),
        'volume': np.zeros(len(notify_info['stockID']), dtype=int)
    }, notify_info['stockID'])
    connection = 1
    try:
        posted = 0
        current_time = datetime.datetime.now()
        print(f'current time : {current_time}')
        if not program_start :
            if current_time.hour < 9:
                time.sleep(60)
                continue
            else:
                line_notify('\n【Program Start】', TOKEN_FOR_NOTIFY, notify_ornot)
                program_start = True
        if all([current_time.hour >= 13, current_time.minute >= 34, not program_test]):
            line_notify('\n【Program Shutdown】', TOKEN_FOR_NOTIFY, notify_ornot)
            sys.exit()
    ########################################################################################改頁數
        # 爬取資料
        for num, id in enumerate(zip(notify_info['stockID'], notify_info['Name'])):
            post = 0
            print(id)
            id = id[0]
            print(id)
            
            #儲存網址 
            T = np.random.randint(7,size = 1)[0]
            # 去到個股網頁
            try:
                try:
                    driver.get(theurl[num]+'.TW')
                    title = driver.find_element(by = By.ID, value = "qsp-overview-realtime-info").text
                    print(theurl[num]+'.TW')
                except:
                    driver.get(theurl[num]+'.TWO')
                    title = driver.find_element(by = By.ID, value = "qsp-overview-realtime-info").text
                    print(theurl[num]+'.TWO')
                if connection == 0:
                    line_notify('\n【Reconnect】', TOKEN_FOR_NOTIFY, notify_ornot)
                    print(f'{bcolors.OK}Reconnect{bcolors.RESET}')
                    connection = 1
                # time.sleep(T)
            except Exception as e:
                line_notify(f'\n【Disconnect : Request {id.split("_")[0]} Web Failed】', TOKEN_FOR_NOTIFY, notify_ornot)
                print(f'{bcolors.WARNING}Request Web Failed{bcolors.RESET}')
                print(e)
                print(f'{bcolors.WARNING}Disconnect{bcolors.RESET}')
                try:
                    driver.close()
                except Exception as e:
                    print(e)
                    print(f'{bcolors.WARNING}Close Google Failed{bcolors.RESET}')
                    pass
                #time.sleep(2)
                # service = ChromeService(executable_path=ChromeDriverManager().install())
                driver = webdriver.Chrome(service=service, options=chrome_options)
                connection = 0
                print('---------------------------------------------------------------------------------------------------------------------------------------------')
                continue
            #time.sleep(3)
            try:
                title = title.split('\n')
                # 
                #name = title[0]
                # 日期
                data_time = title[1].split('：')[1]
                print(id)
                print(data_time)
                # 現在時間(小時)
                now_hour = data_time.split(' ')[1].split(':')[0]
                # 現在時間(分鐘)
                now_min = data_time.split(' ')[1].split(':')[1]
                # 現價
                price = title[4].replace(',','')
                stock_price_info.loc[id, 'close price'] = float(price)
                # 今日目前總量
                volume = title[22]
                stock_price_info.loc[id, 'volume'] = float(volume.replace(',',''))
                # 昨日總量
                yesterday_volume = title[24]
                last_stock_price_info.loc[id, 'volume'] = float(yesterday_volume.replace(',',''))
                # 昨日收盤
                yesterday_close = title[16].replace(',','')
                last_stock_price_info.loc[id, 'close price'] = float(yesterday_close)
                print(f"yesterday close:{yesterday_close}")
            except Exception as e:
                line_notify(f'\n【Error : Get {id.split("_")[0]} Data Failed】', TOKEN_FOR_NOTIFY, notify_ornot)
                print(f'{bcolors.FAIL}Get Data Failed{bcolors.RESET}')
                print(e)
                print('---------------------------------------------------------------------------------------------------------------------------------------------')
                continue
    except Exception as e:
        line_notify(f'\n【Error : Get {id.split("_")[0]} Data Failed】', TOKEN_FOR_NOTIFY, notify_ornot)
        print(f'{bcolors.FAIL}Program Failed{bcolors.RESET}')
        print(e)
        print('---------------------------------------------------------------------------------------------------------------------------------------------')
        continue
    is_notify = False
    # 檢查所有股票的提醒
    print(f'\n{bcolors.OK}Stock Notify{bcolors.RESET}')
    for index, row in notify_info.iterrows():
        print(f'\n{bcolors.OK}StockID {row["stockID"]}{bcolors.RESET}')
        stock_id = row['stockID']
        name = row['Name']
        # 準備所有提醒文本
        note_texts = ''
        alert_note_texts = ''
        alert_type = '【|'
        # 將多個價位和 note 分割成列表，處理可能為 None 的情況
        breakout_prices = [float(x.replace(',', '')) for x in row['Breakout price'].split(',')] if row['Breakout price'] else []
        breakout_notes = row['Breakout note'].replace('\n','').split(',') if row['Breakout note'] else []
        profit_prices = [float(x.replace(',', '')) for x in row['Profit price'].split(',')] if row['Profit price'] else []
        profit_notes = row['Profit note'].replace('\n','').split(',') if row['Profit note'] else []
        pullback_prices = [float(x.replace(',', '')) for x in row['Pullback price'].split(',')] if row['Pullback price'] else []
        pullback_notes = row['Pullback note'].replace('\n','').split(',') if row['Pullback note'] else []
        sell_prices = [float(x.replace(',', '')) for x in row['Sell price'].split(',')] if row['Sell price'] else []
        sell_notes = row['Sell note'].replace('\n','').split(',') if row['Sell note'] else []
        
        current_price = stock_price_info.at[stock_id, 'close price']
        last_price = last_stock_price_info.at[stock_id, 'close price']
        est_volume = estimate_volume(int(now_hour), int(now_min), stock_price_info.at[stock_id, 'volume']).split('.')[0]
        avg50_volume = volume_avg(stock_id.split("_")[0]).split('.')[0]
        Template = row['Template']
        Rank = row['Rank']
        Technical = str(row['Technical'])
        Shareholder = str(row['Shareholder'])
        Fundamentals = str(row['Fundamental'])
        Status = row['Status']
        if Status != '持有':
            Holdposition = 0
        else:
            Holdposition = row['Position']
        score = round((float(row['Technical']) + float(row['Shareholder']) + float(row['Fundamental'])/3)*10/15, 1)
        shares = row['shares per 0.1position']


        
        # 檢查每個條件
        breakout_notes, breakout_alert = check_breakout(current_price, last_price, breakout_prices, breakout_notes)
        profit_notes, profit_alert = check_profit(current_price, last_price, profit_prices, profit_notes)
        pullback_notes, pullback_alert = check_pullback(current_price, last_price, pullback_prices, pullback_notes)
        sell_notes, sell_alert = check_sell(current_price, last_price, sell_prices, sell_notes)
        
        # 整合所有提醒文本
        notes = [breakout_notes, profit_notes, pullback_notes, sell_notes]
        alert_list = [breakout_alert, profit_alert, pullback_alert, sell_alert]
        # if notes:
            # note_texts.append(f"StockID {stock_id}:\n{notes}")
        for alert, note in zip(alert_list, notes):
            if alert is not None:
                alert_type += f' {alert}|'
            if np.shape(note)[0] > 1:
                alert_note_texts += '======================\n'
                for note_index, n in enumerate(note):
                    alert_note_texts += f"{n}\n"
                    if note_index == 0:
                        alert_note_texts += '======================\n'
                # note_texts += '===================\n'
        alert_type += '】'
        if alert_note_texts:
            note_texts = f"\n{alert_type}\n【{stock_id} {name}】--> {Template}\n\
Score: {score}\nTechnical: {Technical}\nShareholder: {Shareholder}\nFundamentals: {Fundamentals}\n---------------------\
\nLast price:{last_price}\nCurrent price:{current_price}\n---------------------\
\nShares/0.1Position: {shares}\nHold position: {round(float(Holdposition)*100, 2)}%\n\n{alert_note_texts}"
            note_texts += f"目前成交量:{stock_price_info.at[stock_id, 'volume']}\n預估量:{est_volume}\n昨日總量:{last_stock_price_info.at[stock_id, 'volume']}\n50日均量:{avg50_volume}\n\n"
            line_notify(note_texts, TOKEN_FOR_NOTIFY, notify_ornot) #TOKEN_FOR_NOTIFY
            is_notify = True
        print(note_texts)
    if is_notify:
        sigment_line = '==========='
        line_notify(sigment_line, TOKEN_FOR_NOTIFY, notify_ornot)
    time.sleep(300)
    # 更新 last_stock_price_info 為當前的 stock_price_info
    # last_stock_price_info = stock_price_info.copy()