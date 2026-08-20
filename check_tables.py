import sqlite3
conn = sqlite3.connect('db.sqlite3')
c = conn.cursor()

# Check all tables
c.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
all_tables = [t[0] for t in c.fetchall()]
print("ALL TABLES:", all_tables)

# Check profile columns
for table in all_tables:
    if 'profile' in table or 'skill' in table or 'userskill' in table:
        print(f"\n=== {table} ===")
        c.execute(f"PRAGMA table_info({table})")
        for col in c.fetchall():
            print(f"  {col[1]} ({col[2]})")

conn.close()
