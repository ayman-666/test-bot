
from cgi import print_environ_usage
from numpy import angle
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
    dataframe['cci'] = talib.CCI(dataframe['high'], dataframe['low'], dataframe['close'], timeperiod=3)
    dataframe['ema'] = talib.EMA(dataframe['open'],timeperiod = 4)
    dataframe['ATR'] = talib.ATR(dataframe['high'], dataframe['low'], dataframe['close'], timeperiod=5)
    dataframe['rsi'] = talib.RSI(dataframe['close'], timeperiod=10)
    dataframe['LR_angle'] = talib.LINEARREG_ANGLE(dataframe['close'], timeperiod=2)
    dataframe['LR'] = talib.LINEARREG(dataframe['close'], timeperiod=10)
    dataframe['upperband'], dataframe['middleband'], dataframe['lowerband'] = talib.BBANDS(dataframe['close'], timeperiod=50, nbdevup=1.6, nbdevdn=1.6, matype=0)
    print(dataframe.tail(20))

#back test using dataframe rolling window
    for win in dataframe.rolling(window = 4):
        try:
            angle1 = int(win.iloc[[0]]['LR_angle'])
            angle2 = int(win.iloc[[1]]['LR_angle'])
            UB = float(win.iloc[[1]]['upperband'])
            LB = float(win.iloc[[1]]['lowerband'])
            cci = int(win.iloc[[1]]['cci'])
            ema = float(win.iloc[[1]]['ema'])
            close = float(win.iloc[[1]]['close'])
            atr = float(win.iloc[[1]]['ATR'])
            rsi = float(win.iloc[[1]]['rsi'])
            previous_candle_is_green_and_above_TRIMA = (float(win.iloc[[1]]['close']) < float(win.iloc[[1]]['open'])) and (float(win.iloc[[1]]['close']) > float(win.iloc[[1]]['ema']))
            previous_candle_is_red_and_below_TRIMA = float(win.iloc[[1]]['close']) > float(win.iloc[[1]]['open']) and (float(win.iloc[[1]]['open']) < float(win.iloc[[1]]['ema']))

            if previous_candle_is_green_and_above_TRIMA and cci > 70:
                if float(win.iloc[[2]]['open']) < float(win.iloc[[2]]['close']):
                    call_win = call_win +1
                    initial_balance = initial_balance + (stake * 0.95)
                    pnl_seq.append(f"w({initial_balance})")
                elif float(win.iloc[[1]]['open']) > float(win.iloc[[2]]['close']):
                    call_lose = call_lose + 1
                    initial_balance = initial_balance - stake
                    pnl_seq.append(f"l({initial_balance})")
            elif previous_candle_is_red_and_below_TRIMA  and cci < -70:
                if float(win.iloc[[2]]['open']) > float(win.iloc[[2]]['close']):
                    put_win = put_win +1
                    initial_balance = initial_balance + (stake * 0.95)
                    pnl_seq.append(f"w({initial_balance})") 
                elif float(win.iloc[[2]]['open']) < float(win.iloc[[2]]['close']):
                    put_lose = put_lose + 1
                    initial_balance = initial_balance - stake
                    pnl_seq.append(f"l({initial_balance})")
            stake = initial_balance // 10
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
#backtest.to_excel("backtest3.xlsx")



