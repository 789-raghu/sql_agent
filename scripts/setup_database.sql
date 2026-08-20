-- Create electricity database schema and sample dataset

CREATE TABLE IF NOT EXISTS locations (
    location_id SERIAL PRIMARY KEY,
    city VARCHAR(100) NOT NULL,
    state VARCHAR(100) NOT NULL,
    postal_code VARCHAR(20) NOT NULL
);

CREATE TABLE IF NOT EXISTS clusters (
    cluster_id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    region VARCHAR(100) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS consumers (
    consumer_id VARCHAR(50) PRIMARY KEY,
    name VARCHAR(150) NOT NULL,
    cluster_id INT REFERENCES clusters(cluster_id),
    location_id INT REFERENCES locations(location_id),
    category VARCHAR(50) NOT NULL,
    join_date DATE NOT NULL
);

CREATE TABLE IF NOT EXISTS meters (
    meter_id VARCHAR(50) PRIMARY KEY,
    consumer_id VARCHAR(50) REFERENCES consumers(consumer_id),
    install_date DATE NOT NULL,
    meter_type VARCHAR(50) NOT NULL,
    status VARCHAR(20) NOT NULL
);

CREATE TABLE IF NOT EXISTS tariffs (
    tariff_id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    rate_per_kwh NUMERIC(10, 4) NOT NULL,
    peak_rate_per_kwh NUMERIC(10, 4) NOT NULL
);

CREATE TABLE IF NOT EXISTS weather (
    location_id INT REFERENCES locations(location_id),
    timestamp TIMESTAMP NOT NULL,
    temperature NUMERIC(5, 2) NOT NULL,
    humidity NUMERIC(5, 2) NOT NULL,
    solar_radiation NUMERIC(6, 2) NOT NULL,
    PRIMARY KEY (location_id, timestamp)
);

CREATE TABLE IF NOT EXISTS alerts (
    alert_id SERIAL PRIMARY KEY,
    consumer_id VARCHAR(50) REFERENCES consumers(consumer_id),
    timestamp TIMESTAMP NOT NULL,
    alert_type VARCHAR(100) NOT NULL,
    severity VARCHAR(20) NOT NULL,
    description TEXT
);

CREATE TABLE IF NOT EXISTS consumption (
    consumer_id VARCHAR(50) REFERENCES consumers(consumer_id),
    timestamp TIMESTAMP NOT NULL,
    consumption NUMERIC(12, 4) NOT NULL,
    status VARCHAR(20) DEFAULT 'VALID',
    PRIMARY KEY (consumer_id, timestamp)
);

CREATE TABLE IF NOT EXISTS predictions (
    consumer_id VARCHAR(50) REFERENCES consumers(consumer_id),
    timestamp TIMESTAMP NOT NULL,
    predicted_consumption NUMERIC(12, 4) NOT NULL,
    model_version VARCHAR(50) DEFAULT 'v1.0',
    PRIMARY KEY (consumer_id, timestamp)
);

CREATE TABLE IF NOT EXISTS daily_summary (
    consumer_id VARCHAR(50) REFERENCES consumers(consumer_id),
    date DATE NOT NULL,
    total_consumption NUMERIC(12, 4) NOT NULL,
    avg_consumption NUMERIC(12, 4) NOT NULL,
    max_consumption NUMERIC(12, 4) NOT NULL,
    min_consumption NUMERIC(12, 4) NOT NULL,
    PRIMARY KEY (consumer_id, date)
);

-- Seed metadata
INSERT INTO locations (location_id, city, state, postal_code) VALUES
(1, 'Mumbai', 'Maharashtra', '400001'),
(2, 'Pune', 'Maharashtra', '411001'),
(3, 'Nagpur', 'Maharashtra', '440001')
ON CONFLICT (location_id) DO NOTHING;

INSERT INTO clusters (cluster_id, name, region) VALUES
(1, 'Industrial Zone East', 'North-East'),
(2, 'Commercial Hub Central', 'Central'),
(3, 'Residential Park South', 'South')
ON CONFLICT (cluster_id) DO NOTHING;

INSERT INTO consumers (consumer_id, name, cluster_id, location_id, category, join_date) VALUES
('67002820', 'Apex Manufacturing Ltd', 1, 1, 'Industrial', '2023-01-15'),
('67001972', 'Global Tech Park', 2, 1, 'Commercial', '2023-02-20'),
('67004989', 'Sunrise Towers', 3, 2, 'Residential', '2023-03-10'),
('67006433', 'Metro Logistics Center', 1, 2, 'Industrial', '2023-04-05'),
('67004504', 'City Mall & Retails', 2, 1, 'Commercial', '2023-05-12'),
('67006825', 'Zenith Pharma Works', 1, 3, 'Industrial', '2023-06-18'),
('67002957', 'Orchid Heights', 3, 3, 'Residential', '2023-07-22')
ON CONFLICT (consumer_id) DO NOTHING;

INSERT INTO meters (meter_id, consumer_id, install_date, meter_type, status) VALUES
('MTR-67002820', '67002820', '2023-01-15', 'Smart Three-Phase', 'ACTIVE'),
('MTR-67001972', '67001972', '2023-02-20', 'Smart Three-Phase', 'ACTIVE'),
('MTR-67004989', '67004989', '2023-03-10', 'Smart Single-Phase', 'ACTIVE'),
('MTR-67006433', '67006433', '2023-04-05', 'Smart Three-Phase', 'ACTIVE'),
('MTR-67004504', '67004504', '2023-05-12', 'Smart Three-Phase', 'ACTIVE'),
('MTR-67006825', '67006825', '2023-06-18', 'Smart Three-Phase', 'ACTIVE'),
('MTR-67002957', '67002957', '2023-07-22', 'Smart Single-Phase', 'ACTIVE')
ON CONFLICT (meter_id) DO NOTHING;

INSERT INTO tariffs (tariff_id, name, rate_per_kwh, peak_rate_per_kwh) VALUES
(1, 'Industrial Tariff A', 8.50, 11.20),
(2, 'Commercial Tariff B', 9.20, 12.50),
(3, 'Residential Standard', 6.00, 7.80)
ON CONFLICT (tariff_id) DO NOTHING;

-- Seed weather and alerts sample data
INSERT INTO weather (location_id, timestamp, temperature, humidity, solar_radiation) VALUES
(1, CURRENT_DATE - INTERVAL '1 day' + INTERVAL '12 hours', 31.5, 78.0, 650.0),
(2, CURRENT_DATE - INTERVAL '1 day' + INTERVAL '12 hours', 29.0, 70.0, 710.0),
(3, CURRENT_DATE - INTERVAL '1 day' + INTERVAL '12 hours', 34.2, 55.0, 800.0)
ON CONFLICT (location_id, timestamp) DO NOTHING;

INSERT INTO alerts (alert_id, consumer_id, timestamp, alert_type, severity, description) VALUES
(1, '67002820', CURRENT_DATE - INTERVAL '2 days', 'HIGH_DEMAND_SPIKE', 'WARNING', 'Consumption exceeded baseline by 25%'),
(2, '67006433', CURRENT_DATE - INTERVAL '1 day', 'VOLTAGE_FLUCTUATION', 'INFO', 'Transient voltage drop detected')
ON CONFLICT (alert_id) DO NOTHING;

-- Function to seed hourly data dynamically for key date ranges (July 2026, yesterday, last week)
DO $$
DECLARE
    cid TEXT;
    dt TIMESTAMP;
    base_val NUMERIC;
    pred_val NUMERIC;
BEGIN
    FOR cid IN SELECT consumer_id FROM consumers LOOP
        -- Seed July 2026 hourly data
        dt := '2026-07-01 00:00:00'::TIMESTAMP;
        WHILE dt <= '2026-07-31 23:00:00'::TIMESTAMP LOOP
            IF cid = '67002820' THEN base_val := 150.0 + (EXTRACT(HOUR FROM dt) * 3) + ((random() * 20) - 10);
            ELSIF cid = '67001972' THEN base_val := 200.0 + (EXTRACT(HOUR FROM dt) * 5) + ((random() * 30) - 15);
            ELSE base_val := 40.0 + (EXTRACT(HOUR FROM dt) * 1.5) + ((random() * 10) - 5);
            END IF;
            pred_val := base_val * 0.92; -- prediction slightly lower so actual exceeds prediction by ~8-12%
            
            INSERT INTO consumption (consumer_id, timestamp, consumption)
            VALUES (cid, dt, ROUND(base_val, 4))
            ON CONFLICT (consumer_id, timestamp) DO NOTHING;

            INSERT INTO predictions (consumer_id, timestamp, predicted_consumption)
            VALUES (cid, dt, ROUND(pred_val, 4))
            ON CONFLICT (consumer_id, timestamp) DO NOTHING;
            
            dt := dt + INTERVAL '1 hour';
        END LOOP;

        -- Seed recent 14 days up to today
        dt := date_trunc('day', CURRENT_DATE - INTERVAL '14 days');
        WHILE dt < date_trunc('day', CURRENT_DATE + INTERVAL '1 day') LOOP
            IF cid = '67002820' THEN base_val := 160.0 + (EXTRACT(HOUR FROM dt) * 3.5) + ((random() * 15) - 7);
            ELSIF cid = '67006825' THEN base_val := 220.0 + (EXTRACT(HOUR FROM dt) * 4) + ((random() * 25) - 12);
            ELSE base_val := 45.0 + (EXTRACT(HOUR FROM dt) * 2) + ((random() * 8) - 4);
            END IF;
            pred_val := base_val * 0.88; -- prediction 12% below actual for testing exeeded queries

            INSERT INTO consumption (consumer_id, timestamp, consumption)
            VALUES (cid, dt, ROUND(base_val, 4))
            ON CONFLICT (consumer_id, timestamp) DO NOTHING;

            INSERT INTO predictions (consumer_id, timestamp, predicted_consumption)
            VALUES (cid, dt, ROUND(pred_val, 4))
            ON CONFLICT (consumer_id, timestamp) DO NOTHING;

            dt := dt + INTERVAL '1 hour';
        END LOOP;
    END LOOP;

    -- Aggregate daily_summary
    INSERT INTO daily_summary (consumer_id, date, total_consumption, avg_consumption, max_consumption, min_consumption)
    SELECT
        consumer_id,
        date_trunc('day', timestamp)::DATE as date,
        SUM(consumption) as total_consumption,
        AVG(consumption) as avg_consumption,
        MAX(consumption) as max_consumption,
        MIN(consumption) as min_consumption
    FROM consumption
    GROUP BY consumer_id, date_trunc('day', timestamp)::DATE
    ON CONFLICT (consumer_id, date) DO UPDATE SET
        total_consumption = EXCLUDED.total_consumption,
        avg_consumption = EXCLUDED.avg_consumption,
        max_consumption = EXCLUDED.max_consumption,
        min_consumption = EXCLUDED.min_consumption;
END $$;
