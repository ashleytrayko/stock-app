"""
Database migration runner script
Executes SQL migration files
"""
import os
import sys
from pathlib import Path

# Add parent directory to path to import config
sys.path.append(str(Path(__file__).parent.parent))

from config import settings
import oracledb


def run_migration(migration_file: str):
    """Run a SQL migration file"""
    print(f"Running migration: {migration_file}")

    # Read SQL file
    migration_path = Path(__file__).parent / migration_file

    if not migration_path.exists():
        print(f"Error: Migration file not found: {migration_path}")
        return False

    with open(migration_path, 'r', encoding='utf-8') as f:
        sql_content = f.read()

    # Connect to database
    try:
        # Parse DSN from DATABASE_URL
        # Format: oracle+oracledb://user:pass@dsn
        db_url = settings.DATABASE_URL

        # Extract connection details
        user = settings.DB_USER
        password = settings.DB_PASSWORD

        # Create DSN
        dsn = f"""(description=
            (retry_count=20)
            (retry_delay=3)
            (address=(protocol=tcps)(port={settings.DB_PORT})(host={settings.DB_HOST}))
            (connect_data=(service_name={settings.DB_SERVICE_NAME}))
            (security=(ssl_server_dn_match=yes)))"""

        print(f"Connecting to Oracle database...")
        connection = oracledb.connect(user=user, password=password, dsn=dsn)
        cursor = connection.cursor()

        # Split SQL content by semicolons and execute each statement
        statements = [stmt.strip() for stmt in sql_content.split(';') if stmt.strip() and not stmt.strip().startswith('--')]

        for i, statement in enumerate(statements, 1):
            # Skip comments and empty statements
            if statement.strip().startswith('--') or not statement.strip():
                continue

            try:
                print(f"Executing statement {i}/{len(statements)}...")
                cursor.execute(statement)
            except Exception as e:
                print(f"Error executing statement {i}: {e}")
                print(f"Statement: {statement[:100]}...")
                raise

        connection.commit()
        print("Migration completed successfully!")

        cursor.close()
        connection.close()
        return True

    except Exception as e:
        print(f"Migration failed: {e}")
        return False


def main():
    """Main function"""
    print("=" * 60)
    print("Database Migration Runner")
    print("=" * 60)

    # List available migrations
    migrations_dir = Path(__file__).parent
    sql_files = sorted([f for f in os.listdir(migrations_dir) if f.endswith('.sql')])

    if not sql_files:
        print("No migration files found!")
        return

    print("\nAvailable migrations:")
    for i, sql_file in enumerate(sql_files, 1):
        print(f"  {i}. {sql_file}")

    print("\nWhich migration would you like to run?")
    choice = input(f"Enter number (1-{len(sql_files)}) or 'all' to run all: ").strip()

    if choice.lower() == 'all':
        for sql_file in sql_files:
            if not run_migration(sql_file):
                print("Migration failed. Stopping.")
                break
            print()
    elif choice.isdigit() and 1 <= int(choice) <= len(sql_files):
        sql_file = sql_files[int(choice) - 1]
        run_migration(sql_file)
    else:
        print("Invalid choice!")


if __name__ == "__main__":
    main()
