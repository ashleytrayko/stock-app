from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List, Optional
from decimal import Decimal
from datetime import datetime

from models.transaction import Transaction, TransactionType
from models.portfolio import Portfolio
from schemas.transaction import TransactionCreate, TransactionSummary
from services.stock_service import StockService


class TransactionService:
    """Transaction service for managing buy/sell operations"""

    @staticmethod
    def create_transaction(db: Session, transaction_data: TransactionCreate) -> Transaction:
        """
        Create a new transaction (buy or sell) and update portfolio accordingly

        For BUY:
        - Create transaction record
        - Update portfolio: recalculate average price and increase quantity

        For SELL:
        - Validate: must have enough quantity to sell
        - Create transaction record
        - Update portfolio: decrease quantity
        """
        symbol = transaction_data.symbol.upper()

        # Get or create portfolio for this symbol
        portfolio = db.query(Portfolio).filter(Portfolio.symbol == symbol).first()

        if transaction_data.transaction_type == TransactionType.BUY:
            # Handle BUY transaction
            if portfolio:
                # Update existing portfolio
                # Calculate new average price
                # Formula: (current_total_cost + new_cost) / (current_qty + new_qty)
                current_total_cost = float(portfolio.average_price) * portfolio.quantity
                new_cost = transaction_data.price * transaction_data.quantity
                new_quantity = portfolio.quantity + transaction_data.quantity

                portfolio.average_price = Decimal((current_total_cost + new_cost) / new_quantity)
                portfolio.quantity = new_quantity
            else:
                # Create new portfolio
                # Get stock name from yfinance
                stock_info = StockService.get_stock_info(symbol)
                stock_name = stock_info.name if stock_info else None

                portfolio = Portfolio(
                    symbol=symbol,
                    name=stock_name,
                    average_price=Decimal(transaction_data.price),
                    quantity=transaction_data.quantity
                )
                db.add(portfolio)

        elif transaction_data.transaction_type == TransactionType.SELL:
            # Handle SELL transaction
            if not portfolio:
                raise ValueError(f"Cannot sell {symbol}: No portfolio found")

            if portfolio.quantity < transaction_data.quantity:
                raise ValueError(
                    f"Cannot sell {transaction_data.quantity} shares of {symbol}: "
                    f"Only {portfolio.quantity} shares available"
                )

            # Decrease quantity (average price stays the same)
            portfolio.quantity -= transaction_data.quantity

            # If quantity becomes 0, we could optionally delete the portfolio
            # But for now, we'll keep it with 0 quantity for history

        # Create transaction record
        transaction = Transaction(
            symbol=symbol,
            transaction_type=transaction_data.transaction_type,
            price=Decimal(transaction_data.price),
            quantity=transaction_data.quantity,
            transaction_date=transaction_data.transaction_date or datetime.now()
        )

        db.add(transaction)
        db.commit()
        db.refresh(transaction)
        db.refresh(portfolio)

        return transaction

    @staticmethod
    def get_all_transactions(
        db: Session,
        symbol: Optional[str] = None,
        transaction_type: Optional[TransactionType] = None,
        limit: int = 100
    ) -> List[Transaction]:
        """Get all transactions with optional filters"""
        query = db.query(Transaction)

        if symbol:
            query = query.filter(Transaction.symbol == symbol.upper())

        if transaction_type:
            query = query.filter(Transaction.transaction_type == transaction_type)

        return query.order_by(Transaction.transaction_date.desc()).limit(limit).all()

    @staticmethod
    def get_transaction_by_id(db: Session, transaction_id: int) -> Optional[Transaction]:
        """Get a single transaction by ID"""
        return db.query(Transaction).filter(Transaction.id == transaction_id).first()

    @staticmethod
    def get_transaction_summary(db: Session, symbol: str) -> Optional[TransactionSummary]:
        """Get transaction summary for a symbol"""
        symbol = symbol.upper()

        # Get all transactions for this symbol
        transactions = db.query(Transaction).filter(Transaction.symbol == symbol).all()

        if not transactions:
            return None

        total_bought = sum(t.quantity for t in transactions if t.transaction_type == TransactionType.BUY)
        total_sold = sum(t.quantity for t in transactions if t.transaction_type == TransactionType.SELL)
        current_quantity = total_bought - total_sold

        # Calculate average buy price
        buy_transactions = [t for t in transactions if t.transaction_type == TransactionType.BUY]
        if buy_transactions:
            total_cost = sum(float(t.price) * t.quantity for t in buy_transactions)
            total_qty = sum(t.quantity for t in buy_transactions)
            average_buy_price = total_cost / total_qty if total_qty > 0 else 0
        else:
            average_buy_price = 0

        return TransactionSummary(
            symbol=symbol,
            total_bought=total_bought,
            total_sold=total_sold,
            current_quantity=current_quantity,
            average_buy_price=average_buy_price,
            total_transactions=len(transactions)
        )

    @staticmethod
    def delete_transaction(db: Session, transaction_id: int) -> bool:
        """
        Delete a transaction
        WARNING: This will NOT recalculate portfolio. Use with caution.
        Consider implementing a recalculation mechanism if needed.
        """
        transaction = db.query(Transaction).filter(Transaction.id == transaction_id).first()

        if not transaction:
            return False

        db.delete(transaction)
        db.commit()
        return True
