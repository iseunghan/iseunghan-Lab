# influxDB aggregateWindow 타임존 이슈 여정기
저번 포스팅에 이어, 이번에는 influxdb의 UTC의 데이터를 `aggregateWindow` 함수를 이용해 집계를 내다보니 KST 기준의 데이터와는 차이가 있어 추후에 실수를 방지하기 위해 삽질했던 경험들을 기록하고 해결한 경험을 소개하고자 합니다.

### 테스트 환경
> 이번 테스트를 위한 influxdb 구축은 따로 설명하지 않습니다.
- python 3.12
- influxdb v2.7.12 (docker)
- test dataset: [noaa-water-sample-data](https://docs.influxdata.com/influxdb/v2/reference/sample-data/#noaa-water-sample-data)
  - time range: `2019-08-17T00:00:00Z` ~ `2019-09-17T22:00:00Z`
  - measurement: [`average_temperature`, `h2o_feet`, `h2o_pH`, `h2o_quality`, `h2o_temperature`]
  - location(tag): [`coyote_creek`, `santa_monica`]
  - field_key: [`degrees`, `index`, `level description`, `pH`, `water_level`]  


##  aggregateWindow는 UTC 기준으로 집계가 이뤄진다
> 관련 코드: main.py/aggregate_with_flux_query_timeSrc 

influxdb에 모든 데이터는 UTC 기준으로 저장되어 있습니다. UTC와 KST는 9시간 차이가 납니다.  
그럼 다음 데이터는 어느 날짜 기준으로 합계되었는지 생각해봅시다.
```shell
from(bucket: "iseunghan-test-bucket")
      |> range(start: 2019-08-17T00:00:00Z, stop: 2019-09-17T22:00:00Z)
      |> filter(fn: (r) => r["_measurement"] == "average_temperature")
      |> filter(fn: (r) => r["location"] == "santa_monica")
      |> filter(fn: (r) => r["_field"] == "degrees")
      |> aggregateWindow(every: 1d, fn: mean, createEmpty: false)
```
예상했던 결과가 다음과 같나요?
```text
                      _time     _value
0 2019-08-17 00:00:00+00:00  80.012500
1 2019-08-18 00:00:00+00:00  80.162500
2 2019-08-19 00:00:00+00:00  79.333333
...
```
  
하지만 실행결과는 어떨까요? _time을 비교해보시면, 날짜가 하루 씩 밀린 것을 확인할 수 있습니다.
```text
                      _time     _value
0 2019-08-18 00:00:00+00:00  80.012500
1 2019-08-19 00:00:00+00:00  80.162500
2 2019-08-20 00:00:00+00:00  79.333333
...
```

이는 `aggregateWindow`의 [timeSrc](https://docs.influxdata.com/flux/v0/stdlib/universe/aggregatewindow/#timesrc) 옵션의 기본값이 `_stop`으로 설정되어 있어서 그렇습니다. 물론 개인마다 기준이 다르겠지만 현재 개발중인 서비스 관점에서는 실시간성으로도 집계가 반영되어야 하기 때문에 8월 17일 00시부터 8월 18일 00시 이전의 데이터의 집계는 8월 17일 날짜로 표기되어야 한다고 생각합니다. 즉, `timeSrc`를 `_start`로 설정하였습니다.
  
다음과 같이 쿼리를 수정하면 원하는 결과를 얻을 수 있습니다.
```shell
from(bucket: "iseunghan-test-bucket")
      |> range(start: 2019-08-17T00:00:00Z, stop: 2019-09-17T22:00:00Z)
      |> filter(fn: (r) => r["_measurement"] == "average_temperature")
      |> filter(fn: (r) => r["location"] == "santa_monica")
      |> filter(fn: (r) => r["_field"] == "degrees")
      |> aggregateWindow(every: 1d, fn: mean, timeSrc: "_start", createEmpty: false)
```
실행 결과:
```text
                      _time     _value
0 2019-08-17 00:00:00+00:00  80.012500
1 2019-08-18 00:00:00+00:00  80.162500
2 2019-08-19 00:00:00+00:00  79.333333
...
```