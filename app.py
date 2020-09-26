import flask
from flask import request
from finance import Stocks
import json

app = flask.Flask(__name__)
prices = Stocks()


@app.route('/ticker-price', methods=['POST'])
def getStockPrice():
    data = request.json
    pricedata = prices.getPrices(data['tickers'])
    return pricedata

@app.route('/tickerInfo', methods=['POST'])
def getTickerInfo():
    ticker = request.args.get('ticker')
    data = prices.getTickerInfo(ticker)
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
    pricesdatarange = prices.getPricesRange(data['tickers'], enddt, startdt)
    return pricesdatarange

@app.route('/ticker/getProfiles', methods=['POST'])
def getTickersProfile():
    data = request.json
    profilesdata = prices.getTickersProfile(data['tickers'])
    return profilesdata

if __name__ == '__main__':
    app.run(debug=True)