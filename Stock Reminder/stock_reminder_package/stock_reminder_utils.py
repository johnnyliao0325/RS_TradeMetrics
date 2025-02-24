import yfinance as yf

# 設定顏色
class bcolors:
    OK = '\033[92m' #GREEN
    WARNING = '\033[93m' #YELLOW
    FAIL = '\033[91m' #RED
    RESET = '\033[0m' #RESET COLOR
# =====================stocknotify(TW).py=====================
# 50日均量計算
def volume_avg(stockID):
    ticker = str(stockID) + '.TW'
    ticker_obj = yf.Ticker(ticker)
    hist = ticker_obj.history(period="3mo")
    avg_volume = hist["Volume"].mean()/1000
    if avg_volume != avg_volume:
        ticker = str(ticker) + 'O'
        ticker_obj = yf.Ticker(ticker)
        hist = ticker_obj.history(period="3mo")
        avg_volume = hist["Volume"].mean()/1000
    return str(avg_volume)
#預估成交量
def estimate_volume(hour, minutes, vol):
    '''
    Parameters
    ----------
    hour : int
        現在時間的小時
    min : int
        現在時間的分鐘
    vol : int
        現在時間的成交量
    Returns
    -------
    str
        預估成交量
    '''
    # 定義時間區間、分鐘區間、預估倍數
    hour_range = [9, 10, 11, 12, 13]
    min_range = [0, 15, 30, 45]
    estimate_num = [8, 5, 4, 3, 2.5, 2.2, 2, 1.8, 1.7, 1.6, 1.5, 1.45, 1.38, 1.32, 1.25, 1.17, 1.1, 1]
    # 計算預估成交量
    if hour not in hour_range:
        return str(vol * estimate_num[-1])
    hour_index = hour_range.index(hour)
    min_index = minutes // 15
    if min_index >= len(min_range): 
        min_index = len(min_range) - 1
    # 透過時間區間、分鐘區間計算預估成交量
    total_index = hour_index * len(min_range) + min_index
    total_index = min(total_index, len(estimate_num) - 1)
    return str(vol * estimate_num[total_index])
# 倉位計算
def position(all_money,confidence,number_of_stocks,price,stop_loss):
    ## 總投資金額
    all_money = all_money
    ## 信心指數
    confidence = confidence
    ## string
    ## 市價
    market_price = price
    ## 停損點
    stop_loss_point = stop_loss
    ## 停損%數
    stop_loss_per = round((market_price-stop_loss_point)/market_price, 4)
    ## 可承擔金額
    afford_loss = all_money*confidence/(number_of_stocks*100)
    ## 投資金額
    invest_money = afford_loss/stop_loss_per
    # print('\n' + f'市價 : {market_price}, 停損點 : {stop_loss_point}, 停損%數 : {stop_loss_per*100}%, \
    # 可承擔損失 : {afford_loss}({round(afford_loss/all_money, 5)*100}%), \
    # 投資金額 : {int(invest_money)}({round(invest_money/all_money, 4)*100}%), {round(int(invest_money)/market_price,1)}股')
    m = [int(invest_money), round(invest_money*100/all_money, 2), int(int(invest_money)/market_price)]
    
    return m
