"""
MLOps Feature Store Demo - Streamlit Frontend

5-tab interface for autonomous vehicle risk prediction demo.
"""

import streamlit as st
import requests
import json
import os
import math
from datetime import datetime

# API configuration
API_BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8000")

# Page configuration
st.set_page_config(
    page_title="MLOps Feature Store Demo",
    page_icon="🚗",
    layout="wide",
)

st.title("🚗 MLOps Feature Store Demo")
st.subheader("Autonomous Vehicle Risk Prediction")


def call_api(endpoint: str, method: str = "GET", json_data: dict = None, timeout: int = 10):
    """Helper function to call the API"""
    url = f"{API_BASE_URL}{endpoint}"
    try:
        if method == "GET":
            response = requests.get(url, params=json_data, timeout=timeout)
        else:
            response = requests.post(url, json=json_data, timeout=timeout)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        st.error(f"API Error: {e}")
        return None


def render_feature_store_status_widget(
    vehicle_id: str,
    lookback_hours: int = 24,
    stale_threshold_seconds: int = 600,
    key_prefix: str = "status",
):
    """Render feature store freshness/materialization status."""
    refresh_key = f"{key_prefix}_refresh_{vehicle_id}"
    state_key = f"{key_prefix}_feature_store_status_{vehicle_id}"

    if st.button("📡 Refresh Feature Store Status", key=refresh_key):
        st.session_state[state_key] = call_api(
            "/api/features/status",
            method="GET",
            json_data={"vehicle_id": vehicle_id, "lookback_hours": lookback_hours},
        )
        st.rerun()

    status = st.session_state.get(state_key)
    if status is None:
        status = call_api(
            "/api/features/status",
            method="GET",
            json_data={"vehicle_id": vehicle_id, "lookback_hours": lookback_hours},
        )
        st.session_state[state_key] = status

    if not status:
        st.info("Feature store status is unavailable.")
        return

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Materialization End", status.get("last_materialization_end_date") or "N/A")
    with col2:
        st.metric("Offline Latest TS", status.get("offline_latest_feature_timestamp") or "N/A")
    with col3:
        age_seconds = status.get("offline_feature_age_seconds")
        st.metric("Offline Age (s)", age_seconds if age_seconds is not None else "N/A")
    with col4:
        online_ready = status.get("online_feature_available", False)
        st.metric("Online Ready", "YES" if online_ready else "NO")

    age_seconds = status.get("offline_feature_age_seconds")
    if age_seconds is None:
        st.info("Freshness status: unknown (no offline feature timestamp in lookback window).")
    elif age_seconds > stale_threshold_seconds:
        st.warning(
            f"Freshness status: stale (age={age_seconds}s, threshold={stale_threshold_seconds}s)."
        )
    else:
        st.success(
            f"Freshness status: healthy (age={age_seconds}s, threshold={stale_threshold_seconds}s)."
        )


# =============================================================================
# Tab 1: Event Simulator
# =============================================================================
tab1, tab2, tab3, tab4, tab5 = st.tabs(
    ["🎮 Event Simulator", "📊 Raw Data", "📁 Offline Features", "🔄 Materialization", "🔮 Online Serving"]
)

with tab1:
    st.header("Event Simulator")
    st.markdown("Generate mock vehicle events and publish to Kafka")

    col1, col2 = st.columns(2)

    with col1:
        vehicle_id = st.text_input("Vehicle ID", value="V001", key="tab1_vehicle_id")

    with col2:
        scenario_map = {
            "Normal Driving": "normal",
            "Heavy Traffic": "heavy_traffic",
            "Pedestrian Nearby": "pedestrian_nearby",
            "Sensor Missing": "sensor_missing",
            "Emergency Vehicle Nearby": "emergency_vehicle",
        }
        scenario_display = st.selectbox(
            "Scenario",
            list(scenario_map.keys()),
        )
        scenario = scenario_map[scenario_display]

    if st.button("🚀 Generate Event", type="primary"):
        with st.spinner("Generating event..."):
            result = call_api(
                "/api/events/simulate",
                method="POST",
                json_data={"vehicle_id": vehicle_id, "scenario": scenario},
            )

            if result:
                st.success("Event generated successfully!")
                st.json(result)
            else:
                st.error("Failed to generate event")

    st.markdown("---")
    st.subheader("24h Backfill")
    st.caption("V001~V007 차량의 과거 24시간 이벤트를 10분 간격(기본)으로 생성합니다.")
    col_b1, col_b2 = st.columns(2)
    with col_b1:
        backfill_interval = st.number_input(
            "Backfill Interval (minutes)",
            min_value=1,
            max_value=1440,
            value=10,
            step=1,
            key="tab1_backfill_interval",
        )
    with col_b2:
        backfill_end_time = st.text_input(
            "Backfill End Time (optional, ISO-8601 UTC)",
            value="",
            placeholder="2026-05-25T00:00:00Z",
            key="tab1_backfill_end_time",
        )

    if st.button("🕒 Run 24h Backfill (V001~V007)"):
        request_body = {"interval_minutes": int(backfill_interval)}
        if backfill_end_time.strip():
            request_body["end_time"] = backfill_end_time.strip()
        with st.spinner("Generating backfill events..."):
            backfill_result = call_api(
                "/api/events/backfill-24h",
                method="POST",
                json_data=request_body,
                timeout=180,
            )
            if backfill_result:
                st.success("Backfill completed")
                st.json(backfill_result)
            else:
                st.error("Backfill failed")

    st.markdown("---")
    st.markdown("**Scenario Descriptions:**")
    st.info("""
    - **Normal Driving**: Standard driving conditions
    - **Heavy Traffic**: High speed, congested environment
    - **Pedestrian Nearby**: Low obstacle distance, high pedestrian count
    - **Sensor Missing**: High sensor missing rate
    - **Emergency Vehicle Nearby**: Siren detected, urgent situation
    """)

# =============================================================================
# Tab 2: Raw Data
# =============================================================================
with tab2:
    st.header("Raw Data Status")
    st.markdown("View raw data stored in InfluxDB and MinIO")

    if st.button("🔄 Refresh Status"):
        status_data = call_api("/api/raw/status", method="GET")
        if status_data:
            st.session_state.raw_data_status = status_data
        st.rerun()

    # Get status from session state or use defaults
    status = st.session_state.get("raw_data_status", {
        "influx_sensor_count": 0,
        "minio_image_count": 0,
        "minio_audio_count": 0
    })

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric("InfluxDB Sensor Records", status.get("influx_sensor_count", 0))
        st.caption("Time-series sensor data")

    with col2:
        st.metric("MinIO Images", status.get("minio_image_count", 0))
        st.caption("Raw camera images")

    with col3:
        st.metric("MinIO Audio", status.get("minio_audio_count", 0))
        st.caption("Raw audio recordings")

    st.markdown("---")
    st.markdown("**Note:** Raw data is populated by Kafka consumers after events are generated.")

# =============================================================================
# Tab 3: Offline Features
# =============================================================================
with tab3:
    st.header("Offline Features")
    st.markdown("Historical feature preview와 training dataset 생성을 분리해 제공합니다.")
    vehicle_id_filter = st.text_input("Filter by Vehicle ID", value="V001", key="tab3_vehicle_id_filter")

    def retrieve_features():
        if vehicle_id_filter:
            with st.spinner(f"Retrieving features for {vehicle_id_filter}..."):
                return call_api(
                    "/api/features/offline",
                    method="GET",
                    json_data={"vehicle_id": vehicle_id_filter, "interval_minutes": 10},
                )
    
    offline_data = retrieve_features()

    st.markdown("**Feature Catalog (Feast Feature Views):**")

    catalog = call_api("/api/features/catalog", method="GET")
    selected_feature_view = None
    selected_feature_name = None

    if catalog and catalog.get("feature_views"):
        rows = []
        for feature_view in catalog["feature_views"]:
            rows.append(
                {
                    "feature_view": feature_view.get("name"),
                    "source": feature_view.get("source"),
                    "ttl_hours": feature_view.get("ttl_hours"),
                    "online": feature_view.get("online"),
                    "features": ", ".join(feature_view.get("features", [])),
                }
            )
        st.dataframe(rows, use_container_width=True)

        feature_view_names = [fv.get("name") for fv in catalog["feature_views"] if fv.get("name")]
        selected_feature_view = st.selectbox(
            "Drill-down Feature View",
            feature_view_names,
            key="tab3_drilldown_feature_view",
        )
        selected_feature_options = []
        for fv in catalog["feature_views"]:
            if fv.get("name") == selected_feature_view:
                selected_feature_options = fv.get("features", [])
                break
        if selected_feature_options:
            selected_feature_name = st.selectbox(
                "Drill-down Feature",
                selected_feature_options,
                key="tab3_drilldown_feature_name",
            )

        if selected_feature_name:
            drilldown_rows = []
            if offline_data:
                for record in offline_data:
                    features = record.get("features", {})
                    value = features.get(selected_feature_name)
                    if value is None:
                        continue
                    event_ts = record.get("event_timestamp") or record.get("timestamp")
                    drilldown_rows.append(
                        {
                            "vehicle_id": record.get("vehicle_id"),
                            "timestamp": event_ts,
                            selected_feature_name: value,
                        }
                    )
            st.markdown(
                f"**Drill-down Result:** `{selected_feature_view}` / `{selected_feature_name}`"
            )
            if drilldown_rows:
                st.dataframe(drilldown_rows, use_container_width=True)
            else:
                st.info("No drill-down rows found for current vehicle/time range.")
    else:
        st.info("Feature catalog is unavailable.")

    st.markdown("---")

    col1, col2 = st.columns([1, 2])

    with col1:
        build_vehicle_id = st.text_input("Vehicle ID for Build", value="V001", key="tab3_build_vehicle_id")
        if st.button("🔨 Build Features"):
            with st.spinner("Building features from raw data..."):
                result = call_api("/api/features/build", method="POST", json_data={"vehicle_id": build_vehicle_id})
                if result:
                    st.success(result.get("message", "Features built successfully!"))
                    st.json(result)

    with col2:
        st.markdown("**Training Dataset Generation (Historical Features 기반)**")
        td_output_path = st.text_input(
            "Output Path",
            value="./data/training_dataset.parquet",
            key="tab3_training_output_path",
        )
        td_hours = st.number_input(
            "Lookback Hours",
            min_value=1,
            max_value=24 * 30,
            value=168,
            step=1,
            key="tab3_training_hours",
        )
        td_interval = st.number_input(
            "Interval Minutes",
            min_value=1,
            max_value=1440,
            value=60,
            step=1,
            key="tab3_training_interval",
        )
        td_vehicle_ids = st.text_input(
            "Vehicle IDs (comma-separated)",
            value="V001,V002,V003",
            key="tab3_training_vehicle_ids",
        )
        if st.button("📥 Training Dataset"):
            vehicle_ids = [v.strip() for v in td_vehicle_ids.split(",") if v.strip()]
            payload = {
                "output_path": td_output_path,
                "hours": int(td_hours),
                "interval_minutes": int(td_interval),
                "vehicle_ids": vehicle_ids,
            }
            with st.spinner("Generating training dataset from historical features..."):
                result = call_api(
                    "/api/features/training-dataset",
                    method="POST",
                    json_data=payload,
                )
                if result:
                    st.success(result.get("message", "Training dataset generated"))
                    st.json(result)

    st.markdown("---")
    st.markdown(f"**Historical Features ({vehicle_id_filter}):**")
    if st.button("🔨 Retrieve Features"):
        offline_data = retrieve_features()

    # Fetch offline features if vehicle_id_filter is provided
    if vehicle_id_filter:
        if offline_data:
            # Flatten the feature dictionary for display
            display_data = []

            def _is_empty_feature_value(value):
                if value is None:
                    return True
                if isinstance(value, str) and value.strip() == "":
                    return True
                if isinstance(value, float) and math.isnan(value):
                    return True
                return False

            for record in offline_data:
                features = record.get("features", {})
                event_ts = record.get("event_timestamp") or record.get("timestamp")
                display_record = {"vehicle_id": record.get("vehicle_id"), "timestamp": event_ts}
                cleaned_features = {
                    k: v
                    for k, v in features.items()
                    if k not in {"event_timestamp", "vehicle_id"}
                }
                if cleaned_features and all(
                    _is_empty_feature_value(value) for value in cleaned_features.values()
                ):
                    continue
                display_record.update(cleaned_features)
                display_data.append(display_record)
            if display_data:
                st.dataframe(display_data, use_container_width=True)
            else:
                st.info("All retrieved rows had empty feature values.")
        else:
            st.info("No features found for this vehicle ID or API error.")
    else:
        # Mock data for demo when no filter is applied
        st.info("Sample Data")
        sample_data = [
            {"vehicle_id": "V001", "timestamp": "2026-05-21 10:00:00", "avg_speed_10s": 42.1, "obstacle_distance_min": 18.4, "pedestrian_count": 0, "siren_detected": False},
            {"vehicle_id": "V001", "timestamp": "2026-05-21 10:01:00", "avg_speed_10s": 51.3, "obstacle_distance_min": 8.2, "pedestrian_count": 2, "siren_detected": False},
            {"vehicle_id": "V002", "timestamp": "2026-05-21 10:02:00", "avg_speed_10s": 33.8, "obstacle_distance_min": 21.5, "pedestrian_count": 1, "siren_detected": True},
        ]
        st.dataframe(sample_data, use_container_width=True)

# =============================================================================
# Tab 4: Materialization
# =============================================================================
with tab4:
    st.header("Materialization")
    st.markdown("latest offline features를 online store(Redis)로 incremental 적재합니다.")

    st.info("""
    **Materialization**은 `FeatureStore.materialize_incremental(end_date)`를 호출합니다.
    실제 적재 범위(start)는 Feast registry state가 관리합니다.
    """)

    col1, col2 = st.columns(2)

    with col1:
        end_date_text = st.text_input(
            "End Date (optional, ISO-8601 UTC)",
            value="",
            placeholder="2026-05-24T12:00:00Z",
            key="tab4_materialize_end_date",
        )
        if st.button("🔄 Materialize Incremental"):
            payload = {}
            if end_date_text.strip():
                payload["end_date"] = end_date_text.strip()
            with st.spinner("Materializing features to Redis..."):
                result = call_api("/api/features/materialize", method="POST", json_data=payload)
                if result:
                    st.success(result.get("message", "Materialization complete!"))
                    st.json(result)

    with col2:
        st.markdown("**Feast Commands:**")
        st.code("""
# Apply feature registry
feast apply

# Materialize incremental features
feast materialize-incremental --end-date 2026-05-24T12:00:00Z
        """, language="bash")

    st.markdown("---")
    st.markdown("**Feature Store Status (Freshness / Lag):**")
    render_feature_store_status_widget(
        vehicle_id="V001", lookback_hours=24, key_prefix="tab4_status"
    )

# =============================================================================
# Tab 5: Online Serving
# =============================================================================
with tab5:
    st.header("Online Serving")
    st.markdown("Online feature lookup(현재값)과 risk prediction(모델/규칙)을 분리해 확인합니다.")

    vehicle_id_input = st.text_input("Vehicle ID", value="V001", key="tab5_vehicle_id_input")

    col1, col2 = st.columns(2)

    with col1:
        if st.button("🔍 Get Online Features"):
            with st.spinner("Fetching features from Redis..."):
                result = call_api("/api/features/online", method="GET", json_data={"vehicle_id": vehicle_id_input})
                if result:
                    st.success("Features retrieved!")
                    st.json(result)

    with col2:
        if st.button("🔮 Predict Risk"):
            with st.spinner("Calculating risk score..."):
                result = call_api("/api/predict", method="POST", json_data={"vehicle_id": vehicle_id_input})
                if result:
                    st.success("Prediction complete!")

                    # Display risk score with color
                    risk_score = result.get("risk_score", 0)
                    risk_level = result.get("risk_level", "UNKNOWN")

                    if risk_level == "HIGH":
                        st.error(f"⚠️ Risk Level: {risk_level} (Score: {risk_score})")
                    elif risk_level == "MEDIUM":
                        st.warning(f"⚡ Risk Level: {risk_level} (Score: {risk_score})")
                    else:
                        st.success(f"✅ Risk Level: {risk_level} (Score: {risk_score})")

                    st.json(result)

    st.markdown("---")
    st.markdown("**Feature Store Status (for selected vehicle):**")
    render_feature_store_status_widget(
        vehicle_id=vehicle_id_input, lookback_hours=24, key_prefix="tab5_status"
    )

    st.markdown("---")
    st.markdown("**Risk Score Calculation:**")
    st.markdown("""
    The demo uses a **rule-based** risk calculation:
    - Obstacle distance (closer = higher risk)
    - Speed (higher = higher risk)
    - Pedestrian count
    - Siren detection
    - Sensor missing rate
    """)


# Footer
st.markdown("---")
st.caption("MLOps Feature Store Demo | Built with Feast, FastAPI, and Streamlit")
