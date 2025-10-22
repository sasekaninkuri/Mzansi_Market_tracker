import psycopg2
from streamlit import connection
from db_setup import create_tables

def get_connection():
    conn = psycopg2.connect(
        host="localhost",
        database="mzansi_market",
        user="postgres",
        password="12345"
    )
    return conn