import random
from datetime import date, timedelta

import pandas as pd
from faker import Faker

# Initialize Faker with French locale for credible French labels (PCG/Audit context)
fake = Faker("fr_FR")

# --- 1. PCG Simplified Constants and Transaction Logic ---

# Maps a typical financial transaction to its corresponding Debit and Credit PCG account.
# This ensures accounting balance (Double-Entry Bookkeeping).
TRANSACTIONS_LOGIC = {
    # Sales and Purchases (Income/Expense Accounts - Class 7 and 6)
    "Sales of Goods": {
        "debit": 411,
        "credit": 707,
    },  # 411: Clients (Receivable) vs 707: Sales (Income)
    "Purchase of Goods": {
        "debit": 607,
        "credit": 401,
    },  # 607: Purchases (Expense) vs 401: Suppliers (Payable)
    # Cash/Bank Operations (Treasury - Class 5)
    "Client Payment Received": {
        "debit": 512,
        "credit": 411,
    },  # 512: Bank (Asset) vs 411: Clients (Receivable decrease)
    "Supplier Payment Made": {
        "debit": 401,
        "credit": 512,
    },  # 401: Suppliers (Payable decrease) vs 512: Bank (Asset decrease)
    "Bank Fees": {
        "debit": 627,
        "credit": 512,
    },  # 627: Bank Services (Expense) vs 512: Bank (Asset decrease)
    # HR/Payroll (for diversity)
    "Payroll Payment": {
        "debit": 641,
        "credit": 512,
    },  # 641: Salaries (Expense) vs 512: Bank (Asset decrease)
}


def generate_grand_livre(num_entries=10000):
    """
    Generates a DataFrame simulating a General Ledger (Grand Livre) of accounting entries.
    Each entry respects double-entry bookkeeping rules (Debit = Credit).
    """
    records = []
    start_date = date(2024, 1, 1)

    for i in range(1, num_entries + 1):
        # Choose a random transaction type
        libelle_type, logic = random.choice(list(TRANSACTIONS_LOGIC.items()))

        # Generate a random date within 2024
        delta = timedelta(days=random.randint(0, 365))
        transaction_date = (start_date + delta).isoformat()

        # Generate a credible transaction amount (between 50 and 5000)
        montant = round(random.uniform(50, 5000), 2)

        # Generate a rich French label using Faker, based on the transaction type
        if libelle_type == "Sales of Goods":
            full_libelle = f"Facture Vente n°V{i} {fake.company()}"
        elif libelle_type == "Purchase of Goods":
            full_libelle = f"Facture Achat n°A{i} auprès de {fake.company()}"
        elif libelle_type == "Client Payment Received":
            full_libelle = f"Virement client {fake.name()}"
        elif libelle_type == "Supplier Payment Made":
            full_libelle = f"Règlement fournisseur {fake.name()}"
        else:
            full_libelle = libelle_type  # Default label for others

        # Record the double-entry
        records.append(
            {
                "Date": transaction_date,
                "Compte_Debit": logic["debit"],
                "Compte_Credit": logic["credit"],
                "Montant": montant,
                "Libelle": full_libelle,
                "ID_Transaction": i,
            }
        )

    df = pd.DataFrame(records)
    # Ensure account numbers are stored as strings (standard accounting practice)
    df[["Compte_Debit", "Compte_Credit"]] = df[
        ["Compte_Debit", "Compte_Credit"]
    ].astype(str)
    return df


if __name__ == "__main__":
    # Generate 10,000 accounting entries
    df_gl = generate_grand_livre(num_entries=10000)

    # Export for immediate use by the analysis module
    output_file = "grand_livre_10k.csv"
    df_gl.to_csv(output_file, index=False)

    print(f"✅ File '{output_file}' generated with {len(df_gl)} entries.")
    print("\n--- Data Sample (Head) ---")
    print(df_gl.head())
