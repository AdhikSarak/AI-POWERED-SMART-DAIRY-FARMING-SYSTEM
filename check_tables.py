import psycopg2
from backend.core.config import settings

try:
    conn = psycopg2.connect(settings.DATABASE_URL)
    cursor = conn.cursor()
    cursor.execute("SELECT table_name FROM information_schema.tables WHERE table_schema = 'public';")
    tables = cursor.fetchall()
    print('Tables in database:')
    for table in tables:
        print(f'  - {table[0]}')
    cursor.close()
    conn.close()
except Exception as e:
    print(f'Error: {e}')