## Erastothenes

![enter image description here](https://imgur.com/MEQ4Ysz.png)

Erastothenes is a discord bot made primarily to track the individual option trading performance of members in a server over time, based on the callouts that they've made. Erastothenes is fast, efficient, and scalable, although it is recommended to follow certain guidelines while utilizing it.

I hope to use the data collected by this bot (currently also scans for a tickers in any sentence) for other purposes, such as overall server sentiment analysis, i.e, bullish or bearish, and hopefuly some more as they come to me.

### Instructions on setting up the bot locally

1.  Clone the repo
2.  You will need to run three processes simultaneously, work is currently being done to write a single script that does this.
3.  Navigate into the `erasto-backend` directory and start the flask server with `./bin/server-debug.sh`. This may not work on windows, so please refer to the [Flask documentation](https://flask.palletsprojects.com/en/1.1.x/quickstart/) for help. Remember to change the connection port for the bot accordingly
4.  Now execute `updater.py` (as a seperate process) with `python3 updater.py`
5.  Finally, go up one directory and run `python3 bot.py`
6.  Make sure to store your bot token in the `/.env`
