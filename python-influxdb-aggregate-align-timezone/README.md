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
