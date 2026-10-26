
BEGIN;

-- Rebuild the analytics tables from the current staging data.
-- Dropping and recreating these derived tables avoids stale results
-- caused by CREATE TABLE IF NOT EXISTS.

DROP VIEW IF EXISTS analytics.monthly_delinquency_summary;
DROP TABLE IF EXISTS analytics.monthly_performance;
DROP TABLE IF EXISTS analytics.loan_origination;

CREATE TABLE analytics.loan_origination AS
SELECT
    NULLIF(BTRIM(loan_identifier), '') AS loan_identifier,
    NULLIF(BTRIM(classic_fico), '')::INTEGER AS classic_fico,
    TO_DATE(first_payment_date || '01', 'YYYYMMDD') AS first_payment_date,
    TO_DATE(maturity_date || '01', 'YYYYMMDD') AS maturity_date,
    NULLIF(BTRIM(property_state), '') AS property_state,
    NULLIF(BTRIM(postal_code), '') AS postal_code,
    NULLIF(BTRIM(loan_purpose), '') AS loan_purpose,
    NULLIF(BTRIM(number_of_units), '')::INTEGER AS number_of_units,
    NULLIF(BTRIM(occupancy_status), '') AS occupancy_status,
    NULLIF(BTRIM(original_cltv), '')::NUMERIC(6,2) AS original_cltv,
    NULLIF(BTRIM(original_dti_ratio), '')::NUMERIC(6,2) AS original_dti_ratio,
    NULLIF(BTRIM(original_upb), '')::NUMERIC(14,2) AS original_upb,
    NULLIF(BTRIM(original_ltv), '')::NUMERIC(6,2) AS original_ltv,
    NULLIF(BTRIM(original_interest_rate), '')::NUMERIC(7,4) AS original_interest_rate,
    NULLIF(BTRIM(original_loan_term), '')::INTEGER AS original_loan_term,
    NULLIF(BTRIM(number_of_borrowers), '')::INTEGER AS number_of_borrowers,
    NULLIF(BTRIM(first_time_homebuyer_indicator), '') AS first_time_homebuyer_indicator,
    NULLIF(BTRIM(property_type), '') AS property_type,
    NULLIF(BTRIM(channel), '') AS channel,
    NULLIF(BTRIM(amortization_type), '') AS amortization_type
FROM staging.origination_raw;

CREATE TABLE analytics.monthly_performance AS
SELECT
    NULLIF(BTRIM(loan_identifier), '') AS loan_identifier,
    TO_DATE(period || '01', 'YYYYMMDD') AS reporting_month,
    NULLIF(BTRIM(current_actual_upb), '')::NUMERIC(14,2) AS current_actual_upb,
    NULLIF(BTRIM(delinquency_status), '') AS delinquency_status,
    NULLIF(BTRIM(loan_age), '')::INTEGER AS loan_age,
    NULLIF(BTRIM(remaining_months_to_legal_maturity), '')::INTEGER
        AS remaining_months_to_legal_maturity,
    NULLIF(BTRIM(current_interest_rate), '')::NUMERIC(7,4) AS current_interest_rate,
    NULLIF(BTRIM(current_non_interest_bearing_upb), '')::NUMERIC(14,2)
        AS current_non_interest_bearing_upb,
    NULLIF(BTRIM(zero_balance_code), '') AS zero_balance_code,
    NULLIF(BTRIM(modification_flag), '') AS modification_flag,
    NULLIF(BTRIM(actual_loss), '')::NUMERIC(14,2) AS actual_loss,
    NULLIF(BTRIM(estimated_ltv), '')::NUMERIC(6,2) AS estimated_ltv,
    NULLIF(BTRIM(servicer_name), '') AS servicer_name
FROM staging.performance_raw;

CREATE INDEX idx_loan_origination_loan_id
    ON analytics.loan_origination (loan_identifier);

CREATE INDEX idx_monthly_performance_loan_month
    ON analytics.monthly_performance (loan_identifier, reporting_month);

CREATE INDEX idx_monthly_performance_status
    ON analytics.monthly_performance (delinquency_status);

CREATE VIEW analytics.monthly_delinquency_summary AS
SELECT
    reporting_month,
    COUNT(*) AS total_records,
    COUNT(*) FILTER (
        WHERE delinquency_status ~ '^[0-9]+$'
          AND delinquency_status::INTEGER >= 1
    ) AS delinquent_30_plus,
    COUNT(*) FILTER (
        WHERE delinquency_status ~ '^[0-9]+$'
          AND delinquency_status::INTEGER >= 2
    ) AS delinquent_60_plus,
    COUNT(*) FILTER (
        WHERE delinquency_status ~ '^[0-9]+$'
          AND delinquency_status::INTEGER >= 3
    ) AS delinquent_90_plus
FROM analytics.monthly_performance
GROUP BY reporting_month;

ANALYZE analytics.loan_origination;
ANALYZE analytics.monthly_performance;



-- Final assertions: abort the analytics refresh if critical
-- record counts or loan relationships are incorrect.
DO $$
DECLARE
    origination_count BIGINT;
    performance_count BIGINT;
    unique_loan_count BIGINT;
    missing_performance BIGINT;
    missing_origination BIGINT;
    month_count BIGINT;
    summary_record_count BIGINT;
BEGIN
    SELECT COUNT(*)
    INTO origination_count
    FROM analytics.loan_origination;

    SELECT COUNT(*), COUNT(DISTINCT loan_identifier)
    INTO performance_count, unique_loan_count
    FROM analytics.monthly_performance;

    IF origination_count <> 50000 THEN
        RAISE EXCEPTION
            'Origination count check failed: %', origination_count;
    END IF;

    IF performance_count <> 2517857 THEN
        RAISE EXCEPTION
            'Performance count check failed: %', performance_count;
    END IF;

    IF unique_loan_count <> 50000 THEN
        RAISE EXCEPTION
            'Unique performance loan check failed: %', unique_loan_count;
    END IF;

    SELECT COUNT(*)
    INTO missing_performance
    FROM analytics.loan_origination o
    LEFT JOIN analytics.monthly_performance p
        ON o.loan_identifier = p.loan_identifier
    WHERE p.loan_identifier IS NULL;

    IF missing_performance <> 0 THEN
        RAISE EXCEPTION
            'Loans without performance records: %', missing_performance;
    END IF;

    SELECT COUNT(*)
    INTO missing_origination
    FROM analytics.monthly_performance p
    LEFT JOIN analytics.loan_origination o
        ON p.loan_identifier = o.loan_identifier
    WHERE o.loan_identifier IS NULL;

    IF missing_origination <> 0 THEN
        RAISE EXCEPTION
            'Performance records without origination: %', missing_origination;
    END IF;

    SELECT COUNT(*), COALESCE(SUM(total_records), 0)
    INTO month_count, summary_record_count
    FROM analytics.monthly_delinquency_summary;

    IF month_count <> 75 THEN
        RAISE EXCEPTION
            'Monthly period check failed: % periods', month_count;
    END IF;

    IF summary_record_count <> 2517857 THEN
        RAISE EXCEPTION
            'Monthly summary total check failed: % records',
            summary_record_count;
    END IF;

    RAISE NOTICE 'All seven analytics assertions passed.';
END $$;

COMMIT;
