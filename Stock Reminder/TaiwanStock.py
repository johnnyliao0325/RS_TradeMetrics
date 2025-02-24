import yfinance as yf

start_time = "2000-01-01"
end_time = "2023-04-10"

data = yf.download("SPY", start=start_time, end=end_time)


print(data)

