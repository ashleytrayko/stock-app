"""
Stock Service Tests
Similar to Spring's @SpringBootTest
"""
import pytest
from services.stock_service import StockService


class TestStockService:
    """
    Stock service test class
    Similar to Spring's test class with @Test methods
    """

    def test_get_stock_info_success(self):
        """Test getting valid stock information (like @Test in Spring)"""
        # given
        symbol = "AAPL"

        # when
        result = StockService.get_stock_info(symbol)

        # then
        assert result is not None  # assertThat(result).isNotNull()
        assert result.symbol == "AAPL"  # assertThat(result.getSymbol()).isEqualTo("AAPL")
        assert result.current_price > 0  # assertThat(result.getCurrentPrice()).isGreaterThan(0)
        assert result.name is not None

    def test_get_stock_info_invalid_symbol(self):
        """Test with invalid stock symbol"""
        # given
        invalid_symbol = "INVALID_SYMBOL_XYZ"

        # when
        result = StockService.get_stock_info(invalid_symbol)

        # then
        assert result is None  # Should return None for invalid symbols

    def test_get_stock_history_success(self):
        """Test getting stock history"""
        # given
        symbol = "AAPL"
        period = "5d"

        # when
        result = StockService.get_stock_history(symbol, period)

        # then
        assert result is not None
        assert result["symbol"] == "AAPL"
        assert result["period"] == "5d"
        assert len(result["data"]) > 0  # Should have data

        # Check first data point structure
        first_data = result["data"][0]
        assert "date" in first_data
        assert "open" in first_data
        assert "close" in first_data
        assert "high" in first_data
        assert "low" in first_data
        assert "volume" in first_data


# pytest fixtures (similar to @BeforeEach in Spring)
@pytest.fixture
def sample_symbol():
    """Fixture to provide sample stock symbol"""
    return "TSLA"


def test_with_fixture(sample_symbol):
    """Test using fixture (like @BeforeEach setup)"""
    # when
    result = StockService.get_stock_info(sample_symbol)

    # then
    assert result is not None
    assert result.symbol == "TSLA"
