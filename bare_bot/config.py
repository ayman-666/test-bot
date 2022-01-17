token = 'YSlL7MkIy8mM90q'

app_id = 24354



DB_NAME = "test.db"

apiUrl = "wss://ws.binaryws.com/websockets/v3?app_id="+str(app_id)

req_json = {
     "ticks_history": "R_100",
    "adjust_start_time": 1,
     "count": 5,
    "end": "latest",
    "start": 1,
    "style": "candles",
    "granularity" : 60
    }

in_position = False