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

@app.route('/range/getPrices', methods=['POST'])
def getPricesRange():
    data = request.json
    enddt = None
    startdt = None
    if 'enddate' in data:
        enddt = data['enddate']
    if 'startdate' in data:
        startdt = data['startdate']
    pricesdatarange = prices.getPricesRange(data['tickers'], enddt, startdt)
    return pricesdatarange

if __name__ == '__main__':
    app.run(debug=True)