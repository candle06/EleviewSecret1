from flask import Flask, request, jsonify, render_template
import csv

app = Flask(__name__)

# CSV 로드
elevator_data = []

def load_csv(file):
    with open(file, newline='', encoding='utf-8') as f:
        reader = csv.reader(f)
        return list(reader)

# 두 CSV 합치기
elevator_data = load_csv('elevators1.csv') + load_csv('elevators2.csv')
print(f"CSV Loaded: {len(elevator_data)} rows")

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
            if len(results) >= 50:  # 최대 50개 제한
                break
    return jsonify(results)

if __name__ == '__main__':
    app.run(debug=True)
