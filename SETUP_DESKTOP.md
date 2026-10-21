# 집 데스크톱(Windows)에서 메소 시세 매일 수집하기

GitHub Actions(해외 IP)에서는 아이템매니아 연결이 시간 초과된다. 한국 IP인 집 데스크톱에서 `update_rates.sh`를 매일 실행해 `rates.js`를 푸시하면 GitHub Pages가 자동 재배포된다.

## 0. 준비

- Git for Windows(Git Bash), Python 3
- Python 실행 명령 확인: Git Bash에서 `python --version`이 "Python was not found…"를 출력하면 MS Store 바로가기다. 이때는 `py --version`이 동작하는지 확인하고 아래의 `PYTHON=python`을 `PYTHON=py`로 바꾼다.

## 1. 레포 받기·첫 실행 (Git Bash)

```bash
git clone https://github.com/Jawooni/maple_boss_ssalmuk.git
cd maple_boss_ssalmuk && PYTHON=python sh update_rates.sh && git log --oneline -1
```

첫 푸시 때 GitHub 로그인 창이 뜬다. GitHub에 `rates.js 갱신 (날짜)` 커밋이 생기고, 1~2분 뒤 사이트의 "자동 기록 마지막 실행"이 바뀌면 성공.
(이미 최신이면 커밋 없이 끝난다.)

## 2. 매일 실행 등록 (PowerShell, 작업 스케줄러)

`$dir`은 레포 위치를 Git Bash 경로 형식으로 적는다. Git 설치 경로가 다르면 `bash.exe` 경로를 바꾼다.

```powershell
$dir = "/c/Users/이름/maple_boss_ssalmuk"
$action = New-ScheduledTaskAction -Execute "C:\Program Files\Git\bin\bash.exe" -Argument "-lc `"cd '$dir' && PYTHON=python sh update_rates.sh >> rates.log 2>&1`""
$trigger = New-ScheduledTaskTrigger -Daily -At 11:00
$settings = New-ScheduledTaskSettingsSet -StartWhenAvailable
Register-ScheduledTask -TaskName "maple_boss_rates" -Action $action -Trigger $trigger -Settings $settings
Start-ScheduledTask -TaskName "maple_boss_rates"
```

11시로 잡은 이유: 아이템매니아는 10시 무렵 전날까지 집계한다. `-StartWhenAvailable`이라 11시에 PC가 꺼져 있었으면 켜진 뒤 실행된다.
`rates.log`에 `저장 (N건)`이 찍히고 GitHub에 커밋이 생기면 성공. 실패 원인도 `rates.log`에서 확인한다(`.gitignore`에 포함됨).

## 주의

- 데스크톱이 꺼져 있던 날이 있어도 다음 실행에서 최근 90일치를 다시 받아 빈 날을 채운다. 2일 넘게 멈추면 사이트에 `[갱신 중단]`이 표시된다.
- 등록 해제: `Unregister-ScheduledTask -TaskName "maple_boss_rates"`
