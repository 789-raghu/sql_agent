import pytest
from security.sql_validator import sql_validator


@pytest.mark.parametrize("attack_query", [
    "DROP TABLE consumers;",
    "DELETE FROM consumption WHERE 1=1;",
    "UPDATE consumers SET name='hacked';",
    "ALTER TABLE consumers DROP COLUMN name;",
    "TRUNCATE TABLE alerts;",
    "GRANT ALL PRIVILEGES ON DATABASE electricity TO public;",
    "SELECT pg_read_file('/etc/passwd');",
    "SELECT * FROM consumers WHERE consumer_id = '1' UNION SELECT username, password FROM users;",
    "SELECT consumer_id FROM consumers; COPY consumers TO '/tmp/out.csv';"
])
def test_adversarial_queries_are_rejected(attack_query):
    is_valid, errors, _ = sql_validator.validate(attack_query)
    assert is_valid is False
    assert len(errors) > 0
