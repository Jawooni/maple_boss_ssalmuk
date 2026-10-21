# 작업 인계 계획 (노트북 → 데스크톱)

작성: 2026-10-21, Claude Code (노트북 세션).
`worklog.md`·`DECISIONS.md`·`reference/`는 `.gitignore`로 레포에 없으므로, 이어서 작업하는 데 필요한 맥락을 이 문서에 정리한다.

## 1. 현재 상태

| 항목 | 상태 |
|---|---|
| 사이트 | GitHub Pages 배포됨: https://jawooni.github.io/maple_boss_ssalmuk/ |
| 보스 조회 | 브라우저 → 넥슨 Open API 직접 호출. `github.io` 출처 CORS 허용 확인(curl 사전 요청). **실제 API Key로 배포 사이트 조회는 미검증** |
| 시세 자동 수집 | **미가동.** `rates.js`는 2026-10-20 시세까지(180건) |
| GitHub Actions | 해외 IP에서 아이템매니아 연결 시간 초과(`<urlopen error timed out>`)로 실패 → 예약 실행 제거, 수동 실행만 남김 |
| Oracle Cloud | 가입 화면 홈 영역에 서울·춘천 없음 → 보류 |

## 2. 파일 구성

| 파일 | 역할 |
|---|---|
| `index.html` | 앱 전체(단일 파일, vanilla JS, 상태는 localStorage). 설정 창(API Key·조회일·캐릭터 선택·파티 인원), 수익 요약, 보스 클리어 보드, 메소 시세 기록, 결정석 가격표 |
| `rates.js` | `window.AUTO_RATES = {...}` 형식의 시세 기록(원/1억 메소). `fetch_rates.py`가 생성 |
| `fetch_rates.py` | 아이템매니아 일 평균시세 XML(스카니아 660, 에오스 12030, 최근 90일)을 받아 `rates.js`에 병합. 표준 라이브러리만 사용 |
| `update_rates.sh` | `git pull` → `fetch_rates.py` → `rates.js` 변경 시 커밋·푸시. `PYTHON` 환경변수로 인터프리터 지정(기본 `python3`) |
| `.github/workflows/rates.yml` | 수동 실행 전용 시세 갱신 워크플로(해외 IP라 실패함) |
| `DESIGN.md` | 디스코드 계열 디자인 토큰. `index.html` 스타일의 근거 |
| `SETUP_ORACLE.md` | Oracle VM 수집 안내. 한국 리전을 고를 수 없어 현재 사용 불가 |

## 3. 지금까지 정해진 것 (사용자 결정)

- 원화 환산은 **메소 시세(원/1억 메소)** 기록 방식. 기준 서버는 **스카니아·에오스**.
- 월 수익 = **주간 결정석 × 그 달의 목요일 수 + 월간 보스(검은 마법사)**. 보스 초기화가 목요일이기 때문.
- 결정석 몫 = 가격 ÷ 파티 인원(소수점 버림). 최대 인원: 익스트림 스우 2, 유피테르·발드릭스·벨로나·림보·찬란한 흉성·최초의 대적자 3, 나머지 6.
- 시세 출처는 **아이템매니아 일 평균시세**(gamebit 제외). 매일 10시 무렵 전날까지 집계됨.
- 시즌 보스(메이린 등)는 표시·계산에서 제외.
- 디자인은 `DESIGN.md`(디스코드 계열), 글꼴은 메이플스토리 Light(본문)/Bold(강조) — 눈누 CDN.
- 시세 수집은 **한국 IP**에서만 동작하는 것으로 확인됨(노트북에서 0.1초, GitHub 러너에서 시간 초과).

## 4. 데스크톱에서 할 일 (순서대로)

### 4-1. 시세 자동 수집 가동 (사용자 작업)

1. Git Bash에서 레포를 받고 한 번 실행한다. 첫 푸시 때 GitHub 로그인 창이 뜬다.
   ```bash
   git clone https://github.com/Jawooni/maple_boss_ssalmuk.git
   cd maple_boss_ssalmuk && PYTHON=python sh update_rates.sh && git log --oneline -1
   ```
   → 검증: `rates.js 갱신 (날짜)` 커밋이 GitHub에 생기고, 1~2분 뒤 사이트의 "자동 기록 마지막 실행"이 바뀐다.
2. PowerShell에서 작업 스케줄러에 등록한다(`$dir`은 Git Bash 경로 형식).
   ```powershell
   $dir = "/c/Users/이름/maple_boss_ssalmuk"
   $action = New-ScheduledTaskAction -Execute "C:\Program Files\Git\bin\bash.exe" -Argument "-lc `"cd '$dir' && PYTHON=python sh update_rates.sh >> rates.log 2>&1`""
   $trigger = New-ScheduledTaskTrigger -Daily -At 11:00
   $settings = New-ScheduledTaskSettingsSet -StartWhenAvailable
   Register-ScheduledTask -TaskName "maple_boss_rates" -Action $action -Trigger $trigger -Settings $settings
   Start-ScheduledTask -TaskName "maple_boss_rates"
   ```
   → 검증: `rates.log`에 `저장 (N건)`이 찍히고 GitHub에 커밋이 생긴다. 다음 날 11시 이후 다시 확인.
   - **미검증**: 이 명령은 노트북에서 실행해 보지 않았다. Git 설치 경로가 다르면 `bash.exe` 경로를 바꾼다.

### 4-2. 배포 사이트 실사용 확인 (사용자 작업)

1. 배포 주소에서 설정 → API Key 입력 → 캐릭터 목록 불러오기 → 캐릭터 선택 → 보스 현황 조회.
   → 검증: 캐릭터 카드와 보스 보드가 표시되고 콘솔 에러가 없다. 실패하면 상태 문구의 오류 메시지를 확인.

### 4-3. 승인 대기 중인 제안 (Claude Code가 제안, 아직 미반영)

1. `SETUP_ORACLE.md`를 4-1 내용의 `SETUP_DESKTOP.md`로 교체하고, `rates.yml` 주석도 맞춘다.
2. `.gitignore`에 `rates.log` 추가(작업 스케줄러 로그가 `git status`에 계속 보이는 것 방지).
3. 보스 칸에서 긴 이름(예: 가디언 엔젤 슬라임)이 잘림 → 칸 너비 조정 또는 줄바꿈 허용.

### 4-4. 다음 UI 작업 후보 (방향 미정, 사용자 결정 필요)

- 수익 요약·메소 시세 영역은 아직 표 형태. 카드·그래프 등으로 바꿀지.
- 캐릭터 이미지: `character/list`가 이미지를 주지 않아 이름 첫 글자로 대체 중. 넣으려면 캐릭터마다 `character/basic` 추가 호출 필요.
- DESIGN.md의 대형 대문자 디스플레이 타이포·움직이는 그라데이션은 계산기 화면에 맞지 않아 적용 보류.
- 여러 기기 간 기록(파티 인원·수동 시세·주차 기록) 공유가 필요해지면 서버+DB(예: Cloudflare Workers + D1)와 로그인 설계가 필요.

## 5. 알려진 한계·위험

- 시세 수집이 집 데스크톱에 의존: 꺼져 있던 날은 다음 실행 때 최근 90일치로 채워짐. 2일 넘게 멈추면 사이트에 `[갱신 중단]` 표시.
- 아이템매니아 XML은 비공식 경로이며 robots.txt 기준 회색지대. 경로·형식이 바뀌면 `fetch_rates.py`가 `실패: ...`로 종료하고 기존 파일은 유지된다.
- 결정석 가격은 2026-10-22 패치 기준(나무위키 등 교차 확인). 출처 간 일부 불일치(노멀 카링·흉성)가 있어 가격표에서 직접 수정 가능.
- 기록(API Key·파티 인원·수동 시세·주차 기록)은 브라우저 localStorage에만 있어 기기·브라우저마다 따로다.
- 메이플스토리 글꼴은 CDN에서 받으므로 오프라인이면 시스템 글꼴로 대체된다.

## 6. 작업 규칙 메모

- 코드는 사용자가 명시적으로 수정을 요청할 때만 바꾸고, 개선안은 제안 후 승인받아 반영한다.
- 검증하지 않은 것은 "미검증"으로 표시한다.
- 로컬 검증은 `python -m http.server 8765 --bind 127.0.0.1`로 서빙해 브라우저에서 확인했다(file://은 localStorage 검증이 어려움).
