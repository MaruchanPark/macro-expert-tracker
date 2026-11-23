# Macro Expert Tracker

매크로 전문가 18인의 BTC · ETH · Nasdaq(NDX) · 미국 국채(UST)에 대한 의견을 매주 수집해 누적하는 저장소입니다.
매주 일요일 18:00(KST)에 예약 작업이 실행되어 지난 실행 이후의 의견을 수집하고 이 저장소에 커밋합니다.

## 구조

| 파일 | 내용 |
|---|---|
| `data/roster.csv` | 전문가 명단과 자산별 기존(예상) 스탠스, 주요 출처 |
| `data/runs.csv` | 실행 기록 (append-only) |
| `data/opinions.csv` | 수집된 의견 (append-only, 한 항목이 여러 자산을 다루면 자산별로 한 행) |
| `reports/run-NNN.md` | 실행별 읽기용 리포트 (전문가별 요약 + 자산 스코어보드) |
| `PROCEDURE.md` | 매주 실행 절차 (예약 작업과 스킬이 따르는 기준) |
| `scripts/query.py` | 조회 스크립트 (Python 표준 라이브러리만 사용) |
| `data/catalog.csv` | 전문가별 장문 읽을거리 카탈로그 (책·논문·장문 글, 읽음 여부) |
| `scripts/catalog.py` | 카탈로그 조회·추가·읽음 처리 스크립트 |
| `briefs/YYYY-MM/YYYY-MM-DD.md` | 일일 긍정/부정 전망 브리프 (BTC·ETH·나스닥·달러 패권 + 미국 매크로 지표) |
| `data/briefs.csv` | 일일 브리프 색인 (날짜, 자산별 분위기, 헤드라인, 파일 경로) |

### 일일 브리프
매일 아침(KST) 예약 작업이 미국 매크로 지표와 4개 자산의 긍정·부정 근거를 조사해 `briefs/YYYY-MM/YYYY-MM-DD.md`에 저장하고 `data/briefs.csv`에 한 줄을 추가합니다. 절차는 `PROCEDURE.md`의 "Daily outlook brief procedure"를 따릅니다.

| 컬럼 (`data/briefs.csv`) | 설명 |
|---|---|
| `date` | 브리프 날짜 (KST, YYYY-MM-DD) |
| `btc` / `eth` / `ndx` / `usd` | 그날 자산별 분위기 `Bull` / `Bear` / `Mixed` (`usd` = 달러 패권) |
| `headline` | 한 줄 요약 (한국어) |
| `file` | 브리프 파일 경로 |

### `data/runs.csv`
| 컬럼 | 설명 |
|---|---|
| `run_no` | 실행 번호 (1부터 증가) |
| `run_date` | 실행 시각 (UTC, ISO 8601) |
| `period_start` / `period_end` | 수집 기간. `period_start` = 직전 성공 실행의 `period_end` (첫 실행은 7일 전) |
| `status` | `success` / `failed` |
| `items` | 이번 실행에서 추가된 항목(링크) 수 |
| `notes` | 메모 |

### `data/opinions.csv`
| 컬럼 | 설명 |
|---|---|
| `run_no` | 수집한 실행 번호 |
| `expert` | 전문가 이름 (`roster.csv`와 동일 표기) |
| `published_date` | 원문 게시일 (YYYY-MM-DD) |
| `asset` | `BTC` / `ETH` / `NDX` / `UST` |
| `stance` | `Bull` / `Bear` / `Neutral` |
| `stance_change` | 명단의 기존 스탠스와 다르면 `Y` |
| `title` | 원문 제목 |
| `summary` | 5줄 이내 요약 (한국어) |
| `link` | 원문 링크. 같은 링크는 다시 추가하지 않음 (중복 제거 키) |

### `data/catalog.csv` (읽을거리 카탈로그)
| 컬럼 | 설명 |
|---|---|
| `expert` | 전문가 이름 |
| `tier` | `3` = 책·논문·리서치 보고서, `2` = 5분 이상 읽는 장문 글. 5분 미만 짧은 글(1등급)은 넣지 않음 |
| `title` | 제목 |
| `published_date` | 발행일 (YYYY-MM-DD, 모르면 YYYY-MM 또는 YYYY) |
| `outlet` | 매체·출판사 |
| `read` | 읽음 여부 `Y`/`N` (기본 `N`) |
| `link` | 링크 (있으면) |

전문가별로 묶어 최신순으로 정렬됩니다. 매주 트래커가 장문 글을 찾으면 함께 추가하고, 매월 1일 별도 갱신이 놓친 책·논문·장문을 보충합니다.
초기 구축 범위: 책·논문은 전체 이력(로고프는 대표 논문 + 2021년 이후 논문), 장문 글은 2021년 이후.

```bash
python3 scripts/catalog.py stats                                 # 전문가별 건수 / 안 읽은 수
python3 scripts/catalog.py list --expert "Lyn Alden" --unread    # 안 읽은 것만
python3 scripts/catalog.py list --tier 3                          # 책·논문만
python3 scripts/catalog.py mark-read "Broken Money"              # 읽음 처리
```

## 조회 예시

```bash
python3 scripts/query.py last-run                        # 마지막 성공 실행
python3 scripts/query.py run 3                           # 3회차 실행의 모든 의견
python3 scripts/query.py scoreboard 3                    # 3회차 자산별 Bull/Bear 집계
python3 scripts/query.py expert "Luke Gromen"            # Gromen 의견 전체 (최신순)
python3 scripts/query.py expert "Luke Gromen" --nth 0    # Gromen 최신 의견
python3 scripts/query.py expert "Luke Gromen" --nth 2    # 최신에서 2개 전 의견
python3 scripts/query.py expert "Lyn Alden" --asset BTC  # Alden의 BTC 의견만
python3 scripts/query.py asset UST --run 3               # 3회차 UST 의견
```

`--nth`는 `published_date` 기준 최신순으로 센 순번입니다 (0 = 최신).
CSV라서 GitHub 화면, 엑셀, 구글 시트, pandas 어디서든 바로 열 수 있습니다.
