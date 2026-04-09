# MTS FDS Platform

운영형 포트폴리오를 목표로 한 Python 기반 가상 주식 MTS + 모의매매 + FDS + 관리자 운영 콘솔 프로젝트다.

## 구조

```text
mts-fds/
  backend/
    app/
      api/
      core/
      db/
      fds/
      market/
      models/
      repositories/
      schemas/
      services/
      workers/
    scripts/
    tests/
  frontend/
    src/
  docker-compose.yml
```

## 주요 기능

- FastAPI 기반 인증, 시세, 주문, 관리자 위험이벤트 API
- PostgreSQL + SQLAlchemy 데이터 모델
- Redis + Celery 워커 골격
- Mock market data provider 및 real provider 교체 인터페이스
- 룰 기반 FDS 엔진 초안
- 관리자/사용자 화면 분리 React 레이아웃
- seed 데이터 포함

## 기본 계정

- admin@example.com / Admin1234!
- user@example.com / User1234!

## 실행

```bash
cd mts-fds
docker compose up --build
```

백엔드 -- http://localhost:8000
프론트 -- http://localhost:3000
Swagger -- http://localhost:8000/docs

## 주요 API

- POST /api/v1/auth/login
- GET /api/v1/market/stocks
- GET /api/v1/market/stocks/{stock_code}/quote
- POST /api/v1/orders
- GET /api/v1/admin/risk-events

## 주문 예시

```bash
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H 'Content-Type: application/json' \
  -d '{"email":"user@example.com","password":"User1234!","ip_address":"1.1.1.1","region":"KR-SEOUL"}'
```

```bash
curl -X POST http://localhost:8000/api/v1/orders \
  -H 'Content-Type: application/json' \
  -H 'Authorization: Bearer <TOKEN>' \
  -d '{
    "account_id":1,
    "stock_code":"005930",
    "side":"BUY",
    "order_type":"LIMIT",
    "quantity":10,
    "price":83500,
    "device_id":"device-main",
    "ip_address":"1.1.1.1",
    "region":"KR-SEOUL"
  }'
```

## 현재 포함된 FDS 룰

- 신규 디바이스 고액 주문
- 해외 IP 로그인 후 즉시 주문
- 로그인 실패 반복 후 주문
- 평균 대비 주문금액 급증
- 특정 종목 집중 주문
- 동일 IP 다계정 유사 주문

## 보안/운영 포인트

- JWT 인증 및 관리자 권한 분리
- 감사로그 테이블 분리
- 추가인증 요청 테이블 분리
- 블랙리스트 계정/종목 테이블 분리
- env 기반 설정 분리

## 다음 고도화 우선순위

1. Alembic migration 도입 및 초기 스키마 버전 관리
2. 주문 정정/취소/부분체결 엔진 확장
3. 관리자 조치 API, 계정 잠금/해제, 블랙리스트 관리 UI 추가
4. 실 시세 provider 연동 및 websocket 시세 push
5. 리포트 HTML/PDF 생성기 추가
6. React API 연동 및 인증 흐름 완성
7. 통합테스트/부하테스트 추가
