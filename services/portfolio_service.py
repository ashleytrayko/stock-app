from sqlalchemy.orm import Session
from database.models import Portfolio
from models.portfolio import PortfolioCreate, PortfolioUpdate, PortfolioWithProfit
from services.stock_service import StockService
from typing import List, Optional


class PortfolioService:
    """
    Portfolio service layer - handles business logic
    Similar to @Service in Spring
    """

    @staticmethod
    def create_portfolio(db: Session, portfolio_data: PortfolioCreate) -> Portfolio:
        """Create a new portfolio entry"""
        # Get stock name from yfinance
        stock_info = StockService.get_stock_info(portfolio_data.symbol)
        stock_name = stock_info.name if stock_info else None

        db_portfolio = Portfolio(
            symbol=portfolio_data.symbol.upper(),
            name=stock_name,
            purchase_price=portfolio_data.purchase_price,
            quantity=portfolio_data.quantity
        )

        db.add(db_portfolio)
        db.commit()
        db.refresh(db_portfolio)
        return db_portfolio

    @staticmethod
    def get_all_portfolios(db: Session) -> List[Portfolio]:
        """Get all portfolio entries"""
        return db.query(Portfolio).all()

    @staticmethod
    def get_portfolio_by_id(db: Session, portfolio_id: int) -> Optional[Portfolio]:
        """Get portfolio by ID"""
        return db.query(Portfolio).filter(Portfolio.id == portfolio_id).first()

    @staticmethod
    def get_portfolios_by_symbol(db: Session, symbol: str) -> List[Portfolio]:
        """Get all portfolios for a specific symbol"""
        return db.query(Portfolio).filter(Portfolio.symbol == symbol.upper()).all()

    @staticmethod
    def update_portfolio(db: Session, portfolio_id: int, portfolio_data: PortfolioUpdate) -> Optional[Portfolio]:
        """Update portfolio entry"""
        db_portfolio = db.query(Portfolio).filter(Portfolio.id == portfolio_id).first()

        if not db_portfolio:
            return None

        if portfolio_data.purchase_price is not None:
            db_portfolio.purchase_price = portfolio_data.purchase_price

        if portfolio_data.quantity is not None:
            db_portfolio.quantity = portfolio_data.quantity

        db.commit()
        db.refresh(db_portfolio)
        return db_portfolio

    @staticmethod
    def delete_portfolio(db: Session, portfolio_id: int) -> bool:
        """Delete portfolio entry"""
        db_portfolio = db.query(Portfolio).filter(Portfolio.id == portfolio_id).first()

        if not db_portfolio:
            return False

        db.delete(db_portfolio)
        db.commit()
        return True

    @staticmethod
    def get_portfolio_with_profit(db: Session, portfolio_id: int) -> Optional[PortfolioWithProfit]:
        """Get portfolio with current price and profit/loss calculation"""
        db_portfolio = db.query(Portfolio).filter(Portfolio.id == portfolio_id).first()

        if not db_portfolio:
            return None

        # Get current stock price
        stock_info = StockService.get_stock_info(db_portfolio.symbol)
        current_price = stock_info.current_price if stock_info else None

        # Calculate profit/loss
        total_cost = float(db_portfolio.purchase_price) * db_portfolio.quantity
        current_value = (current_price * db_portfolio.quantity) if current_price else None
        profit_loss = (current_value - total_cost) if current_value else None
        profit_loss_percent = ((profit_loss / total_cost) * 100) if profit_loss else None

        return PortfolioWithProfit(
            id=db_portfolio.id,
            symbol=db_portfolio.symbol,
            name=db_portfolio.name,
            purchase_price=float(db_portfolio.purchase_price),
            quantity=db_portfolio.quantity,
            current_price=current_price,
            total_cost=total_cost,
            current_value=current_value,
            profit_loss=profit_loss,
            profit_loss_percent=profit_loss_percent,
            created_at=db_portfolio.created_at
        )

    @staticmethod
    def get_all_portfolios_with_profit(db: Session) -> List[PortfolioWithProfit]:
        """Get all portfolios with profit/loss calculation"""
        portfolios = db.query(Portfolio).all()
        result = []

        for portfolio in portfolios:
            # Get current stock price
            stock_info = StockService.get_stock_info(portfolio.symbol)
            current_price = stock_info.current_price if stock_info else None

            # Calculate profit/loss
            total_cost = float(portfolio.purchase_price) * portfolio.quantity
            current_value = (current_price * portfolio.quantity) if current_price else None
            profit_loss = (current_value - total_cost) if current_value else None
            profit_loss_percent = ((profit_loss / total_cost) * 100) if profit_loss else None

            result.append(PortfolioWithProfit(
                id=portfolio.id,
                symbol=portfolio.symbol,
                name=portfolio.name,
                purchase_price=float(portfolio.purchase_price),
                quantity=portfolio.quantity,
                current_price=current_price,
                total_cost=total_cost,
                current_value=current_value,
                profit_loss=profit_loss,
                profit_loss_percent=profit_loss_percent,
                created_at=portfolio.created_at
            ))

        return result
