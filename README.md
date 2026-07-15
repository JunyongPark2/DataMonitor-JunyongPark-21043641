# DataMonitor

반도체 시료 생산주문관리 시스템의 "데이터 모니터링 Tool" PoC.
현재 저장된 시료(Sample)·주문(Order) 데이터 상태를 콘솔에서 실시간으로 조회할 수 있는 관리자 도구입니다.

## 구성

- `datamonitor/models.py` — Sample, Order 데이터 모델과 주문 상태(OrderStatus).
  `DataPersistence` PoC(`sampleorder` 패키지)의 JSON 스키마와 동일한 필드(`customer_name`, `created_at` 포함)를 사용하므로
  `--data-dir`로 `DataPersistence/data`를 직접 가리켜도 그대로 조회할 수 있습니다.
- `datamonitor/repository.py` — JSON 파일 기반 데이터 영속성(CRUD)
- `datamonitor/monitor.py` — 상태별 주문 집계, 시료별 재고 상태(여유/부족/고갈) 산출
- `datamonitor/render.py` — 콘솔 대시보드 문자열 렌더링
- `datamonitor/app.py` — 지정한 주기로 화면을 갱신하는 실시간 모니터링 루프 및 CLI 진입점

## 실행

```bash
python -m datamonitor.app                # data/ 디렉터리를 2초 주기로 실시간 모니터링 (Ctrl+C 종료)
python -m datamonitor.app --interval 1    # 갱신 주기 변경
python -m datamonitor.app --once          # 현재 상태를 한 번만 조회하고 종료
python -m datamonitor.app --data-dir path # 다른 데이터 디렉터리 조회
python -m datamonitor.app --data-dir ../DataPersistence/data --once  # DataPersistence의 실제 데이터 조회
```

`--data-dir`로 지정한 경로가 존재하지 않으면 에러 없이 빈 `samples.json`/`orders.json`을 새로
생성합니다. 경로를 잘못 입력해도 조용히 빈 데이터셋을 보여줄 수 있으니, 다른 PoC의 데이터가
보이지 않는다면 오타부터 의심하세요.

## 재고 상태 판정 (`datamonitor/monitor.py`)

대기 수요(`pending_demand`)는 아직 출고되지 않은 주문(`RESERVED`/`PRODUCING`/`CONFIRMED`)의 수량 합계입니다.
(`RELEASE`는 이미 출고 완료, `REJECTED`는 취소된 주문이라 수요에서 제외)

| 상태 | 판정 기준 |
| --- | --- |
| 고갈 | `재고 <= 0` |
| 부족 | `재고 < 대기 수요` |
| 여유 | 그 외 (재고 >= 대기 수요) |

**잔여율(%)** = 대기 수요를 채우고 남는 재고의 비율:

```
재고 <= 0        → 0%
대기 수요 <= 0   → 100%
그 외            → max(0, (재고 - 대기 수요) / 재고 * 100)
```

수요가 재고보다 많아 `(재고 - 대기 수요)`가 음수가 되는 경우(=부족 상태)는 0%로 표시합니다.
따라서 부족한 정도(조금 부족/많이 부족)는 잔여율만으로는 구분되지 않으며, "부족" 라벨 자체로만 판단해야 합니다.

## 테스트

```bash
pip install -r requirements.txt
pytest
```
