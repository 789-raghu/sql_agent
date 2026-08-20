import pytest
from semantic.retriever import schema_retriever


def test_schema_retrieval_prediction_query():
    retrieved = schema_retriever.retrieve("Compare predicted and actual consumption for consumer 67002820.")
    tables = retrieved["relevant_tables"]
    assert "predictions" in tables
    assert "consumption" in tables
    assert "consumer_predictions" in tables


def test_schema_retrieval_cluster_query():
    retrieved = schema_retriever.retrieve("What is the average consumption by cluster?")
    tables = retrieved["relevant_tables"]
    assert "clusters" in tables or "consumer_cluster_summary" in tables


def test_schema_retrieval_july_query():
    retrieved = schema_retriever.retrieve("Show the top 20 consumers by consumption in July.")
    tables = retrieved["relevant_tables"]
    assert "consumer_monthly_summary" in tables or "daily_summary" in tables


def test_schema_retrieval_dtr_query():
    retrieved = schema_retriever.retrieve("How many consumers are connected to DTR structure code DTR_1001?")
    tables = retrieved["relevant_tables"]
    assert "epdatalake.dtr_master" in tables
    assert "epdatalake.consumer_mapping" in tables


def test_schema_retrieval_smart_meter_query():
    retrieved = schema_retriever.retrieve("Get the latest 1-phase smart meter reading for consumer UKSC12345.")
    tables = retrieved["relevant_tables"]
    assert "epdatalake.smart_meters_install_m" in tables
    assert "epdatalake.t_blp_sp" in tables
    assert "epdatalake.lt_consumer_master" in tables


def test_schema_retrieval_amr_query():
    retrieved = schema_retriever.retrieve("Fetch the DTR AMR block load profile (t_nw_blp) reading for DTR_2002.")
    tables = retrieved["relevant_tables"]
    assert "epdatalake.fdr_dtr_newcharge" in tables
    assert "epdatalake.t_nw_blp" in tables


def test_schema_retrieval_ht_consumer_query():
    retrieved = schema_retriever.retrieve("What is the contract demand and supply voltage for HT consumer HT99001?")
    tables = retrieved["relevant_tables"]
    assert "epdatalake.ht_consumer_master" in tables


def test_schema_retrieval_billing_query():
    retrieved = schema_retriever.retrieve("Show recent billing data for LT consumers.")
    tables = retrieved["relevant_tables"]
    assert "epdatalake.lt_billing_data" in tables
