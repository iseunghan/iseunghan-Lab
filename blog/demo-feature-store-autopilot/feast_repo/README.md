# Feast Feature Store Configuration

루트 [README](../README.md)에는 feature 흐름, 파이프라인, 실제 사용 예시를 정리했고, 이 문서는 `feast_repo/` 내부 설정과 기본 명령만 남깁니다.

## Structure

```
feast_repo/
├── feature_store.yaml    # Main configuration
├── entities.py           # Entity definitions
├── feature_views.py      # Feature View definitions
├── requirements.txt      # Python dependencies
└── data/                 # Local data directory (for DuckDB)
    ├── duckdb.db         # Offline store database
    └── features/         # Feature parquet files
        ├── sensor_features/
        ├── image_features/
        └── audio_features/
```

## Commands

### Apply configuration
```bash
cd feast_repo
feast apply
```

### Materialize features to online store
```bash
feast materialize-incremental $(date -u +%Y-%m-%dT%H:%M:%S)
```

### Get historical features
```bash
feast get-historical-features --feature-view sensor_features --entity vehicle
```

## Notes

- Feature view 정의와 데모/프로덕션 차이는 루트 README의 `Feature Store & Pipeline` 섹션을 참고하세요.
- `data/` 디렉토리는 로컬 DuckDB 및 실험용 파일을 위한 경로입니다.
