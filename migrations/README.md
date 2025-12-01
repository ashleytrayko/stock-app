# Database Migrations

이 폴더는 데이터베이스 스키마 변경 스크립트를 포함합니다.

## Migration 001: Transaction Tracking System

**파일**: `001_add_transaction_tracking.sql`

**목적**:
거래 내역 추적 시스템을 추가하여 실제 증권 앱처럼 동작하도록 개선

**변경사항**:
1. `transactions` 테이블 생성
   - 모든 매수/매도 거래 기록
   - 거래 타입, 가격, 수량, 일시 저장

2. `portfolio` 테이블 수정
   - `purchase_price` → `average_price` (컬럼명 변경)
   - `symbol`에 UNIQUE 제약 조건 추가 (종목당 1개의 포트폴리오)
   - 이제 포트폴리오는 거래 내역의 요약본 역할

3. 기존 데이터 마이그레이션
   - 기존 포트폴리오 항목들을 BUY 거래로 변환

**실행 방법**:

### Oracle SQL Developer 또는 SQL*Plus 사용
```sql
-- Oracle Cloud DB에 접속 후
@001_add_transaction_tracking.sql
```

### Python 스크립트로 실행
프로젝트 루트에서:
```bash
python migrations/run_migration.py
```

**주의사항**:
- 실행 전 데이터베이스 백업 권장
- 테스트 환경에서 먼저 실행해보기
- 기존 포트폴리오 데이터가 있다면 자동으로 transactions로 변환됨

**롤백 (필요시)**:
```sql
-- transactions 테이블 삭제
DROP TABLE transactions;
DROP SEQUENCE transactions_seq;

-- portfolio 테이블 복원
ALTER TABLE portfolio ADD purchase_price NUMBER(10, 2);
UPDATE portfolio SET purchase_price = average_price;
ALTER TABLE portfolio DROP COLUMN average_price;
ALTER TABLE portfolio DROP CONSTRAINT uk_portfolio_symbol;

COMMIT;
```

## 향후 Migration 추가 방법

1. 새로운 SQL 파일 생성: `00X_description.sql`
2. 변경사항 설명 주석 포함
3. 이 README에 문서 추가
4. Git에 커밋 전 테스트 환경에서 검증
