# MLOps Feature Store Demo

자율주행 차량 위험도 예측을 위한 Feature Store 데모 프로젝트입니다.

## 아키텍처

```
Vehicle Simulator → Kafka → Sensor/Media Consumers
                         ↓
                    InfluxDB (raw sensor)
                    MinIO (raw media)
                         ↓
              Feature Engineering → Parquet
                         ↓
                    Feast (DuckDB + Redis)
                         ↓
                    FastAPI → Streamlit
```

## Feature Pipeline

raw 데이터를 feature 로 변환하고, offline store 에서 online store 로 전달하는 전체 흐름입니다.

### 흐름

```
Raw Data (InfluxDB/MinIO)
         │
         ├──→ build_features.py (Feature Engineering)
         │        │
         │        ├──→ Sensor Features (InfluxDB → aggregation)
         │        ├──→ Image Features (metadata-based demo, raw CV flow 미구현)
         │        └──→ Audio Features (metadata-based demo, raw audio flow 미구현)
         │
         ↓
Parquet Files (MinIO: mlops-features)
 │
 ├──→ sensor_features/{vehicle_id}/{date}.parquet
 ├──→ image_features/{vehicle_id}/{date}.parquet
 └──→ audio_features/{vehicle_id}/{date}.parquet
         │
         ↓
Feast FeatureViews (registry)
 │
 ├──→ sensor_features
 ├──→ image_features
 └──→ audio_features
         │
         ↓
Materialization → Redis (online store)
```

### Feature Views

| Feature View | 소스 | Feature 설명 | 구현 상태 |
|--------------|------|--------------|-----------|
| **sensor_features** | InfluxDB (time-series) | `avg_speed_10s`, `accel_std_10s`, `obstacle_distance_min`, `lidar_point_count`, `sensor_missing_rate` | ✅ 구현됨 |
| **image_features** | MinIO (media metadata JSON) | `object_count`, `pedestrian_count`, `lane_detect_score` | ⚠️ 데모용만 구현, raw image 기반 CV feature engineering 미구현 |
| **audio_features** | MinIO (media metadata JSON) | `noise_level`, `siren_detected` | ⚠️ 데모용만 구현, raw audio 기반 signal feature engineering 미구현 |

### Feature Engineering

**Backend API 를 통해**:
```bash
curl -X POST http://localhost:8000/api/features/build
```

**직접 실행** (로컬 개발 시):
```bash
cd backend && python -m app.main
# 또는
python jobs/build_features.py
```

기본 동작:
- `build_features.py` 는 최근 `168h`(7일) 데이터를 lookback 으로 사용합니다. 필요하면 `FEATURE_BUILD_LOOKBACK_HOURS` 로 변경할 수 있습니다.
- `/api/features/offline` 와 frontend preview 는 기본적으로 `10m` 간격으로 historical rows 를 조회합니다.

**동작**:
1. InfluxDB 에서 raw sensor data 조회
2. Time-window 별 aggregation (10-second windows)
3. Media metadata 에서 demo feature 생성
4. Parquet 파일로 MinIO 에 저장
5. Feast FeatureViews 에 등록

**미구현 / 예정**
- image raw bytes를 읽어 CV 모델을 돌리는 경로
- audio raw bytes를 읽어 waveform / spectral feature를 만드는 경로
- 추론 결과를 feature schema로 표준화하는 버전 관리

**정석적인 image/audio 플로우**
1. MinIO에서 raw image 또는 raw audio 파일 읽기
2. 파일 디코딩 및 전처리
3. CV 또는 audio 모델 추론 / 신호 처리 수행
4. 추론 결과를 feature row로 정규화
5. `vehicle_id`와 `event_timestamp`를 붙여 Parquet 저장
6. Feast `FeatureView`가 offline/online serving에 사용

**기본값 요약**:
- feature build lookback: `168h (7d)`
- historical preview interval: `10m`

### Materialization

`latest offline features -> Redis online store` incremental 적재:

**Backend API 를 통해**:
```bash
curl -X POST http://localhost:8000/api/features/materialize \
  -H "Content-Type: application/json" \
  -d '{"end_date":"2026-05-24T12:00:00Z"}'
```

**Feast CLI 로**:
```bash
cd feast_repo && feast materialize-incremental --end-date <timestamp>
```

**스크립트 사용**:
```bash
./scripts/run_materialize.sh [END_DATE]
```

### Training Dataset 생성

학습 데이터셋은 online snapshot 이 아니라 historical feature 조회로 생성됩니다.

```bash
curl -X POST http://localhost:8000/api/features/training-dataset \
  -H "Content-Type: application/json" \
  -d '{
    "output_path":"./data/training_dataset.parquet",
    "hours":168,
    "interval_minutes":60,
    "vehicle_ids":["V001","V002","V003"]
  }'
```

또는 job 스크립트:

```bash
python jobs/generate_training_dataset.py --output ./data/training_dataset.parquet --hours 168 --interval-minutes 60 --vehicle-ids V001,V002,V003
```

### Sample Feature 생성 스크립트

`feast_repo/scripts/create_sample_features.py` 는 로컬 파일을 만들지 않고 MinIO 에 직접 업로드합니다.

```bash
python feast_repo/scripts/create_sample_features.py
```

- 사용 환경변수: `MINIO_ENDPOINT`, `MINIO_ACCESS_KEY`, `MINIO_SECRET_KEY`, `MINIO_SECURE`, `MINIO_BUCKET`
- 업로드 경로: `s3://mlops-features/<feature_view>/<vehicle_id>/<YYYY-MM-DD>.parquet`

### 저장소 구성

| Store | 기술 | 용도 |
|-------|------|------|
| **Offline Store** | DuckDB + Parquet | Batch feature 조회, feature engineering |
| **Online Store** | Redis | 실시간 feature serving (low-latency) |
| **Registry** | SQLite | FeatureView metadata 저장 |

### 선행 사항

Materialization 을 실행하기 전에 다음이 필요합니다:

1. **Docker 이미지 빌드**: `feast apply` 가 이미지 빌드 시 자동으로 실행됩니다
2. **Parquet 데이터 존재**: MinIO 버킷 `mlops-features` 에 feature 파일이 있어야 함

### MinIO Parquet 경로 규칙

```
s3://mlops-features/
├── sensor_features/<vehicle_id>/<YYYY-MM-DD>.parquet
├── image_features/<vehicle_id>/<YYYY-MM-DD>.parquet
└── audio_features/<vehicle_id>/<YYYY-MM-DD>.parquet
```

### Offline 조회 소스

Feast `FileSource` 는 MinIO 경로를 직접 조회하며, 로컬 미러링인 `feast_repo/data/features/` 는 사용하지 않습니다.
조회 패턴은 `sensor_features/*/*.parquet`, `image_features/*/*.parquet`, `audio_features/*/*.parquet` 입니다.

### 로컬 개발 모드

Docker 대신 로컬에서 실행하려면:

```bash
# Backend
cd backend && pip install -r requirements.txt
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Frontend
cd frontend && pip install -r requirements.txt
streamlit run app.py
```

**참고:**
- Docker 모드: `feast apply` 는 이미지 빌드 시 자동으로 실행됩니다
- 로컬 개발 시: `./scripts/feast_apply.sh` 를 사용하세요 (venv 자동 관리)

## 기술 스택

| 컴포넌트 | 기술 |
|---------|------|
| Feature Store | Feast |
| Offline Store | DuckDB + Parquet |
| Online Store | Redis |
| Streaming | Kafka |
| Backend | FastAPI |
| Frontend | Streamlit |

## 인프라 서비스

| 서비스 | 포트 | 용도 | 로그인 |
|-------|------|------|--------|
| Kafka | 9092 | Event streaming | - |
| MinIO API | 9000 | Object storage | - |
| MinIO Console | 9001 | Web UI | admin / admin123 |
| InfluxDB | 8086 | Time-series DB | admin / admin123 |
| Redis | 6379 | Online feature store | default / redis123 |
| Kafka UI | 8090 | Topic monitoring | - |
| RedisInsight | 5540 | Redis inspection | - |
| media-consumer | - | Media → MinIO | - |
| sensor-consumer | - | Sensor → InfluxDB | - |

## 프로젝트 구조

```
demo-mlops-feature-store/
├── docker-compose.yml      # 인프라 서비스
├── .env                    # 환경 변수
├── backend/                # FastAPI application
├── frontend/               # Streamlit application
├── feast_repo/             # Feast configuration
├── consumers/              # Kafka consumers (Dockerized)
│   ├── sensor_consumer/    # Sensor data → InfluxDB
│   │   ├── Dockerfile
│   │   └── sensor_consumer.py
│   ├── media_consumer/     # Media metadata → MinIO
│   │   ├── Dockerfile
│   │   └── media_consumer.py
│   └── requirements.txt
├── jobs/                   # Feature engineering jobs
├── simulator/              # Vehicle event simulator
└── scripts/                # Initialization scripts
```

## Kafka Consumers

`consumers/` 디렉토리는 Kafka 이벤트를 받아 raw 데이터를 각 저장소에 분배합니다.

| 컨슈머 | 용도 | 저장소 | 처리 데이터 |
|--------|------|--------|-------------|
| `sensor_consumer.py` | 센서 데이터 수집 | InfluxDB | speed, acceleration, obstacle_distance, lidar_points |
| `media_consumer.py` | 미디어 메타데이터 저장 | MinIO | image/audio 메타데이터 (JSON) |

**데이터 흐름**:
```
Kafka (vehicle-events)
         │
         ├──→ sensor_consumer.py ──→ InfluxDB (time-series sensor data)
         │
         └──→ media_consumer.py ──→ MinIO (media metadata JSON)
```

**Docker 실행**:

```bash
# 모든 서비스 시작 (Consumers 포함)
docker-compose up -d

# Consumer 로그 확인
docker-compose logs -f media-consumer
docker-compose logs -f sensor-consumer

# 특정 Consumer 중지
docker-compose stop media-consumer
```

**수동 실행** (Docker 외 로컬 개발 시):
```bash
cd consumers && python media_consumer.py
```

---

## 빠른 시작

### 1. Docker 인프라 시작

```bash
# 모든 서비스 시작 (Infrastructure + Consumers)
docker-compose up -d

# Consumer 상태 확인
docker-compose ps | grep consumer
```

### 2. 초기화 스크립트 실행

```bash
# MinIO bucket 생성 (mlops-raw-sensor, mlops-raw-media, mlops-features)
./scripts/init_minio.sh

# InfluxDB 설정 (bucket: features)
./scripts/init_influxdb.sh
```

### 3. 데이터 생성 및 파이프라인 실행

```bash
# 이벤트 생성 (시뮬레이션)
curl -X POST http://localhost:8000/api/events/simulate \
  -H "Content-Type: application/json" \
  -d '{"vehicle_id": "V001", "scenario": "normal"}'

# Feature Engineering (Parquet 생성)
curl -X POST http://localhost:8000/api/features/build

# Training Dataset (historical features 기반)
curl -X POST http://localhost:8000/api/features/training-dataset \
  -H "Content-Type: application/json" \
  -d '{"output_path":"./data/training_dataset.parquet","hours":168,"interval_minutes":60,"vehicle_ids":["V001","V002","V003"]}'

# Materialization (Redis 적재)
curl -X POST http://localhost:8000/api/features/materialize

# Online Feature 조회
curl "http://localhost:8000/api/features/online?vehicle_id=V001"
```

### 4. 브라우저에서 접속

| 서비스 | URL | 로그인 |
|--------|-----|--------|
| Streamlit Frontend | http://localhost:8501 | - |
| FastAPI Docs | http://localhost:8000/docs | - |
| MinIO Console | http://localhost:9001 | admin / admin123 |
| Kafka UI | http://localhost:8090 | - |
| InfluxDB UI | http://localhost:8086 | admin / admin123 |

## API 엔드포인트

### 이벤트 및 Raw Data

| 엔드포인트 | 메서드 | 설명 |
|-----------|--------|------|
| `/api/events/simulate` | POST | 차량 이벤트 생성 및 Kafka 발행 |
| `/api/events/backfill-24h` | POST | V001~V007 기본값으로 과거 24시간 이벤트 백필 발행 |
| `/api/raw/status` | GET | InfluxDB/MinIO 의 raw data 상태 조회 |

### Feature Operations

| 엔드포인트 | 메서드 | 설명 |
|-----------|--------|------|
| `/api/features/build` | POST | Feature engineering 실행 |
| `/api/features/offline?vehicle_id=XXX` | GET | Historical features 조회 (DuckDB) |
| `/api/features/training-dataset` | POST | Historical features 기반 training dataset 생성 |
| `/api/features/materialize` | POST | Offline → Online incremental materialization (`end_date` optional) |
| `/api/features/online?vehicle_id=XXX` | GET | 실시간 features 조회 (Redis) |
| `/api/predict` | POST | 위험도 예측 |

### Backfill Script

과거 24시간 raw 이벤트를 빠르게 생성하려면:

```bash
./scripts/backfill_events_24h.sh
```

옵션 예시:

```bash
./scripts/backfill_events_24h.sh \
  --interval-minutes 10 \
  --end-time 2026-05-25T00:00:00Z \
  --vehicle-ids V001,V002,V003,V004,V005,V006,V007
```

## Streamlit Frontend

Streamlit Frontend 는 5 개의 탭으로 구성되어 있습니다.

### 탭 구조

| 탭 | 기능 |
|----|------|
| **Event Simulator** | Kafka 이벤트 생성 및 시뮬레이션 |
| **Raw Data** | InfluxDB/MinIO 의 raw data 상태 확인 |
| **Offline Features** | 역사적 feature 조회 및 빌드 |
| **Materialization** | Redis 적재 실행 |
| **Online Serving** | 실시간 feature 조회 및 위험도 예측 |

## 환경 변수

`.env` 파일의 주요 환경 변수:

| 변수 | 설명 | 기본값 |
|------|------|--------|
| `MINIO_ENDPOINT` | MinIO API 엔드포인트 | `localhost:9000` |
| `MINIO_ACCESS_KEY` | MinIO 접근 키 | `admin` |
| `MINIO_SECRET_KEY` | MinIO 시크릿 키 | `admin123` |
| `MINIO_SECURE` | MinIO TLS 사용 여부 | `false` |
| `MINIO_BUCKET` | 샘플 데이터 업로드 대상 버킷 | `mlops-features` |
| `INFLUXDB_URL` | InfluxDB URL | `http://localhost:8086` |
| `INFLUXDB_TOKEN` | InfluxDB 인증 토큰 | `influx-admin-token` |
| `INFLUXDB_ORG` | InfluxDB 조직명 | `mlops` |
| `INFLUXDB_BUCKET` | InfluxDB 버킷명 | `features` |
| `REDIS_URL` | Redis 엔드포인트 | `localhost:6379` |
| `KAFKA_BROKER` | Kafka 브roker 주소 | `localhost:9092` |
| `KAFKA_TOPIC` | Kafka 토픽명 | `vehicle-events` |

---

## 테스트 실행

```bash
# 모든 테스트 실행
cd backend && pytest tests/

# 특정 테스트 파일 실행
pytest tests/test_feature_builder.py
pytest tests/test_feast_service.py
```

---

## Troubleshooting

### 서비스 연결 실패

| 문제 | 해결 방법 |
|------|----------|
| Kafka connection refused | `docker-compose ps` 로 Kafka 서비스 상태 확인 |
| Redis connection error | Redis 비밀번호 확인 (`redis123`) |
| InfluxDB authentication failed | 토큰 확인 (`influx-admin-token`) |

### Materialization 실패

1. Docker 이미지를 재빌드했는지 확인 (`docker-compose up -d --build`)
2. MinIO 버킷 경로에 Parquet 가 존재하는지 확인 (`s3://mlops-features/<feature_view>/<vehicle_id>/<date>.parquet`)
3. Timestamp 형식이 올바른지 확인 (ISO 8601: `YYYY-MM-DDTHH:MM:SS`)

### Offline 조회 실패 (MinIO/S3)

| 에러 | 원인/확인 포인트 |
|------|------------------|
| `InvalidAccessKeyId` | MinIO 키가 아닌 AWS S3 로 잘못 붙은 경우. `MINIO_*` 값과 backend 재빌드 여부 확인 |
| `Could not resolve hostname ... mlops-features.minio` | 컨테이너 DNS/네트워크 alias 문제. `docker-compose`의 minio alias 확인 |
| `404 Not Found` on `s3://mlops-features/sensor_features/` | 경로가 디렉터리만 가리키는 경우. `FileSource` 패턴(`*/*.parquet`) 및 실제 객체 키 확인 |

### Common Errors

```bash
# Redis 비밀번호 확인
docker-compose exec redis redis-cli -a redis123 ping

# Kafka 브roker 연결 테스트
docker-compose exec kafka kafka-broker-api-versions --bootstrap-server localhost:9092

# MinIO bucket 목록 확인
docker-compose exec backend minio-client ls minio
```
