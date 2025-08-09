from ib_insync import *

# Connect to TWS (make sure TWS is open and listening on port 7497)
ib = IB()
ib.connect('127.0.0.1', 7497, clientId=1)

# Define the contract for QQQ
qqq = Stock('QQQ', 'SMART', 'USD')

# Request historical data (1-day bars for the past 30 days)
bars = ib.reqHistoricalData(
    qqq,
    endDateTime='',
    durationStr='30 D',
    barSizeSetting='1 day',
    whatToShow='TRADES',
    useRTH=True,
    formatDate=1
)

# Convert to DataFrame for viewing or analysis
df = util.df(bars)
print(df[['date', 'open', 'high', 'low', 'close', 'volume']])

# Disconnect after you're done
ib.disconnect()
