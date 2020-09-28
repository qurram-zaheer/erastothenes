import json
import time
import schedule
import os
from os.path import join, dirname
from dotenv import load_dotenv
from markupsafe import escape
import requests
import datetime
import pytz


# Create .env file path.
dotenv_path = join(dirname(__file__), '.env')

# Load file from the path.
load_dotenv(dotenv_path)

token = os.getenv('TOKEN')
print(token)


def stat_update():
    cache = {}
    count = 0
    db = open('temp_db.json')
    db_data = json.load(db)

    for ticker_obj in db_data.values():
        for ticker, data_obj in ticker_obj.items():
            if ticker not in cache:
                count += 1
                if (count >= 60):
                    time.sleep(120)
                    count = 0
                # price_quote = requests.get(
                #     'https://finnhub.io/api/v1/quote?symbol={}&token={}'.format(ticker, token)).json()
                cache['ticker'] = {}
                for index, position in enumerate(data_obj['positions']):
                    exp_fmt = [int(x) for x in position['exp'].split('/')]
                    if len(exp_fmt) == 2:
                        dt = datetime.datetime(datetime.date.today(
                        ).year, exp_fmt[0], exp_fmt[1], 0, 0) - datetime.datetime.now()
                        if dt.days < 0:
                            break
                        exp_fmt = datetime.datetime(
                            datetime.date.today().year, exp_fmt[0], exp_fmt[1], 0, 0, tzinfo=pytz.timezone('US/Eastern')).replace(tzinfo=datetime.timezone.utc).timestamp()
                    else:
                        dt = datetime.datetime(
                            exp_fmt[2], exp_fmt[0], exp_fmt[1], 0, 0) - datetime.datetime.now()
                        if dt.days < 0:
                            break
                        exp_fmt = datetime.datetime(
                            exp_fmt[2], exp_fmt[1], exp_fmt[0], 0, 0, tzinfo=pytz.timezone('US/Eastern')).replace(tzinfo=datetime.timezone.utc).timestamp()
                    print("EXPIRY: ", int(exp_fmt))

                    price_quote = requests.get(
                        'https://query1.finance.yahoo.com/v7/finance/options/{}?date={}'.format(ticker, int(exp_fmt))).json()
                    if position['opt'] == 'c':
                        price_quote = price_quote['optionChain']['result'][0]['options'][0]['calls']
                    else:
                        price_quote = price_quote['optionChain']['result'][0]['options'][0]['puts']
                    print(position['strike'])
                    chain = next(
                        (option for option in price_quote if option['strike'] == int(position['strike'])), None)
                    stats = {'bid': chain['bid'], 'ask': chain['ask'],
                             'last': chain['lastPrice'], 'iv': chain['impliedVolatility']}
                    data_obj['stats'][index].append(stats)
                    cache['ticker']['{}{}{}'.format(
                        position['strike'], position['exp'], position['opt'])] = stats

            else:
                for index, position in enumerate(data_obj['positions']):
                    if '{}{}'.format(position['strike'], position['exp']) not in cache:
                        exp_fmt = [int(x) for x in position['exp'].split('/')]
                        if len(exp_fmt) == 2:
                            dt = datetime.datetime(datetime.date.today(
                            ).year, exp_fmt[0], exp_fmt[1], 0, 0) - datetime.datetime.now()
                            if dt.days < 0:
                                break
                            exp_fmt = datetime.datetime(
                                datetime.date.today().year, exp_fmt[0], exp_fmt[1], 0, 0, tzinfo=pytz.timezone('US/Eastern')).replace(tzinfo=datetime.timezone.utc).timestamp()
                        else:
                            dt = datetime.datetime(datetime.date.today(
                            ).year, exp_fmt[0], exp_fmt[1], 0, 0) - datetime.datetime.now()
                            if dt.days < 0:
                                break
                            exp_fmt = datetime.datetime(
                                exp_fmt[2], exp_fmt[1], exp_fmt[0], 0, 0, tzinfo=pytz.timezone('US/Eastern')).replace(tzinfo=datetime.timezone.utc).timestamp()
                        print("EXPIRY: ", int(exp_fmt))
                        price_quote = requests.get(
                            'https://query1.finance.yahoo.com/v7/finance/options/{}?date={}'.format(ticker, int(exp_fmt))).json()
                        if position['opt'] == 'c':
                            price_quote = price_quote['optionChain']['result'][0]['options'][0]['calls']
                        else:
                            price_quote = price_quote['optionChain']['result'][0]['options'][0]['puts']
                        print(position['strike'])
                        chain = next(
                            (option for option in price_quote if option['strike'] == int(position['strike'])), None)
                        stats = {'bid': chain['bid'], 'ask': chain['ask'],
                                 'last': chain['lastPrice'], 'iv': chain['impliedVolatility']}
                        data_obj['stats'][index].append(stats)
                        cache['ticker']['{}{}{}'.format(
                            position['strike'], position['exp'], position['opt'])] = stats
                    else:
                        stats = cache['{}{}{}'.format(
                            position['strike'], position['exp'], position['opt'])]
                        data_obj['stats'][index].append(stats)
     # Update database
    with open('temp_db.json', 'w') as outfile:
        json.dump(db_data, outfile)

    print(cache)

    with open('temp_db.json', 'w') as outfile:
        json.dump(db_data, outfile)


schedule.every().minute.do(stat_update)

friday_to_monday = 65.5*60*60
next_mo = 17.5*60*60


while True:
    now = datetime.datetime.now(tz=pytz.timezone('US/Eastern'))
    market_start = now.replace(
        hour=9, minute=30, second=0, microsecond=0, tzinfo=pytz.timezone('US/Eastern'))
    market_end = now.replace(hour=16, minute=5, second=0,
                             microsecond=0,  tzinfo=pytz.timezone('US/Eastern'))
    if datetime.datetime.now(tz=pytz.timezone('US/Eastern')).weekday() == 5 and datetime.datetime.now(tz=pytz.timezone('US/Eastern')) == market_end:
        print('EOW')
        time.sleep(friday_to_monday)
    if datetime.datetime.now(tz=pytz.timezone('US/Eastern')) == market_end:
        print('EOD')
        time.sleep(next_mo)
    elif datetime.datetime.now(tz=pytz.timezone('US/Eastern')) >= market_start and datetime.datetime.now(tz=pytz.timezone('US/Eastern')) <= market_end:
        print('starting')
        schedule.run_pending()
        time.sleep(1)
