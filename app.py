from flask import Flask, request, jsonify, render_template
import csv, os, requests

app = Flask(__name__)

# 구글 드라이브 공유 링크 → 다운로드용
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
        with open(path, 'wb') as f:
            for chunk in r.iter_content(chunk_size=8192):
                f.write(chunk)
        print(f"{path} 다운로드 완료")

# CSV 로드
def load_csv(file):
    with open(file, newline='', encoding='utf-8') as f:
        reader = csv.reader(f)
        return list(reader)

# 두 CSV 다운로드 + 병합
for url, path in zip(CSV_LINKS, CSV_FILES):
    download_csv(url, path)

elevator_data = load_csv(CSV_FILES[0]) + load_csv(CSV_FILES[1])
print(f"총 {len(elevator_data)}행 CSV 로드 완료")

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/search')
def search():
    model_query = request.args.get('model', '').strip().lower()
    if not model_query:
        return jsonify([])

    results = []
    for row in elevator_data:
        if len(row) < 2:
            continue
        model = row[-2].strip().lower()
        if model_query in model:
            results.append(row)
            if len(results) >= 50:  # 최대 50개
                break
    return jsonify(results)

if __name__ == '__main__':
    app.run(debug=True)
