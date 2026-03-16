import json
import urllib.request
import os

# GitHub API URL to fetch all public repositories
url = "https://api.github.com/users/sahajananddigital/repos?per_page=100"
req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})

try:
    with urllib.request.urlopen(req) as response:
        repos = json.loads(response.read().decode())
except Exception as e:
    print("Error fetching repos:", e)
    exit(1)

# Categorization Logic
CATEGORIES = {
    "Server & Hosting": ["cipi", "hestia", "server", "docker", "cloud", "dns", "fossbilling"],
    "WordPress & Plugins": ["wordpress", "wp-", "woocommerce", "elementor", "gutenberg", "quickwp"],
    "Automation & Tools": ["attendance", "certificate", "generator", "automated", "workflow", "script", "labels", "printing"],
    "Business & Management": ["hrm", "erp", "gst", "accounting", "inventory", "project-manager", "billing", "support"],
    "Communication": ["whatsapp", "sms", "chat", "gateway", "messenger"],
    "Education & Social": ["gurukul", "student", "learning", "assignment", "quiz", "satsang", "invitation", "selfie", "photo-frame"]
}

def get_category(repo):
    name = repo['name'].lower()
    desc = (repo.get('description') or "").lower()
    topics = [t.lower() for t in repo.get('topics', [])]
    
    combined_text = name + " " + desc + " " + " ".join(topics)
    
    for category, keywords in CATEGORIES.items():
        if any(kw in combined_text for kw in keywords):
            return category
    return "Other Projects"

# Group repositories
grouped_repos = {}
for repo in repos:
    if repo['name'] in ['sahajananddigital', 'sahajananddigital.github.io']:
        continue
    
    cat = get_category(repo)
    if cat not in grouped_repos:
        grouped_repos[cat] = []
    grouped_repos[cat].append(repo)

# Sort categories (Keep "Other" at the end)
category_order = list(CATEGORIES.keys()) + ["Other Projects"]
sorted_categories = [c for c in category_order if c in grouped_repos]

os.makedirs("projects", exist_ok=True)

sections_html = ""
for category in sorted_categories:
    category_repos = sorted(grouped_repos[category], key=lambda x: (x.get('homepage') is not None and x.get('homepage') != "", x.get('stargazers_count', 0)), reverse=True)
    
    sections_html += f'<h2 class="section-title">{category}</h2>\n<div class="grid">\n'
    
    for repo in category_repos:
        name = repo['name']
        desc = repo.get('description', '') or "No description available."
        html_url = repo.get('html_url', '#')
        homepage = repo.get('homepage', '')
        demo_url = homepage if homepage else html_url
        
        repo_dir = f"projects/{name}"
        os.makedirs(repo_dir, exist_ok=True)
        
        # Detail Page Template
        page_content = f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{name} | Sahajanand Digital</title>
    <style>
        :root {{ --primary: #2563eb; --primary-dark: #1d4ed8; --bg: #f8fafc; --text-main: #0f172a; --text-muted: #64748b; --card-bg: #ffffff; --border: #e2e8f0; }}
        * {{ box-sizing: border-box; margin: 0; padding: 0; }}
        body {{ font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif; background-color: var(--bg); color: var(--text-main); line-height: 1.6; padding: 2rem; }}
        .container {{ max-width: 800px; margin: 0 auto; background: var(--card-bg); padding: 2.5rem; border-radius: 0.5rem; border: 1px solid var(--border); box-shadow: 0 4px 6px rgba(0,0,0,0.05); }}
        h1 {{ color: var(--primary); margin-bottom: 1rem; font-size: 2.5rem; }}
        p {{ margin-bottom: 2rem; color: var(--text-muted); font-size: 1.1rem; }}
        .btn {{ display: inline-block; padding: 0.6rem 1.2rem; background-color: var(--primary); color: white; text-decoration: none; border-radius: 0.375rem; font-weight: 500; margin-right: 1rem; transition: background-color 0.2s; }}
        .btn:hover {{ background-color: var(--primary-dark); }}
        .btn-outline {{ background-color: transparent; color: var(--primary); border: 1px solid var(--primary); }}
        .btn-outline:hover {{ background-color: var(--primary); color: white; }}
        .back-link {{ display: inline-block; margin-top: 3rem; color: var(--primary); text-decoration: none; font-weight: 500; }}
    </style>
</head>
<body>
    <div class="container">
        <span style="color: var(--primary); font-weight: bold; text-transform: uppercase; font-size: 0.8rem;">{category}</span>
        <h1>{name}</h1>
        <p>{desc}</p>
        <div style="margin-top: 2rem;">
            <a href="{demo_url}" class="btn" target="_blank">View Live Demo</a>
            <a href="{html_url}" class="btn btn-outline" target="_blank">Source Code</a>
        </div>
        <a href="../../index.html" class="back-link">&larr; Back to Portfolio</a>
    </div>
</body>
</html>'''
        with open(f"{repo_dir}/index.html", "w") as f:
            f.write(page_content)
            
        sections_html += f'''
        <div class="card">
            <h3><a href="projects/{name}/index.html">{name}</a></h3>
            <p>{desc}</p>
            <div class="card-footer">
                <a href="projects/{name}/index.html">Details &rarr;</a>
                <span style="margin: 0 0.5rem; color: var(--border);">|</span>
                <a href="{demo_url}" target="_blank">Live Demo</a>
            </div>
        </div>'''
    
    sections_html += "</div>\n"

# Final update to index.html
try:
    with open("index.html", "r") as f:
        html = f.read()

    # We now replace everything inside <main> to handle categories
    main_start = html.find('<main>') + 6
    main_end = html.find('</main>')

    if main_start != -1 and main_end != -1:
        new_html = html[:main_start] + "\n" + sections_html + "\n" + html[main_end:]
        with open("index.html", "w") as f:
            f.write(new_html)
        print("Portfolio categorized successfully!")
except Exception as e:
    print(f"Error updating index.html: {e}")
