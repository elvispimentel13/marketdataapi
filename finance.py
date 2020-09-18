import yfinance as yf
import datetime
import json
import math
import pandas as pd
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
        if tickerData.empty:
            priceLast = 0
        else:
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
        tickerslist = []
        if not tickers:
            print("List cannot be empty.")
        elif isinstance(tickers, str):
            tickers = [tickers]
        elif len(tickers) > 1:
            tickersData = self.downloadTickersData(tickers)
            if tickersData.empty:
                tickersData = self.downloadTickersData(tickers, 2)
            if tickersData.empty:
                for tkr in tickers:
                    tickerslist.append({"symbol": tkr, "price": 0})
                return (json.dumps(tickerslist))
            else:
                for ticker, pricelast in tickersData["Close"].iloc[-1].items():
                    if math.isnan(pricelast):
                        pricelast = 0
                    tickerslist.append({"symbol": ticker, "price": pricelast})
                return (json.dumps(tickerslist))
        else:
            return self.getPrice(tickers)

    def downloadTickersData(self, tickers, interval = None):
        today = datetime.datetime.today()
        try:
            if not interval:
                tickerDF = yf.download(tickers, period='1h')
                return tickerDF
            else:
                lastClose = (today - datetime.timedelta(days=2)).isoformat()[:10]
                tickerDF = yf.download(period='1d', start=lastClose, end=today.isoformat()[:10])
                return tickerDF
        except:
            return pd.DataFrame()

#stocks = Stocks()
#stocks.getTickerInfo('CQPRR')
#print(stocks.getPrice(['AAPLRR']))
#print(stocks.getPrices(['KMIXXX']))
#print(stocks.getPrices(['KMIRX', 'PLMXXR']))

#[{"symbol":"ddd", "price":334.00}, {"symbol":"ddd", "price":334.00}]
