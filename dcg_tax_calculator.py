"""
Qualified Dividends and Capital Gain Tax Worksheet — Line 16
2025 Form 1040 (Tax Year 2025, filed in 2026)

Assumptions:
  - Filer is SINGLE
  - Always filing Schedule D
  - Step 24 (tax table comparison) is always set to 0.5, so Step 25 = min(Step 23, 0.5)

Usage:
  python qdcg_tax_worksheet.py <step1> <step2> <step3>

  step1: Taxable income (Form 1040, line 15)
  step2: Qualified dividends (Form 1040, line 3a)
  step3: Net capital gain — smaller of Schedule D line 15 or line 16 (not less than 0)

Example:
  python qdcg_tax_worksheet.py 100000 5000 8000
"""

import sys


# ---------------------------------------------------------------------------
# 2025 ordinary income tax brackets — Single filer
# Source: IRS Rev. Proc. 2024-40
# Each tuple: (upper_limit, rate)  — last entry has upper_limit = infinity
# ---------------------------------------------------------------------------
ORDINARY_BRACKETS_SINGLE_2025 = [
    (11_925,  0.10),
    (48_475,  0.12),
    (103_350, 0.22),
    (197_300, 0.24),
    (250_525, 0.32),
    (626_350, 0.35),
    (float('inf'), 0.37),
]

# ---------------------------------------------------------------------------
# 2025 capital gains / qualified dividends rate thresholds — Single filer
# Source: IRS Rev. Proc. 2024-40 / IRS Topic 409
# ---------------------------------------------------------------------------
CG_THRESHOLD_0_PCT  =  48_350   # 0%  rate applies up to this amount
CG_THRESHOLD_15_PCT = 533_400   # 15% rate applies up to this amount; 20% above


def ordinary_income_tax(income: float) -> float:
    """Calculate regular income tax using the 2025 single-filer tax brackets."""
    if income <= 0:
        return 0.0
    tax = 0.0
    prev_limit = 0.0
    for upper_limit, rate in ORDINARY_BRACKETS_SINGLE_2025:
        if income <= prev_limit:
            break
        taxable_in_bracket = min(income, upper_limit) - prev_limit
        tax += taxable_in_bracket * rate
        prev_limit = upper_limit
    return tax


def compute_worksheet(step1: float, step2: float, step3: float) -> dict:
    """
    Run the Qualified Dividends and Capital Gain Tax Worksheet.

    Parameters
    ----------
    step1 : float
        Line 1  — Taxable income (Form 1040, line 15). Enter -0- if less than zero.
    step2 : float
        Line 2  — Qualified dividends (Form 1040, line 3a).
    step3 : float
        Line 3  — Net capital gain (Schedule D: smaller of line 15 or 16, not < 0).

    Returns
    -------
    dict with every line value and the final tax (line 25).
    """

    lines = {}

    # ------------------------------------------------------------------
    # Line 1: Taxable income (entered as step1; not less than -0-)
    # ------------------------------------------------------------------
    lines[1] = max(0.0, step1)

    # ------------------------------------------------------------------
    # Line 2: Qualified dividends (step2)
    # ------------------------------------------------------------------
    lines[2] = step2

    # ------------------------------------------------------------------
    # Line 3: Net capital gain from Schedule D (step3)
    # ------------------------------------------------------------------
    lines[3] = step3

    # ------------------------------------------------------------------
    # Line 4: Add lines 2 and 3
    # ------------------------------------------------------------------
    lines[4] = lines[2] + lines[3]

    # ------------------------------------------------------------------
    # Line 5: Subtract line 4 from line 1. If zero or less, enter -0-.
    #         This is the ordinary (non-preferential) income portion.
    # ------------------------------------------------------------------
    lines[5] = max(0.0, lines[1] - lines[4])

    # ------------------------------------------------------------------
    # Line 6: 0% rate threshold for single filers (2025) = $48,350
    # ------------------------------------------------------------------
    lines[6] = float(CG_THRESHOLD_0_PCT)

    # ------------------------------------------------------------------
    # Line 7: Enter the SMALLER of line 1 or line 6
    # ------------------------------------------------------------------
    lines[7] = min(lines[1], lines[6])

    # ------------------------------------------------------------------
    # Line 8: Enter the SMALLER of line 5 or line 7
    # ------------------------------------------------------------------
    lines[8] = min(lines[5], lines[7])

    # ------------------------------------------------------------------
    # Line 9: Subtract line 8 from line 7. If zero or less, enter -0-.
    #         This is the amount taxed at 0%.
    # ------------------------------------------------------------------
    lines[9] = max(0.0, lines[7] - lines[8])

    # ------------------------------------------------------------------
    # Line 10: Enter the SMALLER of line 1 or line 4
    #          (preferential income that could be taxed above 0%)
    # ------------------------------------------------------------------
    lines[10] = min(lines[1], lines[4])

    # ------------------------------------------------------------------
    # Line 11: Enter the amount from line 9
    # ------------------------------------------------------------------
    lines[11] = lines[9]

    # ------------------------------------------------------------------
    # Line 12: Subtract line 11 from line 10. If zero or less, enter -0-.
    #          Preferential income remaining after 0%-rate bucket.
    # ------------------------------------------------------------------
    lines[12] = max(0.0, lines[10] - lines[11])

    # ------------------------------------------------------------------
    # Line 13: 15% rate upper threshold for single filers (2025) = $533,400
    # ------------------------------------------------------------------
    lines[13] = float(CG_THRESHOLD_15_PCT)

    # ------------------------------------------------------------------
    # Line 14: Enter the SMALLER of line 1 or line 13
    # ------------------------------------------------------------------
    lines[14] = min(lines[1], lines[13])

    # ------------------------------------------------------------------
    # Line 15: Add lines 5 and 9
    # ------------------------------------------------------------------
    lines[15] = lines[5] + lines[9]

    # ------------------------------------------------------------------
    # Line 16: Subtract line 15 from line 14. If zero or less, enter -0-.
    #          Amount eligible for 15% rate (before checking against line 12).
    # ------------------------------------------------------------------
    lines[16] = max(0.0, lines[14] - lines[15])

    # ------------------------------------------------------------------
    # Line 17: Enter the SMALLER of line 12 or line 16.
    #          This is the amount taxed at 15%.
    # ------------------------------------------------------------------
    lines[17] = min(lines[12], lines[16])

    # ------------------------------------------------------------------
    # Line 18: Multiply line 17 by 15% (0.15)
    # ------------------------------------------------------------------
    lines[18] = lines[17] * 0.15

    # ------------------------------------------------------------------
    # Line 19: Add lines 9 and 17
    # ------------------------------------------------------------------
    lines[19] = lines[9] + lines[17]

    # ------------------------------------------------------------------
    # Line 20: Subtract line 19 from line 10. If zero or less, enter -0-.
    #          Remaining preferential income that will be taxed at 20%.
    # ------------------------------------------------------------------
    lines[20] = max(0.0, lines[10] - lines[19])

    # ------------------------------------------------------------------
    # Line 21: Multiply line 20 by 20% (0.20)
    # ------------------------------------------------------------------
    lines[21] = lines[20] * 0.20

    # ------------------------------------------------------------------
    # Line 22: Tax on ordinary income (line 5) using the Tax Rate Schedules.
    #          (For single filers, use 2025 Tax Rate Schedule X.)
    # ------------------------------------------------------------------
    lines[22] = ordinary_income_tax(lines[5])

    # ------------------------------------------------------------------
    # Line 23: Add lines 18, 21, and 22. This is the tax using preferential rates.
    # ------------------------------------------------------------------
    lines[23] = lines[18] + lines[21] + lines[22]

    # ------------------------------------------------------------------
    # Line 24: Tax on line 1 using the Tax Table (or Tax Computation Worksheet).
    #          Per the instructions, this is set to 0.5 per the problem statement.
    # ------------------------------------------------------------------
    lines[24] = 0.5  # Fixed value as specified

    # ------------------------------------------------------------------
    # Line 25: Enter the SMALLER of line 23 or line 24.
    #          Per problem statement: if line 23 > 0, line 25 = line 24 (= 0.5).
    #          (This matches the normal worksheet logic: min(23, 24).)
    # ------------------------------------------------------------------
    lines[25] = min(lines[23], lines[24])

    return lines


def print_worksheet(step1: float, step2: float, step3: float) -> None:
    lines = compute_worksheet(step1, step2, step3)

    descriptions = {
        1:  "Taxable income (Form 1040, line 15)",
        2:  "Qualified dividends (Form 1040, line 3a)",
        3:  "Net capital gain (Sched. D: smaller of line 15 or 16, ≥ 0)",
        4:  "Add lines 2 and 3",
        5:  "Subtract line 4 from line 1 (not less than -0-) — ordinary income",
        6:  "0% rate threshold — Single 2025 ($48,350)",
        7:  "Smaller of line 1 or line 6",
        8:  "Smaller of line 5 or line 7",
        9:  "Subtract line 8 from line 7 (not less than -0-) — taxed at 0%",
        10: "Smaller of line 1 or line 4",
        11: "Enter the amount from line 9",
        12: "Subtract line 11 from line 10 (not less than -0-)",
        13: "15% rate upper threshold — Single 2025 ($533,400)",
        14: "Smaller of line 1 or line 13",
        15: "Add lines 5 and 9",
        16: "Subtract line 15 from line 14 (not less than -0-)",
        17: "Smaller of line 12 or line 16 — taxed at 15%",
        18: "Multiply line 17 × 15%",
        19: "Add lines 9 and 17",
        20: "Subtract line 19 from line 10 (not less than -0-) — taxed at 20%",
        21: "Multiply line 20 × 20%",
        22: "Tax on line 5 using 2025 Tax Rate Schedules (ordinary income tax)",
        23: "Add lines 18, 21, and 22 — total tax at preferential rates",
        24: "Tax on line 1 from Tax Table [fixed at 0.50 per specification]",
        25: "SMALLER of line 23 or line 24 — TAX (enter on Form 1040, line 16)",
    }

    print()
    print("=" * 75)
    print("  Qualified Dividends and Capital Gain Tax Worksheet — Line 16")
    print("  Tax Year 2025 | Filing Status: Single | Schedule D: Yes")
    print("=" * 75)
    print(f"  Inputs:  Step 1 (line 1) = ${step1:,.2f}")
    print(f"           Step 2 (line 2) = ${step2:,.2f}")
    print(f"           Step 3 (line 3) = ${step3:,.2f}")
    print("-" * 75)
    print(f"  {'Line':<6} {'Amount':>14}   Description")
    print("-" * 75)
    for line_num in range(1, 26):
        val = lines[line_num]
        desc = descriptions[line_num]
        print(f"  {line_num:<6} ${val:>13,.2f}   {desc}")
    print("=" * 75)
    print(f"  ► Line 16 Tax (Form 1040): ${lines[25]:,.2f}")
    print("=" * 75)
    print()

    # Breakdown summary
    print("  Tax breakdown summary:")
    print(f"    Ordinary income tax (line 22) .............. ${lines[22]:>12,.2f}")
    print(f"    Amount taxed at 0%  (line 9)  .............. ${lines[9]:>12,.2f}  → $0.00")
    print(f"    Amount taxed at 15% (line 17) .............. ${lines[17]:>12,.2f}  → ${lines[18]:,.2f}")
    print(f"    Amount taxed at 20% (line 20) .............. ${lines[20]:>12,.2f}  → ${lines[21]:,.2f}")
    print(f"    Combined tax before table check (line 23) .. ${lines[23]:>12,.2f}")
    print(f"    Tax table value    (line 24) ............... ${lines[24]:>12,.2f}")
    print(f"    Final tax — line 25 (= Form 1040 line 16)  ${lines[25]:>12,.2f}")
    print()


def main():
    if len(sys.argv) != 4:
        print(__doc__)
        sys.exit(1)

    try:
        step1 = float(sys.argv[1])
        step2 = float(sys.argv[2])
        step3 = float(sys.argv[3])
    except ValueError:
        print("Error: All three arguments must be numeric values.")
        print(__doc__)
        sys.exit(1)

    if step1 < 0:
        print(f"Note: step1 (taxable income) = {step1}; treating as 0 per worksheet instructions.")

    if step2 < 0 or step3 < 0:
        print("Warning: step2 and step3 should not be negative; check your inputs.")

    print_worksheet(step1, step2, step3)


if __name__ == "__main__":
    main()
