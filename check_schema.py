import psycopg2
from backend.core.config import settings

try:
    conn = psycopg2.connect(settings.DATABASE_URL)
    cursor = conn.cursor()

    # Check each table structure
    tables = ['users', 'cows', 'milk_collections', 'billing', 'health_records', 'milk_records', 'recommendations']

    for table in tables:
        cursor.execute(f"SELECT column_name, data_type FROM information_schema.columns WHERE table_name = '{table}' ORDER BY ordinal_position;")
        columns = cursor.fetchall()
        print(f'\n{table.upper()} table columns:')
        for col in columns:
            print(f'  - {col[0]}: {col[1]}')

    cursor.close()
    conn.close()
except Exception as e:
    print(f'Error: {e}')