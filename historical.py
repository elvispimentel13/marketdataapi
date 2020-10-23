import copy
import datetime
import json
import math

import multitasking as _multitasking
import requests
import utils
import time as _time
import shared
import time

# vars and instances
utils = utils.Utils()


class Historical:
    # GET EVENTS (DIVIDEND, SPLITS)
    def get_events(self, tickers, start=0, end=9999999999,
                      interval="1mo", event="div", threads=True):
        tickers = utils.format_tickers(tickers)
        start = utils.format_date(start)
        end = utils.format_date(end)
        intervals = utils.getConfig("Configurations", "Intervals").replace(" ", "").split(",")
        if interval not in intervals:
            interval = intervals[len(intervals)-2]
        eventsDefault = json.loads(utils.getConfig("Configurations", "EVENTS"))
        if event in eventsDefault:
            event = eventsDefault[event]
        else:
            event = eventsDefault["dividends"]
        if tickers:
            if len(tickers) >= 1:
                data = self.get_events_data(tickers, start, end, interval, event)
        # Process result data and build json object to append in list.
        resultConfig = utils.getConfig("Results", "DIVIDEND" if event == "div" else "SPLIT")
        resultExclusionConfig = utils.getConfig("Results", "DIVIDEND_exclude" if event == "div" else "SPLIT_exclude").replace(" ", "")
        resultEvent = utils.getConfig("Results", "DIVIDEND_event" if event == "div" else "SPLIT_event")
        resultExclusionObj = resultExclusionConfig.split(",")
        resultObj = json.loads(resultConfig)
        resultEventObj = json.loads(resultEvent)
        eventResult = []
        if bool(data):
            for tkr in tickers:
                try:
                    resultObjCopy = copy.copy(resultObj)
                    tkrValues = data[tkr]["chart"]["result"]
                    if tkrValues:
                        for (key, value) in resultObj.items():
                             if key not in resultExclusionObj:
                                if isinstance(value, dict):
                                    if key in tkrValues[0]:
                                        valueObj = tkrValues[0][key]
                                    else:
                                        valueObj = {}
                                else:
                                    if value in tkrValues[0]:
                                        valueObj = tkrValues[0][value]
                                    else:
                                        valueObj = {}
                                if bool(valueObj):
                                    if hasattr(valueObj, "keys"):
                                        # print(valueObj[valueObj.keys()[0]])
                                        # info = valueObj[valueObj.keys()[0]] if len(valueObj.keys()) == 1 else valueObj[valueObj.keys()[0]]
                                        info = valueObj[next(iter(valueObj))]
                                        resultGrp = []
                                        for dt, k in info.items():
                                            resultEventObjCopy = copy.copy(resultEventObj)
                                            if hasattr(k, "keys"):
                                                for x, y in resultEventObjCopy.items():
                                                    resultEventObjCopy[x] = utils.format_date(k[x]) if y == "date" else k[x]
                                                resultGrp.append(resultEventObjCopy)
                                        resultObjCopy[key] = resultGrp
                                    else:
                                        resultObjCopy[key] = ""
                                else:
                                    resultObjCopy[key] = []
                        resultObjCopy["errors"] = "Ok"
                        if "symbol" in resultObjCopy:
                            if resultObjCopy["symbol"] == "symbol":
                                resultObjCopy["symbol"] = tkr
                        eventResult.append(resultObjCopy)
                except:
                    pass
        return eventResult

    def get_events_data(self, tickers, start=0, end=9999999999, interval="1d", event="div", threads=True):
        tickers = utils.format_tickers(tickers)
        shared._DSH = {}
        if threads:
            if threads is True:
                threadsQty = min([len(tickers), _multitasking.cpu_count() * 2])
                _multitasking.set_max_threads(threadsQty)
                for i, ticker in enumerate(tickers):
                    self.download_events_threaded(ticker, start, end, interval, event)
                while len(shared._DSH) < len(tickers):
                    _time.sleep(0.01)
            else:
                if len(tickers) == 1:
                    ticker = tickers[0]
                    resultEvent = self.download_events(ticker, start, end, interval, event)
                    shared._DSH[ticker.upper()] = resultEvent
                elif len(tickers) <= 5:
                    for i, ticker in enumerate(tickers):
                        resultEvent = self.download_events(ticker, start, end, interval, event)
                        shared._DSH[ticker.upper()] = resultEvent
                else:
                    self.get_events(tickers, start, end, interval, event, threads=True)
        return shared._DSH

    # GET PRICES (RANGE)
    def get_prices(self, tickers, start=0, end=9999999999, interval="1d", threads=True):
        tickers = utils.format_tickers(tickers)
        startdt = utils.format_date(start, True)
        enddt = utils.format_date(end, True)
        dates = self.validate_date_range(start=startdt, end=enddt)
        startdt = dates['start']
        enddt = dates['end']
        intervals = utils.getConfig("Configurations", "Intervals").replace(" ", "").split(",")
        if interval not in intervals:
            interval = intervals[len(intervals)-5]
        if tickers:
            if len(tickers) >= 1:
                data = self.get_prices_data(tickers, startdt, enddt, interval)
        # Process result data and build json object to append in list.
        resultConfig = utils.getConfig("Results", "PRICES")
        resultObj = json.loads(resultConfig)
        pricesResult = []
        if bool(data):
            for tkr in tickers:
                try:
                    resultObjCopy = copy.copy(resultObj)
                    tkrValues = data[tkr]["chart"]["result"]
                    rangeResult = []
                    if tkrValues:
                        if not ('timestamp' in tkrValues[0]):
                            print("not timestamp")
                            resultObjCopy["range"] = rangeResult
                            resultObjCopy["errors"] = "NOT VALUES IN RANGE PROVIDED."
                            if "symbol" in resultObjCopy:
                                if resultObjCopy["symbol"] == "symbol":
                                    resultObjCopy["symbol"] = tkr
                            pricesResult.append(resultObjCopy)
                        else:
                            dateValues = tkrValues[0]['timestamp']
                            pricesValues = tkrValues[0]['indicators']['adjclose']
                            if pricesValues:
                                closeValues = pricesValues[0]['adjclose']
                                # for (idx, dt) in enumerate(dateValues):
                            for idx, dt in enumerate(dateValues):
                                if utils.format_date(dt) in ([duplicate['date'] for duplicate in rangeResult]):
                                    duplicate = {"date": utils.format_date(dt), "price": closeValues[idx]}
                                else:
                                    rangeResult.append({"date": utils.format_date(dt), "price": closeValues[idx]})
                            resultObjCopy["range"] = rangeResult
                            resultObjCopy["errors"] = "Ok"
                            if "symbol" in resultObjCopy:
                                if resultObjCopy["symbol"] == "symbol":
                                    resultObjCopy["symbol"] = tkr
                            pricesResult.append(resultObjCopy)
                except ValueError as ex:
                    print(ex)
        return pricesResult

    def get_prices_data(self, tickers, start=0, end=9999999999, interval="1d", threads=True):
        tickers = utils.format_tickers(tickers)
        shared._DSHP = {}
        if threads:
            if threads is True:
                threadsQty = min([len(tickers), _multitasking.cpu_count() * 2])
                _multitasking.set_max_threads(threadsQty)
                for i, ticker in enumerate(tickers):
                    self.download_prices_threaded(ticker, start, end, interval)
                while len(shared._DSHP) < len(tickers):
                    _time.sleep(0.01)
            else:
                if len(tickers) == 1:
                    ticker = tickers[0]
                    resultPrices = self.download_prices(ticker, start, end, interval)
                    shared._DSHP[ticker.upper()] = resultPrices
                elif len(tickers) <= 5:
                    for i, ticker in enumerate(tickers):
                        resultPrices = self.download_prices(ticker, start, end, interval)
                        shared._DSHP[ticker.upper()] = resultPrices
                else:
                    self.get_prices(tickers, start, end, interval, threads=True)
        return shared._DSHP

    def validate_date_range(self, start=0, end=9999999999):
        startdt = datetime.datetime.utcfromtimestamp(start)
        enddt = datetime.datetime.utcfromtimestamp(end)
        today = datetime.datetime.today()
        now = time.time()
        if startdt >= enddt:
            start = enddt - datetime.timedelta(days=1)
        if startdt > today:
            start = now
        # enddt = enddt + datetime.timedelta(days=1)
        if enddt > today:
            end = now
        if isinstance(start, datetime.date) or isinstance(start, str):
            start = utils.format_date(start.strftime('%Y-%m-%d'), True)
        if isinstance(end, datetime.date) or isinstance(end, str):
            end = utils.format_date(end.strftime('%Y-%m-%d'), True)
        # ADJUST DATE TO MARKET OPEN TIME (9:30AM)
        end = end + 48600
        return {"start": math.trunc(start), "end": math.trunc(end)}

    # DOWNLOAD EVENT(S)
    @_multitasking.task
    def download_events_threaded(self, ticker, start=0, end=9999999999, interval="1d", event="div"):
        data = self.download_events(ticker, start, end, interval, event)
        shared._DSH[ticker.upper()] = data

    def download_events(self, ticker, start=0, end=9999999999, interval="1d", event="div"):
        url = utils.getConfig("Yahoo-api", "EVENTSMODULE").format(symbol=ticker, start=start, end=end,
                                                                  interval=interval, event=event)
        data = requests.get(url).json()
        return data

    # PRICES RANGE
    @_multitasking.task
    def download_prices_threaded(self, ticker, start=0, end=9999999999, interval="1d"):
        data = self.download_prices(ticker, start, end, interval)
        shared._DSHP[ticker.upper()] = data

    def download_prices(self, ticker, start=0, end=9999999999, interval="1d"):
        url = utils.getConfig("Yahoo-api", "PRICERANGE").format(symbol=ticker, start=start, end=end, interval=interval)
        data = requests.get(url).json()
        return data

# historical = Historical()
# print(historical.get_events("aapl, ko", start="2019-01-01", end="2020-10-10", event="dividend"))
# print(historical.get_prices("aapl,kmi", start="2020-10-16", end="2020-10-19"))
# start = "2020-10-17"
# end = "2020-10-17"
# startdt = utils.format_date(start, True)
# enddt = utils.format_date(end, True)
# print(historical.validate_date_range(start=startdt, end=enddt))