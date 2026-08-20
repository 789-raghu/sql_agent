from typing import Dict, Set

# Table Allowlist (Supports both short names and schema-qualified names)
ALLOWED_TABLES: Set[str] = {
    # Public & Analytical Mock / View Tables
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
    "consumer_daily_summary",
    "consumer_monthly_summary",
    "consumer_predictions",
    "consumer_cluster_summary",

    # Production Data Lake Tables (epdatalake schema)
    "consumer_mapping",
    "epdatalake.consumer_mapping",
    "dtr_master",
    "epdatalake.dtr_master",
    "fdr_dtr_newcharge",
    "epdatalake.fdr_dtr_newcharge",
    "t_nw_blp",
    "epdatalake.t_nw_blp",
    "lt_consumer_master",
    "epdatalake.lt_consumer_master",
    "smart_meters_install_m",
    "epdatalake.smart_meters_install_m",
    "t_blp_sp",
    "epdatalake.t_blp_sp",
    "t_blp_tp",
    "epdatalake.t_blp_tp",
    "lt_meter_data",
    "epdatalake.lt_meter_data",
    "ht_consumer_master",
    "epdatalake.ht_consumer_master",
    "lt_billing_data",
    "epdatalake.lt_billing_data",
    "htbpbillprocess_t",
    "epdatalake.htbpbillprocess_t",
    "smart_meters_billdata",
    "epdatalake.oracle.smart_meters_billdata",
    "lt_category_master",
    "epdatalake.lt_category_master"
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
    },

    # epdatalake Data Lake Table Columns
    "consumer_mapping": {"dtr_struc_code", "cons_no"},
    "epdatalake.consumer_mapping": {"dtr_struc_code", "cons_no"},
    "dtr_master": {
        "id", "dtr_structure_code", "dtr_location", "feeder_code", "phase",
        "capacity", "no_of_meters", "meter_num_1", "meter_num_2", "meter_num_3",
        "glat", "glong"
    },
    "epdatalake.dtr_master": {
        "id", "dtr_structure_code", "dtr_location", "feeder_code", "phase",
        "capacity", "no_of_meters", "meter_num_1", "meter_num_2", "meter_num_3",
        "glat", "glong"
    },
    "fdr_dtr_newcharge": {
        "dtr_id", "dtr_master_id", "new_mtr_msn", "new_mtr_make", "new_mtr_mf",
        "new_mtr_ct_ratio", "new_mtr_pt_ratio", "new_mtr_installation_datetime"
    },
    "epdatalake.fdr_dtr_newcharge": {
        "dtr_id", "dtr_master_id", "new_mtr_msn", "new_mtr_make", "new_mtr_mf",
        "new_mtr_ct_ratio", "new_mtr_pt_ratio", "new_mtr_installation_datetime"
    },
    "t_nw_blp": {"msn", "ts", "vah_imp"},
    "epdatalake.t_nw_blp": {"msn", "ts", "vah_imp"},
    "lt_consumer_master": {
        "id", "scno", "ukscno", "name", "category", "phase",
        "contracted_load", "connected_load", "load_type", "feeder_num",
        "trans_struc_code", "billing_status", "sm_mtr", "net_metering"
    },
    "epdatalake.lt_consumer_master": {
        "id", "scno", "ukscno", "name", "category", "phase",
        "contracted_load", "connected_load", "load_type", "feeder_num",
        "trans_struc_code", "billing_status", "sm_mtr", "net_metering"
    },
    "smart_meters_install_m": {
        "ukscno", "mtr_sno", "mtr_type", "consumer_mobileno", "latitude", "longitude"
    },
    "epdatalake.smart_meters_install_m": {
        "ukscno", "mtr_sno", "mtr_type", "consumer_mobileno", "latitude", "longitude"
    },
    "t_blp_sp": {"msn", "ts", "vah_imp"},
    "epdatalake.t_blp_sp": {"msn", "ts", "vah_imp"},
    "t_blp_tp": {"msn", "ts", "vah_imp"},
    "epdatalake.t_blp_tp": {"msn", "ts", "vah_imp"},
    "lt_meter_data": {
        "cons_number", "present_reading", "prev_reading", "present_mtrrddate", "prev_mtrrddate"
    },
    "epdatalake.lt_meter_data": {
        "cons_number", "present_reading", "prev_reading", "present_mtrrddate", "prev_mtrrddate"
    },
    "ht_consumer_master": {
        "id", "cons_number", "name", "type_of_supply", "category", "power_load",
        "contract_demand", "connected_load", "supply_voltage", "actual_voltage",
        "feeder_num", "feeder_code", "trans_struc_code", "trans_location",
        "trans_ser_num", "mtr_no", "meter_make", "meter_type", "metering_type",
        "latitude", "longitude", "smt_mtr"
    },
    "epdatalake.ht_consumer_master": {
        "id", "cons_number", "name", "type_of_supply", "category", "power_load",
        "contract_demand", "connected_load", "supply_voltage", "actual_voltage",
        "feeder_num", "feeder_code", "trans_struc_code", "trans_location",
        "trans_ser_num", "mtr_no", "meter_make", "meter_type", "metering_type",
        "latitude", "longitude", "smt_mtr"
    },
    "lt_billing_data": {"cons_no", "bill_date", "bill_amount"},
    "epdatalake.lt_billing_data": {"cons_no", "bill_date", "bill_amount"},
    "htbpbillprocess_t": {"cons_number", "bill_date", "total_amount"},
    "epdatalake.htbpbillprocess_t": {"cons_number", "bill_date", "total_amount"},
    "smart_meters_billdata": {"mtr_sno", "bill_date", "bill_amount"},
    "epdatalake.oracle.smart_meters_billdata": {"mtr_sno", "bill_date", "bill_amount"},
    "lt_category_master": {"id", "name", "cat_code", "scdesc"},
    "epdatalake.lt_category_master": {"id", "name", "cat_code", "scdesc"}
}
