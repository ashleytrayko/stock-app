"""
Simple migration script that runs each step separately
Safer for Oracle database
"""
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent))

from config import settings
import oracledb


def connect_db():
    """Connect to Oracle database"""
    dsn = f"""(description=
        (retry_count=20)
        (retry_delay=3)
        (address=(protocol=tcps)(port={settings.DB_PORT})(host={settings.DB_HOST}))
        (connect_data=(service_name={settings.DB_SERVICE_NAME}))
        (security=(ssl_server_dn_match=yes)))"""

    return oracledb.connect(user=settings.DB_USER, password=settings.DB_PASSWORD, dsn=dsn)


def run_migration():
    """Run migration step by step"""
    print("=" * 60)
    print("Running Database Migration v1 -> v2")
    print("=" * 60)

    connection = connect_db()
    cursor = connection.cursor()

    try:
        # Step 1: Create transactions table
        print("\n[1/8] Creating transactions table...")
        cursor.execute("""
            CREATE TABLE transactions (
                id INTEGER PRIMARY KEY,
                symbol VARCHAR2(20) NOT NULL,
                transaction_type VARCHAR2(10) NOT NULL CHECK (transaction_type IN ('BUY', 'SELL')),
                price NUMBER(10, 2) NOT NULL,
                quantity INTEGER NOT NULL,
                transaction_date TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL,
                user_id INTEGER,
                created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
            )
        """)
        connection.commit()
        print("   ✓ Transactions table created")

        # Step 2: Create indexes
        print("\n[2/8] Creating indexes...")
        cursor.execute("CREATE INDEX idx_transactions_symbol ON transactions(symbol)")
        cursor.execute("CREATE INDEX idx_transactions_user_id ON transactions(user_id)")
        connection.commit()
        print("   ✓ Indexes created")

        # Step 3: Create sequence
        print("\n[3/8] Creating sequence...")
        cursor.execute("CREATE SEQUENCE transactions_seq START WITH 1 INCREMENT BY 1")
        connection.commit()
        print("   ✓ Sequence created")

        # Step 4: Migrate existing portfolio data to transactions
        print("\n[4/8] Migrating existing portfolio data to transactions...")
        cursor.execute("""
            INSERT INTO transactions (id, symbol, transaction_type, price, quantity, transaction_date, user_id, created_at)
            SELECT
                transactions_seq.NEXTVAL,
                symbol,
                'BUY',
                purchase_price,
                quantity,
                created_at,
                user_id,
                created_at
            FROM portfolio
        """)
        connection.commit()

        # Check how many rows were migrated
        cursor.execute("SELECT COUNT(*) FROM transactions")
        count = cursor.fetchone()[0]
        print(f"   ✓ Migrated {count} portfolio entries to transactions")

        # Step 5: Add average_price column
        print("\n[5/8] Adding average_price column to portfolio...")
        cursor.execute("ALTER TABLE portfolio ADD average_price NUMBER(10, 2)")
        connection.commit()
        print("   ✓ Column added")

        # Step 6: Copy data from purchase_price to average_price
        print("\n[6/8] Copying data from purchase_price to average_price...")
        cursor.execute("UPDATE portfolio SET average_price = purchase_price")
        connection.commit()
        print("   ✓ Data copied")

        # Step 7: Drop old column
        print("\n[7/8] Dropping purchase_price column...")
        cursor.execute("ALTER TABLE portfolio DROP COLUMN purchase_price")
        connection.commit()
        print("   ✓ Old column dropped")

        # Step 8: Make average_price NOT NULL and add unique constraint
        print("\n[8/8] Setting constraints...")
        cursor.execute("ALTER TABLE portfolio MODIFY average_price NOT NULL")

        # Remove duplicates if any
        cursor.execute("""
            DELETE FROM portfolio p1
            WHERE p1.id NOT IN (
                SELECT MAX(p2.id)
                FROM portfolio p2
                GROUP BY p2.symbol
            )
        """)

        # Add unique constraint
        try:
            cursor.execute("ALTER TABLE portfolio ADD CONSTRAINT uk_portfolio_symbol UNIQUE (symbol)")
        except Exception as e:
            if "ORA-02261" in str(e) or "ORA-00001" in str(e):
                print("   ⚠ Unique constraint already exists or duplicate data found")
            else:
                raise

        connection.commit()
        print("   ✓ Constraints set")

        print("\n" + "=" * 60)
        print("Migration completed successfully!")
        print("=" * 60)

        # Verify
        print("\nVerification:")
        cursor.execute("SELECT COUNT(*) FROM transactions")
        trans_count = cursor.fetchone()[0]
        print(f"  - Transactions: {trans_count}")

        cursor.execute("SELECT COUNT(*) FROM portfolio")
        port_count = cursor.fetchone()[0]
        print(f"  - Portfolio: {port_count}")

        return True

    except Exception as e:
        print(f"\n❌ Migration failed: {e}")
        connection.rollback()
        return False
    finally:
        cursor.close()
        connection.close()


if __name__ == "__main__":
    success = run_migration()
    sys.exit(0 if success else 1)
