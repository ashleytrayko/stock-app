-- Migration: Add Transaction Tracking System
-- Date: 2024-12-01
-- Description: Creates transaction table and updates portfolio structure

-- Step 1: Create transactions table
CREATE TABLE transactions (
    id INTEGER PRIMARY KEY,
    symbol VARCHAR2(20) NOT NULL,
    transaction_type VARCHAR2(10) NOT NULL CHECK (transaction_type IN ('BUY', 'SELL')),
    price NUMBER(10, 2) NOT NULL,
    quantity INTEGER NOT NULL,
    transaction_date TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL,
    user_id INTEGER,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Create index on symbol for faster queries
CREATE INDEX idx_transactions_symbol ON transactions(symbol);

-- Create index on user_id for future user authentication
CREATE INDEX idx_transactions_user_id ON transactions(user_id);

-- Create sequence for transactions table
CREATE SEQUENCE transactions_seq START WITH 1 INCREMENT BY 1;

-- Step 2: Backup existing portfolio data to transactions
-- Convert all existing portfolio entries to BUY transactions
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
FROM portfolio;

-- Step 3: Update portfolio table structure
-- Rename purchase_price to average_price (Oracle doesn't support direct rename with data)
ALTER TABLE portfolio ADD average_price NUMBER(10, 2);

COMMIT;

UPDATE portfolio SET average_price = purchase_price;

COMMIT;

ALTER TABLE portfolio DROP COLUMN purchase_price;

COMMIT;

ALTER TABLE portfolio MODIFY average_price NOT NULL;

COMMIT;

-- Add unique constraint on symbol (one portfolio per symbol)
-- First, remove duplicates if any exist by keeping only the latest one
DELETE FROM portfolio p1
WHERE p1.id NOT IN (
    SELECT MAX(p2.id)
    FROM portfolio p2
    GROUP BY p2.symbol
);

COMMIT;

-- Now add the unique constraint
ALTER TABLE portfolio ADD CONSTRAINT uk_portfolio_symbol UNIQUE (symbol);

COMMIT;

-- Step 4: Verify migration
-- Check transactions count
SELECT COUNT(*) as transaction_count FROM transactions;

-- Check portfolio structure
SELECT * FROM portfolio WHERE ROWNUM <= 5;

-- Summary of changes:
-- 1. Created transactions table with proper indexes
-- 2. Migrated existing portfolio data to transactions as BUY records
-- 3. Renamed purchase_price to average_price in portfolio table
-- 4. Added unique constraint on symbol in portfolio table
-- 5. Portfolio now represents a summary of all transactions per symbol

COMMIT;
