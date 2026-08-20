from typing import Dict, Set

# Table Allowlist
ALLOWED_TABLES: Set[str] = {
    "consumers",
    "consumption",
    "predictions",
    "clusters",
    "locations",
    "meters",
    "tariffs",
    "weather",
    "alerts",
    "daily_summary",
    # Analytical Views
    "consumer_daily_summary",
    "consumer_monthly_summary",
    "consumer_predictions",
    "consumer_cluster_summary"
}

# Column Allowlist per Table / View
ALLOWED_COLUMNS: Dict[str, Set[str]] = {
    "consumers": {
        "consumer_id", "name", "cluster_id", "location_id", "category", "join_date"
    },
    "consumption": {
        "consumer_id", "timestamp", "consumption", "status"
    },
    "predictions": {
        "consumer_id", "timestamp", "predicted_consumption", "model_version"
    },
    "clusters": {
        "cluster_id", "name", "region", "created_at"
    },
    "locations": {
        "location_id", "city", "state", "postal_code"
    },
    "meters": {
        "meter_id", "consumer_id", "install_date", "meter_type", "status"
    },
    "tariffs": {
        "tariff_id", "name", "rate_per_kwh", "peak_rate_per_kwh"
    },
    "weather": {
        "location_id", "timestamp", "temperature", "humidity", "solar_radiation"
    },
    "alerts": {
        "alert_id", "consumer_id", "timestamp", "alert_type", "severity", "description"
    },
    "daily_summary": {
        "consumer_id", "date", "total_consumption", "avg_consumption", "max_consumption", "min_consumption"
    },
    "consumer_daily_summary": {
        "consumer_id", "consumer_name", "category", "cluster_name", "city", "date",
        "total_consumption", "avg_consumption", "max_consumption", "min_consumption"
    },
    "consumer_monthly_summary": {
        "consumer_id", "consumer_name", "category", "year_month",
        "monthly_total_consumption", "monthly_avg_consumption", "monthly_peak_consumption"
    },
    "consumer_predictions": {
        "consumer_id", "consumer_name", "timestamp", "actual_consumption",
        "predicted_consumption", "difference", "percentage_exceeded"
    },
    "consumer_cluster_summary": {
        "cluster_id", "cluster_name", "region", "total_consumers",
        "cluster_avg_consumption", "cluster_total_consumption"
    }
}
