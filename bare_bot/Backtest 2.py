
import talib
import websocket
import json
import time
import pandas as pd
import plotly
from config import *

json_data = json.dumps({
     "ticks_history": "frxEURUSD",
    "adjust_start_time": 1,
    "count": 10000,
    "end": "latest",
    "start": 1638518520,
    "style": "candles",
    "granularity" : 600
    })



def send(massege,ws= websocket.WebSocket()):
    ws.connect(apiUrl)
    hs = ws.getstatus()
    print(hs)
    ws.send(massege)
    recieved = pd.DataFrame(json.loads(ws.recv())['candles'])
    return recieved


def analize(dataframe):
    stake = 10
    initial_balance,start_balance = 250 , 250
    call_win = 0
    call_lose = 0 
    put_win = 0 
    put_lose = 0
    dataframe['engulfing'] = talib.CDLENGULFING(dataframe['open'],dataframe['high'],dataframe['low'],dataframe['close'])
    dataframe['harami'] = talib.CDLHARAMI(dataframe['open'],dataframe['high'],dataframe['low'],dataframe['close'])
    #dataframe['epoch'] = [time.ctime(x) for x in dataframe['epoch'] ]
    dataframe['cci'] = talib.CCI(dataframe['high'], dataframe['low'], dataframe['close'], timeperiod=20)
    #dataframe['angle_near'] = talib.LINEARREG_ANGLE(dataframe['close'], timeperiod=14)
    dataframe['angle_far'] = talib.LINEARREG_ANGLE(dataframe['close'], timeperiod=100)
    dataframe['sma'] = talib.SMA(dataframe['close'],timeperiod = 300)
    print(dataframe)

#back test using dataframe rolling window
    for win in dataframe.rolling(window = 3):
        if int(win.iloc[[0]]['engulfing']) == 100  and float(win.iloc[[0]]['sma']) < float(win.iloc[[0]]['close']):
            if float(win.iloc[[1]]['open']) < float(win.iloc[[2]]['open']):
                call_win = call_win +1
                initial_balance = initial_balance + (stake * 0.9)
            elif float(win.iloc[[1]]['open']) > float(win.iloc[[2]]['open']):
                call_lose = call_lose + 1
                initial_balance = initial_balance - stake
        elif int(win.iloc[[0]]['engulfing']) == -100  and float(win.iloc[[0]]['sma']) > float(win.iloc[[0]]['close']):
            if float(win.iloc[[1]]['open']) > float(win.iloc[[2]]['open']):
                put_win = put_win +1
                initial_balance = initial_balance + (stake * 0.9)
            elif float(win.iloc[[1]]['open']) < float(win.iloc[[2]]['open']):
                put_lose = put_lose + 1
                initial_balance = initial_balance - stake
    print(f"initial balance {start_balance} , final balance {initial_balance} , PNL {initial_balance - start_balance}")          
    print(f"total trades {call_win + put_win + call_lose + put_lose}")
    print(f"won trades : {call_win + put_win}")
    print(f"lost trades : {call_lose + put_lose}")
    print(f"total call trades {call_win + call_lose} ,, ITM = {call_win} ,, OTM = {call_lose}")
    print(f"total put trades {put_win + put_lose} ,, ITM {put_win} ,, OTM {put_lose}")

    return dataframe

s = send(json_data)
#s = pd.read_excel("backtest.xlsx")#(,"openpyxl")
#backtest = analize(resp)
backtest = analize(s)
#backtest.to_excel("backtest2.xlsx")



