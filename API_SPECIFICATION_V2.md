# Stock Portfolio API 명세서 v2.0

## 주요 변경사항 (v2.0)

**거래 내역 추적 시스템 추가**
- 실제 증권 앱처럼 매수/매도 거래를 기록
- 평균 단가 자동 계산
- 같은 종목을 여러 번 매수하면 자동으로 평균 단가 갱신
- 매도 시 보유 수량 검증

**권장 사용 방법**:
- ✅ `POST /transaction/` - 매수/매도 등록 (권장)
- ⚠️ `POST /portfolio/` - 직접 포트폴리오 생성 (비권장, 하위 호환용)

---

## Base URL
```
http://127.0.0.1:8000
```

## 공통 사항

### Response Format
- 모든 응답은 JSON 형식
- 날짜/시간은 ISO 8601 형식 (`2024-01-01T12:00:00`)
- 금액은 소수점 2자리까지 표시

### Error Response
```json
{
  "detail": "에러 메시지"
}
```

### HTTP Status Codes
- `200 OK` - 성공
- `201 Created` - 생성 성공
- `400 Bad Request` - 잘못된 요청 (예: 보유 수량보다 많이 매도)
- `404 Not Found` - 리소스 없음
- `500 Internal Server Error` - 서버 오류

---

## 1. Transaction API (거래 내역) 🆕

### 1.1 거래 생성 (매수/매도)

**POST** `/transaction/`

주식을 매수하거나 매도합니다. **가장 권장되는 방법입니다.**

#### Request Body (매수)
```json
{
  "symbol": "AAPL",
  "transaction_type": "BUY",
  "price": 180.50,
  "quantity": 10,
  "transaction_date": "2024-12-01T10:30:00"
}
```

#### Request Body (매도)
```json
{
  "symbol": "AAPL",
  "transaction_type": "SELL",
  "price": 185.00,
  "quantity": 5
}
```

#### Request Fields
| 필드 | 타입 | 필수 | 제약 조건 | 설명 |
|------|------|------|-----------|------|
| symbol | string | Y | - | 주식 심볼 |
| transaction_type | string | Y | "BUY" or "SELL" | 거래 유형 |
| price | float | Y | > 0 | 거래 단가 |
| quantity | int | Y | > 0 | 수량 |
| transaction_date | datetime | N | - | 거래 일시 (기본값: 현재 시간) |

#### Response (201 Created)
```json
{
  "id": 1,
  "symbol": "AAPL",
  "transaction_type": "BUY",
  "price": 180.50,
  "quantity": 10,
  "transaction_date": "2024-12-01T10:30:00",
  "created_at": "2024-12-01T10:30:00"
}
```

#### 동작 방식

**매수 (BUY) 시**:
1. 거래 기록 생성
2. 포트폴리오 업데이트:
   - 해당 종목이 없으면 새로 생성
   - 있으면 평균 단가 재계산 및 수량 증가

**평균 단가 계산 예시**:
```
기존: AAPL 10주, 평균 150달러 (총 1500달러)
추가 매수: AAPL 5주, 180달러 (총 900달러)
→ 새로운 평균: (1500 + 900) / (10 + 5) = 160달러, 15주
```

**매도 (SELL) 시**:
1. 보유 수량 검증 (부족하면 400 에러)
2. 거래 기록 생성
3. 포트폴리오 업데이트: 수량 차감 (평균 단가는 유지)

#### Error Response (400 - 매도 수량 부족)
```json
{
  "detail": "Cannot sell 20 shares of AAPL: Only 15 shares available"
}
```

#### Error Response (400 - 포트폴리오 없음)
```json
{
  "detail": "Cannot sell AAPL: No portfolio found"
}
```

---

### 1.2 거래 내역 조회

**GET** `/transaction/`

모든 거래 내역을 조회합니다. 필터링 가능.

#### Query Parameters
| 이름 | 타입 | 필수 | 기본값 | 설명 |
|------|------|------|--------|------|
| symbol | string | N | - | 특정 종목만 필터링 |
| transaction_type | string | N | - | BUY 또는 SELL만 필터링 |
| limit | int | N | 100 | 최대 결과 수 (1-500) |

#### Response (200 OK)
```json
[
  {
    "id": 2,
    "symbol": "AAPL",
    "transaction_type": "BUY",
    "price": 180.50,
    "quantity": 5,
    "transaction_date": "2024-12-01T14:00:00",
    "created_at": "2024-12-01T14:00:00"
  },
  {
    "id": 1,
    "symbol": "AAPL",
    "transaction_type": "BUY",
    "price": 150.00,
    "quantity": 10,
    "transaction_date": "2024-11-01T10:00:00",
    "created_at": "2024-11-01T10:00:00"
  }
]
```

**정렬**: 최신 거래가 먼저 나옴 (transaction_date DESC)

#### 예시
- 전체 조회: `GET /transaction/`
- AAPL만 조회: `GET /transaction/?symbol=AAPL`
- 매수만 조회: `GET /transaction/?transaction_type=BUY`
- AAPL 매도만 10개: `GET /transaction/?symbol=AAPL&transaction_type=SELL&limit=10`

---

### 1.3 개별 거래 조회

**GET** `/transaction/{transaction_id}`

특정 거래를 ID로 조회합니다.

#### Path Parameters
| 이름 | 타입 | 필수 | 설명 |
|------|------|------|------|
| transaction_id | int | Y | 거래 ID |

#### Response (200 OK)
```json
{
  "id": 1,
  "symbol": "AAPL",
  "transaction_type": "BUY",
  "price": 180.50,
  "quantity": 10,
  "transaction_date": "2024-12-01T10:30:00",
  "created_at": "2024-12-01T10:30:00"
}
```

---

### 1.4 거래 요약 조회

**GET** `/transaction/summary/{symbol}`

특정 종목의 거래 통계를 조회합니다.

#### Path Parameters
| 이름 | 타입 | 필수 | 설명 |
|------|------|------|------|
| symbol | string | Y | 주식 심볼 |

#### Response (200 OK)
```json
{
  "symbol": "AAPL",
  "total_bought": 15,
  "total_sold": 5,
  "current_quantity": 10,
  "average_buy_price": 162.50,
  "total_transactions": 3
}
```

#### Response Fields
| 필드 | 타입 | 설명 |
|------|------|------|
| symbol | string | 주식 심볼 |
| total_bought | int | 총 매수 수량 |
| total_sold | int | 총 매도 수량 |
| current_quantity | int | 현재 보유 수량 (매수 - 매도) |
| average_buy_price | float | 평균 매수가 |
| total_transactions | int | 총 거래 횟수 |

---

### 1.5 거래 삭제

**DELETE** `/transaction/{transaction_id}`

거래를 삭제합니다.

⚠️ **주의**: 이 API는 포트폴리오를 자동으로 재계산하지 않습니다. 실수로 잘못 등록한 거래를 삭제하는 용도로만 사용하세요.

#### Path Parameters
| 이름 | 타입 | 필수 | 설명 |
|------|------|------|------|
| transaction_id | int | Y | 거래 ID |

#### Response (200 OK)
```json
{
  "message": "Transaction deleted successfully"
}
```

---

## 2. Stock API (주식 정보)

### 2.1 주식 정보 조회

**GET** `/stock/{symbol}`

실시간(15-20분 지연) 주식 정보를 조회합니다.

*(v1.0과 동일, 상세 내용 생략)*

---

### 2.2 주식 과거 데이터 조회

**GET** `/stock/{symbol}/history`

주식의 과거 가격 데이터를 조회합니다.

*(v1.0과 동일, 상세 내용 생략)*

---

## 3. Portfolio API (포트폴리오 요약)

**중요**: v2.0에서 포트폴리오는 **거래 내역의 요약**입니다.
- 직접 포트폴리오를 생성/수정하는 것보다 **Transaction API 사용을 권장**합니다.
- Portfolio API는 주로 **조회 용도**로 사용하세요.

### 3.1 포트폴리오 생성

**POST** `/portfolio/`

⚠️ **Deprecated**: `POST /transaction/` 사용을 권장합니다.

직접 포트폴리오 항목을 생성합니다. 하위 호환성을 위해 유지됩니다.

#### Request Body
```json
{
  "symbol": "AAPL",
  "average_price": 160.00,
  "quantity": 15
}
```

**참고**: `purchase_price` → `average_price`로 변경되었습니다.

---

### 3.2 모든 포트폴리오 조회

**GET** `/portfolio/`

보유 중인 모든 주식 요약을 조회합니다.

#### Response (200 OK)
```json
[
  {
    "id": 1,
    "symbol": "AAPL",
    "name": "Apple Inc.",
    "average_price": 160.00,
    "quantity": 15,
    "created_at": "2024-11-01T10:00:00",
    "updated_at": "2024-12-01T14:00:00"
  }
]
```

**변경사항**: `purchase_price` → `average_price`

---

### 3.3 손익 포함 전체 포트폴리오 조회

**GET** `/portfolio/profit`

모든 보유 주식의 현재가와 손익을 계산하여 조회합니다.

#### Response (200 OK)
```json
[
  {
    "id": 1,
    "symbol": "AAPL",
    "name": "Apple Inc.",
    "average_price": 160.00,
    "quantity": 15,
    "current_price": 182.52,
    "total_cost": 2400.00,
    "current_value": 2737.80,
    "profit_loss": 337.80,
    "profit_loss_percent": 14.08,
    "created_at": "2024-11-01T10:00:00"
  }
]
```

**계산 방식**:
- `total_cost` = average_price × quantity
- `current_value` = current_price × quantity
- `profit_loss` = current_value - total_cost
- `profit_loss_percent` = (profit_loss / total_cost) × 100

---

### 3.4 개별 포트폴리오 조회

**GET** `/portfolio/{portfolio_id}`

특정 포트폴리오를 조회합니다.

*(필드명 변경: purchase_price → average_price)*

---

### 3.5 개별 포트폴리오 손익 조회

**GET** `/portfolio/{portfolio_id}/profit`

특정 포트폴리오의 현재가와 손익을 계산하여 조회합니다.

*(필드명 변경: purchase_price → average_price)*

---

### 3.6 포트폴리오 수정

**PUT** `/portfolio/{portfolio_id}`

⚠️ **Deprecated**: `POST /transaction/` 사용을 권장합니다.

직접 포트폴리오를 수정합니다.

#### Request Body
```json
{
  "average_price": 165.00,
  "quantity": 20
}
```

**참고**: `purchase_price` → `average_price`로 변경

---

### 3.7 포트폴리오 삭제

**DELETE** `/portfolio/{portfolio_id}`

보유 주식을 삭제합니다.

*(v1.0과 동일)*

---

## 4. 데이터 모델

### 4.1 Transaction (거래 내역) 🆕
```typescript
{
  id: number;
  symbol: string;
  transaction_type: "BUY" | "SELL";
  price: number;
  quantity: number;
  transaction_date: string;  // ISO 8601 format
  created_at: string;  // ISO 8601 format
}
```

### 4.2 TransactionSummary (거래 요약) 🆕
```typescript
{
  symbol: string;
  total_bought: number;
  total_sold: number;
  current_quantity: number;
  average_buy_price: number | null;
  total_transactions: number;
}
```

### 4.3 Portfolio (포트폴리오) - Updated
```typescript
{
  id: number;
  symbol: string;
  name: string | null;
  average_price: number;  // ⚠️ Changed from purchase_price
  quantity: number;
  created_at: string;
  updated_at: string | null;
}
```

### 4.4 PortfolioWithProfit (손익 포함) - Updated
```typescript
{
  id: number;
  symbol: string;
  name: string | null;
  average_price: number;  // ⚠️ Changed from purchase_price
  quantity: number;
  current_price: number | null;
  total_cost: number;
  current_value: number | null;
  profit_loss: number | null;
  profit_loss_percent: number | null;
  created_at: string;
}
```

---

## 5. 권장 사용 흐름

### 앱 개발 시 권장 API 사용 패턴

**1. 주식 매수**
```
POST /transaction/
{
  "symbol": "AAPL",
  "transaction_type": "BUY",
  "price": 180.50,
  "quantity": 10
}
```

**2. 추가 매수 (평균 단가 자동 계산)**
```
POST /transaction/
{
  "symbol": "AAPL",
  "transaction_type": "BUY",
  "price": 200.00,
  "quantity": 5
}
→ 포트폴리오: 평균 188.33달러, 15주
```

**3. 일부 매도**
```
POST /transaction/
{
  "symbol": "AAPL",
  "transaction_type": "SELL",
  "price": 190.00,
  "quantity": 5
}
→ 포트폴리오: 평균 188.33달러 (유지), 10주
```

**4. 포트폴리오 확인**
```
GET /portfolio/profit
→ 전체 보유 주식의 손익 확인
```

**5. 거래 내역 확인**
```
GET /transaction/?symbol=AAPL
→ AAPL의 모든 거래 내역 조회
```

**6. 거래 통계 확인**
```
GET /transaction/summary/AAPL
→ AAPL의 총 매수/매도 통계
```

---

## 6. 마이그레이션 가이드 (v1.0 → v2.0)

### 데이터베이스 변경사항

1. **새 테이블**: `transactions`
2. **포트폴리오 테이블 변경**:
   - `purchase_price` → `average_price` (컬럼명 변경)
   - `symbol`에 UNIQUE 제약 조건 추가

### 마이그레이션 실행

**방법 1: Python 스크립트**
```bash
python migrations/run_migration.py
```

**방법 2: SQL 직접 실행**
```bash
# Oracle SQL Developer에서
@migrations/001_add_transaction_tracking.sql
```

### 기존 데이터 처리

- 기존 포트폴리오 항목들은 자동으로 BUY 거래로 변환됩니다
- 데이터 손실 없음
- 하위 호환성 유지

---

## 7. API 테스트

### Swagger UI
```
http://127.0.0.1:8000/docs
```

### ReDoc
```
http://127.0.0.1:8000/redoc
```

---

## 8. 주의사항

1. **실시간 데이터 제한**
   - 주식 가격은 15-20분 지연된 데이터입니다

2. **거래 삭제 주의**
   - `DELETE /transaction/` 사용 시 포트폴리오가 자동으로 재계산되지 않습니다
   - 실수로 등록한 거래를 삭제하는 용도로만 사용하세요

3. **매도 검증**
   - 보유 수량보다 많이 매도하려고 하면 400 에러가 발생합니다

4. **평균 단가 계산**
   - 매수 시에만 평균 단가가 재계산됩니다
   - 매도 시에는 평균 단가가 유지됩니다

5. **포트폴리오 직접 수정 비권장**
   - `POST /portfolio/`, `PUT /portfolio/{id}` 대신
   - `POST /transaction/` 사용을 권장합니다
