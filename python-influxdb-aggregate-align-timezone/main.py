import datetime
import warnings
from datetime import timedelta

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
from IPython.display import display
from influxdb_client import InfluxDBClient

warnings.filterwarnings("ignore")

pd.set_option('display.max_columns', None)
client = InfluxDBClient(url="http://localhost:8086",
                        token="wjUebuzyHu58N1c_9O-vAA-8SLN8OzdUH_i1J-vICHz1tHRHiSCSKSsF6aiKH7CQIdSLEX8AVl1qXg9IlnrIJw==",
                        org="iseunghan-org", timeout=30_000)


def aggregate_with_flux_query_timeSrc():
    df = client.query_api().query_data_frame('''
    from(bucket: "iseunghan-test-bucket")
      |> range(start: 2019-08-17T00:00:00Z, stop: 2019-09-17T22:00:00Z)
      |> filter(fn: (r) => r["_measurement"] == "average_temperature")
      |> filter(fn: (r) => r["location"] == "santa_monica")
      |> filter(fn: (r) => r["_field"] == "degrees")
      |> aggregateWindow(every: 1d, fn: mean, timeSrc: "_start", createEmpty: false)
      // timeSrc: '_start'로 설정해야 원하는 기준일로 집계가 된다. (기본값: "_stop")
    ''')

    df = df.drop(columns=["result", "table", "_measurement", "location", "_field", "_start", "_stop"], errors="ignore")
    df["_time_kst"] = pd.to_datetime(df["_time"]).dt.tz_convert("Asia/Seoul")
    display(df.head())
    display(".......")
    display(df.tail())


def aggregate_with_flux_range_timeshift():
    start_dt = datetime.datetime(2019, 8, 17, 0, 0, 0, tzinfo=datetime.timezone(timedelta(hours=9)))
    stop_dt = datetime.datetime(2019, 9, 17, 22, 0, 0, tzinfo=datetime.timezone(timedelta(hours=9)))

    df = client.query_api().query_data_frame(f'''
        from(bucket: "iseunghan-test-bucket")
          |> range(start: {start_dt.isoformat()}, stop: {stop_dt.isoformat()})
          |> filter(fn: (r) => r["_measurement"] == "average_temperature")
          |> filter(fn: (r) => r["location"] == "santa_monica")
          |> filter(fn: (r) => r["_field"] == "degrees")
          |> aggregateWindow(every: 1d, fn: mean, timeSrc: "_start")
        ''')
    df = df.drop(columns=["result", "table", "_measurement", "location", "_field"], errors="ignore")
    display(df.head())


def aggregate_with_flux_offset():
    df = client.query_api().query_data_frame(f'''
        from(bucket: "iseunghan-test-bucket")
          |> range(start: 2019-08-17T00:00:00+09:00, stop: 2019-09-17T22:00:00+09:00)
          |> filter(fn: (r) => r["_measurement"] == "average_temperature")
          |> filter(fn: (r) => r["location"] == "santa_monica")
          |> filter(fn: (r) => r["_field"] == "degrees")
          |> aggregateWindow(every: 1d, fn: mean, timeSrc: "_start", offset: -9h)
        ''')
    df = df.drop(columns=["result", "table", "_measurement", "location", "_field"], errors="ignore")
    df["_time_kst"] = pd.to_datetime(df["_time"]).dt.tz_convert("Asia/Seoul")
    display(df.head())


aggregate_with_flux_query_timeSrc()
aggregate_with_flux_range_timeshift()
aggregate_with_flux_offset()
client.close()
