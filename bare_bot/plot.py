import plotly.graph_objects as go

import pandas as pd
from datetime import datetime

df = pd.read_excel("backtest3.xlsx")#(,"openpyxl")

fig = go.Figure(data=[go.Candlestick(x=df['epoch'],
                open=df['open'],
                high=df['high'],
                low=df['low'],
                close=df['close'],
                line=dict(width=1))])
fig.add_trace(go.Line(x=df['epoch'],y=df["ema"],))
fig.update()
go.Figure()
fig.show()