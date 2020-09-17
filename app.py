import flask
from flask import request
from finance import Stocks
import json

app = flask.Flask(__name__)
prices = Stocks()



@app.route('/ticker-price', methods=['GET'])
def getStockPrice():
    data = request.json
    pricedata = prices.getPrices(data['tickers'])
    return pricedata

if __name__ == '__main__':
    app.run(debug=True)