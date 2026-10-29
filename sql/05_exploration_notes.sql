-- Exploratory queries used during development. The production refresh script is 06_refresh_analytics.sql.
CREATE SCHEMA IF NOT EXISTS staging;

-- Freddie Mac origination file: 31 fields
CREATE TABLE IF NOT EXISTS staging.origination_raw (
    classic_fico TEXT,
    first_payment_date TEXT,
    first_time_homebuyer_indicator TEXT,
    maturity_date TEXT,
    msa_or_division TEXT,
    mortgage_insurance_percentage TEXT,
    number_of_units TEXT,
    occupancy_status TEXT,
    original_cltv TEXT,
    original_dti_ratio TEXT,
    original_upb TEXT,
    original_ltv TEXT,
    original_interest_rate TEXT,
    channel TEXT,
    prepayment_penalty_indicator TEXT,
    amortization_type TEXT,
    property_state TEXT,
    property_type TEXT,
    postal_code TEXT,
    loan_identifier TEXT,
    loan_purpose TEXT,
    original_loan_term TEXT,
    number_of_borrowers TEXT,
    seller_name TEXT,
    super_conforming_flag TEXT,
    pre_harp_loan_sequence_number TEXT,
    special_eligibility_program TEXT,
    harp_indicator TEXT,
    property_valuation_method TEXT,
    interest_only_indicator TEXT,
    vantage_score_4 TEXT
);

-- Freddie Mac monthly performance file: 35 fields
CREATE TABLE IF NOT EXISTS staging.performance_raw (
    loan_identifier TEXT,
    period TEXT,
    current_actual_upb TEXT,
    delinquency_status TEXT,
    loan_age TEXT,
    remaining_months_to_legal_maturity TEXT,
    defect_settlement_date TEXT,
    modification_flag TEXT,
    zero_balance_code TEXT,
    zero_balance_effective_date TEXT,
    current_interest_rate TEXT,
    current_non_interest_bearing_upb TEXT,
    ddlpi TEXT,
    mi_recoveries TEXT,
    net_sales_proceeds TEXT,
    non_mi_recoveries TEXT,
    total_expenses TEXT,
    legal_costs TEXT,
    maintenance_preservation_costs TEXT,
    taxes_and_insurance TEXT,
    miscellaneous_expenses TEXT,
    actual_loss TEXT,
    cumulative_modification_costs TEXT,
    interest_rate_step_indicator TEXT,
    payment_deferral_flag TEXT,
    estimated_ltv TEXT,
    zero_balance_removal_upb TEXT,
    delinquent_accrued_interest TEXT,
    delinquency_due_to_disaster TEXT,
    borrower_assistance_plan TEXT,
    current_period_modification_costs TEXT,
    current_interest_bearing_upb TEXT,
    mi_cancellation_indicator TEXT,
    servicer_name TEXT,
    bankruptcy_cramdown_costs TEXT
);

-- Record table creation and source field counts.
SELECT
    'origination_raw' AS table_name,
    COUNT(*) AS column_count
FROM information_schema.columns
WHERE table_schema = 'staging'
  AND table_name = 'origination_raw'

UNION ALL

SELECT
    'performance_raw',
    COUNT(*)
FROM information_schema.columns
WHERE table_schema = 'staging'
  AND table_name = 'performance_raw';


SELECT
    'origination' AS dataset,
    COUNT(*) AS total_rows,
    COUNT(DISTINCT loan_identifier) AS unique_loans
FROM staging.origination_raw

UNION ALL

SELECT
    'performance',
    COUNT(*),
    COUNT(DISTINCT loan_identifier)
FROM staging.performance_raw;



SELECT
    'origination' AS dataset,
    COUNT(*) FILTER (
        WHERE loan_identifier IS NULL OR BTRIM(loan_identifier) = ''
    ) AS missing_loan_ids
FROM staging.origination_raw

UNION ALL

SELECT
    'performance',
    COUNT(*) FILTER (
        WHERE loan_identifier IS NULL OR BTRIM(loan_identifier) = ''
    )
FROM staging.performance_raw;


SELECT
    delinquency_status,
    COUNT(*) AS record_count
FROM staging.performance_raw
GROUP BY delinquency_status
ORDER BY record_count DESC
LIMIT 20;



-- ## Next step — verify missing identifiers

SELECT
    'origination' AS dataset,
    COUNT(*) FILTER (
        WHERE loan_identifier IS NULL
           OR BTRIM(loan_identifier) = ''
    ) AS missing_loan_ids
FROM staging.origination_raw

UNION ALL

SELECT
    'performance',
    COUNT(*) FILTER (
        WHERE loan_identifier IS NULL
           OR BTRIM(loan_identifier) = ''
    )
FROM staging.performance_raw;

-- Step 6 — Check the monthly reporting periods
SELECT
    MIN(period) AS earliest_period,
    MAX(period) AS latest_period,
    COUNT(*) AS total_records,
    COUNT(*) FILTER (
        WHERE period !~ '^[0-9]{6}$'
           OR SUBSTRING(period, 5, 2)::INTEGER NOT BETWEEN 1 AND 12
    ) AS invalid_periods
FROM staging.performance_raw;

-- Step 7 — Build the analytics-ready tables
SELECT
    first_payment_date,
    maturity_date,
    original_upb,
    original_interest_rate,
    original_ltv,
    original_dti_ratio
FROM staging.origination_raw
LIMIT 10;

SELECT
    period,
    current_actual_upb,
    delinquency_status,
    loan_age,
    current_interest_rate
FROM staging.performance_raw
LIMIT 10;

-- Step 7 — Create the typed analytics tables

CREATE SCHEMA IF NOT EXISTS analytics;

-- One row per loan.
CREATE TABLE IF NOT EXISTS analytics.loan_origination AS
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

-- One row per loan per reporting period.
CREATE TABLE IF NOT EXISTS analytics.monthly_performance AS
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

-- Indexes for joins and monthly risk queries.
CREATE INDEX IF NOT EXISTS idx_loan_origination_loan_id
    ON analytics.loan_origination (loan_identifier);

CREATE INDEX IF NOT EXISTS idx_monthly_performance_loan_month
    ON analytics.monthly_performance (loan_identifier, reporting_month);

CREATE INDEX IF NOT EXISTS idx_monthly_performance_status
    ON analytics.monthly_performance (delinquency_status);

ANALYZE analytics.loan_origination;
ANALYZE analytics.monthly_performance;


SELECT 'loan_origination' AS table_name, COUNT(*) AS total_rows
FROM analytics.loan_origination
UNION ALL
SELECT 'monthly_performance', COUNT(*)
FROM analytics.monthly_performance;

-- Step 8 — Analyse monthly delinquency trends
SELECT
    reporting_month,
    COUNT(*) AS total_loan_records,
    COUNT(*) FILTER (
        WHERE delinquency_status ~ '^[0-9]+$'
          AND delinquency_status::INTEGER >= 1
    ) AS delinquent_records,
    ROUND(
        100.0 * COUNT(*) FILTER (
            WHERE delinquency_status ~ '^[0-9]+$'
              AND delinquency_status::INTEGER >= 1
        ) / NULLIF(COUNT(*), 0),
        2
    ) AS delinquent_record_pct
FROM analytics.monthly_performance
GROUP BY reporting_month
ORDER BY reporting_month;


-- Step 9 — Measure delinquency severity
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
GROUP BY reporting_month
ORDER BY reporting_month;


CREATE OR REPLACE VIEW analytics.monthly_delinquency_summary AS
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

SELECT *
FROM analytics.monthly_delinquency_summary
ORDER BY reporting_month DESC
LIMIT 10;


SELECT
    COUNT(*) AS monthly_periods,
    MIN(reporting_month) AS first_month,
    MAX(reporting_month) AS last_month,
    SUM(total_records) AS total_records
FROM analytics.monthly_delinquency_summary;

-- Next step — automate data quality checks
