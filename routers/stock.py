from fastapi import APIRouter, HTTPException
from models.stock import StockInfo
from services.stock_service import StockService

router = APIRouter(
    prefix="/stock",
    tags=["stock"],
)


@router.get("/{symbol}", response_model=StockInfo)
async def get_stock_info(symbol: str):
    """
    Get real-time stock information for a given symbol.

    Examples:
    - AAPL (Apple)
    - TSLA (Tesla)
    - GOOGL (Google)
    - MSFT (Microsoft)
    - 005930.KS (Samsung - Korean stock)
    """
    stock_info = StockService.get_stock_info(symbol)

    if not stock_info:
        raise HTTPException(
            status_code=404,
            detail=f"Stock symbol '{symbol}' not found"
        )

    return stock_info


@router.get("/{symbol}/history")
async def get_stock_history(symbol: str, period: str = "1mo"):
    """
    Get historical stock data.

    Parameters:
    - symbol: Stock ticker symbol
    - period: Time period (1d, 5d, 1mo, 3mo, 6mo, 1y, 2y, 5y, 10y, ytd, max)

    Examples:
    - /stock/AAPL/history?period=1mo
    - /stock/TSLA/history?period=1y
    """
    history = StockService.get_stock_history(symbol, period)

    if not history:
        raise HTTPException(
            status_code=404,
            detail=f"No historical data found for '{symbol}'"
        )

    return history
