import yfinance as yf
from typing import Dict, List, Optional
from models.stock import StockInfo


class StockService:
    """
    Stock service layer - handles business logic
    Similar to @Service in Spring
    """

    @staticmethod
    def get_stock_info(symbol: str) -> Optional[StockInfo]:
        """
        Fetch real-time stock information for a given symbol

        Args:
            symbol: Stock ticker symbol (e.g., AAPL, TSLA)

        Returns:
            StockInfo object or None if not found
        """
        try:
            stock = yf.Ticker(symbol)
            info = stock.info

            if not info or 'regularMarketPrice' not in info:
                return None

            return StockInfo(
                symbol=symbol.upper(),
                name=info.get('longName', info.get('shortName', 'N/A')),
                current_price=info.get('regularMarketPrice', info.get('currentPrice')),
                previous_close=info.get('previousClose'),
                open_price=info.get('regularMarketOpen', info.get('open')),
                day_high=info.get('dayHigh'),
                day_low=info.get('dayLow'),
                volume=info.get('volume'),
                market_cap=info.get('marketCap'),
                currency=info.get('currency'),
                exchange=info.get('exchange')
            )
        except Exception as e:
            raise Exception(f"Error fetching stock data: {str(e)}")

    @staticmethod
    def get_stock_history(symbol: str, period: str = "1mo") -> Dict:
        """
        Fetch historical stock data

        Args:
            symbol: Stock ticker symbol
            period: Time period (1d, 5d, 1mo, 3mo, 6mo, 1y, 2y, 5y, 10y, ytd, max)

        Returns:
            Dictionary containing symbol, period, and historical data
        """
        try:
            stock = yf.Ticker(symbol)
            hist = stock.history(period=period)

            if hist.empty:
                return None

            history_data = []
            for date, row in hist.iterrows():
                history_data.append({
                    "symbol": symbol.upper(),
                    "date": date.strftime("%Y-%m-%d"),
                    "open": round(row['Open'], 2),
                    "high": round(row['High'], 2),
                    "low": round(row['Low'], 2),
                    "close": round(row['Close'], 2),
                    "volume": int(row['Volume'])
                })

            return {
                "symbol": symbol.upper(),
                "period": period,
                "data": history_data
            }
        except Exception as e:
            raise Exception(f"Error fetching historical data: {str(e)}")
