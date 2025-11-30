"""
API Endpoint Tests
Similar to Spring's @WebMvcTest or MockMvc tests
"""
import pytest
import os
from fastapi.testclient import TestClient
from main import app


# Test client (similar to MockMvc in Spring)
client = TestClient(app)

# Check if running in CI environment
IS_CI = os.getenv("CI", "false").lower() == "true"


class TestStockAPI:
    """Stock API endpoint tests"""

    def test_root_endpoint(self):
        """Test root endpoint (GET /)"""
        # when
        response = client.get("/")

        # then
        assert response.status_code == 200  # assertEquals(200, response.getStatusCode())
        data = response.json()
        assert "message" in data
        assert "endpoints" in data

    def test_get_stock_info(self):
        """Test stock info endpoint (GET /stock/{symbol})"""
        # given
        symbol = "AAPL"

        # when
        response = client.get(f"/stock/{symbol}")

        # then
        assert response.status_code == 200
        data = response.json()

        assert data["symbol"] == "AAPL"
        assert data["current_price"] > 0
        assert data["name"] is not None

    def test_get_stock_info_invalid(self):
        """Test with invalid stock symbol (should return 404)"""
        # given
        invalid_symbol = "INVALID_XYZ"

        # when
        response = client.get(f"/stock/{invalid_symbol}")

        # then
        assert response.status_code == 404  # Not Found

    def test_get_stock_history(self):
        """Test stock history endpoint"""
        # given
        symbol = "AAPL"
        period = "5d"

        # when
        response = client.get(f"/stock/{symbol}/history?period={period}")

        # then
        assert response.status_code == 200
        data = response.json()

        assert data["symbol"] == "AAPL"
        assert data["period"] == "5d"
        assert len(data["data"]) > 0


@pytest.mark.skipif(IS_CI, reason="Skipping DB tests in CI environment")
class TestPortfolioAPI:
    """Portfolio API endpoint tests (requires database)"""

    def test_get_all_portfolios(self):
        """Test getting all portfolios (GET /portfolio/)"""
        # when
        response = client.get("/portfolio/")

        # then
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)  # Should return a list

    def test_get_portfolio_profit(self):
        """Test getting portfolio with profit (GET /portfolio/profit)"""
        # when
        response = client.get("/portfolio/profit")

        # then
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)


# Parametrized tests (similar to @ParameterizedTest in JUnit 5)
@pytest.mark.parametrize("symbol,expected_status", [
    ("AAPL", 200),
    ("TSLA", 200),
    ("GOOGL", 200),
])
def test_multiple_stocks(symbol, expected_status):
    """Test multiple stock symbols (parametrized test)"""
    response = client.get(f"/stock/{symbol}")
    assert response.status_code == expected_status

    if expected_status == 200:
        data = response.json()
        assert data["symbol"] == symbol
