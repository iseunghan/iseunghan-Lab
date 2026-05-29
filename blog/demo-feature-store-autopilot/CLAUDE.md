# CLAUDE.md

이 파일은 이 리포지토리에서 작업할 때 Claude Code(claude.ai/code) 에 지침을 제공합니다.

## 스킬 사용 지침

- **브레인스토밍 필요 시**: `superpowers:brainstorming` 스킬 사용 (새 기능 추가, 컴포넌트 구축, 동작 변경 전)
- **플랜 작성 시**: 항상 `superpowers:writing-plains` 스킬 사용 (명세/요구사항이 있는 다단계 작업 전)
- **플랜 실행 시**: `superpowers:executing-plans` 스킬 사용 (플랜이 준비된 후 구현 작업 수행)

## 프로젝트 개요

Feast 를 활용한 자율주행 차량 위험도 예측 Feature Store 데모 프로젝트. 현재 상태: 인프라 설정 완료 (Step 1), feature store 설정 및 애플리케이션 개발 대기 (Step 2-4).

## 아키텍처

```
Vehicle Simulator → Kafka → Sensor/Media Consumers
                         ↓
                    InfluxDB (raw sensor)
                    MinIO (raw media)
                         ↓
              Feature Engineering → Parquet (MinIO)
                         ↓
                    Feast (DuckDB + Redis)
                         ↓
                    FastAPI → Streamlit
```

**주요 설계 결정**: PostgreSQL 대신 DuckDB offline store 를 선택한 이유 — Feast 의 FileSource 가 Parquet 파일을 네이티브로 지원하여 feature engineering 이 더 단순합니다 (Parquet → FileSource path → FeatureView). schema migration, index 관리, 복잡한 테이블 연산이 필요하지 않습니다.

## 인프라 명령어

```bash
# 모든 서비스 시작
docker-compose up -d

# 서비스 상태 확인
docker-compose ps

# 로그 확인
docker-compose logs -f

# 서비스 중지
docker-compose down
```

## 서비스 엔드포인트

| 서비스 | 포트 | 용도 |
|---------|------|------|
| Kafka | 9092 | Event streaming |
| MinIO API | 9000 | Object storage |
| MinIO Console | 9001 | Web UI (admin/admin123) |
| InfluxDB | 8086 | Time-series data |
| Redis | 6379 | Online feature store |
| Kafka UI | 8090 | Topic monitoring |
| RedisInsight | 5540 | Redis inspection |

## Feature Store 설정 흐름

1. **MinIO bucket 생성** - Bucket 생성: `mlops-raw-sensor`, `mlops-raw-media`, `mlops-features`
2. **Kafka topic 생성** - Topic 생성: `vehicle-events`, `sensor-data`, `media-data`
3. **Feast repository** - DuckDB offline store + Redis online store 로 `feast_repo/` 설정
4. **Feature engineering jobs** - Raw data 읽기, feature 계산, Parquet 을 MinIO 에 쓰기
5. **Materialization** - Redis 채우기를 위해 `feast materialize-incremental` 실행

## 개발 워크플로우

```bash
# 1. 인프라 시작
docker-compose up -d

# 2. MinIO bucket 초기화 (scripts/init_minio.sh)

# 3. Feast 설정 적용
cd feast_repo && feast apply

# 4. Feature engineering 실행
python jobs/build_features.py

# 5. Online store 로 materialize
feast materialize-incremental --start <timestamp> --end <timestamp>

# 6. Backend 시작
cd backend && uvicorn app.main:app --reload

# 7. Frontend 시작
cd frontend && streamlit run app.py
```

## 테스트 및 완료 보고 지침

**각 스텝 구현 시 필수 요구사항**:
1. **테스트 포함**: 각 스텝 구현 시 반드시 테스트 코드 포함
2. **완료 보고**: 스텝 구현 완료 시 사용자에게 다음 형식으로 보고:
   - **Evidence**: 구현된 기능의 증거 (파일 경로, 코드 스니펫, 실행 결과)
   - **Reasonable한 증거**: 테스트 통과 결과, 기능 동작 확인 등 완료처리를 했음을 입증하는 근거

## 커밋 지침

**각 스텝 완료 시 반드시 사용자에게 질문**: "현재 스텝 구현 내용을 git 커밋하시겠습니까?"
- 프로젝트가 단계별 (Step 1-4) 로 진행되므로, 각 스텝 완료 후 사용자의 커밋 의사를 확인

## Feature Views (계획 중)

- **sensor_features**: avg_speed_10s, accel_std_10s, obstacle_distance_min, lidar_point_count, sensor_missing_rate
- **image_features**: object_count, pedestrian_count, lane_detect_score
- **audio_features**: noise_level, siren_detected

## Risk Score 계산

Rule-based 예측:
```
risk_score 는 다음일 경우 증가:
- obstacle_distance_min 이 낮을수록
- avg_speed_10s 가 높을수록
- sensor_missing_rate 가 높을수록
- pedestrian_count 가 많을수록
- siren_detected 가 true 일 경우
```
