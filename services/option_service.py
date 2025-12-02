import yfinance as yf
import pandas as pd
from typing import Optional, List
from schemas.option import (
    OptionExpiryList, MaxPainResponse, PCRResponse,
    IVResponse, OptionChainResponse, OptionData
)


class OptionService:
    """
    Option service layer - handles option analysis business logic
    """

    @staticmethod
    def get_expiry_dates(symbol: str) -> Optional[OptionExpiryList]:
        """
        Get available option expiration dates for a symbol

        Args:
            symbol: Stock ticker symbol

        Returns:
            OptionExpiryList object with available expiry dates
        """
        try:
            ticker = yf.Ticker(symbol)
            current_price = ticker.history(period='1d')['Close'].iloc[-1]

            if not ticker.options:
                return None

            return OptionExpiryList(
                symbol=symbol.upper(),
                current_price=round(current_price, 2),
                expiry_dates=list(ticker.options)
            )
        except Exception as e:
            raise Exception(f"Error fetching expiry dates: {str(e)}")

    @staticmethod
    def get_max_pain(symbol: str, expiry: Optional[str] = None) -> Optional[MaxPainResponse]:
        """
        Calculate Max Pain price for options

        Max Pain is the strike price where option holders lose the most money.
        It's where open interest is highest.

        Args:
            symbol: Stock ticker symbol
            expiry: Option expiry date (YYYY-MM-DD). If None, uses nearest expiry.

        Returns:
            MaxPainResponse with max pain analysis
        """
        try:
            ticker = yf.Ticker(symbol)
            current_price = ticker.history(period='1d')['Close'].iloc[-1]

            if not ticker.options:
                return None

            # Use nearest expiry if not specified
            if not expiry:
                expiry = ticker.options[0]

            # Get option chain
            option_chain = ticker.option_chain(expiry)
            calls = option_chain.calls
            puts = option_chain.puts

            # Calculate total open interest per strike
            strikes = pd.concat(
                [calls[['strike', 'openInterest']], puts[['strike', 'openInterest']]],
                keys=['call', 'put']
            )
            strike_oi = strikes.groupby('strike')['openInterest'].sum().sort_values(ascending=False)

            # Get top 5 strikes
            top_strikes = [
                {"strike": float(strike), "open_interest": int(oi)}
                for strike, oi in strike_oi.head(5).items()
            ]

            # Max pain is the strike with highest open interest
            max_pain_price = float(strike_oi.idxmax())
            price_diff_percent = ((max_pain_price / current_price - 1) * 100)

            return MaxPainResponse(
                symbol=symbol.upper(),
                expiry_date=expiry,
                current_price=round(current_price, 2),
                max_pain_price=round(max_pain_price, 2),
                price_difference_percent=round(price_diff_percent, 2),
                top_strikes=top_strikes
            )
        except Exception as e:
            raise Exception(f"Error calculating max pain: {str(e)}")

    @staticmethod
    def get_pcr(symbol: str, expiry: Optional[str] = None) -> Optional[PCRResponse]:
        """
        Calculate Put-Call Ratio

        PCR is the ratio of put open interest to call open interest.
        - PCR > 1: More puts (bearish or hedging)
        - PCR < 0.7: More calls (bullish)
        - 0.7 < PCR < 1: Neutral

        Args:
            symbol: Stock ticker symbol
            expiry: Option expiry date. If None, uses nearest expiry.

        Returns:
            PCRResponse with put-call ratio analysis
        """
        try:
            ticker = yf.Ticker(symbol)

            if not ticker.options:
                return None

            if not expiry:
                expiry = ticker.options[0]

            option_chain = ticker.option_chain(expiry)
            calls = option_chain.calls
            puts = option_chain.puts

            total_call_oi = int(calls['openInterest'].sum())
            total_put_oi = int(puts['openInterest'].sum())
            pcr = total_put_oi / total_call_oi if total_call_oi > 0 else 0

            # Interpret PCR
            if pcr > 1:
                interpretation = "Bearish"
            elif pcr < 0.7:
                interpretation = "Bullish"
            else:
                interpretation = "Neutral"

            return PCRResponse(
                symbol=symbol.upper(),
                expiry_date=expiry,
                total_call_open_interest=total_call_oi,
                total_put_open_interest=total_put_oi,
                put_call_ratio=round(pcr, 2),
                interpretation=interpretation
            )
        except Exception as e:
            raise Exception(f"Error calculating PCR: {str(e)}")

    @staticmethod
    def get_iv(symbol: str, expiry: Optional[str] = None) -> Optional[IVResponse]:
        """
        Get At-The-Money (ATM) Implied Volatility

        IV represents expected future volatility priced into options.
        - High IV (>30%): Large price movements expected
        - Low IV (<15%): Stable price expected

        Args:
            symbol: Stock ticker symbol
            expiry: Option expiry date. If None, uses nearest expiry.

        Returns:
            IVResponse with implied volatility analysis
        """
        try:
            ticker = yf.Ticker(symbol)
            current_price = ticker.history(period='1d')['Close'].iloc[-1]

            if not ticker.options:
                return None

            if not expiry:
                expiry = ticker.options[0]

            option_chain = ticker.option_chain(expiry)
            calls = option_chain.calls
            puts = option_chain.puts

            # Find ATM options (closest to current price)
            calls['strike_diff'] = abs(calls['strike'] - current_price)
            atm_call = calls.loc[calls['strike_diff'].idxmin()]

            puts['strike_diff'] = abs(puts['strike'] - current_price)
            atm_put = puts.loc[puts['strike_diff'].idxmin()]

            atm_strike = float(atm_call['strike'])
            atm_call_iv = float(atm_call['impliedVolatility'])
            atm_put_iv = float(atm_put['impliedVolatility'])
            avg_iv = (atm_call_iv + atm_put_iv) / 2

            # Interpret IV
            if avg_iv > 0.30:
                interpretation = "High volatility expected"
            elif avg_iv < 0.15:
                interpretation = "Low volatility expected"
            else:
                interpretation = "Moderate volatility expected"

            return IVResponse(
                symbol=symbol.upper(),
                expiry_date=expiry,
                current_price=round(current_price, 2),
                atm_strike=round(atm_strike, 2),
                atm_call_iv=round(atm_call_iv, 4),
                atm_put_iv=round(atm_put_iv, 4),
                average_iv=round(avg_iv, 4),
                interpretation=interpretation
            )
        except Exception as e:
            raise Exception(f"Error calculating IV: {str(e)}")

    @staticmethod
    def get_option_chain(symbol: str, expiry: Optional[str] = None) -> Optional[OptionChainResponse]:
        """
        Get full option chain (calls and puts) for a symbol

        Args:
            symbol: Stock ticker symbol
            expiry: Option expiry date. If None, uses nearest expiry.

        Returns:
            OptionChainResponse with calls and puts data
        """
        try:
            ticker = yf.Ticker(symbol)
            current_price = ticker.history(period='1d')['Close'].iloc[-1]

            if not ticker.options:
                return None

            if not expiry:
                expiry = ticker.options[0]

            option_chain = ticker.option_chain(expiry)

            # Convert calls to OptionData list
            calls_data = [
                OptionData(
                    strike=float(row['strike']),
                    last_price=float(row['lastPrice']) if pd.notna(row['lastPrice']) else None,
                    bid=float(row['bid']) if pd.notna(row['bid']) else None,
                    ask=float(row['ask']) if pd.notna(row['ask']) else None,
                    volume=int(row['volume']) if pd.notna(row['volume']) else None,
                    open_interest=int(row['openInterest']) if pd.notna(row['openInterest']) else None,
                    implied_volatility=float(row['impliedVolatility']) if pd.notna(row['impliedVolatility']) else None
                )
                for _, row in option_chain.calls.iterrows()
            ]

            # Convert puts to OptionData list
            puts_data = [
                OptionData(
                    strike=float(row['strike']),
                    last_price=float(row['lastPrice']) if pd.notna(row['lastPrice']) else None,
                    bid=float(row['bid']) if pd.notna(row['bid']) else None,
                    ask=float(row['ask']) if pd.notna(row['ask']) else None,
                    volume=int(row['volume']) if pd.notna(row['volume']) else None,
                    open_interest=int(row['openInterest']) if pd.notna(row['openInterest']) else None,
                    implied_volatility=float(row['impliedVolatility']) if pd.notna(row['impliedVolatility']) else None
                )
                for _, row in option_chain.puts.iterrows()
            ]

            return OptionChainResponse(
                symbol=symbol.upper(),
                expiry_date=expiry,
                current_price=round(current_price, 2),
                calls=calls_data,
                puts=puts_data
            )
        except Exception as e:
            raise Exception(f"Error fetching option chain: {str(e)}")
