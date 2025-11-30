from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from config import settings

# Create database engine
# Similar to DataSource in Spring Boot
engine = create_engine(
    settings.DATABASE_URL,
    echo=settings.DEBUG,  # Log SQL queries (like show-sql in Spring)
    pool_pre_ping=True,   # Check connection health
    pool_size=5,
    max_overflow=10
)

# Create SessionLocal class
# Similar to EntityManager in JPA
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for models
# Similar to @Entity base class
Base = declarative_base()


# Dependency injection for database session
# Similar to @Autowired EntityManager in Spring
def get_db():
    """
    Get database session for dependency injection
    Usage in FastAPI: def endpoint(db: Session = Depends(get_db))
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
