from flask import Flask, request, render_template_string, jsonify
import os
import json
import subprocess

app = Flask(__name__)
UPLOAD_FOLDER = "uploads"
RESUME_FOLDER = os.path.join(UPLOAD_FOLDER, "resumes")
os.makedirs(RESUME_FOLDER, exist_ok=True)

HTML_TEMPLATE = """
<!doctype html>
<html>
<head>
    <title>Resume Analyzer</title>
</head>
<body>
    <h1>Resume Analyzer</h1>
    <form method="post" enctype="multipart/form-data">
        <p>Upload Job Description (TXT): <input type="file" name="jd" required></p>
        <p>Upload Resumes (TXT/PDF/DOC/DOCX, multiple): <input type="file" name="resumes" multiple required></p>
        <button type="submit">Analyze</button>
    </form>
    {% if results %}
        <h2>Results</h2>
        <ul>
        {% for r in results %}
            <li>{{ r["name"] }} - Match: {{ r["match_percentage"] }}%
                <br>Skills: {{ ", ".join(r["matched_skills"]) }}
            </li>
        {% endfor %}
        </ul>
    {% endif %}
</body>
</html>
"""

@app.route("/", methods=["GET", "POST"])
def index():
    results = []
    if request.method == "POST":
        jd_file = request.files.get("jd")
        resume_files = request.files.getlist("resumes")

        jd_path = os.path.join(UPLOAD_FOLDER, jd_file.filename)
        jd_file.save(jd_path)

        for f in resume_files:
            f.save(os.path.join(RESUME_FOLDER, f.filename))

        out_json = os.path.join(UPLOAD_FOLDER, "results.json")
        cmd = ["python", "analyzer.py", "--jd", jd_path, "--resumes", RESUME_FOLDER, "--out", out_json]
        result = subprocess.run(cmd, capture_output=True, text=True)
        print("Analyzer output:", result.stdout)
        print("Analyzer errors:", result.stderr)

        if os.path.exists(out_json):
            with open(out_json, "r", encoding="utf-8") as f:
                data = json.load(f)
                if isinstance(data, dict):
                    results = [data]
                elif isinstance(data, list):
                    results = []
                    for x in data:
                        if isinstance(x, dict):
                            results.append(x)
                        elif isinstance(x, str):
                            results.append({"name": x, "match_percentage": 0, "matched_skills": []})
    return render_template_string(HTML_TEMPLATE, results=results)

if __name__ == "__main__":
     port = int(os.environ.get("PORT", 5000))
     app.run(host='0.0.0.0', port=port, debug=True)
