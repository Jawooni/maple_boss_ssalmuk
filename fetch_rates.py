"""아이템매니아 일 평균시세(원/1억 메소)를 rates.js에 누적 기록한다.

매일 1회 실행 (아이템매니아는 하루 한 번, 10시 무렵 전날까지의 평균을 집계한다).
최근 90일치를 받아 기존 기록과 병합한다.
마지막 시세일이 그저께보다 오래됐으면 해당 서버를 갱신 중단(stale)으로 표시한다.
"""
import json
import sys
import urllib.request
import xml.etree.ElementTree as ET
from datetime import date, datetime, timedelta, timezone
from pathlib import Path

SERVERS = {'스카니아': 660, '에오스': 12030}  # 아이템매니아 servercode (메이플스토리 gamecode=138)
URL = 'https://www.itemmania.com/_xml/gamemoney_avg.xml.php?gamecode=138&servercode={code}&count=90'
OUT = Path(__file__).with_name('rates.js')
PREFIX = 'window.AUTO_RATES = '
KST = timezone(timedelta(hours=9))


def fetch_prices(code):
    """{날짜: 1억 메소당 원} 반환. XML의 price는 multiple억 메소당 가격이다."""
    req = urllib.request.Request(URL.format(code=code), headers={'User-Agent': 'maple_boss_calc/1.0 (personal daily rate log)'})
    with urllib.request.urlopen(req, timeout=30) as res:
        root = ET.fromstring(res.read())
    if root.get('result') != 'success' or root.get('unit_trade') != '억':
        raise ValueError(f'예상과 다른 응답: result={root.get("result")}, unit_trade={root.get("unit_trade")}')
    multiple = int(root.get('multiple'))
    return {date.fromisoformat(d.get('date').replace('/', '-')): round(int(d.get('price')) / multiple, 2) for d in root.iter('data')}


def load():
    if not OUT.exists():
        return {'rates': [], 'servers': {}}
    return json.loads(OUT.read_text(encoding='utf-8')[len(PREFIX):].rstrip().rstrip(';'))


def main():
    now = datetime.now(KST)
    today = now.date()
    data = load()
    rates = {(r['date'], r['server']): r for r in data['rates']}
    # 네트워크 오류 시 기존 파일을 건드리지 않도록 전부 받은 뒤에 쓴다.
    fetched = {name: fetch_prices(code) for name, code in SERVERS.items()}

    for name, days in fetched.items():
        last = max(days) if days else None
        stale = last is None or last < today - timedelta(days=2)
        added = 0
        for day, price in days.items():
            if day < today:
                key = (day.isoformat(), name)
                added += key not in rates
                rates[key] = {'date': day.isoformat(), 'server': name, 'close': price}
        data['servers'][name] = {'code': SERVERS[name], 'last_date': last.isoformat() if last else None, 'stale': stale}
        print(f'{name}: 마지막 시세일 {last}, 신규 {added}일' + (' [갱신 중단]' if stale else ''))

    data['source'] = '아이템매니아 일 평균시세'
    data['rates'] = sorted(rates.values(), key=lambda r: (r['date'], r['server']))
    data['updated'] = now.strftime('%Y-%m-%d %H:%M')
    OUT.write_text(PREFIX + json.dumps(data, ensure_ascii=False, indent=1) + ';\n', encoding='utf-8')
    print(f'{OUT} 저장 ({len(data["rates"])}건)')


if __name__ == '__main__':
    try:
        main()
    except Exception as e:
        print(f'실패: {e}', file=sys.stderr)
        sys.exit(1)
