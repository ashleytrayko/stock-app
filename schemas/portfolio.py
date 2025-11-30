from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from decimal import Decimal


class PortfolioCreate(BaseModel):
    """Portfolio creation request DTO"""
    symbol: str = Field(..., description="Stock symbol (e.g., AAPL, TSLA)")
    purchase_price: float = Field(..., gt=0, description="Purchase price per share")
    quantity: int = Field(..., gt=0, description="Number of shares")


class PortfolioUpdate(BaseModel):
    """Portfolio update request DTO"""
    purchase_price: Optional[float] = Field(None, gt=0)
    quantity: Optional[int] = Field(None, gt=0)


class PortfolioResponse(BaseModel):
    """Portfolio response DTO"""
    id: int
    symbol: str
    name: Optional[str]
    purchase_price: float
    quantity: int
    created_at: datetime
    updated_at: Optional[datetime]

    class Config:
        from_attributes = True  # Allows ORM model to Pydantic model conversion


class PortfolioWithProfit(BaseModel):
    """Portfolio with profit/loss calculation"""
    id: int
    symbol: str
    name: Optional[str]
    purchase_price: float
    quantity: int
    current_price: Optional[float]
    total_cost: float  # 총 매수금액 = purchase_price * quantity
    current_value: Optional[float]  # 현재 평가금액 = current_price * quantity
    profit_loss: Optional[float]  # 손익 = current_value - total_cost
    profit_loss_percent: Optional[float]  # 수익률 (%)
    created_at: datetime
