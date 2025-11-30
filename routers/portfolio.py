from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from typing import List

from schemas.portfolio import (
    PortfolioCreate,
    PortfolioUpdate,
    PortfolioResponse,
    PortfolioWithProfit
)
from services.portfolio_service import PortfolioService
from database import get_db

router = APIRouter(
    prefix="/portfolio",
    tags=["portfolio"],
)


@router.post("/", response_model=PortfolioResponse, status_code=201)
async def create_portfolio(
    portfolio: PortfolioCreate,
    db: Session = Depends(get_db)
):
    """
    Create a new portfolio entry (주식 매수 등록)

    Example:
    ```json
    {
        "symbol": "AAPL",
        "purchase_price": 150.50,
        "quantity": 10
    }
    ```
    """
    try:
        return PortfolioService.create_portfolio(db, portfolio)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/", response_model=List[PortfolioResponse])
async def get_all_portfolios(db: Session = Depends(get_db)):
    """Get all portfolio entries (내 모든 주식 조회)"""
    return PortfolioService.get_all_portfolios(db)


@router.get("/profit", response_model=List[PortfolioWithProfit])
async def get_all_portfolios_with_profit(db: Session = Depends(get_db)):
    """
    Get all portfolios with current price and profit/loss
    (실시간 손익 계산 포함)
    """
    return PortfolioService.get_all_portfolios_with_profit(db)


@router.get("/{portfolio_id}", response_model=PortfolioResponse)
async def get_portfolio(portfolio_id: int, db: Session = Depends(get_db)):
    """Get portfolio by ID"""
    portfolio = PortfolioService.get_portfolio_by_id(db, portfolio_id)

    if not portfolio:
        raise HTTPException(status_code=404, detail="Portfolio not found")

    return portfolio


@router.get("/{portfolio_id}/profit", response_model=PortfolioWithProfit)
async def get_portfolio_with_profit(portfolio_id: int, db: Session = Depends(get_db)):
    """
    Get portfolio with current price and profit/loss
    (개별 주식 손익 조회)
    """
    portfolio = PortfolioService.get_portfolio_with_profit(db, portfolio_id)

    if not portfolio:
        raise HTTPException(status_code=404, detail="Portfolio not found")

    return portfolio


@router.put("/{portfolio_id}", response_model=PortfolioResponse)
async def update_portfolio(
    portfolio_id: int,
    portfolio_data: PortfolioUpdate,
    db: Session = Depends(get_db)
):
    """Update portfolio entry (매수가/수량 수정)"""
    portfolio = PortfolioService.update_portfolio(db, portfolio_id, portfolio_data)

    if not portfolio:
        raise HTTPException(status_code=404, detail="Portfolio not found")

    return portfolio


@router.delete("/{portfolio_id}")
async def delete_portfolio(portfolio_id: int, db: Session = Depends(get_db)):
    """Delete portfolio entry (보유 주식 삭제)"""
    success = PortfolioService.delete_portfolio(db, portfolio_id)

    if not success:
        raise HTTPException(status_code=404, detail="Portfolio not found")

    return {"message": "Portfolio deleted successfully"}
