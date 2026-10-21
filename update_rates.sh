#!/bin/sh
# 시세 수집 후 rates.js가 바뀌었으면 커밋·푸시한다 (Oracle Cloud VM의 cron에서 매일 실행).
# 푸시되면 GitHub Pages가 자동으로 재배포된다.
set -e
cd "$(dirname "$0")"
git pull -q --rebase
${PYTHON:-python3} fetch_rates.py
git add rates.js
git diff --cached --quiet && exit 0
git commit -q -m "rates.js 갱신 ($(TZ=Asia/Seoul date +%F))"
git push -q
