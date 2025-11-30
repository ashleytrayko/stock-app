from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """
    Application settings
    Similar to application.properties in Spring Boot
    """

    # Database Configuration
    DB_USER: str = "your_username"
    DB_PASSWORD: str = "your_password"
    DB_HOST: str = "your_oracle_host"
    DB_PORT: int = 1521
    DB_SERVICE_NAME: str = "your_service_name"

    # Application Configuration
    APP_NAME: str = "Stock API"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = True

    @property
    def DATABASE_URL(self) -> str:
        """
        Oracle connection string for Autonomous Database
        """
        # DSN format for Oracle Autonomous Database
        dsn = f"(description=(retry_count=20)(retry_delay=3)(address=(protocol=tcps)(port={self.DB_PORT})(host={self.DB_HOST}))(connect_data=(service_name={self.DB_SERVICE_NAME}))(security=(ssl_server_dn_match=yes)))"
        return f"oracle+oracledb://{self.DB_USER}:{self.DB_PASSWORD}@{dsn}"

    class Config:
        env_file = ".env"
        case_sensitive = True


# Singleton instance
settings = Settings()