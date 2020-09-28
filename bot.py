import discord
import logging
import requests
import os
from os.path import join, dirname
from dotenv import load_dotenv
from markupsafe import escape

# -------------------------- Load token for bot -------------------------- #

# Create .env file path.
dotenv_path = join(dirname(__file__), '.env')

# Load file from the path.
load_dotenv(dotenv_path)

token = os.getenv('BOT_TOKEN')


# ---------------------------------- Logging --------------------------------- #

logger = logging.getLogger('discord')
logger.setLevel(logging.DEBUG)
handler = logging.FileHandler(
    filename='discord.log', encoding='utf-8', mode='w')
handler.setFormatter(logging.Formatter(
    '%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
logger.addHandler(handler)

client = discord.Client()


@client.event
async def on_ready():
    print("Logged in as {0.user}".format(client))


# -------------------------------- New callout event------------------------------- #

@client.event
async def on_message(message):
    if message.author == client.user:
        return

    if message.content.startswith('_'):
        response = None
        try:
            ticker, raw_pos, exp = message.content.split()

            opt = raw_pos[-1]
            strike = raw_pos[:-1]
            req_body = {'ticker': ticker[1:].replace('.', '-'),
                        'strike': strike, 'opt': opt, 'exp': exp}
            print(req_body)
            print(message.author.id)
            requests.post(
                "http://127.0.0.1:5000/watchlist/{}".format(message.author.id), json=req_body)
        except ValueError:
            response = 'Please follow this format: ```_<TICKER_NAME> <STRIKE><c/p> <EXP>\nEx: _AAPL 600c 8/21```'
            await message.channel.send(response)
    # else:
    #     await message.channel.send('Please follow this format: ```$<TICKER_NAME> <STRIKE><c/p> <EXP>\nEx: $AAPL 600c 8/21```')

    elif message.content.startswith('%'):
        # inputs = message.content.split()
        username = message.author.id
        res = requests.get(
            "http://127.0.0.1:5000/hist/{}".format(username)).json()

        embed = discord.Embed(
            colour=discord.Colour.blue(),
            title=message.author.name,
        )

        for ticker, ticker_obj in res.items():
            embed.add_field(
                name="Ticker", value="> **{}**".format(ticker), inline=False)
            [positions, stats] = ticker_obj.values()
            print(type(positions), type(positions[0]))
            for index, position in enumerate(positions):
                embed.add_field(
                    name="#", value="############", inline=False)
                embed.add_field(name="Position", value="{}{} {}".format(
                    position['strike'], position['opt'], position['exp']), inline=True)
                embed.add_field(name="Entry", value="{}/{}/**{}**".format(
                    stats[index][0]['bid'], stats[index][0]['ask'], stats[index][0]['last']), inline=True)
                embed.add_field(name="Latest", value="{}/{}/**{}**".format(
                    stats[index][-1]['bid'], stats[index][-1]['ask'], stats[index][-1]['last']), inline=True)
                embed.add_field(name="% change (last)", value="{}".format(
                    (stats[index][-1]['last'] - stats[index][0]['last'])*100/stats[index][0]['last']), inline=True)

        await message.channel.send(embed=embed)


client.run(token)
