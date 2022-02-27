import pandas as pd
df = pd.read_csv(
    "0x3c2c7245793b7e86d4baa5513f8baf8b9e672068.txt",
    sep=";",
    header=0,
    index_col=False,
    names=["txid", "date", "type", "qty_sell", "pair_sell", "qty_buy", "pair_buy"]
)
df["price"] = df.qty_sell / df.qty_buy
recap = df[["date", "qty_sell", "price", "qty_buy"]]
print(recap)
