import sqlite3
import os

def find_path():
    end = 'OneDrive - Rep Fitness/Documents - Product and Engineering/Internal Docs/ID Team/paint.db'
    start = os.path.dirname(os.path.realpath(__file__))
    start = start.split('\\')
    first = '\\'.join(start[:3])
    path = first + '\\' + end
    return path

def print_table_entries(cursor, table_name, limit=20):
    """Print the first 'limit' entries of the specified table."""
    try:
        # Get column names
        cursor.execute(f"PRAGMA table_info({table_name})")
        columns = [column[1] for column in cursor.fetchall()]
        
        # Get the first 'limit' rows
        cursor.execute(f"SELECT * FROM {table_name} LIMIT {limit}")
        rows = cursor.fetchall()
        
        print(f"\n=== TABLE: {table_name} ===")
        print(f"Columns: {', '.join(columns)}")
        print(f"First {min(len(rows), limit)} entries:")
        
        for i, row in enumerate(rows, 1):
            print(f"{i}. {row}")
            
        if not rows:
            print("No entries found in this table.")
            
    except sqlite3.Error as e:
        print(f"Error accessing table {table_name}: {e}")

def main():
    # Connect to the database
    dbpath = find_path()
    print(f"Connecting to database at: {dbpath}")
    
    try:
        conn = sqlite3.connect(dbpath)
        cursor = conn.cursor()
        
        # Get all table names
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        
        if not tables:
            print("No tables found in the database.")
        else:
            print(f"Found {len(tables)} tables in the database.")
            
            # Print entries for each table
            for table in tables:
                table_name = table[0]
                print_table_entries(cursor, table_name)
        
        conn.close()
        print("\nDatabase connection closed.")
        
    except sqlite3.Error as e:
        print(f"Database error: {e}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()
