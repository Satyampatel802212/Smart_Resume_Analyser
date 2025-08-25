import os
import json
import docx
import PyPDF2

from nltk.corpus import stopwords
import nltk
import re

# Download stopwords if not already
nltk.download('stopwords', quiet=True)
stop_words = set(stopwords.words('english'))

def extract_text_from_file(file_path):
    ext = file_path.lower().split('.')[-1]
    text = ""
    if ext == 'txt':
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            text = f.read()
    elif ext == 'pdf':
        try:
            with open(file_path, 'rb') as f:
                reader = PyPDF2.PdfReader(f)
                for page in reader.pages:
                    text += page.extract_text() or ""
        except:
            pass
    elif ext in ['doc', 'docx']:
        try:
            doc = docx.Document(file_path)
            for para in doc.paragraphs:
                text += para.text + " "
        except:
            pass
    return text

def clean_text(text):
    words = re.findall(r'\b[a-zA-Z]+\b', text.lower())
    return [w for w in words if w not in stop_words]

def calculate_match(jd_words, resume_words):
    jd_set = set(jd_words)
    resume_set = set(resume_words)
    matched = jd_set.intersection(resume_set)
    match_percent = round(len(matched) / len(jd_set) * 100, 2) if jd_set else 0
    return match_percent, list(matched)

def main(jd_path, resumes_folder, out_json):
    jd_text = extract_text_from_file(jd_path)
    jd_words = clean_text(jd_text)

    results = []
    for file in os.listdir(resumes_folder):
        if not file.lower().endswith(('txt','pdf','doc','docx')):
            continue
        resume_path = os.path.join(resumes_folder, file)
        resume_text = extract_text_from_file(resume_path)
        resume_words = clean_text(resume_text)
        match_percent, matched = calculate_match(jd_words, resume_words)
        results.append({
            "name": file,
            "match_percentage": match_percent,
            "matched_skills": matched
        })

    with open(out_json, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=4)

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--jd", required=True)
    parser.add_argument("--resumes", required=True)
    parser.add_argument("--out", required=True)
    args = parser.parse_args()
    main(args.jd, args.resumes, args.out)
