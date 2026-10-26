
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
