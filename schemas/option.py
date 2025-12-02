from pydantic import BaseModel
from typing import List, Optional
from datetime import date


class OptionData(BaseModel):
    """Individual option data"""
    strike: float
    last_price: Optional[float]
    bid: Optional[float]
    ask: Optional[float]
    volume: Optional[int]
    open_interest: Optional[int]
    implied_volatility: Optional[float]


class OptionExpiryList(BaseModel):
    """Available option expiration dates"""
    symbol: str
    current_price: float
    expiry_dates: List[str]


class MaxPainResponse(BaseModel):
    """Max Pain analysis response"""
    symbol: str
    expiry_date: str
    current_price: float
    max_pain_price: float
    price_difference_percent: float
    top_strikes: List[dict]  # [{"strike": 280.0, "open_interest": 22306}, ...]

    class Config:
        json_schema_extra = {
            "example": {
                "symbol": "GOOGL",
                "expiry_date": "2025-12-05",
                "current_price": 314.89,
                "max_pain_price": 280.0,
                "price_difference_percent": -11.08,
                "top_strikes": [
                    {"strike": 280.0, "open_interest": 22306},
                    {"strike": 330.0, "open_interest": 19713}
                ]
            }
        }


class PCRResponse(BaseModel):
    """Put-Call Ratio analysis response"""
    symbol: str
    expiry_date: str
    total_call_open_interest: int
    total_put_open_interest: int
    put_call_ratio: float
    interpretation: str  # "Bullish", "Bearish", "Neutral"

    class Config:
        json_schema_extra = {
            "example": {
                "symbol": "GOOGL",
                "expiry_date": "2025-12-05",
                "total_call_open_interest": 132281,
                "total_put_open_interest": 126457,
                "put_call_ratio": 0.96,
                "interpretation": "Neutral"
            }
        }


class IVResponse(BaseModel):
    """Implied Volatility analysis response"""
    symbol: str
    expiry_date: str
    current_price: float
    atm_strike: float
    atm_call_iv: float
    atm_put_iv: float
    average_iv: float
    interpretation: str  # "High volatility expected", "Low volatility expected"

    class Config:
        json_schema_extra = {
            "example": {
                "symbol": "GOOGL",
                "expiry_date": "2025-12-05",
                "current_price": 314.89,
                "atm_strike": 315.0,
                "atm_call_iv": 0.001,
                "atm_put_iv": 0.0001,
                "average_iv": 0.00055,
                "interpretation": "Low volatility expected"
            }
        }


class OptionChainResponse(BaseModel):
    """Option chain response (calls and puts)"""
    symbol: str
    expiry_date: str
    current_price: float
    calls: List[OptionData]
    puts: List[OptionData]
