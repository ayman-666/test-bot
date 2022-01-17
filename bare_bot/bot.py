from pandas.core.frame import DataFrame
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
     "count": 20,
    "end": "latest",
    "start": 1,
    "style": "candles",
    "granularity" : 60
    })


def send(massege,ws= websocket.WebSocket()):
    ws.connect(apiUrl)
    hs = ws.getstatus()
    print(hs)
    ws.send(massege)
    rec = json.loads(ws.recv())
    if 'candles' in rec.keys():
        recived = pd.DataFrame(json.loads(ws.recv())['candles'])
        return recived
    else:
        recived = json.loads(ws.recv())
        print(recived)
        return recived

def analize(dataframe):
    if 'high' in dataframe.keys():
        dataframe['engulfing'] = talib.CDLENGULFING(dataframe['open'],dataframe['high'],dataframe['low'],dataframe['close'])
        print(dataframe)
        return dataframe
    else:
        return False


def pop_signal(dataframe):
    before_row = dataframe.iloc[[18]]
    eng = int(before_row['engulfing'])
    print (f" eng = {eng}")
    print (f"before row {before_row}")
    if eng == 100:
        send(json.dumps({'authorize': token}))
        send(json.dumps({"buy": 1, "subscribe": 1, "price": 10, "parameters": {
                "amount": 10, "basis": "stake", "contract_type": "CALL", "currency": "USD", "duration": 1,
                "duration_unit": "m", "symbol": "R_100"}}))
    elif eng == -100 :
        send(json.dumps({'authorize': token}))
        send(json.dumps({"buy": 1, "subscribe": 1, "price": 10, "parameters": {
                "amount": 10, "basis": "stake", "contract_type": "PUT", "currency": "USD", "duration": 1,
                "duration_unit": "m", "symbol": "R_100"}}))


x = 0
while 1:
    
    print(x)
    resp = send(json_data)
    analized = analize(resp)
    pop_signal(analized)
    time.sleep(3)
    x += 1


