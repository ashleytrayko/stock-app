from fastapi import APIRouter, HTTPException, Depends, Query
from sqlalchemy.orm import Session
from typing import List, Optional

from schemas.transaction import TransactionCreate, TransactionResponse, TransactionSummary
from models.transaction import TransactionType
from services.transaction_service import TransactionService
from database import get_db

router = APIRouter(
    prefix="/transaction",
    tags=["transaction"],
)


@router.post("/", response_model=TransactionResponse, status_code=201)
async def create_transaction(
    transaction: TransactionCreate,
    db: Session = Depends(get_db)
):
    """
    Create a new transaction (매수 또는 매도)

    For BUY:
    - Creates a transaction record
    - Updates portfolio: recalculates average price and increases quantity
    - If symbol doesn't exist in portfolio, creates a new one

    For SELL:
    - Validates that you have enough quantity to sell
    - Creates a transaction record
    - Updates portfolio: decreases quantity

    Example BUY:
    ```json
    {
        "symbol": "AAPL",
        "transaction_type": "BUY",
        "price": 180.50,
        "quantity": 10
    }
    ```

    Example SELL:
    ```json
    {
        "symbol": "AAPL",
        "transaction_type": "SELL",
        "price": 185.00,
        "quantity": 5
    }
    ```
    """
    try:
        return TransactionService.create_transaction(db, transaction)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/", response_model=List[TransactionResponse])
async def get_all_transactions(
    symbol: Optional[str] = Query(None, description="Filter by stock symbol"),
    transaction_type: Optional[TransactionType] = Query(None, description="Filter by transaction type (BUY/SELL)"),
    limit: int = Query(100, ge=1, le=500, description="Maximum number of transactions to return"),
    db: Session = Depends(get_db)
):
    """
    Get all transactions with optional filters

    Query parameters:
    - symbol: Filter by stock symbol (e.g., AAPL)
    - transaction_type: Filter by type (BUY or SELL)
    - limit: Maximum number of results (default: 100, max: 500)

    Returns transactions ordered by date (newest first)
    """
    return TransactionService.get_all_transactions(
        db,
        symbol=symbol,
        transaction_type=transaction_type,
        limit=limit
    )


@router.get("/summary/{symbol}", response_model=TransactionSummary)
async def get_transaction_summary(symbol: str, db: Session = Depends(get_db)):
    """
    Get transaction summary for a specific symbol

    Returns:
    - Total bought quantity
    - Total sold quantity
    - Current quantity (bought - sold)
    - Average buy price
    - Total number of transactions

    Example: /transaction/summary/AAPL
    """
    summary = TransactionService.get_transaction_summary(db, symbol)

    if not summary:
        raise HTTPException(
            status_code=404,
            detail=f"No transactions found for symbol '{symbol}'"
        )

    return summary


@router.get("/{transaction_id}", response_model=TransactionResponse)
async def get_transaction(transaction_id: int, db: Session = Depends(get_db)):
    """Get a single transaction by ID"""
    transaction = TransactionService.get_transaction_by_id(db, transaction_id)

    if not transaction:
        raise HTTPException(status_code=404, detail="Transaction not found")

    return transaction


@router.delete("/{transaction_id}")
async def delete_transaction(transaction_id: int, db: Session = Depends(get_db)):
    """
    Delete a transaction

    WARNING: This will NOT recalculate the portfolio automatically.
    This endpoint is primarily for correcting mistakes.
    Use with caution in production.
    """
    success = TransactionService.delete_transaction(db, transaction_id)

    if not success:
        raise HTTPException(status_code=404, detail="Transaction not found")

    return {"message": "Transaction deleted successfully"}
