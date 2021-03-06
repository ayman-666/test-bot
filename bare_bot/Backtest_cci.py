
import talib
import websocket
import json
import time
import pandas as pd
import plotly
from config import *

json_data = json.dumps({
     "ticks_history": "R_100",
    "adjust_start_time": 1,
    "count": 5000,
    "end": "latest",
    "start": 0,
    "style": "candles",
    "granularity" : 60
    })



def send(massege,ws= websocket.WebSocket()):
    ws.connect(apiUrl)
    hs = ws.getstatus()
    print(hs)
    ws.send(massege)
    recieved = pd.DataFrame(json.loads(ws.recv())['candles'])
    ws.close
    return recieved
    


def analize(dataframe):
    initial_balance,start_balance = 250 , 250
    stake = initial_balance/25
    pnl_seq = []
    call_win = 0
    call_lose = 0 
    put_win = 0 
    put_lose = 0
    dataframe['epoch'] = [time.ctime(x) for x in dataframe['epoch'] ]
    dataframe['cci'] = talib.CCI(dataframe['high'], dataframe['low'], dataframe['close'], timeperiod=4)
    dataframe['ema'] = talib.TRIMA(dataframe['close'],timeperiod = 50)
    dataframe['ATR'] = talib.ATR(dataframe['high'], dataframe['low'], dataframe['close'], timeperiod=5)
    dataframe['rsi'] = talib.RSI(dataframe['close'], timeperiod=3)
    dataframe['LR_angle'] = talib.LINEARREG_ANGLE(dataframe['close'], timeperiod=10)
    dataframe['LR'] = talib.LINEARREG(dataframe['close'], timeperiod=10)
    print(dataframe.tail(20))

#back test using dataframe rolling window
    for win in dataframe.rolling(window = 4):
        try:
            cci1 = float(win.iloc[[0]]['cci'])
            cci2 = float(win.iloc[[1]]['cci'])
            ema = float(win.iloc[[1]]['ema'])
            close = float(win.iloc[[1]]['close'])
            atr = float(win.iloc[[1]]['ATR'])
            rsi = float(win.iloc[[1]]['rsi'])
            
            if abs(cci1 - cci2) > 40 and  cci1 > cci2 and close > ema and rsi > 80: #atr < 14:# :
                if float(win.iloc[[2]]['open']) < float(win.iloc[[3]]['open']):
                    call_win = call_win +1
                    initial_balance = initial_balance + (stake * 0.95)
                    pnl_seq.append(f"w({initial_balance})")
                elif float(win.iloc[[1]]['open']) > float(win.iloc[[2]]['open']):
                    call_lose = call_lose + 1
                    initial_balance = initial_balance - stake
                    pnl_seq.append(f"l({initial_balance})")
            elif abs(cci1 - cci2) > 40 and  cci1 < cci2 and close < ema and rsi < 20:# atr < 14:# and:
                if float(win.iloc[[2]]['open']) > float(win.iloc[[3]]['open']):
                    put_win = put_win +1
                    initial_balance = initial_balance + (stake * 0.95)
                    pnl_seq.append(f"w({initial_balance})") 
                elif float(win.iloc[[2]]['open']) < float(win.iloc[[3]]['open']):
                    put_lose = put_lose + 1
                    initial_balance = initial_balance - stake
                    pnl_seq.append(f"l({initial_balance})")
            stake = initial_balance // 25
        except:
            pass
    print(f"initial balance {start_balance} , final balance {initial_balance} , PNL {initial_balance - start_balance}")          
    print(f"total trades {call_win + put_win + call_lose + put_lose}")
    print(f"won trades : {call_win + put_win}")
    print(f"lost trades : {call_lose + put_lose}")
    print(f"total call trades {call_win + call_lose} ,, ITM = {call_win} ,, OTM = {call_lose}")
    print(f"total put trades {put_win + put_lose} ,, ITM {put_win} ,, OTM {put_lose}")
    print(f"sequence : {pnl_seq}")

    return dataframe

s = send(json_data)
#s = pd.read_excel("backtest.xlsx")#(,"openpyxl")
#backtest = analize(resp)
backtest = analize(s)
backtest.to_excel("backtest3.xlsx")



