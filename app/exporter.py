import pandas as pd


def export_csv(df: pd.DataFrame, filename: str | None) -> None:
    if not filename:
        filename = "output.csv"

    df.to_csv(filename, float_format="%.2f", index=True)

    print(f"Saved to {filename}")
