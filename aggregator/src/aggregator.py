import pg
import os
from dotenv import load_dotenv

load_dotenv()

dbDialect = os.environ.get("DB_DIALECT") or "postgresql"
dbUser = os.environ.get("DB_USER") or "jeronimo"
dbPassword = os.environ.get("DB_PASSWORD") or "password123"
dbHost = os.environ.get("DB_HOST") or "psot_db"
dbPort = os.environ.get("DB_PORT") or 5432
dbName = os.environ.get("DB_NAME") or "psot"

conn = pg.connect(
    dbname=dbName, host=dbHost, port=dbPort, user=dbUser, passwd=dbPassword
)


conn.close()

