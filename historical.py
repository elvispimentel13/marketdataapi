import copy
import json
import multitasking as _multitasking
import requests
import utils
import time as _time
import shared

# vars and instances
utils = utils.Utils()


class Historical:
    def get_events(self, tickers, start=0, end=9999999999,
                      interval="1mo", events="div", threads=True):
        tickers = utils.format_tickers(tickers)
        if not isinstance(start, int):
            start = utils.format_date(start)
        if not isinstance(end, int):
            end = utils.format_date(end)
        intervals = utils.getConfig("Configurations", "Intervals").replace(" ", "").split(",")
        if interval not in intervals:
            interval = intervals[len(intervals)-2]
        eventsDefault = json.loads(utils.getConfig("Configurations", "EVENTS"))
        if events in eventsDefault:
            events = eventsDefault[events]
        else:
            events = eventsDefault["dividends"]
        if tickers:
            if len(tickers) >= 1:
                data = self.get_events_data(tickers, start, end, interval, events)
        # Process result data and build json object to append in list.
        resultConfig = utils.getConfig("Results", "DIVIDEND" if events == "div" else "SPLIT")
        resultExclusionConfig = utils.getConfig("Results", "DIVIDEND_exclude" if events == "div" else "SPLIT_exclude").replace(" ", "")
        resultEvent = utils.getConfig("Results", "DIVIDEND_event" if events == "div" else "SPLIT_event")
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

    def get_events_data(self, tickers, start=0, end=9999999999, interval="1d", events="div", threads=True):
        tickers = utils.format_tickers(tickers)
        shared._DSH = {}
        if threads:
            if threads is True:
                threadsQty = min([len(tickers), _multitasking.cpu_count() * 2])
                _multitasking.set_max_threads(threadsQty)
                for i, ticker in enumerate(tickers):
                    self.download_events_threaded(ticker, start, end, interval, events)
                while len(shared._DSH) < len(tickers):
                    _time.sleep(0.01)
            else:
                if len(tickers) == 1:
                    ticker = tickers[0]
                    resultEvent = self.download_events(ticker, start, end, interval, events)
                    shared._DSH[ticker.upper()] = resultEvent
                elif len(tickers) <= 5:
                    for i, ticker in enumerate(tickers):
                        resultEvent = self.download_events(ticker, start, end, interval, events)
                        shared._DSH[ticker.upper()] = resultEvent
                else:
                    self.get_events(tickers, start, end, interval, events, threads=True)
        return shared._DSH

    @_multitasking.task
    def download_events_threaded(self, ticker, start=0, end=9999999999, interval="1d", events="div"):
        data = self.download_events(ticker, start, end, interval, events)
        shared._DSH[ticker.upper()] = data

    def download_events(self, ticker, start=0, end=9999999999, interval="1d", events="div"):
        url = utils.getConfig("Yahoo-api", "EVENTSMODULE").format(symbol=ticker, start=start, end=end,
                                                                  interval=interval, events=events)
        data = requests.get(url).json()
        return data

# historical = Historical()
# print(historical.get_events("aapl, kmi, cqp", start="2019-01-01", end="2020-10-10", events="dividend"))