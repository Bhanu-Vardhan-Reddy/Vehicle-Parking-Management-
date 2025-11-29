import os
import sys
import sqlite3
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def backup_database(db_path):
    if not os.path.exists(db_path):
        return False
    
    backup_path = db_path.replace('.db', f'_backup_{datetime.now().strftime("%Y%m%d_%H%M%S")}.db')
    
    try:
        import shutil
        shutil.copy2(db_path, backup_path)
        return True
    except:
        return False


def check_column_exists(db_path):
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        cursor.execute("PRAGMA table_info(user)")
        columns = cursor.fetchall()
        
        active_exists = any(col[1] == 'active' for col in columns)
        
        conn.close()
        return active_exists
    except:
        return False


def migrate_database(db_path):
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            CREATE TABLE user_new (
                id INTEGER PRIMARY KEY,
                email VARCHAR(255) UNIQUE NOT NULL,
                username VARCHAR(255) UNIQUE,
                password VARCHAR(255) NOT NULL,
                fs_uniquifier VARCHAR(255) UNIQUE NOT NULL
            )
        """)
        
        cursor.execute("""
            INSERT INTO user_new (id, email, username, password, fs_uniquifier)
            SELECT id, email, username, password, fs_uniquifier
            FROM user
        """)
        
        cursor.execute("DROP TABLE user")
        cursor.execute("ALTER TABLE user_new RENAME TO user")
        
        conn.commit()
        conn.close()
        
        return True
        
    except Exception as e:
        if conn:
            conn.rollback()
            conn.close()
        return False


def main():
    db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'instance', 'parking.db')
    
    if not os.path.exists(db_path):
        print("Database not found. Run 'python app.py' to create a new database.")
        return
    
    if not check_column_exists(db_path):
        print("Database is already up to date!")
        return
    
    print("The 'active' column exists and needs to be removed.")
    confirm = input("Continue with migration? (yes/no): ").strip().lower()
    
    if confirm != 'yes':
        print("Migration cancelled")
        return
    
    if not backup_database(db_path):
        print("Cannot proceed without backup")
        return
    
    if migrate_database(db_path):
        print("Migration successful!")
    else:
        print("Migration failed!")


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        sys.exit(0)
    except:
        sys.exit(1)
