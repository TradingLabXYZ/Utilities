import pandas as pd

input_file = "0xa4f73b08e1af955e021ffe99029d2eae02ac9373.csv"

df = pd.read_csv(
    input_file,
    sep=';',
    names=["txid", "date", "type", "qty_sell", "pair_sell", "qty_buy", "pair_buy"]
)
df["qty_sell"] = df["qty_sell"].astype(str).str.replace(",", "")
df["qty_buy"] = df["qty_buy"].astype(str).str.replace(",", "")
df["qty_sell"] = df["qty_sell"].astype(str).astype(float)
df["qty_buy"] = df["qty_buy"].astype(str).astype(float)
df["price"] = df.qty_sell / df.qty_buy
df["base"] = (df["pair_sell"] + df["pair_buy"]).str.replace("MM", "")
df = df.sort_values(by=["date"], ascending=True)
recap = df[["date", "qty_sell", "pair_sell", "qty_buy", "pair_buy", "price", "base"]]

print(recap)
df.to_csv("{}_output.csv".format(input_file))
