# Oracle Cloud 무료 VM에서 메소 시세 매일 수집하기

GitHub Actions(해외 IP)에서는 아이템매니아 연결이 시간 초과된다. 한국 리전 VM에서 `update_rates.sh`를 매일 실행해 `rates.js`를 푸시하면 GitHub Pages가 자동 재배포된다.

## 1. 가입·VM 생성 (웹 콘솔)

1. https://www.oracle.com/cloud/free/ 가입. **홈 리전은 `South Korea Central (Seoul)` 또는 `South Korea North (Chuncheon)`** 으로 고른다. 홈 리전은 나중에 바꿀 수 없다.
2. Compute → Instances → Create instance
   - Image: **Canonical Ubuntu 22.04 또는 24.04**
   - Shape: Always Free 표시가 있는 것 (`VM.Standard.E2.1.Micro` 또는 `VM.Standard.A1.Flex` 1 OCPU / 6GB)
   - SSH keys: "Generate a key pair" → **개인 키 저장** (분실 시 접속 불가)
3. 생성 후 Public IP 확인.

## 2. 접속

```bash
ssh -i <저장한_개인키_경로> ubuntu@<Public IP>
```

## 3. 먼저 수집 가능 여부 확인 (가장 중요)

```bash
curl -s -o /dev/null -m 30 -w "connect %{time_connect}s, HTTP %{http_code}\n" "https://www.itemmania.com/_xml/gamemoney_avg.xml.php?gamecode=138&servercode=660&count=1"
```

- `HTTP 200` → 계속 진행.
- `HTTP 000` / 시간 초과 → 이 VM에서도 막힌 것. 여기서 중단하고 알려 주세요.

## 4. GitHub 쓰기 권한(배포 키) 설정

```bash
ssh-keygen -t ed25519 -f ~/.ssh/maple_deploy -N ""
cat ~/.ssh/maple_deploy.pub
printf 'Host github.com\n  IdentityFile ~/.ssh/maple_deploy\n' >> ~/.ssh/config
```

출력된 공개 키를 GitHub 레포 → Settings → Deploy keys → Add deploy key 에 붙여 넣고 **Allow write access** 체크.
이 키는 이 레포 하나에만 쓰기 권한이 있다.

## 5. 레포 받기·첫 실행

```bash
git clone git@github.com:Jawooni/maple_boss_ssalmuk.git
cd maple_boss_ssalmuk
git config user.name "maple-rates-bot"
git config user.email "maple-rates-bot@users.noreply.github.com"
sh update_rates.sh && git log --oneline -1
```

GitHub에 `rates.js 갱신 (날짜)` 커밋이 생기고, 1~2분 뒤 사이트의 "자동 기록 마지막 실행"이 바뀌면 성공.

## 6. 매일 실행 등록 (cron)

```bash
date   # VM 시간대 확인. 기본은 UTC
crontab -e
```

맨 아래에 추가 (UTC 02:00 = 한국 11:00, 아이템매니아는 10시 무렵 전날까지 집계):

```
0 2 * * * sh /home/ubuntu/maple_boss_ssalmuk/update_rates.sh >> /home/ubuntu/rates.log 2>&1
```

실패 원인은 `~/rates.log`에서 확인한다.

## 주의

- Oracle은 **오래 유휴 상태인 Always Free 인스턴스를 회수**할 수 있다(약 7일간 CPU·네트워크 사용률이 매우 낮을 때). 하루 1초 실행하는 이 VM은 해당될 수 있다. 회수되면 사이트의 "마지막 시세일"이 멈추고 `[갱신 중단]`이 표시된다. 계정을 Pay As You Go로 올리면(무료 한도 내 과금 없음) 회수 대상에서 빠진다.
- 수집이 멈춘 날이 있어도 다음 실행에서 최근 90일치를 다시 받아 빈 날을 채운다.
