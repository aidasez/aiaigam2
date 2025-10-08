import os
import pandas as pd
from pathlib import Path
from datetime import datetime, timedelta
import calendar
import subprocess

# --- Configuration ---
today = datetime.now()

# Get the script's directory
SCRIPT_DIR = Path(__file__).parent.resolve()

def get_month_info():
    """Returns current month name and total days in month"""
    month_name = today.strftime("%B")
    _, num_days = calendar.monthrange(today.year, today.month)
    return month_name, num_days

def get_day_folder(day_num):
    """Return folder path for a specific day (YYYY-MM-DD)"""
    day_date = datetime(today.year, today.month, day_num)
    folder_name = day_date.strftime("%Y-%m-%d")
    folder_path = SCRIPT_DIR / folder_name
    folder_path.mkdir(exist_ok=True)
    return folder_path

def get_save_path(day_num, source_name="combined_confidence", ext="xlsx"):
    """Return path for data file for a specific day"""
    folder = get_day_folder(day_num)
    filename = f"{day_num:02d}_{source_name}.{ext}"
    return folder / filename

def create_html_table_row(row):
    fixture = row.get('Fixture', 'N/A')
    pick = row.get('Pick', 'N/A')

    def format_conf(value):
        if pd.isna(value) or str(value).strip() == '':
            return '<td class="px-6 py-4 text-center text-gray-400">N/A</td>'
        s = str(value).strip()
        display = s if s.endswith('%') else f"{s}%"
        return f'<td class="px-6 py-4 text-center font-semibold text-blue-600">{display}</td>'

    return f"""
    <tr class="bg-white border-b hover:bg-gray-50 transition-colors duration-150">
        <td class="px-6 py-4 font-medium text-gray-900 whitespace-nowrap">{fixture}</td>
        <td class="px-6 py-4">{pick}</td>
        {format_conf(row.get('AI_Confidence'))}
        {format_conf(row.get('OLBG_Confidence'))}
        {format_conf(row.get('Oddspedia_Confidence'))}
    </tr>
    """

def generate_day_html(day_num):
    """Generates HTML for a specific day"""
    data_file = get_save_path(day_num)
    day_folder = get_day_folder(day_num)

    if not data_file.exists():
        print(f"Skipping {day_folder / data_file.name}: file not found.")
        return

    try:
        df = pd.read_excel(data_file)
    except Exception as e:
        print(f"Failed to read {data_file}: {e}")
        return

    table_rows = []
    for _, row in df.iterrows():
        if all(col in row for col in ['Fixture', 'Pick', 'AI_Confidence', 'OLBG_Confidence', 'Oddspedia_Confidence']):
            table_rows.append(create_html_table_row(row))

    all_rows = "".join(table_rows)
    html_file = day_folder / f"{day_num:02d}_predictions.html"

    html_content = f"""
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{day_num:02d} Predictions</title>
<script src="https://cdn.tailwindcss.com"></script>
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">
<style>body{{font-family:'Inter',sans-serif;min-height:100vh;background:#f7f9fb;}}</style>
</head>
<body class="flex flex-col">
<div class="container mx-auto p-4 sm:p-6 lg:p-8 flex-grow">
<header class="text-center mb-8 bg-white p-6 rounded-xl shadow-md">
<h1 class="text-3xl sm:text-4xl font-extrabold text-indigo-700">Football Predictions</h1>
<p class="text-md text-gray-600 mt-2">Confidence Levels (Auto-generated)</p>
</header>

<div class="bg-white rounded-xl shadow-lg overflow-hidden">
<div class="overflow-x-auto">
<table class="w-full text-sm text-left text-gray-600">
<thead class="text-xs text-gray-700 uppercase bg-indigo-50/70 border-b border-indigo-200">
<tr>
<th class="px-6 py-3 min-w-[250px] font-bold text-indigo-800">Fixture</th>
<th class="px-6 py-3 font-bold text-indigo-800">Pick</th>
<th class="px-6 py-3 text-center font-bold text-indigo-800">AI Confidence</th>
<th class="px-6 py-3 text-center font-bold text-indigo-800">OLBG Confidence</th>
<th class="px-6 py-3 text-center font-bold text-indigo-800">Oddspedia Confidence</th>
</tr>
</thead>
<tbody>
{all_rows if all_rows else '<tr><td colspan="5" class="text-center p-8 text-gray-500">No data available</td></tr>'}
</tbody>
</table>
</div>
</div>
</div>

<footer class="text-center p-4 mt-auto text-sm text-gray-500 bg-white shadow-inner border-t border-gray-200">
<p>Auto-generated report</p>
</footer>
</body>
</html>
"""

    with open(html_file, "w", encoding="utf-8") as f:
        f.write(html_content)
    print(f"Generated {html_file}")

def generate_index_file():
    month_name, num_days = get_month_info()
    button_html = ""
    for day in range(1, today.day + 1):
        day_folder = get_day_folder(day)
        html_file = day_folder / f"{day:02d}_predictions.html"
        if html_file.exists():
            button_html += f"""
<a href="{html_file.name}" class="w-full py-4 px-6 bg-green-600 hover:bg-green-700 text-white font-bold text-lg rounded-xl shadow-lg transition duration-300 transform hover:scale-[1.03] text-center">
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

def push_to_github():
    try:
        subprocess.run(["git", "add", "."], check=True, capture_output=True, text=True)
        commit_msg = f"Auto-generated predictions {today.strftime('%Y-%m-%d')}"
        result = subprocess.run(["git", "diff", "--cached", "--exit-code"], capture_output=True, text=True)
        if result.returncode == 0:
            print("Git: No changes to commit.")
            return
        subprocess.run(["git", "commit", "-m", commit_msg], check=True, capture_output=True, text=True)
        subprocess.run(["git", "push", "origin", "main"], check=True, capture_output=True, text=True)
        print("Git: Successfully pushed to GitHub.")
    except subprocess.CalledProcessError as e:
        print(f"Git error: {e.stderr}")

def main():
    # Generate HTML for all days from 1st to today
    for day in range(1, today.day + 1):
        generate_day_html(day)
    generate_index_file()
    push_to_github()

if __name__ == "__main__":
    main()
