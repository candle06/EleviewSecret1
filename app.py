from flask import Flask, request, jsonify, render_template
import csv, os, requests

app = Flask(__name__)

# 구글 드라이브 다운로드 링크
CSV_LINKS = [
    'https://drive.google.com/uc?export=download&id=1pXzKPyajw_FvIRHIt9YFHAlKkNV78P1d',
    'https://drive.google.com/uc?export=download&id=1O-rJEbGkGo2HT2lJpJkl5p_WnbNF-oY9'
]

CSV_FILES = ['elevators1.csv', 'elevators2.csv']

# CSV 다운로드
def download_csv(url, path):
    if not os.path.exists(path):
        print(f"{path} 다운로드 중...")
        r = requests.get(url, stream=True)
        if r.status_code != 200:
            print(f"다운로드 실패: {path}, 상태코드 {r.status_code}")
            return False
        with open(path, 'wb') as f:
            for chunk in r.iter_content(chunk_size=8192):
                f.write(chunk)
        print(f"{path} 다운로드 완료")
    return True

# CSV 로드
def load_csv(file):
    data = []
    try:
        with open(file, newline='', encoding='utf-8-sig') as f:
            reader = csv.reader(f)
            for row in reader:
                if len(row) > 1:
                    data.append(row)
        print(f"{file} 로드 완료: {len(data)}행")
    except Exception as e:
        print(f"CSV 로드 오류: {file}", e)
    return data

# 두 CSV 다운로드 + 병합
all_data = []
for url, path in zip(CSV_LINKS, CSV_FILES):
    if download_csv(url, path):
        all_data += load_csv(path)

# 모델명 위치 자동 감지 (예: "모델명" 컬럼 찾기)
header = all_data[0] if all_data else []
if '모델명' in header:
    model_index = header.index('모델명')
    all_data = all_data[1:]  # 헤더 제거
else:
    model_index = -2  # 기본: 끝에서 두 번째

print(f"모델명 컬럼 인덱스: {model_index}")
print(f"총 {len(all_data)}행 데이터 준비 완료")

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/search')
def search():
    query = request.args.get('model', '').strip().lower()
    if not query:
        return jsonify([])

    results = []
    for row in all_data:
        if len(row) <= model_index:
            continue
        model = row[model_index].strip().lower()
        if query in model:
            results.append(row)
            if len(results) >= 50:
                break
    return jsonify(results)

if __name__ == '__main__':
    # 배포용: 외부 접속 가능
    app.run(host='0.0.0.0', port=5000)
