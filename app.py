import flask
from flask import request
from historical import Historical
from finance import OldStocks
from finance import Symbols
from price import Prices
from stock import Stock
from flask import jsonify


app = flask.Flask(__name__)
oldStocks = OldStocks()
symbols = Symbols()
prices = Prices()
historical = Historical()
stock = Stock()

@app.route('/ticker-price', methods=['POST'])
def getStockPrice():
    data = request.json
    pricedata = oldStocks.getPrices(data['tickers'])
    return pricedata


@app.route('/tickerInfo', methods=['POST'])
def getTickerInfo():
    ticker = request.args.get('ticker')
    data = oldStocks.getTickerInfo(ticker)
    tickerdata = data.get_info()
    return tickerdata


@app.route('/range/getPrices', methods=['POST'])
def getPricesRange():
    data = request.json
    enddt = None
    startdt = None
    if 'enddate' in data:
        if data['enddate']:
            enddt = data['enddate']
    if 'startdate' in data:
        if data['startdate']:
            startdt = data['startdate']
    pricesdatarange = oldStocks.getPricesRange(data['tickers'], enddt, startdt)
    return pricesdatarange


@app.route('/ticker/getProfiles', methods=['POST'])
def getTickersProfile():
    data = request.json
    profilesdata = oldStocks.getTickersProfile(data['tickers'])
    return profilesdata


@app.route('/ticker/getSuggestions', methods=['POST'])
def getSymbolList():
    data = request.json
    print(data['query'])
    symbolsuggestdata = symbols.getSymbolList(data['query'])
    return symbolsuggestdata


@app.route('/ticker/getSymbol', methods=['POST'])
def getSymbol():
    data = request.json
    symbolyahoodata = symbols.getSymbol(data['query'])
    return symbolyahoodata

@app.route('/ticker/prices', methods=['GET'])
def get_price():
    tickers = request.args.get('tickers')
    priceData = prices.get_price(tickers)
    return jsonify(priceData)

@app.route('/historical/events', methods=['GET'])
def get_event_data():
    tickers = request.args.get('tickers')
    start = request.args.get('start')
    end = request.args.get('end')
    event = request.args.get('event')
    eventData = historical.get_events(tickers=str(tickers), start=str(start), end=str(end), event=str(event))
    return jsonify(eventData)

@app.route('/historical/prices', methods=['GET'])
def get_prices_range():
    tickers = request.args.get('tickers')
    start = request.args.get('start')
    end = request.args.get('end')
    pricesData = historical.get_prices(tickers=str(tickers), start=str(start), end=str(end))
    return jsonify(pricesData)

@app.route('/stock/summary', methods=['GET'])
def get_stock_summary():
    tickers = request.args.get('tickers')
    summaryData = stock.get_summary(tickers=str(tickers))
    return jsonify(summaryData)

if __name__ == '__main__':
    app.run(debug=True)
