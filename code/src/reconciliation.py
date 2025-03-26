import sqlite3

DB_FILE = "reconciliation.db"
TOLERANCE_THRESHOLD = 5  # Set tolerance level for mismatches

def detect_mismatches():
    """Identifies trade mismatches based on tolerance levels."""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM recon_history")
    trades = cursor.fetchall()

    mismatches = []
    for trade in trades:
        _, riskdate, quantity_a, quantity_b, tolerance, comment, _=trade
        expected = quantity_a  # Rename for clarity
        actual = quantity_b
        if abs(expected - actual) > TOLERANCE_THRESHOLD:
            mismatches.append({
                "trade_id": id,
                "riskdate": riskdate,
                "expected": expected,
                "actual": actual,
                "tolerance": tolerance,
                "comment": comment
            })

    conn.close()
    return mismatches


def detect_tolerance_breaches(df=None):
    import sqlite3
    if df is None:
        # Fetch data from the database
        conn = sqlite3.connect("reconciliation.db")
        cursor = conn.cursor()
        cursor.execute("SELECT riskdate, quantity_a, quantity_b, tolerance, comment FROM recon_history")
        trades = cursor.fetchall()
        conn.close()
        # Convert to a list of dicts for consistency
        mismatches = []
        for trade in trades:
            riskdate, quantity_a, quantity_b, tolerance, comment = trade
            if abs(quantity_a - quantity_b) > tolerance:
                mismatches.append({
                    "riskdate": riskdate,
                    "expected": quantity_a,
                    "actual": quantity_b,
                    "tolerance": tolerance,
                    "comment": comment
                })
        return mismatches
    else:
        # Process the provided DataFrame 'df'
        df["Break Type"] = ""
        for index, row in df.iterrows():
            system_a_qty, system_b_qty = row["quantity_a"], row["quantity_b"]
            tolerance = row.get("tolerance", row.get("quantity_tolerance", 0))
            if abs(system_a_qty - system_b_qty) > tolerance:
                df.at[index, "Break Type"] = "Tolerance Breach"
        # Return mismatches as a list of dictionaries
        mismatches = df[df["Break Type"] != ""].to_dict(orient="records")
        return mismatches


if __name__ == "__main__":
    print("⚡ Detected Mismatches:", detect_mismatches())

