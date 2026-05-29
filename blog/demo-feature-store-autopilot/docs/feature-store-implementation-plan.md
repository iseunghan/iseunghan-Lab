# Feature Store Demo Implementation Plan

이 문서는 `demo-mlops-feature-store` 저장소의 feature store 데모를 실제로 작업할 때 기준이 되는 실행 계획이다.

## 목적

- 이 데모가 보여줘야 하는 핵심은 `raw data -> feature engineering -> offline historical retrieval -> training dataset -> materialization -> online serving` 이다.
- 목적은 기능 추가가 아니라, feature store의 역할을 `offline` 과 `online` 으로 분리해서 설명 가능한 상태로 만드는 것이다.
- 특히 학습 데이터 생성은 `online snapshot` 이 아니라 `historical features` 기반이어야 한다.
- 이 문서는 아래 질문에 답할 수 있을 정도로 구체적이어야 하며, 아래 항목을 모두 명시한다.
  - 어떤 함수가 어떤 입력을 받고 어떤 출력을 내는가
  - 어떤 파일이 어떤 책임을 가지는가
  - 어떤 테스트가 통과해야 작업이 끝나는가
  - 실패 시 무엇을 로그로 남기고 어떤 상태 코드/반환값을 내는가
  - 어떤 값이 기본값이고 어떤 값은 반드시 명시해야 하는가

## 현재 문제 요약

- 학습 데이터 생성이 offline store가 아니라 online store 스냅샷에 의존하는 경로가 있다.
- materialization 설명과 실제 구현이 일치하지 않는 부분이 있다.
- `FeatureView schema` 에 entity 와 timestamp 가 feature처럼 들어가 있어 개념이 흐려진다.
- UI와 README가 일부 경로를 placeholder 또는 잘못된 Feast CLI 예시로 보여준다.

## 작업 원칙

- feature store의 개념을 우선한다.
- 구현보다 계약을 먼저 맞춘다.
- 코드, 테스트, 문서를 함께 수정한다.
- 불필요한 추상화보다 데모에서 바로 이해되는 흐름을 우선한다.
- 변경은 가능한 한 작은 단위로 나눈다.
- 각 단계는 독립적으로 검증 가능해야 한다.

## 확정 사항

- 학습 데이터 생성의 canonical path 는 `historical features` 이다.
- training dataset 은 `parquet` 를 기본 저장 형식으로 사용한다.
- materialization 은 `latest offline features -> online store` 적재만 수행한다.
- `FeatureView.schema` 에는 실제 feature 만 남기고 `vehicle_id`, `event_timestamp` 는 제외한다.
- `image_uri`, `audio_uri` 는 Feast feature가 아니라 raw trace metadata 로 취급한다.
- `materialize` API 와 job script 는 동일한 계약을 사용한다.
- UI 는 backend API 만 호출하고, 직접 job script 를 실행하지 않는다.
- training dataset 의 synthetic label 은 `RiskModelService.calculate_risk_score()` 규칙을 따른다.

## 목표 아키텍처

```text
Vehicle Simulator
  -> Kafka
  -> Raw Stores (InfluxDB, MinIO)
  -> Feature Engineering Job
  -> Feast Offline Store (Parquet / DuckDB)
  -> Training Dataset Generation
  -> Feast Materialization
  -> Redis Online Store
  -> FastAPI Serving
  -> Streamlit UI
```

## 범위

### 포함

- historical feature retrieval 기반 training dataset 생성
- incremental materialization 계약 정리
- FeatureView schema 정리
- API, frontend, README, project spec 동기화
- 관련 테스트 갱신

### 제외

- 실제 ML 모델 학습 파이프라인
- 실시간 스트리밍 모델 서빙 최적화
- 이미지/오디오 실제 CV / ASR 모델 구현

## 실행 순서

### 1. Training Dataset 생성 경로 정리

#### 목표

- training dataset 이 `현재 시각 스냅샷`이 아니라 `historical features` 로 생성되게 만든다.
- offline store 가 왜 필요한지 가장 직접적으로 보여준다.

#### 구현 방향

- `jobs/generate_training_dataset.py` 의 production 경로는 `get_historical_features()` 만 사용한다.
- `get_online_features()` 호출은 허용하지 않는다.
- 조회 범위는 다음 규칙으로 계산한다.
  - `end_time = now UTC`
  - `start_time = end_time - hours`
  - `interval_minutes` 간격으로 entity row 를 생성한다.
- `vehicle_ids` 는 명시적으로 주입한다. 기본값은 `["V001", "V002", "V003"]` 이다.
- 각 vehicle 에 대해 historical lookup 을 수행하고, 결과를 하나의 DataFrame 으로 합친다.
- `event_timestamp` 는 Feast가 반환한 historical timestamp 를 그대로 유지한다.
- `datetime.now()` 로 다시 덮어쓰지 않는다.
- `label_source` 는 반드시 `synthetic_rule_v1` 로 고정한다.
- synthetic label 은 `RiskModelService.calculate_risk_score()` 와 동일한 규칙을 사용한다.

#### 확정 API / 스크립트 계약

- `jobs/generate_training_dataset.py`
  - demo mode: `python jobs/generate_training_dataset.py --demo --output <path>`
  - production mode: `python jobs/generate_training_dataset.py --output <path> [--hours 168] [--interval-minutes 60] [--vehicle-ids V001,V002,V003]`
  - 기본 출력 형식은 `parquet` 이다.
  - `csv` 는 명시적으로 preview 가 필요할 때만 사용한다.
- `FeastService.get_historical_features(vehicle_id, feature_views=None, start_time=None, end_time=None, interval_minutes=60) -> List[Dict]`
  - 반환 dict 는 최소한 `vehicle_id`, `event_timestamp`, feature columns 를 포함한다.
  - `feature_views` 기본값은 `["sensor_features", "image_features", "audio_features"]` 이다.
- `generate_from_feast(feast_service, vehicle_ids, output_path, hours=DEFAULT_HOURS, interval_minutes=60) -> bool`
  - 반드시 `get_historical_features()` 를 호출한다.
  - `hours` 는 조회 범위 계산에만 사용한다.
  - vehicle 별 결과가 모두 비어 있으면 실패를 반환한다.
- `POST /api/features/training-dataset`
  - 요청 body 예시: `{"output_path":"./data/training_dataset.parquet","hours":168,"interval_minutes":60,"vehicle_ids":["V001","V002","V003"]}`
  - 응답 body 예시:
    ```json
    {
      "success": true,
      "message": "Training dataset generated successfully",
      "output_path": "./data/training_dataset.parquet",
      "row_count": 36,
      "feature_count": 10,
      "label_distribution": {"LOW": 12, "MEDIUM": 16, "HIGH": 8}
    }
    ```
- `main()`
  - demo/prod 모드를 분리한다.
  - production 경로가 canonical path 다.

#### 확정 출력 스키마

| 컬럼 | 타입 | 규칙 |
|---|---|---|
| `vehicle_id` | string | entity key |
| `event_timestamp` | timestamp(UTC) | historical lookup timestamp, 재작성 금지 |
| `avg_speed_10s` | float | Feast sensor feature |
| `accel_std_10s` | float | Feast sensor feature |
| `obstacle_distance_min` | float | Feast sensor feature |
| `lidar_point_count` | int | Feast sensor feature |
| `sensor_missing_rate` | float | Feast sensor feature |
| `object_count` | int | Feast image feature |
| `pedestrian_count` | int | Feast image feature |
| `lane_detect_score` | float | Feast image feature |
| `noise_level` | float | Feast audio feature |
| `siren_detected` | bool | Feast audio feature |
| `risk_score` | float | `RiskModelService` 규칙으로 생성 |
| `risk_level` | string | `HIGH` / `MEDIUM` / `LOW` |
| `label_source` | string | 항상 `synthetic_rule_v1` |

#### 완료 기준

- 같은 차량에 대해 여러 historical row 가 나온다.
- training dataset 에는 online snapshot timestamp 가 들어가지 않는다.
- offline preview 와 training dataset 이 같은 historical source 를 쓴다.
- row 수가 `vehicle_ids * time steps` 구조로 이해 가능해야 한다.
- training dataset 생성 로그만 봐도 historical retrieval 을 사용했는지 알 수 있어야 한다.
- parquet 파일이 기본 산출물이다.

#### 테스트 포인트

- `get_historical_features()` 가 training dataset 생성에 사용되는지 검증
- `get_online_features()` 가 호출되지 않는지 검증
- label 컬럼 존재 여부
- timestamp 가 과거 시점인지 검증
- `event_timestamp` 가 `datetime.now()` 로 덮어써지지 않는지 검증
- empty historical result 에 대한 실패/경고 처리 검증

### 2. Materialization 계약 정리

#### 목표

- `materialize` 가 하는 일을 한 문장으로 설명 가능하게 만든다.
- `latest offline features -> redis online store` 로 의미를 고정한다.

#### 구현 방향

- `jobs/materialize.py` 와 `/api/features/materialize` 는 동일한 입력/출력 계약을 가진다.
- `--hours` 는 제거한다.
- `start_date` / `start_time` 은 materialization 입력이 아니다.
- 입력은 `end_date` 하나로 충분하다.
- `end_date` 가 없으면 now UTC 를 사용한다.
- materialization 은 registry state 기준 incremental update 로 동작한다.
- offline store 의 최신 데이터만 online store 로 적재한다.
- historical dataset 생성과 materialization 은 분리한다.

#### 확정 계약

- 입력
  - `end_date` optional, ISO-8601 UTC
- 동작
  - `FeatureStore.materialize_incremental(end_date=end_date)` 호출
  - offline store 에서 Redis online store 로 최신 feature 적재
- 출력
  - `success: bool`
  - `message: str`
  - `end_date: str`
  - `materialized_feature_views: List[str]`

#### 확정 함수 계약

- `FeastService.materialize_incremental(end_date=None) -> bool`
  - 내부에서 `FeatureStore.materialize_incremental(end_date=end_date)` 를 호출한다.
  - `end_date` 는 timezone-aware UTC 여야 한다.
- `jobs/materialize.py`
  - `--end-date` 만 파싱한다.
  - `--hours` 는 존재하지 않는다.
  - 성공 시 0, 실패 시 1 을 반환한다.
- `POST /api/features/materialize`
  - 요청 body 예시: `{"end_date":"2026-05-24T12:00:00Z"}`
  - 응답 body 예시:
    ```json
    {
      "success": true,
      "message": "Materialization completed successfully",
      "end_date": "2026-05-24T12:00:00Z",
      "materialized_feature_views": ["sensor_features", "image_features", "audio_features"]
    }
    ```

#### 완료 기준

- 코드, 문서, UI의 materialization 설명이 동일하다.
- `--hours` 가 의미 없는 옵션으로 남아 있지 않다.
- API 호출과 job script 호출이 같은 의미를 가진다.
- 사용자가 “최근 N시간만 online store 에 반영된다”라고 오해하지 않게 된다.
- `end_date` 가 없을 때의 기본 동작이 명시되어 있다.

#### 테스트 포인트

- `materialize_incremental()` 호출 인자 검증
- `end_date` 가 API 에서 job 으로 전달되는지 검증
- API 와 job script 가 동일한 의미를 가지는지 검증
- materialization 문구가 README/UI 에서 일치하는지 검증

### 3. FeatureView Schema 정리

#### 목표

- Feast schema 에서 feature 와 entity/timestamp 의 경계를 분리한다.

#### 구현 방향

- `vehicle_id` 는 entity 이므로 `schema` 에서 제거한다.
- `event_timestamp` 는 `timestamp_field` 로만 사용하고 `schema` 에서 제거한다.
- `image_uri`, `audio_uri` 는 Feast FeatureView 에 포함하지 않는다.
- `schema` 에는 실제 feature 컬럼만 남긴다.
- `entities=[vehicle]` 와 `timestamp_field="event_timestamp"` 로 역할을 분리한다.
- sensor / image / audio feature view 모두 같은 기준을 적용한다.
- online serving 은 다음 feature set 만 사용한다.
  - `sensor_features`: `avg_speed_10s`, `accel_std_10s`, `obstacle_distance_min`, `lidar_point_count`, `sensor_missing_rate`
  - `image_features`: `object_count`, `pedestrian_count`, `lane_detect_score`
  - `audio_features`: `noise_level`, `siren_detected`
- `RiskModelService` 는 위 feature set 중 필요한 subset 만 사용한다.

#### 완료 기준

- `FeatureView` 정의만 봐도 feature 목록이 자연스럽다.
- schema 와 데이터 컬럼의 역할이 혼동되지 않는다.
- `vehicle_id` 와 `event_timestamp` 는 feature ref 에 포함되지 않는다.
- `get_online_features()` 와 `RiskModelService` 입력이 더 명확하게 맞아떨어진다.
- `image_uri`, `audio_uri` 는 Feast registry 에 등록되지 않는다.

#### 테스트 포인트

- `feast apply` 후 schema 의 의도 확인
- online retrieval feature set 과 risk model 입력이 일치하는지 확인
- registry 생성 후 feature refs 가 feature-only 인지 확인

### 4. UI / 문서 동기화

#### 목표

- 사용자가 데모를 따라갈 때 막히지 않게 한다.

#### 구현 방향

- `frontend/app.py`
  - Training Dataset 버튼은 `POST /api/features/training-dataset` 를 호출한다.
  - Materialization 버튼은 `POST /api/features/materialize` 를 호출한다.
  - Offline tab 은 historical feature preview 와 training dataset 생성을 분리해 설명한다.
  - Online serving 탭은 feature retrieval 과 prediction 의 차이를 분리해 보여준다.
- `README.md`
  - Feast CLI 예시는 `--end-date` 중심으로 수정한다.
  - offline / training / online 역할을 분리해서 설명한다.
- `project-spec.md`
  - 구현과 다르면 구현 기준으로 우선 정리한다.

#### 사용자 흐름

1. 이벤트 생성
2. raw data 저장 확인
3. feature build
4. offline feature preview 확인
5. training dataset 생성
6. materialization 실행
7. online feature 조회
8. risk prediction 확인

#### 완료 기준

- 사용자가 README 만 보고도 데모의 순서를 따라갈 수 있다.
- UI 텍스트가 실제 API 동작과 어긋나지 않는다.
- feature store 역할 설명이 offline/online/training 으로 분리되어 있다.
- 버튼 설명과 backend 응답 구조가 동일한 용어를 사용한다.

## 단계별 작업 체크리스트

### Step 1

- `jobs/generate_training_dataset.py` 수정
- 관련 service 호출 변경
- unit test 갱신

#### 1-1. 호출 경로 분리

- `generate_training_dataset.py` 에서 demo 경로와 production 경로를 명확히 분리한다.
- production 경로는 canonical path 로 남긴다.
- demo 경로는 fixture 생성용으로만 둔다.

#### 1-2. historical retrieval 연결

- `FeastService.get_historical_features()` 를 호출하도록 바꾼다.
- 조회 범위는 다음 기준으로 계산한다.
  - `end_time = now UTC`
  - `start_time = end_time - hours`
- `vehicle_ids` 를 순회하며 historical row 를 수집한다.
- 각 차량별 결과를 하나의 DataFrame 으로 합친다.
- `interval_minutes` 는 entity row 생성 간격이다.
- point-in-time lookup 결과만 포함한다.

#### 1-3. label 생성 규칙 정리

- 데모 목적상 synthetic label 은 허용한다.
- 다만 label 계산은 feature retrieval 이후 별도 단계로 분리한다.
- label 생성 함수는 feature extraction 과 독립적으로 작성한다.
- `label_source = synthetic_rule` 같은 메타 컬럼을 추가한다.
- `label_source` 의 최종 값은 `synthetic_rule_v1` 이다.

#### 1-4. 파일 저장 형식 정리

- 기본 저장 형식은 parquet 로 간다.
- CSV 는 preview 또는 디버깅 용도로만 쓴다.
- 출력 파일명은 날짜 기반보다 `dataset_type + timestamp` 형태가 더 안전하다.
  - 예: `training_dataset_20260524T120000Z.parquet`

#### 1-5. 로그 정리

- 시작 로그에 조회 범위, vehicle 수, interval 을 남긴다.
- 종료 로그에 row 수, feature 수, label 분포를 남긴다.
- 실패 시에는 어떤 vehicle 에서 실패했는지 남긴다.
- historical retrieval 을 사용했는지 로그에서 바로 식별 가능해야 한다.

#### 1-6. 테스트 정리

- `get_online_features()` 호출이 없어야 한다.
- `get_historical_features()` 호출이 있어야 한다.
- `event_timestamp` 가 현재 시각으로 덮어써지지 않아야 한다.
- 빈 결과에서의 동작은 경고를 남기고 실패 반환이다.

#### Step 1 완료 기준

- production 경로로 실행하면 historical rows 가 생성된다.
- training dataset 이 point-in-time lookup 기반임을 로그와 결과로 확인할 수 있다.
- 관련 test 가 새 계약을 반영한다.

### Step 2

- `jobs/materialize.py` 수정
- `/api/features/materialize` 정리
- README CLI 예시 정정

#### 2-1. job 계약 단순화

- `--hours` 는 제거한다.
- job 입력은 `end_date` 중심으로 단순화한다.
- materialization 범위는 registry state 에 의해 결정되도록 둔다.
- start / end 혼동을 없앤다.

#### 2-2. API 계약 정리

- `/api/features/materialize` 는 job 과 같은 의미를 가져야 한다.
- 응답에는 성공 여부와 materialized 대상 feature view 를 포함한다.
- 요청 body 에 `end_date` 를 받을 수 있어야 한다.

#### 2-3. 문구 동기화

- README 와 UI 에서 `materialize` 설명을 동일하게 맞춘다.
- `start/end` 와 `hours` 같은 혼동 요소를 제거한다.
- CLI 예시와 버튼 라벨이 같은 동사를 사용한다.

#### 2-4. 테스트 정리

- job script 가 실제로 어떤 인자로 `FeastService.materialize_incremental()` 을 호출하는지 검증한다.
- API response 가 성공/실패를 명확히 구분하는지 검증한다.
- `end_date` 기본값(now UTC) 검증을 포함한다.

#### Step 2 완료 기준

- materialization 이 feature refresh 용어로만 설명되지 않고, online store 적재 의미로만 설명된다.
- script / API / 문서가 같은 계약을 말한다.

### Step 3

- `feast_repo/feature_views.py` 정리
- `feast apply` 영향 확인
- schema 관련 테스트 정리

#### 3-1. schema 정리

- 각 FeatureView 에서 entity/timestamp 를 schema 에서 제거한다.
- 실제 feature 만 schema 에 남긴다.
- `image_uri`, `audio_uri` 도 schema 에서 제거한다.

#### 3-2. online feature set 축소 여부 결정

- `image_uri`, `audio_uri` 는 online serving 에서 제외한다.

#### 3-3. feature refs 정리

- `FeastService.get_online_features()` 와 `get_historical_features()` 의 feature refs 를 새 schema 와 맞춘다.
- 반환 dict 에는 entity/timestamp 가 포함되지 않는다.

#### 3-4. 테스트 정리

- registry apply 후 schema 가 의도대로 등록되는지 확인한다.
- online retrieval key 가 feature-only 로 유지되는지 확인한다.
- FeatureView 정의만으로 feature 목록을 검증할 수 있어야 한다.

#### Step 3 완료 기준

- Feast 개념상 schema 가 자연스럽다.
- entity/timestamp 와 feature 의 역할이 구분된다.

### Step 4

- `frontend/app.py` 수정
- README / project-spec 동기화
- 사용자 흐름 문구 정리

#### 4-1. UI 행동 연결

- Training Dataset 버튼이 실제 동작을 하도록 연결한다.
- Offline Features 탭에서 historical preview 와 dataset generation 의 차이를 드러낸다.
- Materialization 버튼은 end_date 를 전달하는 API 호출이어야 한다.

#### 4-2. 문구 정리

- materialization 안내 문구를 실제 구현과 맞춘다.
- online serving 설명을 current feature lookup 과 prediction 으로 나눈다.
- 버튼, 탭, API 문구에 `historical`, `online`, `materialize` 용어를 일관되게 사용한다.

#### 4-3. 문서 정렬

- README 는 사용자가 처음 보는 진입점이므로 가장 먼저 읽히도록 정리한다.
- project-spec 은 구현 기준으로 역추적 가능한 수준이면 충분하다.
- README 의 예시는 실제 실행 가능한 명령만 남긴다.

#### Step 4 완료 기준

- 사용자가 UI 만 보고도 전체 데모 흐름을 이해할 수 있다.
- 문서와 실제 버튼 동작이 어긋나지 않는다.

## 검증 방법

- 단위 테스트
- `backend/tests/test_training_dataset_job.py`
- `backend/tests/test_training_dataset_api.py`
  - `backend/tests/test_feast_service.py`
  - `backend/tests/test_feast_service_historical.py`
  - `backend/tests/test_offline_features_api.py`
  - `backend/tests/test_feature_views.py`
- 수동 검증
  - feature build 후 offline preview 확인
  - training dataset 생성 확인
  - materialization 후 online feature 조회 확인
  - prediction 결과 확인
- 문서 검증
  - README 에 적힌 명령이 실제 코드 흐름과 일치하는지 확인

## 수정 대상 파일 후보

- `jobs/generate_training_dataset.py`
- `jobs/materialize.py`
- `backend/app/services/feast_service.py`
- `feast_repo/feature_views.py`
- `backend/app/api/features.py`
- `frontend/app.py`
- `README.md`
- `project-spec.md`
- `backend/tests/*`

## 추천 작업 단위

1. Training dataset 경로부터 먼저 고친다.
2. materialization 계약을 정리한다.
3. FeatureView schema 를 정리한다.
4. 문서와 UI 를 마지막에 맞춘다.

## 최종 완료 정의

- offline historical retrieval 기반 training dataset 생성이 동작한다.
- materialization 이 의미와 구현이 일치한다.
- FeatureView schema 가 Feast 개념에 맞는다.
- 문서와 UI 가 실제 플로우와 같다.
- 관련 테스트가 통과한다.
- 사용자가 이 문서만 읽고도 구현 순서를 재현할 수 있다.
- 각 단계의 입력, 출력, 실패 조건이 문서에 고정되어 있다.
