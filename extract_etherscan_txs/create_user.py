import os
import uuid
import string
import pandas as pd
import psycopg2
import requests
import random
from dotenv import load_dotenv
from requests.structures import CaseInsensitiveDict

wallet = "0xa4f73b08e1af955e021ffe99029d2eae02ac9373"

def main():
    conn, cur = connect_db()
    create_user(conn, cur)
    session_id = create_session(conn, cur)
    api_token = generate_api_token(session_id)
    print(api_token)

def connect_db():
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
    return conn, cur


def create_user(conn, cur):
    default_picture = "https://tradinglab.fra1.digitaloceanspaces.com/profile_pictures/default_picture.png"
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

def create_session(conn, cur):
    session_id = uuid.uuid4()
    query_session = """
        INSERT INTO sessions (code, userwallet, createdat, origin)
            VALUES ('{}', '{}', current_timestamp, 'web');
        """.format(session_id, wallet)
    cur.execute(query_session)
    conn.commit()
    return session_id

def generate_api_token(session_id):
    headers = CaseInsensitiveDict()
    headers["Access-Control-Allow-Origin"] = "*"
    headers["Authorization"] = "Bearer sessionId={}".format(session_id)
    response = requests.get("https://api.tradinglab.xyz/generate_api_token", headers=headers)
    return response.text

if __name__ == '__main__':
    main()
