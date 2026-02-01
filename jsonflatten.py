# import json

# INPUT_FILE = "60_testpapers_flat.json"
# OUTPUT_FILE = "sample_papers.py"  # or .json if you prefer

# with open(INPUT_FILE, "r", encoding="utf-8") as f:
#     papers = json.load(f)  # list of {category, title, abstract}

# sample_papers = []

# for p in papers:
#     entry = {
#         "name": f"{p['category'].capitalize()} paper",
#         "expected_category": p["category"],
#         "title": p["title"],
#         "abstract": p["abstract"],
#         "dissemination": "Internal only",
#         "audience": "Governance auditor"
#     }
#     sample_papers.append(entry)

# # If you want a Python file with a SAMPLE_PAPERS variable:
# with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
#     f.write("SAMPLE_PAPERS = ")
#     json.dump(sample_papers, f, ensure_ascii=False, indent=2)

import json
from test_categories import TEST_PAPERS

output = []

for category, paper in TEST_PAPERS.items():
    output.append({
        "name": f"{category.capitalize()} paper",
        "expected_category": category,
        "title": paper["title"],
        "abstract": paper["abstract"],
        "dissemination": paper["dissemination"],
        "audience": paper["audience"]
    })

with open("test_papers_formatted.json", "w", encoding="utf-8") as f:
    json.dump(output, f, ensure_ascii=False, indent=2)
