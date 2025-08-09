import pandas as pd

def process(input_df: pd.DataFrame) -> pd.DataFrame:
    # Switch the first two columns
    cols = list(input_df.columns)
    if len(cols) >= 2:
        cols[0], cols[1] = cols[1], cols[0]
    output_df = input_df[cols].copy()
    return output_df