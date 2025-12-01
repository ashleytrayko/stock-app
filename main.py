from fastapi import FastAPI
from routers import stock_router
from routers.portfolio import router as portfolio_router
from routers.transaction import router as transaction_router

app = FastAPI(
    title="Stock API",
    description="Real-time stock information and portfolio management API with transaction tracking",
    version="2.0.0"
)

# Register routers (similar to Spring @ComponentScan)
app.include_router(stock_router)
app.include_router(portfolio_router)
app.include_router(transaction_router)


@app.get("/")
async def root():
    return {
        "message": "Stock API - Real-time stock information and portfolio management with transaction tracking",
        "version": "2.0.0",
        "endpoints": {
            "/stock/{symbol}": "Get current stock information",
            "/stock/{symbol}/history": "Get historical stock data",
            "/transaction": "Buy/Sell stocks (NEW - recommended)",
            "/transaction/summary/{symbol}": "View transaction summary",
            "/portfolio": "View portfolio summary (auto-calculated from transactions)",
            "/portfolio/profit": "View portfolio with profit/loss",
            "/docs": "API documentation"
        }
    }
