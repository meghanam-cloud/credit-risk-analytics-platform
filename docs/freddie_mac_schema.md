# Freddie Mac Dataset Schema

Source: Freddie Mac Single-Family Loan-Level Dataset
Layout: July 2026
Format: Pipe-delimited text with no header row.

## Origination File — 31 fields

1. Classic FICO®
2. First Payment Date
3. First Time Homebuyer Indicator
4. Maturity Date
5. Metropolitan Statistical Area (MSA) Or Metropolitan Division
6. Mortgage Insurance Percentage (MI %)
7. Number of Units
8. Occupancy Status
9. Original Combined Loan-to-Value (CLTV)
10. Original Debt-to-Income (DTI) Ratio
11. Original UPB
12. Original Loan-to-Value (LTV)
13. Original Interest Rate
14. Channel
15. Prepayment Penalty Indicator
16. Amortization Type
17. Property State
18. Property Type
19. Postal Code
20. Loan Identifier
21. Loan Purpose
22. Original Loan Term
23. Number of Borrowers
24. Seller Name
25. Super Conforming Flag
26. Pre-HARP Loan Sequence Number
27. Special Eligibility Program
28. HARP Indicator
29. Property Valuation Method
30. Interest Only (I/O) Indicator
31. VantageScore® 4.0

## Monthly Performance File — 35 fields

1. Loan Identifier
2. Period
3. Current Actual UPB
4. Current Loan Delinquency Status
5. Loan Age
6. Remaining Months to Legal Maturity
7. Underwriting Defect and Major Servicing Defect Settlement Date
8. Modification Flag
9. Zero Balance Code
10. Zero Balance Effective Date
11. Current Interest Rate
12. Current Non-Interest Bearing UPB
13. Due Date of Last Paid Installment (DDLPI)
14. MI Recoveries
15. Net Sales Proceeds
16. Non MI Recoveries
17. Total Expenses
18. Legal Costs
19. Maintenance and Preservation Costs
20. Taxes and Insurance
21. Miscellaneous Expenses
22. Actual Loss
23. Cumulative Modification Costs
24. Interest Rate Step Indicator
25. Payment Deferral Flag
26. Estimated Loan-to-Value (ELTV)
27. Zero Balance Removal UPB
28. Delinquent Accrued Interest
29. Delinquency Due to Disaster
30. Borrower Assistance Plan
31. Current Period Modification Costs
32. Current Interest Bearing UPB
33. Mortgage Insurance Cancellation Indicator
34. Servicer Name
35. Bankruptcy Cramdown Costs

## Join Key

Origination file: field 20 — Loan Identifier
Monthly performance file: field 1 — Loan Identifier

## Data handling

- Preserve raw source files unchanged.
- Keep raw loan-level data out of public GitHub repositories.
- Follow the dataset terms of use.
- Validate field counts before processing.
- Treat blank fields according to the official field definitions.
