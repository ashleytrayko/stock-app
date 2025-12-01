from sqlalchemy import Column, Integer, String, DateTime, Float, Numeric, Sequence
from sqlalchemy.sql import func
from database.db import Base


class Portfolio(Base):
    """
    User's stock portfolio (내 주식 포트폴리오)
    Similar to @Entity in JPA
    """
    __tablename__ = "portfolio"

    # Primary Key (similar to @Id @GeneratedValue)
    id = Column(Integer, Sequence('portfolio_seq'), primary_key=True)

    # Stock symbol (similar to @Column(nullable = false))
    # UNIQUE constraint ensures one portfolio record per symbol
    symbol = Column(String(20), nullable=False, unique=True, index=True)

    # Stock name
    name = Column(String(200), nullable=True)

    # Average purchase price (평균 매수가)
    # This is calculated from all buy transactions
    average_price = Column(Numeric(10, 2), nullable=False)

    # Total quantity (총 보유 수량)
    # This is the sum of all buy transactions minus sell transactions
    quantity = Column(Integer, nullable=False, default=0)

    # User ID (for future user authentication)
    user_id = Column(Integer, nullable=True, index=True)

    # Timestamps (similar to @CreatedDate, @LastModifiedDate)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    def __repr__(self):
        return f"<Portfolio(id={self.id}, symbol={self.symbol}, quantity={self.quantity}, average_price={self.average_price})>"
