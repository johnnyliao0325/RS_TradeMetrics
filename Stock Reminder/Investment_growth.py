from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager
import time
from random import randint
import pandas as pd
import openpyxl
import requests
import numpy as np
import time
# 字體顏色
class bcolors:
    WIN = '\033[92m' #GREEN
    SHOW = '\033[93m' #YELLOW
    LOSE = '\033[91m' #RED
    RESET = '\033[0m' #RESET COLOR
# 持有股票，記得改
my_stock = '3680 2645'.split(' ')

# 購買價格，記得改
buy_price = (np.array([0, 0]))
# 購買股數，記得改
stock_share = [51, 200]
all_money = 600000
# 自動下載ChromeDriver
service = ChromeService(executable_path=ChromeDriverManager().install())
# 關閉通知提醒
chrome_options = webdriver.ChromeOptions()
prefs = {"profile.default_content_setting_values.notifications" : 2}
chrome_options.add_experimental_option("prefs",prefs)
# 開啟瀏覽器
driver = webdriver.Chrome(service=service, options=chrome_options)
profit_df = pd.DataFrame([0],columns=['date'])

profit_df[['profit1','profit2','profit3','profit4','profit5',
                'profit6','profit7','profit8','profit9','profit10','profit11','Total Position',
                'Total Profit','Investment Growth Rate','assets']] = 0
profit_df[['n1','n2','Now Assets',600000]] = ''
profit_df['assets'] = all_money
column_name = profit_df.columns.values
print(profit_df)
while(1):
    excel = pd.read_excel('C:/Users/User/Desktop/投資檢討/資金成長600000(有試倉).xlsx')
    # excel.columns = column_name
    print(excel)
    total_position = 0
    for i,stock_ID in enumerate(my_stock):
        url = 'https://tw.stock.yahoo.com/quote/' + stock_ID
        try:
            driver.get(url)
            title = driver.find_element(by = By.ID, value = "qsp-overview-realtime-info").text
            #name = driver.find_element(by= By.CLASS_NAME, value = 'D(id)').text
            # time.sleep(T)
        except:
            continue
        # time.sleep(randint(1,3))
        print(f'stock_ID : {stock_ID}')
        title = title.split('\n')
        print(f'{title[1]}')
        name = title[0]
        data_time = title[1].split('：')[1].split(' ')[0].replace('/','')
        yesterday_close = float(title[16])
        now_price = float(title[4])
        
        if buy_price[i] > 0:
            buy_position = int(stock_share[i]*buy_price[i]*1.001)
            now_position = int(stock_share[i]*now_price)
            now_profit = now_position - buy_position
            total_position += now_position
            print(f'Buy/Now price : {round(1.001*buy_price[i],2)}/{now_price} | now position : {now_position} | bought position : {buy_position} |', end = ' ')
            if now_profit > 0:
                print(f'{bcolors.WIN}now profit : {now_profit} ({round(100*now_profit/buy_position,2)} %){bcolors.RESET}')
            else: 
                print(f'{bcolors.LOSE}now profit : {now_profit} ({round(100*now_profit/buy_position,2)} %){bcolors.RESET}')
        elif buy_price[i] < 0:
            last_position = int(stock_share[i]*yesterday_close)
            sold_position = int(stock_share[i]*(-1*buy_price[i])*0.997)
            now_profit = sold_position - last_position
            print(f'Sell/Now price : {round(-0.997*buy_price[i],2)}/{now_price} | sold position : {sold_position} | last position : {last_position} |', end = ' ')
            if now_profit > 0:
                print(f'{bcolors.WIN}now profit : {now_profit} ({round(100*now_profit/last_position,2)} %){bcolors.RESET}')
            else:
                print(f'{bcolors.LOSE}now profit : {now_profit} ({round(100*now_profit/last_position,2)} %){bcolors.RESET}')
        else:
            last_position = int(stock_share[i]*yesterday_close)
            now_position = int(stock_share[i]*now_price)
            now_profit = now_position-last_position
            total_position += now_position
            print(f'Now/Last Price : {now_price}/{yesterday_close} | now_position : {now_position} | last position : {last_position} |', end = ' ')
            if now_profit > 0:
                print(f'{bcolors.WIN}now profit : {now_profit} ({round(100*now_profit/last_position,2)} %){bcolors.RESET}')
            else:
                print(f'{bcolors.LOSE}now profit : {now_profit} ({round(100*now_profit/last_position,2)} %){bcolors.RESET}')
        
        # print(profit_df)
        profit_df.loc[0,column_name[i+1]] = now_profit
        profit_df['date'] = data_time
        
        print('----------------------------------------------------------------------------------------------')
    for i in profit_df.iloc[0,1:12]:
        print(i, type(i)) 
    if sum(profit_df.iloc[0,1:12].values) > 0:
        print(f'total profit : {bcolors.WIN}{sum(profit_df.iloc[0,1:12].values)}{bcolors.RESET}')
    else:
        print(f'total profit : {bcolors.LOSE}{sum(profit_df.iloc[0,1:12].values)}{bcolors.RESET}')
    
    profit_df['Total Profit'] = sum(profit_df.iloc[0,1:12].values)
    profit_df['Total Position'] = total_position
    profit_df['Investment Growth Rate'] = round(100*(profit_df['Total Profit']/all_money),3)
    for i in range(11):
        try:
            profit_df.iloc[0,i+1] = str(profit_df.iloc[0,i+1]) + f'(ID : {my_stock[i]})'
        except:
            profit_df.iloc[0,i+1] = 0
    print(profit_df)
    last_row_time = str(int(excel.iloc[-1]['date']))
    print(f'{bcolors.SHOW}Same Date : {last_row_time == profit_df.loc[0,"date"]}{bcolors.RESET}')

    if last_row_time == profit_df.loc[0,'date']:
        excel.iloc[-1] = profit_df.loc[0]
        excel.to_excel('C:/Users/User/Desktop/投資檢討/資金成長600000(有試倉).xlsx',index=False)
        print(excel)
    else:
        excel = pd.concat([excel,profit_df],ignore_index=True)
        excel.to_excel('C:/Users/User/Desktop/投資檢討/資金成長600000(有試倉).xlsx',index=False)
        print(excel)
    
    time.sleep(600)

# profit_df.to_excel('C:/Users/User/Desktop/投資檢討/資金成長.xlsx')
        