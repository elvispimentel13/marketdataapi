import copy
import json
import time as _time
import multitasking as _multitasking
import requests
import utils
import shared


# vars and instances
utils = utils.Utils()


class Stock:
    def get_summary(self, tickers, threads=True, format="default"):
        tickers = utils.format_tickers(tickers)

        if tickers:
            if len(tickers) >= 1:
                data = self.get_summary_data(tickers, threads)
        # Process result data and build json object to append in list.
        resultConfig = utils.getConfig("Results", "SUMMARY")
        resultFormats = utils.getConfig("Results", "DEFAULT_valueFormat")
        resultExclusionConfig = utils.getConfig("Results", "DEFAULT_exclude").replace(" ", "")
        resultExclusionObj = resultExclusionConfig.split(",")
        resultObj = json.loads(resultConfig)
        formatsObj = json.loads(resultFormats)
        summaryResult = []
        if bool(data):
            for tkr in tickers:
                resultObjCopy = copy.copy(resultObj)
                tkrValues = data[tkr]["quoteSummary"]["result"] if tkr in data else False
                if tkrValues:
                    try:
                        for (key, value) in resultObj.items():
                            if key not in resultExclusionObj:
                                valueObj = tkrValues[0]["summaryDetail"][value] if value in tkrValues[0]["summaryDetail"] else []
                                if bool(valueObj):
                                    if hasattr(valueObj, "keys"):
                                        # Evaluate keys and determine what key to use
                                        # Majority of cases:
                                        #     raw - values as is,
                                        #     fmt - string value,
                                        #     longFmt - formatted string value
                                        if format in formatsObj:
                                            if format in valueObj:
                                                resultObjCopy[key] = valueObj[formatsObj[format]]
                                            else:
                                                if formatsObj[format] in valueObj:
                                                    resultObjCopy[key] = valueObj[formatsObj[format]]
                                                else:
                                                    resultObjCopy[key] = valueObj["raw"]
                                        else:
                                            resultObjCopy[key] = valueObj["raw"]
                                    else:
                                        resultObjCopy[key] = valueObj
                                else:
                                    resultObjCopy[key] = 0
                        resultObjCopy["errors"] = "Ok"
                        if "symbol" in resultObjCopy:
                            resultObjCopy["symbol"] = tkr
                    except:
                        resultObjCopy["errors"] = "Exception getting prices: {}"
                    summaryResult.append(resultObjCopy)
        return (summaryResult)

    def get_summary_data(self, tickers, threads=True):
        tickers = utils.format_tickers(tickers)
        # Clear shared._DSSS
        shared._DSSS = {}
        if threads:
            if threads is True:
                threadsQty = min([len(tickers), _multitasking.cpu_count() * 2])
                _multitasking.set_max_threads(threadsQty)
                for i, ticker in enumerate(tickers):
                    self.download_summary_threaded(ticker)
                while len(shared._DSSS) < len(tickers):
                    _time.sleep(0.01)
            else:
                if len(tickers) == 1:
                    ticker = tickers[0]
                    resultSummary = self.download_summary(ticker)
                    shared._DSSS[ticker.upper()] = resultSummary
                elif len(tickers) <= 5:
                    for i, ticker in enumerate(tickers):
                        resultSummary = self.download_summary(ticker)
                        shared._DSSS[ticker.upper()] = resultSummary
                else:
                    self.get_summary(tickers, threads=True)
        data = shared._DSSS
        return data

    @_multitasking.task
    def download_summary_threaded(self, ticker):
        data = self.download_summary(ticker)
        shared._DSSS[ticker.upper()] = data

    def download_summary(self, ticker):
        url = utils.getConfig("Yahoo-api", "SUMMARYQUERY").format(ticker, "summaryDetail")
        data = requests.get(url).json()
        return data

# stock = Stock()
# print(stock.get_summary("kmi"))
# print(stock.download_summary("KMI"))
# print(stock.get_summary_data("AAPL"))
# print(utils.getConfig("Yahoo-api", "QUERY").format("KMI", "price"))