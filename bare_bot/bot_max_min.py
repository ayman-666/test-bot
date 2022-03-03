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
        #
        if 'error' in message.keys():
            print('Error Happened: %s' % message)
            # With Websockets we can not control the order things are processed in so we need
            # to ensure that we have received a response to authorize before we continue.
        elif message["msg_type"] == 'authorize':
            balance = message["authorize"]["balance"]
            print("Authorized OK, so now buy Contract")
            json_data1 = json.dumps({"buy": 1, "subscribe": 1,"price":100, "parameters": {
                                    "amount": (balance//10), "basis": "stake", "contract_type": f"{direction}", "currency": "USD", "duration": duration, "duration_unit": "m", "symbol": "R_100"}})
            ws2.send(json_data1)
            # Our buy request was successful let's print the results.
        elif message["msg_type"] == 'buy':
            print("contract Id  %s " %  message["buy"]["contract_id"] )
            print("Details %s " % message["buy"]["longcode"] )

        elif message["msg_type"] == 'proposal_open_contract':
            isSold = bool(message["proposal_open_contract"]["is_sold"])
                # If `isSold` is true it means our contract has finished and we can see if we won or not.
            if isSold:
                print("Contract %s " % message["proposal_open_contract"]["status"] )
                print("Profit %s " %  message["proposal_open_contract"]["profit"] )
                ws2.close()
                break
            else:  # We can track the status of our contract as updates to the spot price occur.
                currentSpot = message["proposal_open_contract"]["current_spot"]
                entrySpot = 0
                try:
                    if message["proposal_open_contract"]["entry_tick"] != None:
                        entrySpot = message["proposal_open_contract"]["entry_tick"]
                except:
                    pass
                print ("Entry spot %s" % entrySpot )
                print ("Current spot %s" % currentSpot )
                print ("Difference %s" % (currentSpot - entrySpot) )


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
    try:
        rec = pd.DataFrame(rec['candles'])
        return rec
    except:
        print (f"error happned while retreiving stream ::: {rec}")

def analize(dataframe):

#  {   Sma,    Ema,    Wma,    Dema,    Tema,    Trima,    Kama,    Mama,    T3 };
    dataframe['epoch'] = [time.ctime(x) for x in dataframe['epoch'] ]
    dataframe['ema'] = talib.EMA(dataframe['open'],timeperiod = 10)
    dataframe["ema_angle"] = talib.LINEARREG_ANGLE(dataframe['ema'], timeperiod=10)
    dataframe["TSF"] = talib.TSF(dataframe['close'], timeperiod=10)
    dataframe["ema_angle_long"] = talib.LINEARREG_ANGLE(dataframe['ema'], timeperiod=40)
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
        try:
            rec = analize(get_stream())
            #print (rec.tail(10))
            max_close_list = rec['close']
            max_close = max_close_list[0:-2].max()
            min_close_list = rec['close']
            min_close = min_close_list[0:-2].min()
            ema = float(rec.iloc[[-2]]['ema'])
            ema_angle = ema = float(rec.iloc[[-2]]['ema_angle'])
            ema_angle_l = ema = float(rec.iloc[[-2]]['ema_angle_long'])
            close = float(rec.iloc[[-2]]['close'])
            prev_red = float(rec.iloc[[-2]]['close']) > float(rec.iloc[[-2]]['open'])
            print(rec)
            print(f'max close : {max_close},   min close {min_close}   , ema angle = {ema_angle} , long ema angle {ema_angle_l}')
            if (close <= min_close and not prev_red) or (close >= max_close and prev_red) :
                    buy("CALL")
                    
            elif (close >= max_close and not prev_red) or (close <= min_close and prev_red):
                    buy("PUT")
                    
        except:
            pass
if __name__ == "__main__":
    ws = websocket.WebSocketApp(apiUrl, on_message=on_message, on_open=on_open)
    ws.run_forever()