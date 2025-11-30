# Stock Portfolio API

FastAPI 기반 주식 포트폴리오 관리 및 실시간 손익 계산 API

## 기능

- 📈 **실시간 주식 정보 조회** (yfinance)
- 💼 **포트폴리오 관리** (매수 주식 등록/조회/수정/삭제)
- 💰 **실시간 손익 계산** (현재가 기반 자동 계산)
- 🗄️ **Oracle Cloud Database 연동**

## 기술 스택

- **Framework**: FastAPI
- **ORM**: SQLAlchemy
- **Database**: Oracle Autonomous Database
- **Stock Data**: yfinance (Yahoo Finance)
- **Language**: Python 3.12

## 프로젝트 구조

```
stock/
├── main.py              # 앱 진입점
├── config.py            # 설정 파일
├── models/              # Pydantic 모델 (DTO)
│   ├── stock.py
│   └── portfolio.py
├── routers/             # API 엔드포인트
│   ├── stock.py
│   └── portfolio.py
├── services/            # 비즈니스 로직
│   ├── stock_service.py
│   └── portfolio_service.py
└── database/            # DB 관련
    ├── db.py
    └── models.py        # SQLAlchemy 모델
```

## 설치 및 실행

### 1. 가상환경 생성 및 활성화

```bash
# Windows
python -m venv .venv
.venv\Scripts\activate

# Linux/Mac
python -m venv .venv
source .venv/bin/activate
```

### 2. 의존성 설치

```bash
pip install -r requirements.txt
```

### 3. 환경 변수 설정

`.env.example`을 `.env`로 복사하고 DB 정보를 입력하세요:

```bash
cp .env.example .env
```

`.env` 파일 수정:
```
DB_USER=your_db_username
DB_PASSWORD=your_db_password
DB_HOST=your_oracle_host
DB_PORT=1522
DB_SERVICE_NAME=your_service_name
```

### 4. 데이터베이스 테이블 생성

```bash
python -c "from database.db import Base, engine; from database.models import Portfolio; Base.metadata.create_all(bind=engine); print('Tables created!')"
```

Oracle Sequence 생성:
```bash
python -c "from database.db import engine; from sqlalchemy import text; conn = engine.connect(); conn.execute(text('CREATE SEQUENCE portfolio_seq START WITH 1 INCREMENT BY 1')); conn.commit(); print('Sequence created!')"
```

### 5. 서버 실행

```bash
uvicorn main:app --reload
```

서버 실행 후 접속:
- API: http://127.0.0.1:8000
- Swagger UI: http://127.0.0.1:8000/docs
- ReDoc: http://127.0.0.1:8000/redoc

## API 사용 예시

### 주식 정보 조회

```bash
# Apple 주식 정보 조회
curl http://127.0.0.1:8000/stock/AAPL

# Tesla 주식 과거 데이터 (1개월)
curl http://127.0.0.1:8000/stock/TSLA/history?period=1mo
```

### 포트폴리오 관리

```bash
# 포트폴리오 등록 (Apple 10주를 $150에 매수)
curl -X POST "http://127.0.0.1:8000/portfolio/" \
  -H "Content-Type: application/json" \
  -d '{"symbol": "AAPL", "purchase_price": 150.0, "quantity": 10}'

# 전체 포트폴리오 조회
curl http://127.0.0.1:8000/portfolio/

# 실시간 손익 조회
curl http://127.0.0.1:8000/portfolio/profit
```

## 주요 API 엔드포인트

### Stock API
- `GET /stock/{symbol}` - 실시간 주식 정보
- `GET /stock/{symbol}/history` - 과거 주식 데이터

### Portfolio API
- `POST /portfolio/` - 포트폴리오 등록
- `GET /portfolio/` - 전체 포트폴리오 조회
- `GET /portfolio/profit` - 실시간 손익 조회
- `GET /portfolio/{id}` - 개별 포트폴리오 조회
- `GET /portfolio/{id}/profit` - 개별 손익 조회
- `PUT /portfolio/{id}` - 포트폴리오 수정
- `DELETE /portfolio/{id}` - 포트폴리오 삭제

## License

MIT
