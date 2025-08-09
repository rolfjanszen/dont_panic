import influxdb_client, os, time
from influxdb_client import InfluxDBClient, Point, WritePrecision
from influxdb_client.client.write_api import SYNCHRONOUS, ASYNCHRONOUS
import datetime
import pandas as pd
import yfinance as yf
from os.path import isfile
from typing import List
from influxdb_client.client.flux_table import FluxTable, FluxRecord,TableList
from matplotlib import pyplot as plt

DATA_FILE = "data.csv"
API_TOKEN="Pym_0XIdUpnWNw1gEt-rQFLmxj7ef6oFttcmhNgNEHPRcxqMJc22poEhZ6M9ngUtQIrcaGICKKjfQintRzReA=="
tick_symbol = "QQQ"
TOKEN ="-QNRtO_eyCg9gtFPqqXhzgE5OHsujGwOMFJ3MRHIxN6BMfHYA=="

start = datetime.datetime(2020,1,1)
end = datetime.datetime.now()
# if isfile(DATA_FILE):
#     data = pd.read_csv(DATA_FILE)
# else:
data = yf.download(tick_symbol, start=start, end=end)
pd.DataFrame(data).to_csv(DATA_FILE)

token = os.environ.get("INFLUXDB_TOKEN")
org = "dev1"
url = "http://127.0.0.1:8086"

client = influxdb_client.InfluxDBClient(url=url, token=TOKEN, org=org)
bucket="buck1"
query_api = client.query_api()
# query = f'from(bucket:"{bucket}") |> range(start: -1h)'
# tables = query_api.query(query, org=org)
# print(tables)
# bucket="<BUCKET>"

# write_api = client.write_api(write_options=SYNCHRONOUS)
#    export INFLUX_TOKEN=Dpi3adU5YjulngdvV04pYgb_VtOcE8Fr6Qy5MV-yHR47U5DC5RXuBZcDN7iqpNrGJW0YcWKtsYupagZd92LoBg==
# for value in range(5):
#   point = (
#     Point("measurement1")
#     .tag("tagname1", "tagvalue1")
#     .field("field1", value)
#   )
#   write_api.write(bucket=bucket, org="dev1", record=point)
#   time.sleep(1) # separate points by 1 second


# exit(0)
write_api = client.write_api(write_options=SYNCHRONOUS)
for i in range(len(data)):
    # time_stamp = datetime.datetime.strptime(data["Date"][i], "%Y-%m-%d")
    d_time = datetime.datetime.fromisoformat(data["Date"][i])
    point = Point("stock4").tag("ticker", tick_symbol).field("open", data["Open"][i]).field("high", data["High"][i]).field("low", data["Low"][i]).field("close", data["Close"][i]).field("adjclose", data["Adj Close"][i]).field("volume", data["Volume"][i])
    point.time(time=d_time, write_precision=WritePrecision.S)
    write_api.write(bucket=bucket, record=point, org='dev1')
    # time.sleep(0.01)

query = """from(bucket: "buck1")
|> range(start: -1000d)
|> filter(fn: (r) => r["_field"] == "low" or r["_field"] == "high")
|> filter(fn: (r) => r._measurement == "stock4")"""
tables:TableList = query_api.query(query, org="dev1")
tables.to_values(columns=["_time", "_value","_field"])
for table in tables:
    for record in table.records:
        print(record)
    for column in table.columns:
        print(column)

#plot the table records using matplotlib


query = f'from(bucket:"{bucket}") |> range(start: -1h) |> filter(fn: (r) => true)'
tables = query_api.query(query, org=org)
for table in tables:
    for record in table.records:
        print(record.get_field())
        print(record.get_value())
        print(record.get_time())
        print(record.get_measurement())
print(data)


