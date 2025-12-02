# Feature Ideas for Stock API

프로젝트에 추가할 수 있는 기능 아이디어 모음입니다.

---

## 1. Watchlist (관심 종목) 🌟 추천

**난이도**: ⭐⭐☆☆☆
**실용성**: ⭐⭐⭐⭐⭐
**학습 가치**: CRUD 패턴, 기본 데이터베이스 작업

### API Endpoints
```
GET    /watchlist          - 관심 종목 목록 조회
POST   /watchlist          - 관심 종목 추가
DELETE /watchlist/{symbol} - 관심 종목 삭제
GET    /watchlist/prices   - 관심 종목의 현재가 한번에 조회
```

### 데이터베이스 스키마
```python
class Watchlist(Base):
    __tablename__ = "watchlist"

    id = Column(Integer, primary_key=True, index=True)
    symbol = Column(String(10), nullable=False, unique=True)
    added_date = Column(DateTime, default=datetime.utcnow)
    notes = Column(String(200))  # 메모 (선택)
```

### 구현 순서
1. `models/watchlist.py` - 데이터베이스 모델
2. `schemas/watchlist.py` - Request/Response 모델
3. `services/watchlist_service.py` - 비즈니스 로직
4. `routers/watchlist.py` - API 엔드포인트
5. `main.py` - 라우터 등록
6. `tests/test_watchlist.py` - 테스트 코드

### 배울 수 있는 것
- 기본 CRUD 작업 (Create, Read, Delete)
- 데이터베이스 테이블 생성 및 마이그레이션
- 중복 처리 (이미 있는 종목 추가 시)
- 여러 종목 동시 조회 (병렬 처리)

---

## 2. Stock Comparison (종목 비교)

**난이도**: ⭐⭐☆☆☆
**실용성**: ⭐⭐⭐⭐☆
**학습 가치**: 데이터 처리, 병렬 API 호출

### API Endpoints
```
GET /stock/compare?symbols=GOOGL,AAPL,MSFT
```

### Response Example
```json
{
  "comparison_date": "2025-12-02",
  "stocks": [
    {
      "symbol": "GOOGL",
      "current_price": 315.68,
      "change_percent": 2.5,
      "volume": 25000000,
      "market_cap": 2000000000000
    },
    {
      "symbol": "AAPL",
      "current_price": 283.85,
      "change_percent": -1.2,
      "volume": 50000000,
      "market_cap": 4000000000000
    }
  ]
}
```

### 구현 순서
1. `schemas/stock.py` - StockComparison 모델 추가
2. `services/stock_service.py` - compare_stocks() 메서드 추가
3. `routers/stock.py` - /compare 엔드포인트 추가
4. 병렬 처리: `asyncio.gather()` 활용

### 배울 수 있는 것
- 쿼리 파라미터 배열 처리 (symbols=A,B,C)
- 여러 API 호출 병렬 처리 (asyncio)
- 데이터 정규화 및 비교 로직
- 별도 DB 테이블 불필요 (yfinance만 사용)

---

## 3. Price Alert (가격 알림 설정)

**난이도**: ⭐⭐⭐☆☆
**실용성**: ⭐⭐⭐⭐⭐
**학습 가치**: 조건부 로직, Enum, 상태 관리

### API Endpoints
```
POST   /alert              - 가격 알림 생성
GET    /alert              - 내 알림 목록
GET    /alert/check        - 알림 조건 충족 확인
DELETE /alert/{id}         - 알림 삭제
```

### Request Example
```json
{
  "symbol": "GOOGL",
  "condition": "BELOW",  // ABOVE, BELOW
  "target_price": 300.00,
  "status": "ACTIVE"     // ACTIVE, TRIGGERED, CANCELLED
}
```

### 데이터베이스 스키마
```python
class PriceAlert(Base):
    __tablename__ = "price_alerts"

    id = Column(Integer, primary_key=True)
    symbol = Column(String(10), nullable=False)
    condition = Column(Enum("ABOVE", "BELOW"), nullable=False)
    target_price = Column(Float, nullable=False)
    status = Column(Enum("ACTIVE", "TRIGGERED", "CANCELLED"), default="ACTIVE")
    created_date = Column(DateTime, default=datetime.utcnow)
    triggered_date = Column(DateTime, nullable=True)
```

### 구현 순서
1. Enum 정의 (AlertCondition, AlertStatus)
2. 모델, 스키마, 서비스, 라우터 생성
3. `/alert/check` 엔드포인트: 현재가 조회 후 조건 비교
4. (선택) 백그라운드 작업으로 주기적 체크

### 배울 수 있는 것
- Enum 타입 사용
- 조건부 로직 (if-else)
- 상태 관리 (FSM - Finite State Machine)
- DateTime 처리
- (선택) 백그라운드 작업 (APScheduler)

---

## 4. Technical Indicators (기술적 지표)

**난이도**: ⭐⭐⭐⭐☆
**실용성**: ⭐⭐⭐⭐⭐
**학습 가치**: 수학/통계, pandas, 금융 지표

### API Endpoints
```
GET /stock/{symbol}/sma?period=20   - 단순 이동평균선 (Simple Moving Average)
GET /stock/{symbol}/ema?period=12   - 지수 이동평균선 (Exponential Moving Average)
GET /stock/{symbol}/rsi?period=14   - 상대강도지수 (Relative Strength Index)
GET /stock/{symbol}/macd            - MACD (Moving Average Convergence Divergence)
GET /stock/{symbol}/bollinger       - 볼린저 밴드 (Bollinger Bands)
```

### Response Example (RSI)
```json
{
  "symbol": "GOOGL",
  "indicator": "RSI",
  "period": 14,
  "current_value": 65.4,
  "interpretation": "Neutral",  // Overbought (>70), Oversold (<30), Neutral
  "signal": "HOLD"              // BUY, SELL, HOLD
}
```

### 필요한 라이브러리
```bash
pip install ta-lib  # 또는
pip install pandas-ta
```

### 구현 순서
1. 기술적 지표 라이브러리 설치 (pandas-ta 추천)
2. `services/technical_service.py` 생성
3. 각 지표별 계산 함수 구현
4. 해석 로직 추가 (매수/매도/중립 신호)
5. 라우터 및 스키마 추가

### 배울 수 있는 것
- pandas 데이터 처리
- 금융 수학/통계 이해
- 기술적 분석 개념 (차트 분석)
- 시계열 데이터 처리

---

## 5. Portfolio Statistics (포트폴리오 통계)

**난이도**: ⭐⭐⭐☆☆
**실용성**: ⭐⭐⭐⭐⭐
**학습 가치**: 집계 함수, 금융 지표 계산

### API Endpoints
```
GET /portfolio/stats            - 전체 통계
GET /portfolio/diversification  - 다각화 분석 (섹터별 분포)
GET /portfolio/performance      - 성과 분석 (일간/주간/월간 수익률)
```

### Response Example (stats)
```json
{
  "total_value": 150000.00,
  "total_cost": 100000.00,
  "total_profit": 50000.00,
  "total_profit_percent": 50.0,
  "best_performer": {
    "symbol": "GOOGL",
    "profit_percent": 82.0
  },
  "worst_performer": {
    "symbol": "AAPL",
    "profit_percent": -5.0
  },
  "portfolio_beta": 1.15,      // 시장 대비 변동성
  "sharpe_ratio": 1.8          // 위험 대비 수익률
}
```

### 계산 공식

**베타 (Beta)**
```python
# 포트폴리오의 시장 대비 변동성
# Beta > 1: 시장보다 변동성 큼
# Beta < 1: 시장보다 변동성 작음
beta = covariance(portfolio_returns, market_returns) / variance(market_returns)
```

**샤프 비율 (Sharpe Ratio)**
```python
# 위험 대비 수익률
# Sharpe > 1: 좋음, > 2: 매우 좋음
sharpe_ratio = (portfolio_return - risk_free_rate) / portfolio_std_dev
```

### 구현 순서
1. `services/portfolio_service.py`에 통계 메서드 추가
2. 수익률 계산 (realized + unrealized)
3. 베타, 샤프 비율 계산 (선택)
4. 섹터별 분류 (yfinance의 sector 정보 활용)

### 배울 수 있는 것
- SQL 집계 함수 (SUM, AVG, MAX, MIN, GROUP BY)
- 금융 지표 계산 (베타, 샤프 비율)
- 데이터 분류 및 그룹화
- 통계 분석

---

## 6. News Sentiment Analysis (뉴스 감정 분석 with LLM) 🌟 추천

**난이도**: ⭐⭐⭐⭐☆
**실용성**: ⭐⭐⭐⭐⭐
**학습 가치**: LLM 연동, AI 활용, 감정 분석

### 개요
실시간 뉴스를 가져와 **LLM(Claude, GPT 등)을 활용해 감정 분석**을 수행합니다.
뉴스가 주가에 긍정적인지 부정적인지 자동으로 분석하여 투자 판단을 돕습니다.

### API Endpoints
```
GET /news/{symbol}                    - 종목 관련 뉴스 목록
GET /news/{symbol}/sentiment          - 뉴스 + 감정 분석 결과
GET /news/{symbol}/summary            - 전체 뉴스 종합 의견
POST /news/{symbol}/analyze           - 특정 뉴스 재분석 (캐시 무시)
```

### Response Example (감정 분석 포함)
```json
{
  "symbol": "GOOGL",
  "analysis_date": "2025-12-02T14:30:00Z",
  "overall_sentiment": "POSITIVE",
  "overall_score": 0.65,
  "news": [
    {
      "title": "Google announces breakthrough in quantum computing",
      "summary": "Google reveals new quantum chip that solves problems in minutes...",
      "publisher": "Reuters",
      "publish_date": "2025-12-02T10:00:00Z",
      "url": "https://...",
      "sentiment_analysis": {
        "sentiment": "POSITIVE",
        "confidence": 0.85,
        "score": 0.8,
        "reasoning": "기사는 Google의 기술적 돌파구를 다루고 있으며, '획기적인', '혁신적인' 등 긍정적 표현이 주를 이룹니다. 양자컴퓨팅 분야의 리더십 강화로 장기적 주가에 긍정적 영향 예상됩니다.",
        "key_points": [
          "양자컴퓨팅 기술 혁신",
          "경쟁사 대비 기술적 우위",
          "장기적 성장 가능성"
        ],
        "impact": "SHORT_TERM_POSITIVE",
        "price_impact_estimate": "+2% ~ +5%",
        "investment_recommendation": "매수 고려 (기술적 우위 확대)"
      }
    },
    {
      "title": "Google faces EU antitrust fine",
      "summary": "European regulators impose $500M fine on Google...",
      "publisher": "Bloomberg",
      "publish_date": "2025-12-02T09:30:00Z",
      "url": "https://...",
      "sentiment_analysis": {
        "sentiment": "NEGATIVE",
        "confidence": 0.75,
        "score": 0.3,
        "reasoning": "규제 당국의 벌금 부과는 단기적으로 부정적이나, Google의 재무 상황을 고려하면 큰 영향은 없을 것으로 예상됩니다.",
        "key_points": [
          "EU 규제 강화",
          "$500M 벌금 (매출의 0.2%)",
          "반복적인 규제 리스크"
        ],
        "impact": "SHORT_TERM_NEGATIVE",
        "price_impact_estimate": "-1% ~ -2%",
        "investment_recommendation": "중립 (일시적 약세 후 회복 예상)"
      }
    }
  ],
  "summary": {
    "total_articles": 10,
    "positive_count": 6,
    "neutral_count": 2,
    "negative_count": 2,
    "overall_recommendation": "매수",
    "confidence": "HIGH",
    "rationale": "긍정적 뉴스가 압도적으로 많으며, 특히 기술 혁신 관련 소식이 주를 이룹니다. 단기 규제 리스크는 있으나 장기적으로 긍정적 전망입니다."
  }
}
```

### 구현 아키텍처

```
┌─────────────┐
│   Client    │
└──────┬──────┘
       │ GET /news/GOOGL/sentiment
       ↓
┌─────────────────────┐
│   FastAPI Server    │
│  (News Router)      │
└──────┬──────────────┘
       │
       ↓
┌─────────────────────┐
│  News Service       │
│  1. Fetch News      │ ← yfinance
│  2. Call LLM        │ ← Anthropic/OpenAI API
│  3. Parse Result    │
└─────────────────────┘
```

### 구현 코드 예시

#### 1. 뉴스 가져오기
```python
import yfinance as yf

def get_news(symbol: str, limit: int = 10):
    ticker = yf.Ticker(symbol)
    news = ticker.news[:limit]

    parsed_news = []
    for article in news:
        content = article.get('content', {})
        parsed_news.append({
            'title': content.get('title'),
            'summary': content.get('summary'),
            'publisher': content.get('provider', {}).get('displayName'),
            'publish_date': content.get('pubDate'),
            'url': content.get('canonicalUrl', {}).get('url')
        })

    return parsed_news
```

#### 2. LLM 감정 분석 (Claude API)
```python
import anthropic

def analyze_sentiment_with_claude(news_item: dict, symbol: str) -> dict:
    client = anthropic.Anthropic(api_key=settings.ANTHROPIC_API_KEY)

    prompt = f"""
다음 뉴스 기사를 분석하고 {symbol} 주식에 미칠 영향을 평가해주세요.

제목: {news_item['title']}
요약: {news_item['summary']}
출처: {news_item['publisher']}

다음 형식의 JSON으로 답변해주세요:
{{
  "sentiment": "POSITIVE | NEGATIVE | NEUTRAL",
  "confidence": 0.0 ~ 1.0,
  "score": 0.0 ~ 1.0,
  "reasoning": "분석 이유 (한국어 200자 이내)",
  "key_points": ["핵심 포인트 1", "핵심 포인트 2", "핵심 포인트 3"],
  "impact": "SHORT_TERM_POSITIVE | SHORT_TERM_NEGATIVE | LONG_TERM_POSITIVE | LONG_TERM_NEGATIVE | NEUTRAL",
  "price_impact_estimate": "예상 주가 변동 범위",
  "investment_recommendation": "투자 의견 (매수/중립/매도)"
}}

분석 시 고려사항:
- 기사의 톤 (긍정적/부정적)
- 주요 키워드 및 수치
- 업계 영향도
- 단기/장기 영향 구분
"""

    response = client.messages.create(
        model="claude-3-5-sonnet-20241022",
        max_tokens=2048,
        messages=[{"role": "user", "content": prompt}]
    )

    # JSON 파싱
    import json
    result = json.loads(response.content[0].text)
    return result
```

#### 3. 전체 뉴스 종합 분석
```python
def summarize_all_news(analyses: list, symbol: str) -> dict:
    prompt = f"""
다음은 {symbol} 종목의 최근 뉴스 {len(analyses)}개에 대한 감정 분석 결과입니다.

{json.dumps(analyses, ensure_ascii=False, indent=2)}

전체 뉴스를 종합하여 다음을 분석해주세요:
1. 전체적인 시장 분위기 (긍정/중립/부정)
2. 투자 추천 (매수/중립/매도)
3. 신뢰도 (HIGH/MEDIUM/LOW)
4. 종합 의견 (200자 이내)

JSON 형식으로 답변해주세요.
"""

    # Claude API 호출...
    return summary
```

### 필요한 설정

#### 1. 환경 변수 (.env)
```bash
# Claude API (추천)
ANTHROPIC_API_KEY=sk-ant-xxxxx

# 또는 OpenAI API
OPENAI_API_KEY=sk-xxxxx

# LLM 설정
LLM_PROVIDER=anthropic  # anthropic 또는 openai
LLM_MODEL=claude-3-5-sonnet-20241022
```

#### 2. 라이브러리 설치
```bash
# Claude API
pip install anthropic

# 또는 OpenAI API
pip install openai
```

### 구현 순서
1. `config.py`에 API 키 설정 추가
2. `services/news_service.py` 생성
   - `get_news()` - yfinance로 뉴스 가져오기
   - `analyze_sentiment()` - LLM으로 감정 분석
   - `summarize_news()` - 전체 뉴스 종합
3. `schemas/news.py` - Request/Response 모델
4. `routers/news.py` - API 엔드포인트
5. `main.py` - 라우터 등록
6. (선택) 캐싱 추가 - 같은 뉴스 중복 분석 방지

### 고급 기능 추가

#### 1. 감정 점수 히스토리
```python
# 날짜별 감정 점수 추이 추적
GET /news/{symbol}/sentiment-history?days=30
```

#### 2. 실시간 뉴스 알림
```python
# 부정적 뉴스 발생 시 자동 알림
POST /alert/news-sentiment
{
  "symbol": "GOOGL",
  "condition": "NEGATIVE",
  "threshold": 0.3
}
```

#### 3. 포트폴리오 전체 뉴스 분석
```python
GET /portfolio/news-sentiment
# 보유한 모든 종목의 뉴스를 한번에 분석
```

### 배울 수 있는 것
- **LLM API 연동** (Claude/GPT)
- **프롬프트 엔지니어링** (효과적인 질문 작성)
- **JSON 구조화된 출력** 처리
- **외부 API 데이터 가공**
- **캐싱 전략** (중복 분석 방지)
- **비동기 처리** (여러 뉴스 동시 분석)
- **실용적인 AI 활용**

### 예상 비용

#### Claude API (Anthropic)
- Claude 3.5 Sonnet: $3 / 1M input tokens, $15 / 1M output tokens
- 뉴스 1개 분석: 약 500 input + 300 output tokens
- **비용: 약 $0.006 per article (약 8원)**
- 하루 100개 뉴스 분석: 약 $0.60 (약 800원)

#### OpenAI API
- GPT-4o: $2.50 / 1M input tokens, $10 / 1M output tokens
- **비용: 약 $0.004 per article (약 5.5원)**

### 실제 활용 예시

```bash
# 1. GOOGL 뉴스 감정 분석
curl http://localhost:8000/news/GOOGL/sentiment

# 2. 포트폴리오 전체 뉴스 분석
curl http://localhost:8000/portfolio/news-sentiment

# 3. 특정 뉴스 재분석
curl -X POST http://localhost:8000/news/GOOGL/analyze \
  -H "Content-Type: application/json" \
  -d '{"url": "https://..."}'
```

### 주의사항
1. **API 키 보안**: `.env` 파일은 절대 Git에 커밋하지 말 것
2. **Rate Limiting**: API 호출 제한 고려 (캐싱 필수)
3. **비용 관리**: 무제한 분석 시 비용 증가 가능
4. **정확도**: LLM의 분석은 참고용, 투자 결정은 본인 책임

---

## 7. Dividend Tracker (배당금 추적)

**난이도**: ⭐⭐☆☆☆
**실용성**: ⭐⭐⭐☆☆
**학습 가치**: 금융 개념, 날짜 계산

### API Endpoints
```
GET /stock/{symbol}/dividends      - 배당 이력
GET /portfolio/dividend-income     - 포트폴리오 예상 배당 수익
```

### Response Example
```json
{
  "symbol": "AAPL",
  "dividend_yield": 0.52,  // 배당 수익률 (%)
  "annual_dividend": 0.96,
  "dividend_history": [
    {
      "date": "2025-11-08",
      "amount": 0.24
    }
  ],
  "next_ex_dividend_date": "2026-02-07",
  "estimated_annual_income": 48.00  // 보유 주식 50주 * $0.96
}
```

### 구현 방법
```python
ticker = yf.Ticker("AAPL")
dividends = ticker.dividends  # 배당 이력
dividend_yield = ticker.info.get('dividendYield')
```

---

## 추천 구현 순서

### 초보자 학습용
1. **Watchlist** - CRUD 기본 패턴 익히기
2. **Stock Comparison** - 데이터 처리 연습
3. **News Integration** - 외부 API 연동
4. **Dividend Tracker** - 금융 개념 학습

### 실용성 중심
1. **Price Alert** - 실제 사용 가치 높음
2. **Portfolio Statistics** - 투자 인사이트 제공
3. **Technical Indicators** - 매매 판단 도구
4. **Watchlist** - 관심 종목 관리

---

## 참고 자료

### 필요한 Python 라이브러리
```bash
# 기술적 지표
pip install pandas-ta

# 백그라운드 작업
pip install apscheduler

# 데이터 분석
pip install numpy scipy
```

### 학습 자료
- yfinance 문서: https://pypi.org/project/yfinance/
- FastAPI 문서: https://fastapi.tiangolo.com/
- SQLAlchemy 문서: https://docs.sqlalchemy.org/
- pandas 문서: https://pandas.pydata.org/docs/

---

## 8. Stock Screener (종목 스크리너)

**난이도**: ⭐⭐⭐☆☆
**실용성**: ⭐⭐⭐⭐⭐
**학습 가치**: 복잡한 필터링, 쿼리 최적화

### API Endpoints
```
POST /screener/scan - 조건으로 종목 검색
GET  /screener/presets - 사전 정의된 스크린 (성장주, 가치주 등)
```

### Request Example
```json
{
  "filters": {
    "market_cap_min": 1000000000,     // 시가총액 10억 이상
    "pe_ratio_max": 15,                // PER 15 이하
    "dividend_yield_min": 2.0,         // 배당률 2% 이상
    "volume_min": 1000000,             // 거래량 100만주 이상
    "price_change_percent_min": 5.0,   // 오늘 상승률 5% 이상
    "sector": "Technology"             // 기술주
  },
  "sort_by": "market_cap",
  "order": "desc",
  "limit": 50
}
```

### Response Example
```json
{
  "total_matches": 23,
  "stocks": [
    {
      "symbol": "AAPL",
      "name": "Apple Inc.",
      "market_cap": 4000000000000,
      "pe_ratio": 28.5,
      "dividend_yield": 0.52,
      "price": 283.85,
      "change_percent": 2.3,
      "sector": "Technology"
    }
  ]
}
```

### 구현 방법
```python
# 미리 정의된 종목 리스트 사용 (S&P 500 등)
sp500_symbols = [...list of 500 symbols...]

# 각 종목 필터링
for symbol in sp500_symbols:
    ticker = yf.Ticker(symbol)
    info = ticker.info

    # 조건 체크
    if (info['marketCap'] >= filters['market_cap_min'] and
        info['trailingPE'] <= filters['pe_ratio_max']):
        matches.append(symbol)
```

### 배울 수 있는 것
- 복잡한 필터링 로직
- 동적 쿼리 생성
- 대량 데이터 처리 최적화
- 캐싱 전략

---

## 9. Backtesting (백테스팅)

**난이도**: ⭐⭐⭐⭐⭐
**실용성**: ⭐⭐⭐⭐⭐
**학습 가치**: 알고리즘, 시뮬레이션, 성과 분석

### API Endpoints
```
POST /backtest/strategy - 전략 백테스트 실행
GET  /backtest/{id}     - 백테스트 결과 조회
```

### Request Example
```json
{
  "symbol": "AAPL",
  "start_date": "2024-01-01",
  "end_date": "2025-12-01",
  "initial_capital": 10000,
  "strategy": {
    "type": "SMA_CROSSOVER",  // 이동평균선 교차 전략
    "short_period": 20,
    "long_period": 50
  }
}
```

### Response Example
```json
{
  "backtest_id": "bt_123",
  "symbol": "AAPL",
  "period": "2024-01-01 to 2025-12-01",
  "initial_capital": 10000,
  "final_value": 12500,
  "total_return": 25.0,
  "total_return_percent": 25.0,
  "total_trades": 15,
  "winning_trades": 9,
  "losing_trades": 6,
  "win_rate": 60.0,
  "max_drawdown": -8.5,
  "sharpe_ratio": 1.45,
  "trades": [
    {
      "date": "2024-02-15",
      "action": "BUY",
      "price": 180.50,
      "shares": 50,
      "value": 9025.00
    }
  ]
}
```

### 구현 순서
1. 과거 데이터 가져오기 (yfinance)
2. 전략 로직 구현 (SMA, RSI 등)
3. 시뮬레이션 엔진 (매수/매도 판단)
4. 성과 지표 계산
5. 결과 저장 및 반환

### 배울 수 있는 것
- 알고리즘 트레이딩 기초
- 시뮬레이션 로직
- 성과 측정 (샤프 비율, 최대 낙폭 등)
- 데이터 분석 및 통계

---

## 10. CSV Import/Export (데이터 가져오기/내보내기)

**난이도**: ⭐⭐☆☆☆
**실용성**: ⭐⭐⭐⭐⭐
**학습 가치**: 파일 처리, 데이터 변환

### API Endpoints
```
POST /portfolio/import - CSV에서 거래 내역 가져오기
GET  /portfolio/export - 포트폴리오를 CSV로 내보내기
GET  /transaction/export - 거래 내역을 CSV로 내보내기
```

### Import CSV 형식
```csv
date,symbol,type,price,quantity
2024-11-01,GOOGL,BUY,170.00,10
2024-11-02,AAPL,BUY,180.00,5
2024-11-15,GOOGL,SELL,175.00,5
```

### 구현 예시
```python
import pandas as pd
from fastapi import UploadFile

@router.post("/portfolio/import")
async def import_transactions(file: UploadFile):
    # CSV 읽기
    df = pd.read_csv(file.file)

    # 데이터 검증
    required_columns = ['date', 'symbol', 'type', 'price', 'quantity']
    if not all(col in df.columns for col in required_columns):
        raise HTTPException(400, "Invalid CSV format")

    # DB에 저장
    for _, row in df.iterrows():
        transaction = Transaction(
            symbol=row['symbol'],
            transaction_type=row['type'],
            price=row['price'],
            quantity=row['quantity'],
            transaction_date=pd.to_datetime(row['date'])
        )
        db.add(transaction)

    db.commit()
    return {"imported": len(df)}
```

### 배울 수 있는 것
- 파일 업로드 처리
- pandas로 CSV 처리
- 데이터 검증 및 변환
- 대량 데이터 삽입

---

## 11. Paper Trading (모의 거래)

**난이도**: ⭐⭐⭐⭐☆
**실용성**: ⭐⭐⭐⭐⭐
**학습 가치**: 실시간 처리, 상태 관리, 게임화

### API Endpoints
```
POST /paper/account/create    - 모의 계좌 생성
GET  /paper/account           - 계좌 정보
POST /paper/order             - 모의 주문
GET  /paper/orders            - 주문 내역
GET  /paper/leaderboard       - 리더보드 (수익률 순위)
```

### Request Example (모의 주문)
```json
{
  "symbol": "GOOGL",
  "order_type": "MARKET",  // MARKET, LIMIT
  "side": "BUY",
  "quantity": 10,
  "limit_price": 310.00    // LIMIT 주문시만
}
```

### 데이터베이스 스키마
```python
class PaperAccount(Base):
    __tablename__ = "paper_accounts"

    id = Column(Integer, primary_key=True)
    user_id = Column(String(50), unique=True)  # 사용자 식별
    cash_balance = Column(Float, default=100000.0)  # 초기 자본
    total_value = Column(Float)
    created_date = Column(DateTime, default=datetime.utcnow)

class PaperOrder(Base):
    __tablename__ = "paper_orders"

    id = Column(Integer, primary_key=True)
    account_id = Column(Integer, ForeignKey("paper_accounts.id"))
    symbol = Column(String(10))
    order_type = Column(Enum("MARKET", "LIMIT"))
    side = Column(Enum("BUY", "SELL"))
    quantity = Column(Integer)
    price = Column(Float)
    status = Column(Enum("PENDING", "FILLED", "CANCELLED"))
    created_date = Column(DateTime)
    filled_date = Column(DateTime, nullable=True)
```

### 배울 수 있는 것
- 주문 처리 로직
- 실시간 가격 처리
- 계좌 잔고 관리
- 리더보드 구현 (랭킹)

---

## 12. Multi-Portfolio Support (다중 포트폴리오)

**난이도**: ⭐⭐⭐☆☆
**실용성**: ⭐⭐⭐⭐☆
**학습 가치**: 데이터 모델링, 권한 관리

### API Endpoints
```
POST   /portfolio/create          - 포트폴리오 생성
GET    /portfolio/list            - 내 포트폴리오 목록
GET    /portfolio/{id}            - 특정 포트폴리오 조회
DELETE /portfolio/{id}            - 포트폴리오 삭제
POST   /portfolio/{id}/transfer   - 포트폴리오간 이동
```

### 사용 시나리오
```
- "장기 투자" 포트폴리오
- "단기 트레이딩" 포트폴리오
- "배당주" 포트폴리오
- "암호화폐" 포트폴리오
```

### 데이터베이스 수정
```python
class Portfolio(Base):
    __tablename__ = "portfolios"

    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    description = Column(String(500))
    created_date = Column(DateTime)

class PortfolioHolding(Base):
    __tablename__ = "portfolio_holdings"

    id = Column(Integer, primary_key=True)
    portfolio_id = Column(Integer, ForeignKey("portfolios.id"))
    symbol = Column(String(10))
    quantity = Column(Integer)
    average_price = Column(Float)
```

### 배울 수 있는 것
- 외래 키 관계 (Foreign Key)
- 데이터 격리 (Data Isolation)
- 집계 쿼리 (Portfolio별 통계)

---

## 13. Correlation Analysis (상관관계 분석)

**난이도**: ⭐⭐⭐⭐☆
**실용성**: ⭐⭐⭐⭐☆
**학습 가치**: 통계, 데이터 사이언스

### API Endpoints
```
GET /analysis/correlation?symbols=GOOGL,AAPL,MSFT&period=1y
GET /portfolio/correlation  - 포트폴리오 내 상관관계
```

### Response Example
```json
{
  "period": "1y",
  "correlation_matrix": {
    "GOOGL": {
      "GOOGL": 1.0,
      "AAPL": 0.75,
      "MSFT": 0.82
    },
    "AAPL": {
      "GOOGL": 0.75,
      "AAPL": 1.0,
      "MSFT": 0.68
    },
    "MSFT": {
      "GOOGL": 0.82,
      "AAPL": 0.68,
      "MSFT": 1.0
    }
  },
  "interpretation": {
    "GOOGL-MSFT": "High correlation (0.82) - tend to move together",
    "AAPL-MSFT": "Moderate correlation (0.68)"
  }
}
```

### 구현 방법
```python
import numpy as np
import pandas as pd

# 각 종목의 수익률 계산
returns = {}
for symbol in symbols:
    hist = yf.Ticker(symbol).history(period=period)
    returns[symbol] = hist['Close'].pct_change()

# 상관관계 매트릭스 계산
df = pd.DataFrame(returns)
correlation_matrix = df.corr()
```

### 배울 수 있는 것
- 통계적 상관관계
- numpy/pandas 활용
- 포트폴리오 리스크 분석
- 데이터 시각화 준비

---

## 14. Rebalancing Recommendations (리밸런싱 추천)

**난이도**: ⭐⭐⭐⭐☆
**실용성**: ⭐⭐⭐⭐⭐
**학습 가치**: 최적화 알고리즘, 금융 전략

### API Endpoints
```
POST /portfolio/rebalance - 리밸런싱 제안
```

### Request Example
```json
{
  "target_allocation": {
    "GOOGL": 40,  // 40%
    "AAPL": 30,   // 30%
    "MSFT": 20,   // 20%
    "CASH": 10    // 10%
  }
}
```

### Response Example
```json
{
  "current_allocation": {
    "GOOGL": 50,
    "AAPL": 30,
    "MSFT": 15,
    "CASH": 5
  },
  "target_allocation": {
    "GOOGL": 40,
    "AAPL": 30,
    "MSFT": 20,
    "CASH": 10
  },
  "recommendations": [
    {
      "symbol": "GOOGL",
      "action": "SELL",
      "quantity": 5,
      "reason": "Overweight by 10%"
    },
    {
      "symbol": "MSFT",
      "action": "BUY",
      "quantity": 3,
      "reason": "Underweight by 5%"
    }
  ],
  "estimated_cost": 150.00  // 거래 수수료
}
```

### 배울 수 있는 것
- 포트폴리오 최적화
- 자산 배분 전략
- 수학적 최적화
- 실용적인 금융 조언

---

## 15. WebSocket for Real-time Updates (실시간 업데이트)

**난이도**: ⭐⭐⭐⭐☆
**실용성**: ⭐⭐⭐⭐⭐
**학습 가치**: WebSocket, 실시간 통신, 이벤트 기반

### WebSocket Endpoints
```
WS /ws/price/{symbol}      - 실시간 주가
WS /ws/portfolio           - 포트폴리오 실시간 업데이트
WS /ws/alerts              - 가격 알림 실시간 푸시
```

### 구현 예시
```python
from fastapi import WebSocket

@app.websocket("/ws/price/{symbol}")
async def websocket_price(websocket: WebSocket, symbol: str):
    await websocket.accept()

    while True:
        # 현재가 가져오기
        ticker = yf.Ticker(symbol)
        price = ticker.history(period='1d')['Close'].iloc[-1]

        # 클라이언트에 전송
        await websocket.send_json({
            "symbol": symbol,
            "price": price,
            "timestamp": datetime.now().isoformat()
        })

        await asyncio.sleep(5)  # 5초마다 업데이트
```

### 클라이언트 예시 (JavaScript)
```javascript
const ws = new WebSocket('ws://localhost:8000/ws/price/GOOGL');

ws.onmessage = (event) => {
  const data = JSON.parse(event.data);
  console.log(`${data.symbol}: $${data.price}`);
};
```

### 배울 수 있는 것
- WebSocket 프로토콜
- 양방향 실시간 통신
- 이벤트 기반 아키텍처
- 비동기 프로그래밍

---

## 16. Tax Reporting (세금 보고)

**난이도**: ⭐⭐⭐☆☆
**실용성**: ⭐⭐⭐⭐⭐
**학습 가치**: 비즈니스 로직, 복잡한 계산

### API Endpoints
```
GET /tax/gains?year=2025           - 연간 양도소득 계산
GET /tax/report?year=2025          - 세금 보고서
GET /tax/lots/{symbol}             - 세금 로트 (FIFO/LIFO)
```

### Response Example
```json
{
  "year": 2025,
  "total_realized_gains": 5000.00,
  "total_realized_losses": -1000.00,
  "net_capital_gains": 4000.00,
  "short_term_gains": 2000.00,   // 보유 1년 미만
  "long_term_gains": 2000.00,    // 보유 1년 이상
  "tax_lots": [
    {
      "symbol": "GOOGL",
      "purchase_date": "2024-11-01",
      "sale_date": "2025-03-15",
      "quantity": 5,
      "cost_basis": 850.00,
      "proceeds": 900.00,
      "gain_loss": 50.00,
      "term": "SHORT"
    }
  ]
}
```

### 계산 방법
```python
# FIFO (First In, First Out)
# 먼저 산 주식을 먼저 판 것으로 간주

# 양도소득 = 매도가 - 취득가
realized_gain = sale_price * quantity - cost_basis
```

### 배울 수 있는 것
- 복잡한 비즈니스 로직
- 날짜 계산 (보유 기간)
- FIFO/LIFO 알고리즘
- 실제 금융 서비스 구현

---

## 고급 기능 추천 순서

### 즉시 구현 가능 (쉬움)
1. **CSV Import/Export** - 파일 처리 연습
2. **News Integration** - 이미 yfinance에 내장
3. **Dividend Tracker** - 간단한 데이터 조회

### 중급 학습용
4. **Stock Screener** - 복잡한 필터링
5. **Multi-Portfolio** - 데이터 모델링
6. **Correlation Analysis** - 통계 분석

### 고급/프로젝트 확장
7. **Paper Trading** - 게임화, 재미
8. **Backtesting** - 알고리즘 트레이딩
9. **WebSocket** - 실시간 기능
10. **Rebalancing** - 최적화 알고리즘

### 실전/상용화
11. **Tax Reporting** - 실용적 비즈니스 로직

---

## 추가 아이디어

### 17. 소셜 기능
- 포트폴리오 공유 (SNS 공유)
- 다른 사람의 포트폴리오 팔로우
- 투자 아이디어 커뮤니티

### 18. 모바일 앱 연동
- REST API를 활용한 모바일 앱
- Push 알림 (가격 알림)

### 19. 머신러닝 예측
- 주가 예측 모델
- 추천 시스템 (어떤 주식 살까?)

### 20. 게이미피케이션
- 배지 시스템 (첫 거래, 100% 수익 등)
- 레벨 시스템
- 일일 퀘스트

---

**마지막 업데이트**: 2025-12-02
**프로젝트 버전**: 2.0.0
