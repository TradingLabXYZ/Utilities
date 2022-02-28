import pandas as pd
df = pd.read_csv(
    "0xd59afec43e79257bf580c4ac9f790ca8c632e327.txt",
    sep=";",
    names=["txid", "date", "type", "qty_sell", "pair_sell", "qty_buy", "pair_buy"]
)
df["qty_sell"] = df["qty_sell"].str.replace(",", "")
df["qty_buy"] = df["qty_buy"].str.replace(",", "")
df["qty_sell"] = df["qty_sell"].astype(float)
df["qty_buy"] = df["qty_buy"].astype(float)
df["price"] = df.qty_sell / df.qty_buy
df = df.sort_values(by=["date"], ascending=True)
recap = df[["date", "qty_sell", "price", "qty_buy"]]
print(recap)
