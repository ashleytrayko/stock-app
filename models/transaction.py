from sqlalchemy import Column, Integer, String, DateTime, Numeric, Enum as SQLEnum, Sequence
from sqlalchemy.sql import func
from database.db import Base
import enum


class TransactionType(str, enum.Enum):
    """거래 유형"""
    BUY = "BUY"    # 매수
    SELL = "SELL"  # 매도


class Transaction(Base):
    """
    Stock transaction history (주식 거래 내역)
    Records all buy/sell transactions
    """
    __tablename__ = "transactions"

    # Primary Key (using Oracle sequence)
    id = Column(Integer, Sequence('transactions_seq'), primary_key=True)

    # Stock symbol
    symbol = Column(String(20), nullable=False, index=True)

    # Transaction type (BUY or SELL)
    transaction_type = Column(SQLEnum(TransactionType), nullable=False)

    # Transaction price (거래 단가)
    price = Column(Numeric(10, 2), nullable=False)

    # Quantity (거래 수량)
    quantity = Column(Integer, nullable=False)

    # Transaction date (거래 일시)
    transaction_date = Column(DateTime(timezone=True), nullable=False, server_default=func.now())

    # User ID (for future user authentication)
    user_id = Column(Integer, nullable=True, index=True)

    # Record creation timestamp
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    def __repr__(self):
        return f"<Transaction(id={self.id}, symbol={self.symbol}, type={self.transaction_type}, price={self.price}, quantity={self.quantity})>"
