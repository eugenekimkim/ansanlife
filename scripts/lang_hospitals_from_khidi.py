"""KHIDI(Medical Korea) 공공데이터 CSV → data/lang_hospitals.json

공공데이터포털에서 아래 두 파일을 내려받아 실행합니다.
  - 한국보건산업진흥원_외국인 자주 찾는 병원 (병원 목록: 기관명, 주소 ...)
  - 한국보건산업진흥원_외국인 자주 찾는 병원 언어종류 (기관명, 언어 ...)

  python3 scripts/lang_hospitals_from_khidi.py 병원목록.csv 언어종류.csv

안산시 주소만 남기고, 언어는 ISO 코드(en, vi, zh, ru, uz, mn)로 바꿉니다.
열 이름은 파일마다 조금씩 달라서 '기관명/병원명', '주소', '언어' 가 들어간 열을 찾아 씁니다.
"""
import csv, json, sys, datetime, pathlib

LANG = {'영어': 'en', '베트남어': 'vi', '중국어': 'zh', '러시아어': 'ru', '우즈베크어': 'uz', '우즈벡어': 'uz', '몽골어': 'mn', '일본어': 'ja'}

def rows(path):
    for enc in ('utf-8-sig', 'cp949'):
        try:
            with open(path, encoding=enc, newline='') as f:
                return list(csv.DictReader(f))
        except UnicodeDecodeError:
            continue
    raise SystemExit(f'인코딩을 읽을 수 없음: {path}')

def col(row, *keys):
    for k in row:
        if any(x in k for x in keys):
            return (row[k] or '').strip()
    return ''

def main(hosp_csv, lang_csv):
    ansan = {}
    for r in rows(hosp_csv):
        name, addr = col(r, '기관명', '병원명', '의료기관명'), col(r, '주소')
        if name and '안산' in addr:
            ansan[name] = set()
    for r in rows(lang_csv):
        name = col(r, '기관명', '병원명', '의료기관명')
        if name in ansan:
            for word in col(r, '언어').replace('/', ',').split(','):
                code = LANG.get(word.strip())
                if code:
                    ansan[name].add(code)
    out = {
        'source': 'Medical Korea(한국보건산업진흥원) 외국인 자주 찾는 병원 · 언어종류',
        'updated': datetime.date.today().isoformat(),
        'hospitals': [{'name': n, 'langs': sorted(l)} for n, l in sorted(ansan.items()) if l],
    }
    dst = pathlib.Path(__file__).resolve().parent.parent / 'data' / 'lang_hospitals.json'
    dst.write_text(json.dumps(out, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(f'{len(out["hospitals"])}곳 → {dst}')

if __name__ == '__main__':
    if len(sys.argv) != 3:
        raise SystemExit(__doc__)
    main(sys.argv[1], sys.argv[2])
