import os
from pathlib import Path
from datetime import datetime
import calendar
import pandas as pd
import subprocess

# ----------------- Configuration -----------------
SCRIPT_DIR = Path(__file__).parent.resolve()
today = datetime.now()
today_day = today.day
today_str = today.strftime("%Y-%m-%d")

# Helper: get folder path for a given day number
def get_day_folder(day_num):
    folder_name = today.strftime("%Y-%m") + f"-{day_num:02d}"
    return SCRIPT_DIR / folder_name

# Helper: get save path for a source/file name
def get_save_path(day_num, file_name):
    day_folder = get_day_folder(day_num)
    os.makedirs(day_folder, exist_ok=True)
    return day_folder / file_name

# ----------------- Month Info -----------------
def get_month_info():
    month_name = today.strftime("%B")
    _, num_days = calendar.monthrange(today.year, today.month)
    return month_name, num_days

# ----------------- HTML Table Row -----------------
def create_html_table_row(row):
    fixture = row.get('Fixture', 'N/A')
    pick = row.get('Pick', 'N/A')
    def format_conf(value):
        if pd.isna(value) or str(value).strip() == '':
            return '<td class="px-6 py-4 text-center text-gray-400">N/A</td>'
        s = str(value).strip()
        return f'<td class="px-6 py-4 text-center font-semibold text-blue-600">{s if s.endswith("%") else s+"%"}</td>'
    def format_odds(value):
        if pd.isna(value) or str(value).strip() == '':
            return '<td class="px-6 py-4 text-center text-gray-400">N/A</td>'
        s = str(value).strip()
        return f'<td class="px-6 py-4 text-center font-semibold text-green-600">{value}</td>'
    return f"""
    <tr class="bg-white border-b hover:bg-gray-50 transition-colors duration-150">
        <td class="px-6 py-4 font-medium text-gray-900 whitespace-nowrap">{fixture}</td>
        <td class="px-6 py-4">{pick}</td>
        {format_conf(row.get('AI_Confidence'))}
        {format_conf(row.get('OLBG_Confidence'))}
        {format_conf(row.get('Oddspedia_Confidence'))}
        {format_odds(row.get('Odds'))}
        {format_odds(row.get('Result'))}
    </tr>
    """

# ----------------- Generate Daily HTML -----------------
def generate_html_file(day_num):
    excel_file = get_save_path(day_num, f"{day_num:02d}_combined_confidence.xlsx")
    html_file = get_save_path(day_num, f"{day_num:02d}_predictions.html")

    if not excel_file.exists():
        print(f"Skipping {excel_file}: file not found.")
        return

    try:
        df = pd.read_excel(excel_file)
    except Exception as e:
        print(f"Error reading {excel_file}: {e}")
        return

    rows_html = "".join(create_html_table_row(row) for _, row in df.iterrows())
    html_content = f"""
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Predictions for {day_num:02d}</title>
<script src="https://cdn.tailwindcss.com"></script>
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">
</head>
<body class="bg-gray-100 text-gray-800 flex flex-col">
<div class="container mx-auto p-4 sm:p-6 lg:p-8 flex-grow">
<header class="text-center mb-8 bg-white p-6 rounded-xl shadow-md">
<h1 class="text-3xl sm:text-4xl font-extrabold text-indigo-700">Football Predictions {day_num:02d}</h1>
</header>
<div class="bg-white rounded-xl shadow-lg overflow-hidden">
<div class="overflow-x-auto">
<table class="w-full text-sm text-left text-gray-600">
<thead class="text-xs text-gray-700 uppercase bg-indigo-50/70 border-b border-indigo-200">
<tr>
<th scope="col" class="px-6 py-3 font-bold text-indigo-800">Fixture</th>
<th scope="col" class="px-6 py-3 font-bold text-indigo-800">Pick</th>
<th scope="col" class="px-6 py-3 text-center font-bold text-indigo-800">AI Confidence</th>
<th scope="col" class="px-6 py-3 text-center font-bold text-indigo-800">OLBG Confidence</th>
<th scope="col" class="px-6 py-3 text-center font-bold text-indigo-800">Oddspedia Confidence</th>
<th scope="col" class="px-6 py-3 text-center font-bold text-indigo-800">Odds</th>
<th scope="col" class="px-6 py-3 text-center font-bold text-indigo-800">Result</th>
</tr>
</thead>
<tbody>
{rows_html if rows_html else '<tr><td colspan="5" class="text-center p-8 text-gray-500">No data found.</td></tr>'}
</tbody>
</table>
</div>
</div>
</div>
</body>
</html>
"""
    with open(html_file, "w", encoding="utf-8") as f:
        f.write(html_content)
    print(f"Generated {html_file}")

# ----------------- Generate Index -----------------
def generate_index_file():
    month_name, num_days = get_month_info()
    button_html = ""

    for day in range(1, today_day + 1):
        day_folder = get_day_folder(day)
        html_file = day_folder / f"{day:02d}_predictions.html"
        if html_file.exists():
            # relative path for GitHub Pages
            relative_path = f"{day_folder.name}/{html_file.name}"
            button_html += f"""
<a href="{relative_path}" class="w-full py-4 px-6 bg-green-600 hover:bg-green-700 text-white font-bold text-lg rounded-xl shadow-lg transition duration-300 transform hover:scale-[1.03] text-center">
View {month_name} {day:02d} Predictions
</a>
"""

    index_content = f"""
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{month_name} Predictions Dashboard</title>
<script src="https://cdn.tailwindcss.com"></script>
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&display=swap" rel="stylesheet">
<style>body{{font-family:'Inter',sans-serif;background:#eef2f6;}}</style>
</head>
<body class="min-h-screen flex items-center justify-center p-4">
<div class="w-full max-w-5xl bg-white shadow-2xl rounded-3xl p-8 md:p-12 border border-gray-100">
<header class="text-center mb-10">
<h1 class="text-5xl font-extrabold text-gray-900 mb-3">Forecasts for {month_name}</h1>
<p class="text-xl text-gray-600">Select a day below to view its detailed forecast.</p>
</header>
<div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
{button_html if button_html else '<p class="text-center col-span-full text-gray-500 text-xl py-8">No prediction files found.</p>'}
</div>
<footer class="mt-12 text-center text-sm text-gray-500 pt-6 border-t border-gray-100">
Run the script to generate missing day files.
</footer>
</div>
</body>
</html>
"""
    index_path = SCRIPT_DIR / "index.html"
    with open(index_path, "w", encoding="utf-8") as f:
        f.write(index_content)
    print(f"Generated {index_path}")

# ----------------- Git Push -----------------
# ----------------- Git Push -----------------
def push_to_github():
    """Pushes all generated files and folders to GitHub safely (UTF-8 safe for Windows)."""
    print("\n🚀 Starting Git push process...")

    try:
        # Force UTF-8 for stdout/stderr decoding to avoid cp1252 errors
        env = {**os.environ, "PYTHONIOENCODING": "utf-8"}

        # Stage all changes
        subprocess.run(["git", "add", "."], check=True, capture_output=True, text=True, env=env)
        print("✅ Git: Added all modified and new files.")

        # Check if anything is staged
        diff_check = subprocess.run(["git", "diff", "--cached", "--exit-code"],
                                    capture_output=True, text=True, env=env)
        if diff_check.returncode == 0:
            print("ℹ️  Git: No new changes to commit.")
            return

        # Commit changes
        commit_msg = f"Auto-update predictions and index for {datetime.now().strftime('%Y-%m-%d')}"
        subprocess.run(["git", "commit", "-m", commit_msg], check=True, capture_output=True, text=True, env=env)
        print(f"✅ Git: Committed changes with message: '{commit_msg}'")

        # Push to remote
        subprocess.run(["git", "push", "origin", "main"], check=True, capture_output=True, text=True, env=env)
        print("🎉 Git: Successfully pushed all updated files and folders to GitHub.")

    except subprocess.CalledProcessError as e:
        print("❌ Git command failed!")
        print(f"Command: {e.cmd}")
        print(f"Return code: {e.returncode}")
        print(f"Output:\n{e.stdout}")
        print(f"Error Output:\n{e.stderr}")
    except FileNotFoundError:
        print("❌ Git not found. Please ensure Git is installed and added to PATH.")
    except Exception as e:
        print(f"❌ Unexpected error during Git push: {e}")


# ----------------- Main -----------------
if __name__ == "__main__":
    month_name, num_days = get_month_info()
    # Generate HTML for all days from 1st to today
    for day in range(1, today_day + 1):
        generate_html_file(day)
    # Generate index in root folder
    generate_index_file()
    # Push index to GitHub
    push_to_github()
