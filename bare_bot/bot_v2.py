
import websocket
import json
from config import *
import pandas as pd
import talib
import time

def get_stream(ws2= websocket.WebSocket()):
    ws2.send(json.dumps(req_json))
    return json.loads(ws2.recv())

def analize(dataframe):
    dataframe['engulfing'] = talib.CDLENGULFING(dataframe['open'],dataframe['high'],dataframe['low'],dataframe['close'])
    before_row = dataframe.iloc[[-2]]
    eng = int(before_row['engulfing'])
    print(eng)
    return dataframe,eng

def on_open(ws):
    json_data = json.dumps(req_json)
    ws.send(json_data)

def on_message(ws, message):
    
    data = json.loads(message)
    
    while 'candles' in data.keys() :
        ws.send(json.dumps(req_json))
        data1 = json.loads(message)
        recived,eng = analize(pd.DataFrame(data1['candles']))
        print(recived)
        time.sleep(3)
        if eng != 0 :
            break
    in_position = False
    # if eng != 0 and not in_position :
    #     ws.send(json.dumps({'authorize': token}))
    #     #print('Data: %s' % message) # Uncomment this line to see all response data.
    #     if 'error' in data.keys():
    #         print('Error Happened: %s' % message)
    #         # With Websockets we can not control the order things are processed in so we need
    #         # to ensure that we have received a response to authorize before we continue.
    #     elif data["msg_type"] == 'authorize':
    #         print("Authorized OK, so now buy Contract")
    #         json_data1 = json.dumps({"buy": 1, "subscribe": 1, "price": 10, "parameters": {
    #                                 "amount": 10, "basis": "stake", "contract_type": "CALL", "currency": "USD", "duration": 1, "duration_unit": "m", "symbol": "R_100"}})
    #         ws.send(json_data1)

    #     # Our buy request was successful let's print the results.
    #     elif data["msg_type"] == 'buy':
    #         print("contract Id  %s " %  data["buy"]["contract_id"] )
    #         print("Details %s " % data["buy"]["longcode"] )
    #         in_position = True
        
    #     # Because we subscribed to the buy request we will receive updates on our open contract.
    #     elif data["msg_type"] == 'proposal_open_contract':
    #         isSold = bool(data["proposal_open_contract"]["is_sold"])
    #     # If `isSold` is true it means our contract has finished and we can see if we won or not.
    #         if isSold:
    #             print("Contract %s " % data["proposal_open_contract"]["status"] )
    #             print("Profit %s " %  data["proposal_open_contract"]["profit"] )
    #             in_position = False
    #         else:  # We can track the status of our contract as updates to the spot price occur.
    #             currentSpot = data["proposal_open_contract"]["current_spot"]
    #             entrySpot = 0
    #             if data["proposal_open_contract"]["entry_tick"] != None:
    #                 entrySpot = data["proposal_open_contract"]["entry_tick"]
            
    #         print ("Entry spot %s" % entrySpot )
    #         print ("Current spot %s" % currentSpot )
    #         print ("Difference %s" % (currentSpot - entrySpot) )
           
if __name__ == "__main__":
    ws = websocket.WebSocketApp(apiUrl, on_message=on_message, on_open=on_open,)
    ws.run_forever()