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
from stock_reminder_package.stock_reminder_utils import *
sys.path.append('C:/Users/User/Desktop/StockInfoHub')
from Shared_Modules.shared_functions import *
from Shared_Modules.shared_variables import *
import warnings
warnings.filterwarnings('ignore')
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
# 總資金大小
johnny_allmoney = 1800000
jack_allmoney = 100000
# 曝險大小，同時持有總資金幾%部位
risk = 30
# 最大部位總資金幾%
maxposition = 17 
johnny_maxposition = johnny_allmoney * maxposition / 100
jack_maxposition = jack_allmoney * maxposition / 100
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
# 持有股票
stop_loss_stockID = '1477 6526 2317 3010 2327'.split(' ')
# 持有股票 note
note_text1 = ['停利:15% 460全出。\n停損:382，碰到停損全出。',
              '停利:20% 840全出。\n停損:668，碰到停損全出。',
              '停利:20% 192全出。\n停損:151，碰到停損全出。',
              '停利:15% 148全出。\n停損:120，碰到停損全出。',
              '停利:沿著20MA做長。\n停損:620，碰到停損全出。']
# 持有股票的停利點
get_profit_price = [460, 840, 192, 148, 750]
# 持有股票的停損點
stop_loss_price = [382, 668, 151, 120, 620]

df1 = pd.DataFrame({'stockID':stop_loss_stockID, 'stop_loss_price':stop_loss_price, 'get_profit_price':get_profit_price, 'note':note_text1})
# 準備買入股票
stockID_list = '1477_2 3010_2 2327_2 2317_2 6526_2 3324 3017 3207'.split(' ')
note_text2 = ['A，小時線收破400買0.1，日線收破395.5買0.1，日線收破400買0.3，剩下0.2等拉回買。',
              'A，拉回到131買0.2。',
              'B，開盤掛643拉回買0.2，拉回到636買0.2，小時線收破687買0.1，日線收破687買0.1，剩下0.2等突破700。',
              'A，拉回到162買0.2，拉回到161買0.1，拉回到159.5買0.1。',
              'B，日線收破704買0.1，小時線收破717買0.2，日線收破717買0.2，小時線收破725買0.1，日線收破725買0.2。',
              'B，小時線收破847買0.1，日線收破847買0.1，小時線收破873買0.1，日線收破873買0.1。',
              'A，小時線收破677買0.1，日線收破677買0.1，小時線收破688買0.1，日線收破688買0.1，小時線收破698買0.1，日線收破700買0.1。',
              'B，拉回到152買0.1，拉回到150買0.2，拉回到147買0.1，拉回到146買0.2，剩下0.2等底部反轉訊號，小時線收破160買0.1，日線收破162.5買0.1。']
# 買入點 
buy_price_list = [395.5, 131, 687, 171, 704, 847, 688, 147]
# 準備買入股票的停損點
newstock_stop_loss = [382, 119.5, 620, 149.5, 668, 790, 655, 144.5]
# 準備買入股票 note

df2 = pd.DataFrame({'stockID':stockID_list, 'buy_price':buy_price_list, 'stop_loss_price':newstock_stop_loss, 'note':note_text2})
# 合併兩個DataFrame
stock_df = pd.concat([df1, df2], axis=0, ignore_index=True).set_index('stockID')
# df columns : stockID, stop_loss_price, get_profit_price, note, buy_price
print(stock_df)


theurl = []


# 要發送的訊息
print(f'{bcolors.OK}reset   reset   reset   reset{bcolors.RESET}')
message = f'\n【重新設定】 :\n曝險大小 : 總資金{str(risk)}%\n最大部位 : 總資金{str(maxposition)}%\n\n'
for i, id in enumerate(stock_df.index.values):
    if np.isnan(stock_df.loc[id, 'buy_price']):
        message =  f"{message}{str(i+1)}.{id.split('_')[0]}(持有)\n停利:{str(stock_df.loc[id, 'get_profit_price'])}，停損:{str(stock_df.loc[id, 'stop_loss_price'])}\n"
    else:
        message =  f"{message}{str(i+1)}.{id.split('_')[0]}(買入{stock_df.loc[id, 'note'].split('，')[0]})\n目標:{str(stock_df.loc[id, 'buy_price'])}，停損:{str(stock_df.loc[id, 'stop_loss_price'])}\n"
# 發訊息
line_notify(message, TOKEN_FOR_NOTIFY, notify_ornot)
connection = 1
for id in stock_df.index.values:
    # 去到你想要的網頁
    url = 'https://tw.stock.yahoo.com/quote/' + id.split("_")[0]
    theurl.append(url)
# time.sleep(1500)

try:
    while(1):
        posted = 0
        current_time = datetime.datetime.now()
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
        for num, id in enumerate(stock_df.index.values):
            post = 0
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
                time.sleep(2)
                # service = ChromeService(executable_path=ChromeDriverManager().install())
                driver = webdriver.Chrome(service=service, options=chrome_options)
                connection = 0
                print('---------------------------------------------------------------------------------------------------------------------------------------------')
                continue
            time.sleep(3)
            try:
                title = title.split('\n')
                # 
                name = title[0]
                # 日期
                data_time = title[1].split('：')[1]
                print(id)
                print(data_time)
                # 現在時間(小時)
                hour = data_time.split(' ')[1].split(':')[0]
                # 現在時間(分鐘)
                min = data_time.split(' ')[1].split(':')[1]
                # 現價
                price = title[4].replace(',','')
                # 今日目前總量
                now_volume = title[22]
                # 昨日總量
                yesterday_volume = title[24]
                # 50日均量
                volume50avg = volume_avg(id.split("_")[0])
                #print(now_volume.replace(',',''))
                # 今日預估量
                est_volume = estimate_volume(int(hour), int(min), int(now_volume.replace(',','')))
            except Exception as e:
                line_notify(f'\n【Error : Get {id.split("_")[0]} Data Failed】', TOKEN_FOR_NOTIFY, notify_ornot)
                print(f'{bcolors.FAIL}Get Data Failed{bcolors.RESET}')
                print(e)
                print('---------------------------------------------------------------------------------------------------------------------------------------------')
                continue
            try:
                # ===========================如果是持有股票===========================
                if np.isnan(stock_df.loc[id, 'buy_price']):
                    # 要發送的訊息
                    # 持有股票準備停利
                    if float(price) >= stock_df.loc[id, 'get_profit_price']:
                        message = f'\n【停利提醒】\n【{id}】\n ⚠️ : {stock_df.loc[id, "note"]}\n\n{data_time}\n📈停利股價 : {str(stock_df.loc[id, "get_profit_price"])}\n\
現價 : {price}(超過{str(round(100*(float(price) - stock_df.loc[id, "get_profit_price"])/float(price),2))}%)\n'
                        print(message)
                        post = 1
                    # 持有股票準備停損
                    elif float(price) <= stock_df.loc[id, 'stop_loss_price']:
                        message = f'\n【停損提醒】\n【{id}】\n ⚠️ : {stock_df.loc[id, "note"]}\n\n{data_time}\n📉停損股價 : {str(stock_df.loc[id, "stop_loss_price"])}\n\
現價 : {price}(超過{str(round(100*(float(price) - stock_df.loc[id, "stop_loss_price"])/float(price),2))}%)\n'
                        print(message)
                        post = 1
                    else:
                        post = 0

                # ===========================如果是準備買入股票==========================
                else:
                    # 要發送的訊息
                    # 準備買入股票
                    if float(price) >= stock_df.loc[id, 'buy_price']:
                        message = f'\n【買入提醒】\n【{id}】\n ⚠️ : {stock_df.loc[id, "note"]}\n\n{data_time}\n💵目標股價 : {str(stock_df.loc[id, "buy_price"])}\n\
現價 : {price}(超過{str(round(100*(float(price) - stock_df.loc[id, "buy_price"])/float(price),2))}%)\n\n\
目前成交量 : {now_volume}\n今日預估量 : {est_volume}\n50日均量 : {int(float(volume50avg))}\n昨日總量 : {yesterday_volume}\n\n\
johnny全倉可買股數 : {str(round((johnny_maxposition/float(price))))}\n\
jack全倉可買股數 : {str(round((jack_maxposition/float(price))))}\n'
                        print(message)
                        post = 1
                    else:
                        post = 0
                # ===========================發送買賣股票訊息===========================
                # HTTP 標頭參數與資料
                if post == 1:
                    line_notify(message, TOKEN_FOR_NOTIFY, notify_ornot)
                posted = posted + post
            except Exception as e:
                line_notify(f'\n【Error : Post {id.split("_")[0]} Text Failed】', TOKEN_FOR_NOTIFY, notify_ornot)
                print(e)
                print(f'{bcolors.FAIL}POST TEXT FAILED{bcolors.RESET}')
            print('---------------------------------------------------------------------------------------------------------------------------------------------')
        if posted >= 1:
            line_notify('===========', TOKEN_FOR_NOTIFY, notify_ornot)
        time.sleep(300)
except Exception as e:
    print(e)
    print(f'{bcolors.FAIL}Program Shutdown{bcolors.RESET}')
    line_notify('\n【Program Shutdown】', TOKEN_FOR_NOTIFY, notify_ornot)
    # time.sleep(60)
        