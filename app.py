from flask import Flask, render_template, request, jsonify
import pandas as pd
import json

app = Flask(__name__)

class FalconJSONQA:
    def __init__(self, json_path):
        print("Loading service database...")
        self.df = self.load_json(json_path)

    def load_json(self, json_path):
        with open(json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        df = pd.json_normalize(data)
        print(f"Loaded {len(df)} records from JSON.")
        return df

    def search_context_json(self, user_query, max_records=5):
        search_df = self.df[
            self.df.apply(lambda row: user_query.lower() in str(row).lower(), axis=1)
        ]

        if search_df.empty:
            search_df = self.df.sample(n=min(max_records, len(self.df)))
            message = "❌ No exact match found. Showing random services."
        else:
            message = f"Found {len(search_df)} matching records."

        result = []
        for _, row in search_df.head(max_records).iterrows():
            record = {
                "category": row.get("category", ""),
                "sub_category": row.get("sub-category", ""),
                "service": row.get("name", ""),
                "tags": row.get("tags", [])
            }
            result.append(record)

        return {"message": message, "results": result}

# Initialize the JSON QA system
qa_system = FalconJSONQA('data/output.json')

@app.route('/', methods=['GET', 'POST'])
def index():
    result = None
    if request.method == 'POST':
        user_query = request.form.get('query', '')
        if user_query:
            result = qa_system.search_context_json(user_query)
    return render_template('index.html', result=result)

@app.route('/api/search', methods=['POST'])
def api_search():
    data = request.get_json()
    user_query = data.get('query', '')
    if not user_query:
        return jsonify({"error": "Query is required."}), 400
    result = qa_system.search_context_json(user_query)
    return jsonify(result), 200

if __name__ == '__main__':
    app.run(debug=True)
