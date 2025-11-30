from fastapi import FastAPI
from routers import stock_router
from routers.portfolio import router as portfolio_router

app = FastAPI(
    title="Stock API",
    description="Real-time stock information and portfolio management API",
    version="1.0.0"
)

# Register routers (similar to Spring @ComponentScan)
app.include_router(stock_router)
app.include_router(portfolio_router)


@app.get("/")
async def root():
    return {
        "message": "Stock API - Real-time stock information and portfolio management",
        "version": "1.0.0",
        "endpoints": {
            "/stock/{symbol}": "Get current stock information",
            "/stock/{symbol}/history": "Get historical stock data",
            "/portfolio": "Manage your stock portfolio",
            "/portfolio/profit": "View portfolio with profit/loss",
            "/docs": "API documentation"
        }
    }
