import copy
import json
import time as _time
import multitasking as _multitasking
import numpy
import requests
import pandas
import utils

# vars and instances
utils = utils.Utils()
_DS = {}


class Prices:
    def get_price(self, tickers, threads=True):
        tickers = tickers if isinstance(
            tickers, (list, set, tuple)) else tickers.replace(',', ' ').split()
        tickers = list(set([ticker.upper() for ticker in tickers]))

        if tickers:
            if len(tickers) >= 1:
                data = self.get_price_data(tickers, threads)
        # Process result data and build json object to append in list.
        resultConfig = utils.getConfig("Results", "PRICE")
        resultExclusionConfig = utils.getConfig("Results", "PRICE_exclude")
        resultExclusionObj = resultExclusionConfig.strip(" ").split(",")
        resultObj = json.loads(resultConfig)
        pricesResult = []
        if bool(data):
            for tkr in tickers:
                resultObjCopy = copy.copy(resultObj)
                tkrValues = data[tkr]["quoteSummary"]["result"]
                if tkrValues:
                    for (key, value) in resultObj.items():
                        if key not in resultExclusionObj:
                            valueObj = tkrValues[0]["price"][value]
                            if bool(valueObj):
                                if hasattr(valueObj, "keys"):
                                    # Evaluate keys and determine what key to use
                                    # Majority of cases:
                                    #     raw - values as is,
                                    #     fmt - string value,
                                    #     longFmt - formatted string value
                                    # keys = valueObj.keys()
                                    resultObjCopy[key] = valueObj["raw"]
                                else:
                                    resultObjCopy[key] = valueObj
                            else:
                                resultObjCopy[key] = 0
                    resultObjCopy["errors"] = "Ok"
                    pricesResult.append(resultObjCopy)

        return json.dumps(pricesResult)

    def get_price_data(self, tickers, threads=True):
        tickers = tickers if isinstance(
            tickers, (list, set, tuple)) else tickers.replace(',', ' ').split()

        tickers = list(set([ticker.upper() for ticker in tickers]))
        if threads:
            if threads is True:
                threadsQty = min([len(tickers), _multitasking.cpu_count() * 2])
                _multitasking.set_max_threads(threadsQty)
                for i, ticker in enumerate(tickers):
                    self.download_price_threaded(ticker)
                    # _DS[ticker.upper()] = resultPrice
                while len(_DS) < len(tickers):
                    _time.sleep(0.01)
            else:
                if len(tickers) == 1:
                    ticker = tickers[0]
                    resultPrice = self.download_price(ticker)
                    _DS[ticker.upper()] = resultPrice
                elif len(tickers) <= 5:
                    for i, ticker in enumerate(tickers):
                        resultPrice = self.download_price(ticker)
                        _DS[ticker.upper()] = resultPrice
                else:
                    self.get_price(tickers, threads=True)
        return _DS

    @_multitasking.task
    def download_price_threaded(self, ticker):
        data = self.download_price(ticker)
        _DS[ticker.upper()] = data

    def download_price(self, ticker):
        url = utils.getConfig("Yahoo-api", "QUERY").format(ticker, "price")
        data = requests.get(url).json()
        return data

# prices = Prices()
# print(prices.get_price("KMI,AAPL"))
# print(prices.download_price("KMI"))
# print(utils.getConfig("Yahoo-api", "QUERY").format("KMI", "price"))
