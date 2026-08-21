import pytest
from security.sql_validator import sql_validator


def test_valid_select_query():
    sql = "SELECT msn, vah_imp FROM epdatalake.ht_amr_data WHERE ts >= today();"
    is_valid, errors, clean_sql = sql_validator.validate(sql)
    assert is_valid is True
    assert len(errors) == 0


def test_reject_drop_table():
    sql = "DROP TABLE consumers;"
    is_valid, errors, _ = sql_validator.validate(sql)
    assert is_valid is False
    assert any("Forbidden keyword" in err or "Only SELECT" in err for err in errors)


def test_reject_delete_statement():
    sql = "DELETE FROM consumption WHERE consumer_id = '67002820';"
    is_valid, errors, _ = sql_validator.validate(sql)
    assert is_valid is False
    assert any("Forbidden keyword" in err or "Only SELECT" in err for err in errors)


def test_reject_multiple_statements():
    sql = "SELECT consumer_id FROM consumers; DROP TABLE alerts;"
    is_valid, errors, _ = sql_validator.validate(sql)
    assert is_valid is False
    assert any("Multiple statements" in err or "Forbidden keyword" in err for err in errors)


def test_reject_select_star():
    sql = "SELECT * FROM consumers;"
    is_valid, errors, _ = sql_validator.validate(sql)
    assert is_valid is False
    assert any("SELECT * is forbidden" in err for err in errors)


def test_reject_unallowed_table():
    sql = "SELECT username, password_hash FROM user_passwords;"
    is_valid, errors, _ = sql_validator.validate(sql)
    assert is_valid is False
    assert any("allowlist" in err for err in errors)


def test_reject_sensitive_column():
    sql = "SELECT consumer_id, api_key FROM consumers;"
    is_valid, errors, _ = sql_validator.validate(sql)
    assert is_valid is False
    assert any("sensitive column" in err.lower() for err in errors)
