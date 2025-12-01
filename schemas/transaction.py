from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from models.transaction import TransactionType


class TransactionCreate(BaseModel):
    """Transaction creation request DTO"""
    symbol: str = Field(..., description="Stock symbol (e.g., AAPL, TSLA)")
    transaction_type: TransactionType = Field(..., description="Transaction type: BUY or SELL")
    price: float = Field(..., gt=0, description="Transaction price per share")
    quantity: int = Field(..., gt=0, description="Number of shares")
    transaction_date: Optional[datetime] = Field(None, description="Transaction date (defaults to now)")


class TransactionResponse(BaseModel):
    """Transaction response DTO"""
    id: int
    symbol: str
    transaction_type: TransactionType
    price: float
    quantity: int
    transaction_date: datetime
    created_at: datetime

    class Config:
        from_attributes = True


class TransactionSummary(BaseModel):
    """Transaction summary for a symbol"""
    symbol: str
    total_bought: int  # 총 매수 수량
    total_sold: int  # 총 매도 수량
    current_quantity: int  # 현재 보유 수량
    average_buy_price: Optional[float]  # 평균 매수가
    total_transactions: int  # 총 거래 횟수
