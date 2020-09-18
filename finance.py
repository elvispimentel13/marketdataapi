import yfinance as yf
import datetime
import json
from datetime import timedelta

class Stocks:
    def getTickerInfo(self, ticker):
        tickerInfo = yf.Ticker(ticker)
        return tickerInfo

    def getPrice(self, ticker):
        if not ticker:
            print("Ticker is needed.")
        elif not isinstance(ticker, str):
            ticker = ticker[0]
        tickerInfo = self.getTickerInfo(ticker)
        tickerData = self.downloadTickerData(tickerInfo)
        if tickerData.empty:
            tickerData = self.downloadTickerData(tickerInfo, 2)
        priceLast = tickerData['Close'].iloc[-1]
        stockPrice = {"symbol": ticker, "price": priceLast}
        return (json.dumps(stockPrice))

    def downloadTickerData(self, tickerInfo, interval = None):
        today = datetime.datetime.today()
        if not interval:
            tickerDF = tickerInfo.history(period='1h')
            return tickerDF
        else:
            lastClose = (today - datetime.timedelta(days=2)).isoformat()[:10]
            tickerDF = tickerInfo.history(period='1d', start=lastClose, end=today.isoformat()[:10])
            return tickerDF

    #MULTIPLE TICKERS
    def getPrices(self, tickers):
        if not tickers:
            print("List cannot be empty.")
        elif isinstance(tickers, str):
            tickers = [tickers]
        elif len(tickers)>1:
            tickersData = self.downloadTickersData(tickers)
            if tickersData.empty:
                tickersData = self.downloadTickersData(tickers, 2)
            tickerslist = []
            for ticker, priceLast in tickersData["Close"].iloc[-1].items():
                tickerslist.append({"symbol": ticker, "price": priceLast})
            return tickerslist
        else:
            return self.getPrice(tickers)

    def downloadTickersData(self, tickers, interval = None):
        today = datetime.datetime.today()
        if not interval:
            tickerDF = yf.download(tickers, period='1h')
            return tickerDF
        else:
            lastClose = (today - datetime.timedelta(days=2)).isoformat()[:10]
            tickerDF = yf.download(period='1d', start=lastClose, end=today.isoformat()[:10])
            return tickerDF

stocks = Stocks()
#stocks.getTickerInfo('CQP')
#print(stocks.getPrice(['AAPL']))
#print(stocks.getPrices(['KMI']))
print(stocks.getPrices(['KMI', 'PLM']))

#[{"symbol":"ddd", "price":334.00}, {"symbol":"ddd", "price":334.00}]
