import os
import string
import pandas as pd
import psycopg2
import random
from dotenv import load_dotenv

load_dotenv()
conn = psycopg2.connect(
    sslmode = "require",
    database = os.getenv("DB_NAME"),
    user = os.getenv("DB_USER"),
    password = os.getenv("DB_PASS"),
    host = os.getenv("DB_HOST"),
    port = os.getenv("DB_PORT")
)
cur = conn.cursor()

wallet = "0x3c2c7245793b7e86d4baa5513f8baf8b9e672068"
first_pair = "1027"
second_pair = "10866"
trade_code = "".join(random.choice(string.ascii_lowercase) for i in range(8))
default_picture = "https://tradinglab.fra1.digitaloceanspaces.com/profile_pictures/default_picture.png"

df_recap = pd.read_csv(
    "{}.txt".format(wallet),
    sep=";",
    names=["txid", "date", "type", "qty_sell", "pair_sell", "qty_buy", "pair_buy"]
)
df_recap = df_recap.sort_values(by=["date"], ascending=False)
df_recap["qty_sell"] = df_recap["qty_sell"].str.replace(",", "")
df_recap["qty_buy"] = df_recap["qty_buy"].str.replace(",", "")
df_recap["qty_sell"] = df_recap["qty_sell"].astype(float)
df_recap["qty_buy"] = df_recap["qty_buy"].astype(float)
df_recap["price"] = df_recap.qty_sell / df_recap.qty_buy

query_user = """
    INSERT INTO users (wallet, privacy, profilepicture, createdat, updatedat) VALUES 
	('{0}', 'all', '{1}', current_timestamp, current_timestamp);
""".format(wallet, default_picture)
cur.execute(query_user)
conn.commit()

query_visibility = """
    INSERT INTO visibilities (wallet, totalcounttrades, totalportfolio,
		totalreturn, totalroi, tradeqtyavailable, tradevalue, tradereturn,
		traderoi, subtradesall, subtradereasons, subtradequantity, subtradeavgprice, subtradetotal)
		VALUES ('{}', TRUE, TRUE, TRUE, TRUE, TRUE, TRUE, TRUE ,TRUE, TRUE, TRUE, TRUE, TRUE, TRUE);
""".format(wallet)
cur.execute(query_visibility)
conn.commit()

query_trade = """
    INSERT INTO trades(code, userwallet, createdat, updatedat, firstpair, secondpair, exchange)
    VALUES ('{0}', '{1}', current_timestamp, current_timestamp, {2}, {3}, 'Uniswap');
""".format(trade_code, wallet, first_pair, second_pair)
cur.execute(query_trade)
conn.commit()

values = [] 
for index, row in df_recap.iterrows():
    subtrade_code = "".join(random.choice(string.ascii_lowercase) for i in range(8))
    qty = row["qty_buy"]
    price = row["price"]
    total = row["qty_sell"]
    date = row["date"]
    trade_type = "BUY"
    reason = "Test" + str(df_recap.shape[0] - index)
    row_input = """(
        '{0}', '{1}', '{2}', '{3}', '{4}',
        {5}, {6}, {7}, '{8}', '{8}'
    )""".format(
        wallet, trade_code, subtrade_code, trade_type,
        reason, qty, price, total, date)
    values.append(row_input)
values = ",".join(values)

query_subtrades = """
    INSERT INTO subtrades(
        userwallet, tradecode, code, type, reason,
        quantity, avgprice, total, createdat, updatedat)
		VALUES {};""".format(values)
cur.execute(query_subtrades)
conn.commit()
