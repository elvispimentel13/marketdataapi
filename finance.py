import yfinance as yf
import datetime
import json
import math
import pandas as pd
import requests
import utils


class Stocks:
    def getTickerInfo(self, ticker):
        tickerInfo = yf.Ticker(ticker)
        return tickerInfo

    def getPrice(self, ticker):
        stockPrice = []
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
        stockPrice.append({"symbol": ticker, "price": priceLast})
        return (json.dumps(stockPrice))

    def downloadTickerData(self, tickerInfo, interval=None):
        today = datetime.datetime.today()
        if not interval:
            tickerDF = tickerInfo.history(period='1h')
            return tickerDF
        else:
            lastClose = (today - datetime.timedelta(days=2)).isoformat()[:10]
            tickerDF = tickerInfo.history(period='1d', start=lastClose, end=today.isoformat()[:10])
            return tickerDF

    # Multiple tickers prices
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
                return json.dumps(tickerslist)
        else:
            return self.getPrice(tickers)

    # Ticker price range data based on date(s)
    def getPricesRange(self, tickers, enddt=None, startdt=None):
        tickerslist = []
        if not tickers:
            print("List cannot be empty.")
        elif isinstance(tickers, str):
            tickers = [tickers]
        else:
            tickersData = self.downloadTickersDataRange(tickers, enddt, startdt)
            if tickersData.empty:
                for tkr in tickers:
                    tickerslist.append({"symbol": tkr, "range": []})
                return (json.dumps(tickerslist))
            else:
                for tkr in tickers:
                    tkrdtrg = []
                    if tickers.__len__() > 1:
                        for row in tickersData["Close"].itertuples():
                            rowdict = row._asdict()
                            if rowdict[tkr] is not None:
                                newitem = {"date": rowdict["Index"].isoformat()[:10], "price": 0 if math.isnan(rowdict[tkr]) else rowdict[tkr]}
                                duplicate = list(filter(lambda d: d['date'] in rowdict["Index"].isoformat()[:10], tkrdtrg))
                                if len(duplicate) == 0:
                                   tkrdtrg.append(newitem)
                        tickerslist.append({"symbol": tkr, "range": tkrdtrg})
                    else:
                        tkrdtrg = []
                        for row in tickersData["Close"].items():
                            if row[1] is not None:
                                newitem = {"date": row[0].isoformat()[:10], "price": 0 if math.isnan(row[1]) else row[1]}
                                duplicate = list(filter(lambda d: d['date'] in row[0].isoformat()[:10], tkrdtrg))
                                if len(duplicate) == 0:
                                   tkrdtrg.append(newitem)
                        tickerslist.append({"symbol": tickers[0], "range": tkrdtrg})
                return json.dumps(tickerslist)

    def downloadTickersData(self, tickers, interval=None):
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

    def downloadTickersDataRange(self, tickers, enddt=None, startdt=None):
        today = datetime.datetime.today()
        try:
            if enddt is not None:
                enddate = datetime.datetime.strptime(enddt, '%Y-%m-%d')
                enddate = enddate + datetime.timedelta(days=1)
            elif enddt is None:
                enddate = today
            if startdt is not None:
                startdate = datetime.datetime.strptime(startdt, '%Y-%m-%d')
            elif startdt is None:
                startdate = today - datetime.timedelta(days=1)
            if startdate >= enddate:
                startdate = enddate - datetime.timedelta(days=1)
            tickerDF = yf.download(tickers, start=startdate.isoformat()[:10], end=enddate.isoformat()[:10])
            return tickerDF
        except:
            return pd.DataFrame()

    def getTickersProfile(self, tickerlist):
        tickerprofilelist = []
        valuelist = ["symbol", "sector", "industry", "forwardPE"]
        lisnames = [{"symbol": "ticker"}, {"forwardPE": "PER"}]
        tickers = yf.Tickers((" ").join(tickerlist))
        dictData = tickers.tickers._asdict()
        for tkr in tickerlist:
            infodict = {}
            jsonTickerData = dictData[tkr].info
            for key in valuelist:
                infodict.update({key: jsonTickerData[key] if key in jsonTickerData else ""})
            tickerprofilelist.append(infodict)
        return json.dumps(tickerprofilelist)


class Symbols:
    def getSymbol(self, symbol):
        url = utils.getConfig("Yahoo-api", "URL").format(symbol)
        listsymbols = []
        result = requests.get(url).json()
        print(result)
        for x in result['ResultSet']['Result']:
            if x['symbol'] == symbol:
                del listsymbols[:]
                listsymbols.append({"symbol": x['symbol'], "name": x['name']})
                return listsymbols
            else:
                listsymbols.append({"symbol": x['symbol'], "name": x['name']})
        return json.dumps(listsymbols)

    def getSymbolList(self, query):
        markets = (utils.getSection("Markets", "USA")).split(", ")
        if isinstance(query, list):
            query = query[0]
        url = utils.getConfig("Yahoo-api", "URL").format(query)
        listsymbols = []
        result = requests.get(url).json()
        # print(result['ResultSet']['Result'])
        for x in result['ResultSet']['Result']:
            if x['exchDisp'] in markets:
                listsymbols.append({"symbol": x['symbol'], "name": x['name']})
        return json.dumps(listsymbols)




