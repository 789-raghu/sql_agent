from typing import List, Dict

RELATIONSHIPS: List[Dict[str, str]] = [
    # Summary & Analytics Schema (public) Relationships
    {
        "from_table": "consumption",
        "from_column": "consumer_id",
        "to_table": "consumers",
        "to_column": "consumer_id",
        "type": "many-to-one",
        "join_condition": "consumption.consumer_id = consumers.consumer_id"
    },
    {
        "from_table": "predictions",
        "from_column": "consumer_id",
        "to_table": "consumers",
        "to_column": "consumer_id",
        "type": "many-to-one",
        "join_condition": "predictions.consumer_id = consumers.consumer_id"
    },
    {
        "from_table": "consumption",
        "from_column": "consumer_id, timestamp",
        "to_table": "predictions",
        "to_column": "consumer_id, timestamp",
        "type": "one-to-one",
        "join_condition": "consumption.consumer_id = predictions.consumer_id AND consumption.timestamp = predictions.timestamp"
    },
    {
        "from_table": "consumers",
        "from_column": "cluster_id",
        "to_table": "clusters",
        "to_column": "cluster_id",
        "type": "many-to-one",
        "join_condition": "consumers.cluster_id = clusters.cluster_id"
    },
    {
        "from_table": "consumers",
        "from_column": "location_id",
        "to_table": "locations",
        "to_column": "location_id",
        "type": "many-to-one",
        "join_condition": "consumers.location_id = locations.location_id"
    },
    {
        "from_table": "meters",
        "from_column": "consumer_id",
        "to_table": "consumers",
        "to_column": "consumer_id",
        "type": "many-to-one",
        "join_condition": "meters.consumer_id = consumers.consumer_id"
    },
    {
        "from_table": "daily_summary",
        "from_column": "consumer_id",
        "to_table": "consumers",
        "to_column": "consumer_id",
        "type": "many-to-one",
        "join_condition": "daily_summary.consumer_id = consumers.consumer_id"
    },

    # Data Lake Schema (epdatalake) Relationships
    {
        "from_table": "epdatalake.consumer_mapping",
        "from_column": "CONS_NO",
        "to_table": "epdatalake.lt_consumer_master",
        "to_column": "SCNO",
        "type": "many-to-one",
        "join_condition": "epdatalake.consumer_mapping.CONS_NO = epdatalake.lt_consumer_master.SCNO"
    },
    {
        "from_table": "epdatalake.consumer_mapping",
        "from_column": "DTR_STRUC_CODE",
        "to_table": "epdatalake.dtr_master",
        "to_column": "DTR_STRUCTURE_CODE",
        "type": "many-to-one",
        "join_condition": "epdatalake.consumer_mapping.DTR_STRUC_CODE = epdatalake.dtr_master.DTR_STRUCTURE_CODE"
    },
    {
        "from_table": "epdatalake.consumer_mapping",
        "from_column": "DTR_STRUC_CODE",
        "to_table": "epdatalake.fdr_dtr_newcharge",
        "to_column": "DTR_ID",
        "type": "many-to-one",
        "join_condition": "epdatalake.consumer_mapping.DTR_STRUC_CODE = epdatalake.fdr_dtr_newcharge.DTR_ID"
    },
    {
        "from_table": "epdatalake.fdr_dtr_newcharge",
        "from_column": "NEW_MTR_MSN",
        "to_table": "epdatalake.t_nw_blp",
        "to_column": "msn",
        "type": "one-to-many",
        "join_condition": "epdatalake.fdr_dtr_newcharge.NEW_MTR_MSN = epdatalake.t_nw_blp.msn"
    },
    {
        "from_table": "epdatalake.lt_consumer_master",
        "from_column": "UKSCNO",
        "to_table": "epdatalake.smart_meters_install_m",
        "to_column": "UKSCNO",
        "type": "one-to-one",
        "join_condition": "epdatalake.lt_consumer_master.UKSCNO = epdatalake.smart_meters_install_m.UKSCNO"
    },
    {
        "from_table": "epdatalake.smart_meters_install_m",
        "from_column": "MTR_SNO",
        "to_table": "epdatalake.t_blp_sp",
        "to_column": "msn",
        "type": "one-to-many",
        "join_condition": "epdatalake.smart_meters_install_m.MTR_SNO = epdatalake.t_blp_sp.msn"
    },
    {
        "from_table": "epdatalake.smart_meters_install_m",
        "from_column": "MTR_SNO",
        "to_table": "epdatalake.t_blp_tp",
        "to_column": "msn",
        "type": "one-to-many",
        "join_condition": "epdatalake.smart_meters_install_m.MTR_SNO = epdatalake.t_blp_tp.msn"
    },
    {
        "from_table": "epdatalake.lt_consumer_master",
        "from_column": "ID",
        "to_table": "epdatalake.lt_meter_data",
        "to_column": "CONS_NUMBER",
        "type": "one-to-many",
        "join_condition": "epdatalake.lt_consumer_master.ID = epdatalake.lt_meter_data.CONS_NUMBER"
    },
    {
        "from_table": "epdatalake.lt_consumer_master",
        "from_column": "CATEGORY",
        "to_table": "epdatalake.lt_category_master",
        "to_column": "NAME",
        "type": "many-to-one",
        "join_condition": "epdatalake.lt_consumer_master.CATEGORY = epdatalake.lt_category_master.NAME"
    }
]
