import websocket, json , talib , time
import pandas as pd
from config import *

def buy(direction , duration = 1 ,ws2 = websocket.WebSocket()):
    ws2.connect(apiUrl)
    data = json.dumps({'authorize': token})
    ws2.send(data)
    
    while True :
        message = json.loads(ws2.recv())
        print("message conatins")
        print(message)
        if 'error' in message.keys():
            print('Error Happened: %s' % message)
            # With Websockets we can not control the order things are processed in so we need
            # to ensure that we have received a response to authorize before we continue.
        elif message["msg_type"] == 'authorize':
            print("Authorized OK, so now buy Contract")
            json_data1 = json.dumps({"buy": 1, "price":100, "parameters": {
                                    "amount": 10, "basis": "stake", "contract_type": f"{direction}", "currency": "USD", "duration": duration, "duration_unit": "m", "symbol": "R_100"}})
            ws2.send(json_data1)
            # Our buy request was successful let's print the results.
        elif message["msg_type"] == 'buy':
            print("contract Id  %s " %  message["buy"]["contract_id"] )
            print("Details %s " % message["buy"]["longcode"] )
            break
        ws2.close


def get_stream(ws10 = websocket.WebSocket()):
    ws10.connect(apiUrl)
    json_data = json.dumps({
     "ticks_history": "R_100",
    "adjust_start_time": 1,
     "count": 200,
    "end": "latest",
    "start": 1,
    "style": "candles",
    "granularity" : 60
    })
    ws10.send(json_data)
    rec = json.loads(ws10.recv())
    rec = pd.DataFrame(rec['candles'])
    return rec

def analize(dataframe):
    dataframe['engulfing'] = talib.CDLENGULFING(dataframe['open'],dataframe['high'],dataframe['low'],dataframe['close'])
    dataframe['epoch'] = [time.ctime(x) for x in dataframe['epoch'] ]
    dataframe['cci'] = talib.CCI(dataframe['high'], dataframe['low'], dataframe['close'], timeperiod=10)
    dataframe['angle_near'] = talib.LINEARREG_ANGLE(dataframe['close'], timeperiod=14)
    dataframe['angle_far'] = talib.LINEARREG_ANGLE(dataframe['close'], timeperiod=30)
    return dataframe

def on_open(ws):
    data = json.dumps(req_json)
    ws.send(data)

def on_message(ws, message):
    data = json.loads(message)
    #print('Data: %s' % message) # Uncomment this line to see all response data.
    if 'error' in data.keys():
        print('Error Happened: %s' % message)
    while True :
        rec = analize(get_stream())
        print (rec.tail(10))
        eng = int(rec.iloc[[-2]]['engulfing'])
        ang_n = float(rec.iloc[[-2]]['angle_near'])
        ang_f = float(rec.iloc[[-2]]['angle_far'])
        
        if eng != 0:
            if eng == 100 and ang_n > 0  :
                buy("CALL")
                time.sleep(60)
            elif eng == -100 and ang_n < 0 :
                buy("PUT")
                time.sleep(60)
        # if  (ang_n not in range (-80 , 80)) and (ang_f not in range (-75 , 75)) :
        #     if ang_n < -80 and ang_f < -75 :
        #             buy("PUT")
        #             time.sleep(60)
        #     elif  ang_n > 80 and ang_f > 75 :
        #             buy("CALL")
        #             time.sleep(60)
        time.sleep(3)
    
if __name__ == "__main__":
    ws = websocket.WebSocketApp(apiUrl, on_message=on_message, on_open=on_open)
    ws.run_forever()