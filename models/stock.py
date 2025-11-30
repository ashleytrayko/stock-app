from pydantic import BaseModel
from typing import Optional


class StockInfo(BaseModel):
    """Stock information response model (DTO)"""
    symbol: str
    name: str
    current_price: Optional[float]
    previous_close: Optional[float]
    open_price: Optional[float]
    day_high: Optional[float]
    day_low: Optional[float]
    volume: Optional[int]
    market_cap: Optional[int]
    currency: Optional[str]
    exchange: Optional[str]


class StockHistory(BaseModel):
    """Historical stock data model"""
    symbol: str
    date: str
    open: float
    high: float
    low: float
    close: float
    volume: int
