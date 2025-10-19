from typing import Any, Dict

import pandas as pd

# Load the data once. This variable name is kept in French as it's the source data type.
try:
    GRAND_LIVRE = pd.read_csv(
        "grand_livre_10k.csv", dtype={"Compte_Debit": str, "Compte_Credit": str}
    )
except FileNotFoundError:
    print("Error: grand_livre_10k.csv not found. Please run data_generator.py first.")
    # Exiting here as analysis is impossible without data
    exit(1)


def calculate_balance_by_account(df: pd.DataFrame) -> pd.DataFrame:
    """
    Calculates the final balance (Débit - Crédit) for every account in the ledger.
    The result represents the General Balance (Balance Générale).

    Args:
        df: The DataFrame representing the General Ledger entries.

    Returns:
        A DataFrame indexed by account number, showing Total_Debit, Total_Credit,
        and the Final_Balance (Débit - Crédit).
    """
    # 1. Aggregate Total Debits by account
    debits = df.groupby("Compte_Debit")["Montant"].sum().rename("Total_Debit")

    # 2. Aggregate Total Credits by account
    credits = df.groupby("Compte_Credit")["Montant"].sum().rename("Total_Credit")

    # 3. Combine both aggregations and fill accounts with only Debits or Credits with 0
    balance_df = pd.concat([debits, credits], axis=1).fillna(0)

    # 4. Calculate the final balance (Débit - Crédit).
    # Balance sign: Debit accounts (Assets/Expenses) are typically positive;
    # Credit accounts (Liabilities/Equity/Income) are typically negative.
    balance_df["Final_Balance"] = balance_df["Total_Debit"] - balance_df["Total_Credit"]

    # Sort by account number (PCG order)
    balance_df.index = balance_df.index.astype(int)
    balance_df = balance_df.sort_index()
    balance_df.index = balance_df.index.astype(
        str
    )  # Convert back to string for consistency

    return balance_df[["Total_Debit", "Total_Credit", "Final_Balance"]]


def calculate_net_income(balance_df: pd.DataFrame) -> Dict[str, Any]:
    """
    Calculates Net Income (Résultat Net) based on the balances of Income (Class 7)
    and Expense (Class 6) accounts, as per the French PCG.
    Net Income = Total Products (Crédits in Class 7) - Total Charges (Débits in Class 6).

    Args:
        balance_df: The DataFrame resulting from calculate_balance_by_account.

    Returns:
        A dictionary containing Total_Products, Total_Charges, and the Net_Income.
    """

    # Filter for Class 6 (Charges/Expenses) and Class 7 (Produits/Income)
    income_expense_df = balance_df[
        (balance_df.index.str.startswith("6")) | (balance_df.index.str.startswith("7"))
    ]

    # Total Products (Class 7): Sum of Credit side
    total_products = income_expense_df[income_expense_df.index.str.startswith("7")][
        "Total_Credit"
    ].sum()

    # Total Charges (Class 6): Sum of Debit side
    total_charges = income_expense_df[income_expense_df.index.str.startswith("6")][
        "Total_Debit"
    ].sum()

    # Net Income calculation (Products - Charges)
    net_income = total_products - total_charges

    return {
        "Total_Products": round(total_products, 2),
        "Total_Charges": round(total_charges, 2),
        "Net_Income": round(net_income, 2),
    }


if __name__ == "__main__":
    # --- Execution of the analysis ---

    balance_sheet = calculate_balance_by_account(GRAND_LIVRE)
    income_statement_results = calculate_net_income(balance_sheet)

    print("\n--- General Balance (Synthesis) ---")
    print(balance_sheet)

    print("\n--- Net Income Calculation ---")
    print(
        f"Total Products (Class 7): {income_statement_results['Total_Products']:,.2f} €"
    )
    print(
        f"Total Charges (Class 6): {income_statement_results['Total_Charges']:,.2f} €"
    )
    print(f"Net Income (Résultat Net): {income_statement_results['Net_Income']:,.2f} €")

    # Quick check for overall accounting balance (Total Debits must equal Total Credits in the whole ledger)
    total_debits = (
        GRAND_LIVRE["Montant"]
        .where(
            GRAND_LIVRE.apply(
                lambda row: row["Compte_Debit"] in balance_sheet.index, axis=1
            )
        )
        .sum()
    )
    total_credits = (
        GRAND_LIVRE["Montant"]
        .where(
            GRAND_LIVRE.apply(
                lambda row: row["Compte_Credit"] in balance_sheet.index, axis=1
            )
        )
        .sum()
    )

    print("\n--- Accounting Integrity Check ---")
    print(f"Total Grand Livre Debits: {total_debits:,.2f} €")
    print(f"Total Grand Livre Credits: {total_credits:,.2f} €")
    print(f"Difference: {total_debits - total_credits:,.2f} € (Should be 0.00)")
