import flask
from flask import request
from finance import Stocks
from finance import Symbols
from price import Prices
import json

app = flask.Flask(__name__)
stocks = Stocks()
symbols = Symbols()
prices = Prices()

@app.route('/ticker-price', methods=['POST'])
def getStockPrice():
    data = request.json
    pricedata = stocks.getPrices(data['tickers'])
    return pricedata


@app.route('/tickerInfo', methods=['POST'])
def getTickerInfo():
    ticker = request.args.get('ticker')
    data = stocks.getTickerInfo(ticker)
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
    pricesdatarange = stocks.getPricesRange(data['tickers'], enddt, startdt)
    return pricesdatarange


@app.route('/ticker/getProfiles', methods=['POST'])
def getTickersProfile():
    data = request.json
    profilesdata = stocks.getTickersProfile(data['tickers'])
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

@app.route('/ticker/prices', methods=['POST'])
def get_price():
    tickers = request.args.get('tickers')
    priceData = prices.get_price(tickers)
    return priceData


if __name__ == '__main__':
    app.run(debug=True)
