import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import yfinance as yf
from selenium.webdriver.common.by import By
from selenium import webdriver
import talib
# 設定顏色
class bcolors:
    OK = '\033[92m' #GREEN
    WARNING = '\033[93m' #YELLOW
    FAIL = '\033[91m' #RED
    RESET = '\033[0m' #RESET COLOR
# =====================rs plot.ipynb=====================
# 畫RS圖
def rsplot(ID, taiex, start_length=250, end_index = 1):
    try:
        stock =pd.read_csv('C:/Users/User/Desktop/StockInfoHub/Stock_Data_Collector/history_data/' + ID + '.TW.csv', encoding='utf-8-sig', parse_dates=['Date'], index_col=['Date'])
    except:
        stock =pd.read_csv('C:/Users/User/Desktop/StockInfoHub/Stock_Data_Collector/history_data/' + ID + '.TWO.csv', encoding='utf-8-sig', parse_dates=['Date'], index_col=['Date'])
    index = stock.index.values[-start_length:-end_index]
    index_stock = stock.loc[index]
    y_taiex = taiex.loc[index, 'Adj Close']
    y_stock = stock.loc[index, 'RS 250rate']
    y_stock2 = stock.loc[index, 'RS 50rate']
    y_stock3 = stock.loc[index, 'RS 20rate']
    y_volume = stock.loc[index, 'Volume']
    y_price = stock.loc[index, 'Adj Close']
    plt.rcParams['axes.facecolor'] = '#F5F5F5'  # 将背景色设为浅灰色
    plt.rcParams['figure.facecolor'] = '#F5F5F5'  # 将图形的背景色设为浅灰色
    plt.rcParams['font.size'] = 20  # 设置字体大小为12
    fig = plt.figure(figsize=(32, 16))  # 指定宽度为8英寸，高度为6英寸
    # 加權指數
    ax1 = fig.add_subplot(111)
    line1, = ax1.plot(range(len(y_taiex)),y_taiex, linestyle='-', color='#118AB2', linewidth=2, label='TAIEX')
    ax1.set_ylabel('TAIEX', color='#118AB2')  # 设置第一个Y轴的标签和颜色
    ax1.tick_params('y', color='#118AB2')  # 设置第一个Y轴的刻度颜色
    # RS rate
    ax2 = ax1.twinx()
    line2, = ax2.plot(range(len(y_stock)), y_stock, linestyle='--', color='#EF476F', linewidth=2, label='RS 250rate')
    line3, = ax2.plot(range(len(y_stock2)), y_stock2, linestyle='--', color='#06D6A0', linewidth=2, label='RS 50rate')
    line6, = ax2.plot(range(len(y_stock3)), y_stock3, linestyle='--', color='#B0C4DE', linewidth=2, label='RS 20rate')
    # RS MAX
    scatter1 = ax2.scatter(np.arange(0,len(y_price))[index_stock['RS 250MA is 10MAX']], index_stock.loc[index_stock['RS 250MA is 10MAX'],'RS 250rate'].values, label='RS is MAX')
    ax2.text(len(y_stock)+1, y_stock[-1], str(round(y_stock[-1],1)), color='#EF476F')
    ax2.text(len(y_stock2)+1, y_stock2[-1], str(round(y_stock2[-1],1)), color='#06D6A0')
    ax2.text(len(y_stock3)+1, y_stock3[-1], str(round(y_stock3[-1],1)), color='#B0C4DE')
    # ax2.text(len(y_stock3)+1, y_stock3[-1], str(round(y_stock3[-1],1)), color='#C0C0C0')
    ax2.set_yticks(np.arange(0,100,5))
    # ax2.set_xticks(np.arange(0,250,10))
    # print(list(map(lambda x:x.split('T')[0].split('-')[1], index.astype(str)[::10])))
    xticks = list(map(lambda x:f"{x.split('T')[0]}", index.astype(str)[::20]))
    xticks.append(index.astype(str)[-1].split('T')[0])
    ax1.set_xticks(np.append(np.arange(0,start_length-end_index+1,20), start_length-end_index), xticks, rotation = 45, ha = 'right')
    # ax2.set_xticklabels(list(map(lambda x:x.split('T')[0], index.astype(str)[::10])), ha = 'right')
    ax2.set_ylabel('RS Rate', color='#EF476F')  # 设置第二个Y轴的标签和颜色
    ax2.tick_params('y', color='#EF476F')  # 设置第二个Y轴的刻度颜色
    # 成交量
    ax3 = ax1.twinx()
    line4 = ax3.bar(range(len(y_volume)), y_volume, linestyle='--', color='#444444', linewidth=1, label='Volume')
    ax3.set_yticks([0, max(y_volume)*7])
    ax3.set_axis_off()
    # 股票收盤價
    ax4 = ax1.twinx()
    line5, = ax4.plot(range(len(y_price)), y_price, linestyle='-', color='#FFA500', linewidth=2, label='Close Price')
    ax4.set_axis_off()

    # 显示图形
    plt.title(f'{ID} RS Rate(SMA) Plot')
    plt.xlabel('Date')
    ax1.grid(axis='x')
    ax2.grid()
    ax3.grid()
    fig.legend(handles = [line1, line2, line3, line6, line4, line5, scatter1])
    plt.show()
# 畫ERS圖
def EMA_rsplot(ID, taiex, start_length=250, end_index = 1, plot_ERS_MACD = False):
    try:
        stock =pd.read_csv('C:/Users/User/Desktop/stock/data_test/' + ID + '.TW.csv', encoding='utf-8-sig', parse_dates=['Date'], index_col=['Date'])
    except:
        stock = pd.read_csv('C:/Users/User/Desktop/stock/data_test/' + ID + '.TWO.csv', encoding='utf-8-sig', parse_dates=['Date'], index_col=['Date'])
    if end_index == 0:
        index = stock.index.values[-start_length:]
    else:
        index = stock.index.values[-start_length:-end_index]
    index = [i for i in index if i in taiex.index]
    index_stock = stock.loc[index]
    
    y_taiex = taiex.loc[index, 'Adj Close']
    y_stock = stock.loc[index, 'ERS_rate_250']
    y_stock2 = stock.loc[index, 'ERS_rate_50']
    y_stock3 = stock.loc[index, 'ERS_rate_20']
    y_volume = stock.loc[index, 'Volume']
    y_price = stock.loc[index, 'Adj Close']
    plt.rcParams['axes.facecolor'] = '#F5F5F5'  # 将背景色设为浅灰色
    plt.rcParams['figure.facecolor'] = '#F5F5F5'  # 将图形的背景色设为浅灰色
    plt.rcParams['font.size'] = 20  # 设置字体大小为12
    fig = plt.figure(figsize=(34, 16))  # 指定宽度为8英寸，高度为6英寸
    # 加權指數
    ax1 = fig.add_subplot(111)
    line1, = ax1.plot(range(len(y_taiex)),y_taiex, linestyle='-', color='#118AB2', linewidth=1, label='TAIEX')
    ax1.set_ylabel('TAIEX', color='#118AB2')  # 设置第一个Y轴的标签和颜色
    ax1.tick_params('y', color='#118AB2')  # 设置第一个Y轴的刻度颜色
    # RS rate
    ax2 = ax1.twinx()
    line2, = ax2.plot(range(len(y_stock)), y_stock, linestyle='--', color='#EF476F', linewidth=2, label='250ERS')
    line3, = ax2.plot(range(len(y_stock2)), y_stock2, linestyle='--', color='#06D6A0', linewidth=1, label='50ERS')
    line4, = ax2.plot(range(len(y_stock3)), y_stock3, linestyle='--', color='#B0C4DE', linewidth=1, label='20ERS')
    # RS MAX
    scatter1 = ax2.scatter(np.arange(0,len(y_price))[index_stock['RS 250EMA is 10MAX']], 
                           index_stock.loc[index_stock['RS 250EMA is 10MAX'],'ERS_rate_250'].values+1, label='ERS>10MAX', color='#B0C4DE', marker = 'v', s = 80)
    scatter2 = ax2.scatter(np.arange(0,len(y_price))[index_stock['RS 250EMA is 50MAX']], 
                           index_stock.loc[index_stock['RS 250EMA is 50MAX'],'ERS_rate_250'].values+2, label='ERS>50MAX', color = '#06D6A0' , marker = 'v', s = 80)
    scatter3 = ax2.scatter(np.arange(0,len(y_price))[index_stock['RS 250EMA is 250MAX']], 
                           index_stock.loc[index_stock['RS 250EMA is 250MAX'],'ERS_rate_250'].values+3, label='ERS>250MAX', color = '#EF476F' , marker = 'v', s = 80)
    max_y = max([y_stock[-1], y_stock2[-1], y_stock3[-1]])
    y_text = [y_stock, '#EF476F']
    y_text2 = [y_stock2, '#06D6A0']
    y_text3 = [y_stock3, '#B0C4DE']
    # sort y_text by y_stock
    y_text = sorted([y_text, y_text2, y_text3], key=lambda x:x[0][-1], reverse=True)
    for i in range(3):
        ax2.text(len(y_stock)+2, max_y+5-i*5, str(round(y_text[i][0][-1],1)), color=y_text[i][1])

    # ax2.text(len(y_stock)+1, max_y+20, str(round(y_stock[-1],1)), color='#EF476F')
    # ax2.text(len(y_stock2)+1, max_y+15, str(round(y_stock2[-1],1)), color='#06D6A0')
    # ax2.text(len(y_stock3)+1, max_y+10, str(round(y_stock3[-1],1)), color='#C0C0C0')
    ax2.set_yticks(np.arange(0,100,5))
    # ax2.set_xticks(np.arange(0,250,10))
    # print(list(map(lambda x:x.split('T')[0].split('-')[1], index.astype(str)[::10])))


    # xticks = list(map(lambda x:f"{x.split('T')[0]}", index.astype(str)[::20]))
    # xticks.append(index.astype(str)[-1].split('T')[0])

    xticks = list(map(lambda x:f"{str(x).split('T')[0]}", index[::20]))
    xticks.append(str(index[-1]).split('T')[0])



    ax1.set_xticks(np.append(np.arange(0,start_length-end_index+1,20), start_length-end_index), xticks, rotation = 45, ha = 'right')
    # ax2.set_xticklabels(list(map(lambda x:x.split('T')[0], index.astype(str)[::10])), ha = 'right')
    ax2.set_ylabel('RS Rate', color='#EF476F')  # 设置第二个Y轴的标签和颜色
    ax2.tick_params('y', color='#EF476F')  # 设置第二个Y轴的刻度颜色
    # 成交量
    ax3 = ax1.twinx()
    line5 = ax3.bar(range(len(y_volume)), y_volume, linestyle='--', color='#444444', linewidth=1, label='Volume')
    ax3.set_yticks([0, max(y_volume)*7])
    ax3.set_axis_off()
    # 股票收盤價
    ax4 = ax1.twinx()
    line6, = ax4.plot(range(len(y_price)), y_price, linestyle='-', color='#FFA500', linewidth=1, label='Close')
    ax4.set_axis_off()

    if plot_ERS_MACD:
        ax5 = ax1.twinx()
        ## close price MACD
        close_MACD = talib.MACD(y_price, fastperiod=12, slowperiod=26, signalperiod=9)
        ## plot MACD hist
        # bar1 = ax5.bar(range(len(close_MACD[2])), close_MACD[2], color = 'green', alpha = 0.5, label = 'Close MACD hist')

        ## close price MACD hist bar diff with yesterday
        close_MACD_diff = np.diff(close_MACD[2])
        bar1 = ax5.bar(range(1,len(close_MACD_diff)+1), close_MACD_diff, color = 'green', alpha = 0.5, label = 'Close MACD hist diff with yesterday')
        
        

        # ERS MACD
        
        ERS_MACD = talib.MACD(y_stock, fastperiod=12, slowperiod=26, signalperiod=9)
        ## plot MACD hist
        # bar2 = ax5.bar(range(len(ERS_MACD[2])), ERS_MACD[2], color = 'gray', alpha = 0.5, label = 'MACD hist')

        ## ERS MACD hist bar diff with yesterday
        ERS_MACD_diff = np.diff(ERS_MACD[2])
        bar2 = ax5.bar(range(1,len(ERS_MACD_diff)+1), ERS_MACD_diff, color = 'gray', alpha = 0.5, label = 'ERS MACD hist diff with yesterday')
        

        ax5.set_axis_off()

        
        

    # 显示图形
    plt.title(f'{ID} RS Rate(EMA) Plot')
    plt.xlabel('Date')
    ax1.grid(axis='x')
    ax2.grid()
    ax3.grid()
    if plot_ERS_MACD:
        fig.legend(handles = [line1, line2, line3, line4, line5, line6, scatter1, scatter2, scatter3, bar1, bar2])
    else:
        fig.legend(handles = [line1, line2, line3, line4, line5, line6, scatter1, scatter2, scatter3])
    plt.show()

# =====================fundamental.ipynb=====================
# 畫出要查詢股票的基本面
def plot_all(service, chrome_options, stockID, season = 8):
    fsize = 20
    fsize2 = 14
    # global driver
    plt.rcParams['axes.facecolor'] = '#F5F5F5'  # 将背景色设为浅灰色
    plt.rcParams['figure.facecolor'] = '#F5F5F5'  # 将图形的背景色设为浅灰色
    ##存貨
    url = f'https://histock.tw/stock/{stockID}/%E7%87%9F%E9%81%8B%E9%80%B1%E8%BD%89'
    print(f'股票代碼 : {stockID}')
    try:
        driver.get(url)
        title = driver.find_element(by = By.TAG_NAME, value = "tbody").text
    except Exception as e:
        print(f'{bcolors.WARNING}{e}{bcolors.RESET}')
        print(f'{bcolors.WARNING}Close Google Failed{bcolors.RESET}')
        try:
            driver.close()
            driver = webdriver.Chrome(service=service, chrome_options=chrome_options)
        except:
            pass
        return [0,0]
        # service = ChromeService(executable_path=ChromeDriverManager().install())
        # driver = webdriver.Chrome(service=service, chrome_options=chrome_options)
    text = title.split('\n')[1:-1]
    column = title.split('\n')[0].split(' ')[1:]
    text_list = []
    index = []
    for i,t in enumerate(text):
        text_list.append(t.split(' ')[1:])
        index.append(t.split(' ')[0])
    IT = pd.DataFrame(text_list, index=index, columns=column)
    date = IT.index.values[0]
    IT_list = IT['存貨週轉(次)'].values
    IT_list = IT_list[:season+8]
    IT_list = list(map(lambda x : x.replace(',',''),IT_list))
    IT_list = list(map(float, IT_list))
    ITyoy = []
    for i in range(season+4):
        if IT_list[i]>IT_list[i+4]:
            ITyoy.append(abs((IT_list[i]-IT_list[i+4])/IT_list[i+4])*100)
        else:
            ITyoy.append(-1*abs((IT_list[i]-IT_list[i+4])/IT_list[i+4])*100)
    avg_ITyoy = []
    avgITyoy_growth = []
    for i in range(season+3):
        # 兩季存貨成長率平均
        avg_ITyoy.append((ITyoy[i]+ITyoy[i+1])/2)
    for i in range(season+2):
        # 兩季存貨成長率平均相減
        if avg_ITyoy[i] > avg_ITyoy[i+1]: 
            avgITyoy_growth.append(((avg_ITyoy[i]-avg_ITyoy[i+1])))
        else:
            avgITyoy_growth.append(((avg_ITyoy[i]-avg_ITyoy[i+1])))
    IT_df = pd.DataFrame([IT_list[:season+4], ITyoy, avg_ITyoy, avgITyoy_growth],index=['IT', 'IT年增率', 'IT年增率2季平均', 'IT年增率2季平均成長率'], columns=range(1,season+5))
    Ix4,Iy4 = range(len(np.flip(IT_df.loc['IT'].values)[-season:])),np.flip(IT_df.loc['IT'].values)[-season:]
    colors = np.where(Iy4 >= 0, 'g', 'orange')
    plt.figure(figsize=(34,17))
    plt.subplot(4,4,1)
    for a,b in zip(Ix4,Iy4):
        plt.text(a, b+0.01, '%.2f' % b, ha='center', va= 'bottom',fontsize=fsize2)
    plt.bar(Ix4,Iy4, color = colors)
    plt.title(f'ID:{stockID}({date})      IT', fontsize=fsize, loc='left')
    Ix3,Iy3 = range(len(np.flip(IT_df.loc['IT年增率'].values)[-season:])),np.flip(IT_df.loc['IT年增率'].values)[-season:]
    colors = np.where(Iy3 >= 0, 'g', 'orange')
    plt.subplot(4,4,2)
    for a,b in zip(Ix3,Iy3):
        plt.text(a, b+0.05, '%.1f' % b, ha='center', va= 'bottom',fontsize=fsize2)
    plt.bar(Ix3,Iy3, color = colors)
    plt.title('IT yoy', fontsize=fsize)
    plt.subplot(4,4,3)
    Ix2,Iy2 = range(len(np.flip(IT_df.loc['IT年增率2季平均'].values)[-season:])),np.flip(IT_df.loc['IT年增率2季平均'].values)[-season:]
    colors = np.where(Iy2 >= 0, 'g', 'orange')
    for a,b in zip(Ix2,Iy2):
        plt.text(a, b+0.05, '%.1f' % b, ha='center', va= 'bottom',fontsize=fsize2)
    plt.bar(Ix2,Iy2, color = colors)
    plt.title('IT yoy 2Q AVG', fontsize=fsize)
    plt.subplot(4,4,4)
    Ix,Iy = range(len(np.flip(IT_df.loc['IT年增率2季平均成長率'].values)[-season:])),np.flip(IT_df.loc['IT年增率2季平均成長率'].values)[-season:]
    colors = np.where(Iy >= 0, 'g', 'orange')
    for a,b in zip(Ix,Iy):
        plt.text(a, b+0.05, '%.1f' % b, ha='center', va= 'bottom',fontsize=fsize2)
    plt.bar(Ix,Iy, color = colors)
    plt.title('Growth of IT yoy 2Q AVG', fontsize=fsize)
    ##EPS
    url2 = f'https://histock.tw/stock/{stockID}/%E6%AF%8F%E8%82%A1%E7%9B%88%E9%A4%98'
    try:
        driver.get(url2)
        title = driver.find_element(by = By.TAG_NAME, value = "tbody").text
    except Exception as e:
        print(f'{bcolors.WARNING}{e}{bcolors.RESET}')
        print(f'{bcolors.WARNING}Close Google Failed{bcolors.RESET}')
        pass
        # service = ChromeService(executable_path=ChromeDriverManager().install())
        # driver = webdriver.Chrome(service=service, chrome_options=chrome_options)
    text = title.split('\n')[1:-1]
    column = title.split('\n')[0].split(' ')[1:]
    text_list = []
    index = []
    for i,t in enumerate(text):
        text_list.append(t.split(' ')[1:])
        index.append(t.split(' ')[0])
    EPS = pd.DataFrame(text_list, index=index, columns=column.extend([' ',' ',' ',' ',' ',' ',' ',' ',' '])).replace('-','n')
    EPS_list = []
    for i in EPS.transpose().values:
        EPS_list.extend(i[i!='n'])
    EPS_list = EPS_list[-season-8:][::-1]
    EPS_list = list(map(float, EPS_list))
    EPSyoy = []
    for i in range(season+4):
        if EPS_list[i]>EPS_list[i+4]:
            try:
                EPSyoy.append(abs((EPS_list[i]-EPS_list[i+4])/EPS_list[i+4])*100)
            except:
                EPSyoy.append(0)
        else:
            try:
                EPSyoy.append(-1*abs((EPS_list[i]-EPS_list[i+4])/EPS_list[i+4])*100)
            except:
                EPSyoy.append(0)
    avg_EPSyoy = []
    avgEPSyoy_growth = []
    for i in range(season+3):
        # 兩季EPS成長率平均
        avg_EPSyoy.append((EPSyoy[i]+EPSyoy[i+1])/2)
    for i in range(season+2):
        # 兩季EPS成長率平均相減
        if avg_EPSyoy[i] > avg_EPSyoy[i+1]: 
            avgEPSyoy_growth.append(((avg_EPSyoy[i]-avg_EPSyoy[i+1])))
        else:
            avgEPSyoy_growth.append(((avg_EPSyoy[i]-avg_EPSyoy[i+1])))
    EPS_df = pd.DataFrame([EPS_list[:season+4], EPSyoy, avg_EPSyoy, avgEPSyoy_growth],index=['EPS', 'EPS年增率', 'EPS年增率2季平均', 'EPS年增率2季平均成長率'], columns=range(1,season+5))
    x4,y4 = range(len(np.flip(EPS_df.loc['EPS'].values)[-season:])),np.flip(EPS_df.loc['EPS'].values)[-season:]
    colors = np.where(y4 >= 0, 'g', 'orange')
    plt.subplot(4,4,5)
    for a,b in zip(x4,y4):
        plt.text(a, b+0.01, '%.2f' % b, ha='center', va= 'bottom',fontsize=fsize2)
    plt.bar(x4,y4, color = colors)
    plt.title('EPS', fontsize=fsize)
    x3,y3 = range(len(np.flip(EPS_df.loc['EPS年增率'].values)[-season:])),np.flip(EPS_df.loc['EPS年增率'].values)[-season:]
    colors = np.where(y3 >= 0, 'g', 'orange')
    plt.subplot(4,4,6)
    for a,b in zip(x3,y3):
        plt.text(a, b+0.05, '%.1f' % b, ha='center', va= 'bottom',fontsize=fsize2)
    plt.bar(x3,y3, color = colors)
    plt.title('EPS yoy', fontsize=fsize)
    plt.subplot(4,4,7)
    x2,y2 = range(len(np.flip(EPS_df.loc['EPS年增率2季平均'].values)[-season:])),np.flip(EPS_df.loc['EPS年增率2季平均'].values)[-season:]
    colors = np.where(y2 >= 0, 'g', 'orange')
    for a,b in zip(x2,y2):
        plt.text(a, b+0.05, '%.1f' % b, ha='center', va= 'bottom',fontsize=fsize2)
    plt.bar(x2,y2, color = colors)
    plt.title('EPS yoy 2Q AVG', fontsize=fsize)
    plt.subplot(4,4,8)
    x,y = range(len(np.flip(EPS_df.loc['EPS年增率2季平均成長率'].values)[-season:])),np.flip(EPS_df.loc['EPS年增率2季平均成長率'].values)[-season:]
    colors = np.where(y >= 0, 'g', 'orange')
    for a,b in zip(x,y):
        plt.text(a, b+0.05, '%.1f' % b, ha='center', va= 'bottom',fontsize=fsize2)
    plt.bar(x,y, color = colors)
    plt.title('Growth of EPS yoy 2Q AVG', fontsize=fsize)
    ## 營收
    url3 = f'https://histock.tw/stock/financial.aspx?no={stockID}&t=5&st=4&q=2'
    try:
        driver.get(url3)
        title = driver.find_element(by = By.TAG_NAME, value = "tbody").text
    except Exception as e:
        print(f'{bcolors.WARNING}{e}{bcolors.RESET}')
        print(f'{bcolors.WARNING}Close Google Failed{bcolors.RESET}')
        pass
        # service = ChromeService(executable_path=ChromeDriverManager().install())
        # driver = webdriver.Chrome(service=service, chrome_options=chrome_options)
    text = title.replace('%','').split('\n')
    column = title.split('\n')[0].split(' ')
    text_list = []
    index = []
    for i,t in enumerate(text):
        text_list.append(t.split(' '))
    revenue = pd.DataFrame(text_list)
    revenue1 = revenue.loc[1:,:2]
    revenue2 = revenue.loc[1:,3:]
    revenue2.columns = [0,1,2]
    revenue = pd.concat([revenue1, revenue2], axis=0, ignore_index=True)
    # revenue.columns = column[0:3]
    avg_revenueyoy = []
    revenueyoy = revenue.iloc[:season, 1].astype(float)
    for i in range(season+1):
        avg_revenueyoy.append(np.mean(revenue.iloc[[i,i+1],1].astype(float)))
    avgrevenueyoy_growth = []
    for i in range(season):
        avgrevenueyoy_growth.append(avg_revenueyoy[i]-avg_revenueyoy[i+1])
    revenue_df = pd.DataFrame([np.zeros(season), revenueyoy, avg_revenueyoy, avgrevenueyoy_growth],index=['營收', '營收年增率', '營收年增率2季平均', '營收年增率2季平均成長率'])
    Rx4,Ry4 = range(len(np.flip(revenue_df.loc['營收',:season-1].values[::-1]))),(revenue_df.loc['營收',:season-1].values[::-1])
    colors = np.where(Ry4 >= 0, 'g', 'orange')
    plt.subplot(4,4,9)
    # for a,b in zip(Rx4,Ry4):
    #     plt.text(a, b+0.01, '%.2f' % b, ha='center', va= 'bottom',fontsize=fsize2)
    # plt.bar(Rx4,Ry4, color = colors)
    # plt.title('Revenue', fontsize=fsize)
    Rx3,Ry3 = range(len((revenue_df.loc['營收年增率',:season-1].values[::-1]))),(revenue_df.loc['營收年增率', :season-1].values[::-1])
    colors = np.where(Ry3 >= 0, 'g', 'orange')
    plt.subplot(4,4,10)
    for a,b in zip(Rx3,Ry3):
        plt.text(a, b+0.05, '%.1f' % b, ha='center', va= 'bottom',fontsize=fsize2)
    plt.bar(Rx3,Ry3, color = colors)
    plt.title('Revenue yoy', fontsize=fsize)
    plt.subplot(4,4,11)
    Rx2,Ry2 = range(len((revenue_df.loc['營收年增率2季平均', :season-1].values[::-1]))),(revenue_df.loc['營收年增率2季平均', :season-1].values[::-1])
    colors = np.where(Ry2 >= 0, 'g', 'orange')
    for a,b in zip(Rx2,Ry2):
        plt.text(a, b+0.05, '%.1f' % b, ha='center', va= 'bottom',fontsize=fsize2)
    plt.bar(Rx2,Ry2, color = colors)
    plt.title('Revenue yoy 2Q AVG', fontsize=fsize)
    plt.subplot(4,4,12)
    Rx,Ry = range(len((revenue_df.loc['營收年增率2季平均成長率',:season-1].values[::-1]))),(revenue_df.loc['營收年增率2季平均成長率',:season-1].values[::-1])
    colors = np.where(Ry >= 0, 'g', 'orange')
    for a,b in zip(Rx,Ry):
        plt.text(a, b+0.05, '%.1f' % b, ha='center', va= 'bottom',fontsize=fsize2)
    plt.bar(Rx,Ry, color = colors)
    plt.title('Growth of Revenue yoy 2Q AVG', fontsize=fsize)
    ##現金流
    url4 = f'https://histock.tw/stock/{stockID}/%E7%8F%BE%E9%87%91%E6%B5%81%E9%87%8F%E8%A1%A8'
    try:
        driver.get(url4)
        title = driver.find_element(by = By.TAG_NAME, value = "tbody").text
    except Exception as e:
        print(f'{bcolors.WARNING}{e}{bcolors.RESET}')
        print(f'{bcolors.WARNING}Close Google Failed{bcolors.RESET}')
        try:
            driver.close()
            driver = webdriver.Chrome(service=service, chrome_options=chrome_options)
        except:
            pass
        # service = ChromeService(executable_path=ChromeDriverManager().install())
        # driver = webdriver.Chrome(service=service, chrome_options=chrome_options)
    text = title.replace(',', '').split('\n')
    column = title.split('\n')[0].split(' ')[1:]
    CF_df = pd.DataFrame(list(map(lambda x:x.split(' '), text[1:])), columns=text[0].split(' '))
    CF_index = CF_df['年度/季別'].values
    CF_df.drop('年度/季別', axis=1, inplace=True)
    CF_df.index = CF_index
    CF_df = CF_df.astype(float)/1000
    years = int(season/4)
    CF_sum_year = []
    for year in range(years):
        CF_sum_year.append(sum(CF_df.iloc[(year)*4:(year+1)*4]['自由現金流'].values))
    plt.subplot(4,4,13)
    plt.title(f'ID:{stockID}({CF_df.index.values[0]})    CF', fontsize=fsize, loc='left')
    CFx,CFy = range(len(np.flip(CF_df.iloc[:season]['自由現金流'].values))),np.flip(CF_df.iloc[:season]['自由現金流'].values)
    colors = np.where(CFy >= 0, 'g', 'orange')
    for a,b in zip(CFx,CFy):
        plt.text(a, b+0.05, '%.1f' % b, ha='center', va= 'bottom',fontsize=fsize2)
    plt.bar(CFx,CFy, color = colors)
    plt.subplot(4,4,14)
    plt.title('CF Sum of Year', fontsize=fsize)
    CFx2,CFy2 = range(len(np.flip(CF_sum_year))),np.flip(CF_sum_year)
    colors = np.where(CFy2 >= 0, 'g', 'orange')
    for a,b in zip(CFx2,CFy2):
        plt.text(a, b+0.05, '%.1f' % b, ha='center', va= 'bottom',fontsize=fsize2)
    plt.bar(CFx2,CFy2, color = colors)
    plt.xticks([0,1,2],[0,1,2])
    plt.subplot(4,4,15)
    plt.title('--', fontsize=fsize)
    plt.subplot(4,4,16)
    plt.title('--', fontsize=fsize)
    # plt.show()
    return [y3, y2]
# 用基本面篩選股票
def choose_all(service, chrome_options, stockID, season = 8):
    fsize = 20
    fsize2 = 14
    global driver
    plt.rcParams['axes.facecolor'] = '#F5F5F5'  # 将背景色设为浅灰色
    plt.rcParams['figure.facecolor'] = '#F5F5F5'  # 将图形的背景色设为浅灰色
    ##存貨
    url = f'https://histock.tw/stock/{stockID}/%E7%87%9F%E9%81%8B%E9%80%B1%E8%BD%89'
    print(f'股票代碼 : {stockID}')
    try:
        driver.get(url)
        title = driver.find_element(by = By.TAG_NAME, value = "tbody").text
    except Exception as e:
        print(f'{bcolors.WARNING}{e}{bcolors.RESET}')
        print(f'{bcolors.WARNING}Close Google Failed{bcolors.RESET}')
        try:
            driver.close()
            driver = webdriver.Chrome(service=service, chrome_options=chrome_options)
        except:
            pass
        return [0,0]
        # service = ChromeService(executable_path=ChromeDriverManager().install())
        # driver = webdriver.Chrome(service=service, chrome_options=chrome_options)
    text = title.split('\n')[1:-1]
    column = title.split('\n')[0].split(' ')[1:]
    text_list = []
    index = []
    for i,t in enumerate(text):
        text_list.append(t.split(' ')[1:])
        index.append(t.split(' ')[0])
    IT = pd.DataFrame(text_list, index=index, columns=column)
    date = IT.index.values[0]
    IT_list = IT['存貨週轉(次)'].values
    IT_list = IT_list[:season+8]
    IT_list = list(map(lambda x : x.replace(',',''),IT_list))
    IT_list = list(map(float, IT_list))
    ITyoy = []
    for i in range(season+4):
        if IT_list[i]>IT_list[i+4]:
            ITyoy.append(abs((IT_list[i]-IT_list[i+4])/IT_list[i+4])*100)
        else:
            ITyoy.append(-1*abs((IT_list[i]-IT_list[i+4])/IT_list[i+4])*100)
    avg_ITyoy = []
    avgITyoy_growth = []
    for i in range(season+3):
        # 兩季存貨成長率平均
        avg_ITyoy.append((ITyoy[i]+ITyoy[i+1])/2)
    for i in range(season+2):
        # 兩季存貨成長率平均相減
        if avg_ITyoy[i] > avg_ITyoy[i+1]: 
            avgITyoy_growth.append(((avg_ITyoy[i]-avg_ITyoy[i+1])))
        else:
            avgITyoy_growth.append(((avg_ITyoy[i]-avg_ITyoy[i+1])))
    IT_df = pd.DataFrame([IT_list[:season+4], ITyoy, avg_ITyoy, avgITyoy_growth],index=['IT', 'IT年增率', 'IT年增率2季平均', 'IT年增率2季平均成長率'], columns=range(1,season+5))
    Ix4,Iy4 = range(len(np.flip(IT_df.loc['IT'].values)[-season:])),np.flip(IT_df.loc['IT'].values)[-season:]
    Ix3,Iy3 = range(len(np.flip(IT_df.loc['IT年增率'].values)[-season:])),np.flip(IT_df.loc['IT年增率'].values)[-season:]
    Ix2,Iy2 = range(len(np.flip(IT_df.loc['IT年增率2季平均'].values)[-season:])),np.flip(IT_df.loc['IT年增率2季平均'].values)[-season:]
    Ix,Iy = range(len(np.flip(IT_df.loc['IT年增率2季平均成長率'].values)[-season:])),np.flip(IT_df.loc['IT年增率2季平均成長率'].values)[-season:]
    ##EPS
    url2 = f'https://histock.tw/stock/{stockID}/%E6%AF%8F%E8%82%A1%E7%9B%88%E9%A4%98'
    try:
        driver.get(url2)
        title = driver.find_element(by = By.TAG_NAME, value = "tbody").text
    except Exception as e:
        print(f'{bcolors.WARNING}{e}{bcolors.RESET}')
        print(f'{bcolors.WARNING}Close Google Failed{bcolors.RESET}')
        pass
        # service = ChromeService(executable_path=ChromeDriverManager().install())
        # driver = webdriver.Chrome(service=service, chrome_options=chrome_options)
    text = title.split('\n')[1:-1]
    column = title.split('\n')[0].split(' ')[1:]
    text_list = []
    index = []
    for i,t in enumerate(text):
        text_list.append(t.split(' ')[1:])
        index.append(t.split(' ')[0])
    EPS = pd.DataFrame(text_list, index=index, columns=column.extend([' ',' ',' ',' ',' ',' ',' ',' ',' '])).replace('-','n')
    EPS_list = []
    for i in EPS.transpose().values:
        EPS_list.extend(i[i!='n'])
    EPS_list = EPS_list[-season-8:][::-1]
    EPS_list = list(map(float, EPS_list))
    EPSyoy = []
    for i in range(season+4):
        if EPS_list[i]>EPS_list[i+4]:
            try:
                EPSyoy.append(abs((EPS_list[i]-EPS_list[i+4])/EPS_list[i+4])*100)
            except:
                EPSyoy.append(0)
        else:
            try:
                EPSyoy.append(-1*abs((EPS_list[i]-EPS_list[i+4])/EPS_list[i+4])*100)
            except:
                EPSyoy.append(0)
    avg_EPSyoy = []
    avgEPSyoy_growth = []
    for i in range(season+3):
        # 兩季EPS成長率平均
        avg_EPSyoy.append((EPSyoy[i]+EPSyoy[i+1])/2)
    for i in range(season+2):
        # 兩季EPS成長率平均相減
        if avg_EPSyoy[i] > avg_EPSyoy[i+1]: 
            avgEPSyoy_growth.append(((avg_EPSyoy[i]-avg_EPSyoy[i+1])))
        else:
            avgEPSyoy_growth.append(((avg_EPSyoy[i]-avg_EPSyoy[i+1])))
    EPS_df = pd.DataFrame([EPS_list[:season+4], EPSyoy, avg_EPSyoy, avgEPSyoy_growth],index=['EPS', 'EPS年增率', 'EPS年增率2季平均', 'EPS年增率2季平均成長率'], columns=range(1,season+5))
    x4,y4 = range(len(np.flip(EPS_df.loc['EPS'].values)[-season:])),np.flip(EPS_df.loc['EPS'].values)[-season:]
    x3,y3 = range(len(np.flip(EPS_df.loc['EPS年增率'].values)[-season:])),np.flip(EPS_df.loc['EPS年增率'].values)[-season:]
    x2,y2 = range(len(np.flip(EPS_df.loc['EPS年增率2季平均'].values)[-season:])),np.flip(EPS_df.loc['EPS年增率2季平均'].values)[-season:]
    x,y = range(len(np.flip(EPS_df.loc['EPS年增率2季平均成長率'].values)[-season:])),np.flip(EPS_df.loc['EPS年增率2季平均成長率'].values)[-season:]
    
    return [y3, y2]
