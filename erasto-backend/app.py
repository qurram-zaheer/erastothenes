from flask import Flask, request
import os
from os.path import join, dirname
from dotenv import load_dotenv
from markupsafe import escape
import requests
import datetime
import json
import pytz

# -------------------------- Load token for finnhub -------------------------- #

# Create .env file path.
dotenv_path = join(dirname(__file__), '.env')

# Load file from the path.
load_dotenv(dotenv_path)

token = os.getenv('TOKEN')
print(token)

# --------------------------------- Flask app -------------------------------- #

app = Flask(__name__)


@app.route('/hist/<user_id>', methods=['GET'])
def chart_data(user_id):
    if request.method == 'GET':
        db = open('/temp_db.json')
        db_data = json.load(db)

        return db_data[user_id]


@app.route('/watchlist/<user_id>', methods=['GET', 'POST'])
def watchlist(user_id):
    if request.method == 'POST':
        content = request.json

        ticker, strike, opt, exp = content.values()

        # Update logs
        with open('./erasto-backend/logs.log', 'a') as f:
            print('{} called ${} {}{} {}'.format(
                escape(user_id), ticker, strike, opt, exp), file=f)

        # Read JSON database
        db = open('./erasto-backend/temp_db.json')
        db_data = json.load(db)

        # Configure and update database

        # Check if user exists as a dict key
        if user_id not in db_data:
            db_data[user_id] = {}

        # Check if ticker exists as a dict key for user
        if ticker not in db_data[user_id]:
            db_data[user_id][ticker] = {'positions': [], 'stats': [[]]}

        callout = {'strike': strike, 'exp': exp, 'opt': opt}

        # Format input expiration date into unix epoch
        exp_fmt = [int(x) for x in exp.split('/')]
        if len(exp_fmt) == 2:
            exp_fmt = datetime.datetime(
                datetime.date.today().year, exp_fmt[0], exp_fmt[1], 0, 0, tzinfo=pytz.timezone('US/Eastern')).replace(tzinfo=datetime.timezone.utc).timestamp()
        else:
            exp_fmt = datetime.datetime(
                exp_fmt[2], exp_fmt[1], exp_fmt[0], 0, 0, tzinfo=pytz.timezone('US/Eastern')).replace(tzinfo=datetime.timezone.utc).timestamp()
        print("EXPIRY: ", int(exp_fmt))

        # Update position for user
        db_data[user_id][ticker]['positions'].append(callout)

        # Get number of positions, used to seperate stats for different positions in the same ticker
        pos_index = len(db_data[user_id][ticker]['positions']) - 1

        # Option/Stock prices
        # price_quote = requests.get(
        #     'https://finnhub.io/api/v1/quote?symbol={}&token={}'.format(ticker, token))
        # print(price_quote.json())
        price_quote = requests.get(
            'https://query1.finance.yahoo.com/v7/finance/options/{}?date={}'.format(ticker, int(exp_fmt))).json()
        if opt == 'c':
            price_quote = price_quote['optionChain']['result'][0]['options'][0]['calls']
        else:
            price_quote = price_quote['optionChain']['result'][0]['options'][0]['puts']
        print(strike)
        chain = next(
            (option for option in price_quote if option['strike'] == float(strike)), None)

        if chain == None:
            return 'Error, your contract date is invalid'
        stats = {'bid': chain['bid'], 'ask': chain['ask'],
                 'last': chain['lastPrice'], 'iv': chain['impliedVolatility']}

        # Match position and stats
        if pos_index != len(db_data[user_id][ticker]['stats']) - 1:
            db_data[user_id][ticker]['stats'].append([])

        # Update database
        db_data[user_id][ticker]['stats'][pos_index].append(stats)
        print(db_data)
        with open('./erasto-backend/temp_db.json', 'w') as outfile:
            json.dump(db_data, outfile)
    return 'success'