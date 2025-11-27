"""
Database Migration Script
Removes the 'active' column from User table

This script is needed if you have an existing database with the old schema.
New installations will not need this script.

Usage:
    python migrate_remove_active_column.py
"""

import os
import sys
import sqlite3
from datetime import datetime

# Add backend to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def backup_database(db_path):
    """Create a backup of the database before migration"""
    if not os.path.exists(db_path):
        print(f"❌ Database not found at: {db_path}")
        return False
    
    backup_path = db_path.replace('.db', f'_backup_{datetime.now().strftime("%Y%m%d_%H%M%S")}.db')
    
    try:
        import shutil
        shutil.copy2(db_path, backup_path)
        print(f"✅ Database backed up to: {backup_path}")
        return True
    except Exception as e:
        print(f"❌ Backup failed: {e}")
        return False


def check_column_exists(db_path):
    """Check if the active column exists in the user table"""
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Get table info
        cursor.execute("PRAGMA table_info(user)")
        columns = cursor.fetchall()
        
        # Check if 'active' column exists
        active_exists = any(col[1] == 'active' for col in columns)
        
        conn.close()
        return active_exists
    except Exception as e:
        print(f"❌ Error checking table: {e}")
        return False


def migrate_database(db_path):
    """Remove the active column from user table"""
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        print("\n📋 Starting migration...")
        
        # SQLite doesn't support DROP COLUMN directly, so we need to:
        # 1. Create new table without 'active' column
        # 2. Copy data from old table
        # 3. Drop old table
        # 4. Rename new table
        
        print("   1. Creating new user table without 'active' column...")
        cursor.execute("""
            CREATE TABLE user_new (
                id INTEGER PRIMARY KEY,
                email VARCHAR(255) UNIQUE NOT NULL,
                username VARCHAR(255) UNIQUE,
                password VARCHAR(255) NOT NULL,
                fs_uniquifier VARCHAR(255) UNIQUE NOT NULL
            )
        """)
        
        print("   2. Copying data from old table...")
        cursor.execute("""
            INSERT INTO user_new (id, email, username, password, fs_uniquifier)
            SELECT id, email, username, password, fs_uniquifier
            FROM user
        """)
        
        print("   3. Dropping old table...")
        cursor.execute("DROP TABLE user")
        
        print("   4. Renaming new table...")
        cursor.execute("ALTER TABLE user_new RENAME TO user")
        
        conn.commit()
        conn.close()
        
        print("✅ Migration completed successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Migration failed: {e}")
        if conn:
            conn.rollback()
            conn.close()
        return False


def main():
    """Main migration function"""
    print("\n" + "="*70)
    print(" 🔄 DATABASE MIGRATION: Remove 'active' column from User table")
    print("="*70)
    
    # Determine database path
    db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'instance', 'parking.db')
    
    print(f"\n📍 Database location: {db_path}")
    
    # Check if database exists
    if not os.path.exists(db_path):
        print("\n⚠️  Database not found!")
        print("   This is normal for new installations.")
        print("   Run 'python app.py' to create a new database with the updated schema.")
        return
    
    # Check if column exists
    print("\n🔍 Checking current schema...")
    if not check_column_exists(db_path):
        print("✅ Database is already up to date!")
        print("   The 'active' column does not exist in the user table.")
        return
    
    print("⚠️  The 'active' column exists and needs to be removed.")
    
    # Confirm migration
    print("\n⚠️  WARNING: This will modify your database!")
    print("   A backup will be created automatically.")
    confirm = input("\nContinue with migration? (yes/no): ").strip().lower()
    
    if confirm != 'yes':
        print("\n❌ Migration cancelled by user")
        return
    
    # Backup database
    print("\n📦 Creating backup...")
    if not backup_database(db_path):
        print("\n❌ Cannot proceed without backup")
        return
    
    # Run migration
    if migrate_database(db_path):
        print("\n" + "="*70)
        print(" ✅ MIGRATION SUCCESSFUL!")
        print("="*70)
        print("\n📝 Summary:")
        print("   - 'active' column removed from user table")
        print("   - All user data preserved")
        print("   - Backup created for safety")
        print("\n🚀 You can now restart your application!")
    else:
        print("\n" + "="*70)
        print(" ❌ MIGRATION FAILED!")
        print("="*70)
        print("\n📝 Your database was not modified.")
        print("   The backup is available if needed.")
        print("   Please check the error messages above.")


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n❌ Migration interrupted by user")
        sys.exit(0)
    except Exception as e:
        print(f"\n\n❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

