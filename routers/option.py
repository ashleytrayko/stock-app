from fastapi import APIRouter, HTTPException, Query
from typing import Optional
from schemas.option import (
    OptionExpiryList, MaxPainResponse, PCRResponse,
    IVResponse, OptionChainResponse
)
from services.option_service import OptionService

router = APIRouter(
    prefix="/option",
    tags=["option"],
)


@router.get("/{symbol}/expiry", response_model=OptionExpiryList)
async def get_option_expiry_dates(symbol: str):
    """
    Get available option expiration dates for a stock

    This endpoint returns all available option expiry dates for the given symbol,
    along with the current stock price.

    Example:
    - `/option/GOOGL/expiry` - Get all available expiry dates for Google
    """
    result = OptionService.get_expiry_dates(symbol)

    if not result:
        raise HTTPException(
            status_code=404,
            detail=f"No options found for symbol '{symbol}'"
        )

    return result


@router.get("/{symbol}/max-pain", response_model=MaxPainResponse)
async def get_max_pain_analysis(
    symbol: str,
    expiry: Optional[str] = Query(None, description="Option expiry date (YYYY-MM-DD). If not provided, uses nearest expiry.")
):
    """
    Get Max Pain analysis for options

    **Max Pain Theory**: The strike price where option holders lose the most money.
    Market makers may push the stock price toward this level by expiry.

    **How it works**:
    - Identifies the strike with highest total open interest (calls + puts)
    - This is where most options expire worthless

    **Interpretation**:
    - If current price > max pain: Stock may drift down toward max pain by expiry
    - If current price < max pain: Stock may drift up toward max pain by expiry

    Example:
    - `/option/GOOGL/max-pain` - Uses nearest expiry
    - `/option/GOOGL/max-pain?expiry=2025-12-05` - Specific expiry date
    """
    result = OptionService.get_max_pain(symbol, expiry)

    if not result:
        raise HTTPException(
            status_code=404,
            detail=f"No options data found for '{symbol}'"
        )

    return result


@router.get("/{symbol}/pcr", response_model=PCRResponse)
async def get_put_call_ratio(
    symbol: str,
    expiry: Optional[str] = Query(None, description="Option expiry date (YYYY-MM-DD)")
):
    """
    Get Put-Call Ratio (PCR) analysis

    **What is PCR**: Ratio of put open interest to call open interest

    **Interpretation**:
    - **PCR > 1.0 (Bearish)**: More puts than calls
      - Traders expect downside or are hedging
      - Could also indicate bullish sentiment (protective puts)
    - **PCR < 0.7 (Bullish)**: More calls than puts
      - Traders expect upside
      - Optimistic sentiment
    - **0.7 < PCR < 1.0 (Neutral)**: Balanced sentiment

    Example:
    - `/option/GOOGL/pcr` - Get PCR for nearest expiry
    - `/option/AAPL/pcr?expiry=2025-12-20` - Get PCR for specific date
    """
    result = OptionService.get_pcr(symbol, expiry)

    if not result:
        raise HTTPException(
            status_code=404,
            detail=f"No options data found for '{symbol}'"
        )

    return result


@router.get("/{symbol}/iv", response_model=IVResponse)
async def get_implied_volatility(
    symbol: str,
    expiry: Optional[str] = Query(None, description="Option expiry date (YYYY-MM-DD)")
):
    """
    Get At-The-Money (ATM) Implied Volatility analysis

    **What is IV**: Expected future volatility priced into options

    **Interpretation**:
    - **High IV (>30%)**: Market expects large price swings
      - Earnings announcements, FDA approvals, economic data releases
      - Options are expensive (high premiums)
    - **Low IV (<15%)**: Market expects stable prices
      - Quiet periods, no major catalysts expected
      - Options are cheap (low premiums)
    - **Moderate IV (15-30%)**: Normal market conditions

    **ATM Options**: Strike price closest to current stock price
    - Most liquid and representative of market expectations

    Example:
    - `/option/TSLA/iv` - Check if Tesla expects volatility
    - `/option/AAPL/iv?expiry=2026-01-16` - Check IV for specific date
    """
    result = OptionService.get_iv(symbol, expiry)

    if not result:
        raise HTTPException(
            status_code=404,
            detail=f"No options data found for '{symbol}'"
        )

    return result


@router.get("/{symbol}/chain", response_model=OptionChainResponse)
async def get_option_chain(
    symbol: str,
    expiry: Optional[str] = Query(None, description="Option expiry date (YYYY-MM-DD)")
):
    """
    Get full option chain (all calls and puts)

    Returns complete option chain data including:
    - Strike prices
    - Last traded prices
    - Bid/Ask spreads
    - Volume
    - Open Interest
    - Implied Volatility

    This is raw option data. For interpreted analysis, use:
    - `/option/{symbol}/max-pain` - Price prediction
    - `/option/{symbol}/pcr` - Market sentiment
    - `/option/{symbol}/iv` - Volatility expectations

    Example:
    - `/option/GOOGL/chain` - Get all options for nearest expiry
    - `/option/SPY/chain?expiry=2025-12-31` - Get options for year-end
    """
    result = OptionService.get_option_chain(symbol, expiry)

    if not result:
        raise HTTPException(
            status_code=404,
            detail=f"No options data found for '{symbol}'"
        )

    return result
