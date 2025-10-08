import os
import pandas as pd
from pathlib import Path
from datetime import datetime
import subprocess
today = datetime.now().strftime("%d")
today_folder = datetime.now().strftime("%Y-%m-%d")
# --- Configuration ---
# NOTE: Using .xlsx as specified in your original code. 
# Pandas is used to read this binary file type.
def get_save_path(source_name):
    os.makedirs(today_folder, exist_ok=True)
    return os.path.join(today_folder, f"{source_name}")

CSV_FILE_PATH = get_save_path(f'{today}_combined_confidence.xlsx')

HTML_OUTPUT_PATH = get_save_path(f'{today}_predictions.html')
# -------------------

# Get the absolute path of the directory containing the current script file
# This is crucial for running the script reliably from any location (e.g., Colab, GitHub Actions)
SCRIPT_DIR = Path(__file__).parent.resolve()
FULL_FILE_PATH = SCRIPT_DIR / CSV_FILE_PATH


def create_html_table_row(row):
    """Formats a single row of data (from a Pandas Series) into an HTML table row."""
    # Pandas row data is accessed like a dictionary
    fixture = row.get('Fixture', 'N/A')
    pick = row.get('Pick', 'N/A')
    
    # Helper to format confidence values
    def format_confidence(value):
        # Handle NaN values (which can occur when reading Excel/CSV)
        if pd.isna(value) or str(value).strip() == '':
            return '<td class="px-6 py-4 text-center text-gray-400">N/A</td>'
        
        # Ensure value is converted to a string for strip() and f-string
        str_value = str(value).strip()
        
        # Check if it contains a percentage sign, if not, add one for display
        display_value = str_value if str_value.endswith('%') else f"{str_value}%"
        
        return f'<td class="px-6 py-4 text-center font-semibold text-blue-600">{display_value}</td>'

    ai_confidence = format_confidence(row.get('AI_Confidence'))
    olbg_confidence = format_confidence(row.get('OLBG_Confidence'))
    oddspedia_confidence = format_confidence(row.get('Oddspedia_Confidence'))

    return f"""
    <tr class="bg-white border-b hover:bg-gray-50 transition-colors duration-150">
        <td class="px-6 py-4 font-medium text-gray-900 whitespace-nowrap">{fixture}</td>
        <td class="px-6 py-4">{pick}</td>
        {ai_confidence}
        {olbg_confidence}
        {oddspedia_confidence}
    </tr>
    """

def generate_html_file():
    """Reads the Excel/CSV file using Pandas and generates a complete HTML file."""
    
    # 1. Check if the file exists
    if not FULL_FILE_PATH.exists():
        print(f"Error: The file '{CSV_FILE_PATH}' was not found at '{FULL_FILE_PATH}'.")
        print("Please ensure the data file is in the same directory as this script.")
        return

    data_df = pd.DataFrame()
    
    # 2. Read the file using Pandas
    try:
        # Use pandas based on the file extension
        if CSV_FILE_PATH.endswith('.xlsx'):
            print(f"Reading Excel file: {CSV_FILE_PATH}")
            data_df = pd.read_excel(FULL_FILE_PATH)
        elif CSV_FILE_PATH.endswith('.csv'):
            print(f"Reading CSV file: {CSV_FILE_PATH}. Trying common encodings...")
            # Attempt to handle common non-UTF-8 files robustly
            try:
                data_df = pd.read_csv(FULL_FILE_PATH, encoding='utf-8')
            except UnicodeDecodeError:
                # Fallback to Latin-1/Windows-1252, which often resolves the 0xc7 error
                data_df = pd.read_csv(FULL_FILE_PATH, encoding='windows-1252')
        else:
            print(f"Error: Unsupported file extension for '{CSV_FILE_PATH}'. Must be .csv or .xlsx.")
            return

    except Exception as e:
        print(f"An error occurred while reading the data file with Pandas: {e}")
        return

    # 3. Generate HTML rows
    table_rows_html = []
    # Iterate over dataframe rows, converting each row to a dictionary/Series for processing
    for _, row in data_df.iterrows():
        # Ensure all required columns are present; otherwise, skip the row
        if all(col in row for col in ['Fixture', 'Pick', 'AI_Confidence', 'OLBG_Confidence', 'Oddspedia_Confidence']):
            table_rows_html.append(create_html_table_row(row))
        else:
            print(f"Skipping row due to missing required columns: {row.to_dict()}")

    # 4. Assemble HTML structure
    all_rows = "".join(table_rows_html)

    html_template = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Football Predictions Confidence</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">
    <style>
        body {{
            font-family: 'Inter', sans-serif;
            min-height: 100vh;
        }}
    </style>
</head>
<body class="bg-gray-100 text-gray-800 flex flex-col">

    <div class="container mx-auto p-4 sm:p-6 lg:p-8 flex-grow">
        <header class="text-center mb-8 bg-white p-6 rounded-xl shadow-md">
            <h1 class="text-3xl sm:text-4xl font-extrabold text-indigo-700">Football Predictions</h1>
            <p class="text-md text-gray-600 mt-2">Confidence Levels from Various Sources (Auto-generated)</p>
        </header>

        <div class="bg-white rounded-xl shadow-lg overflow-hidden">
            <div class="overflow-x-auto">
                <table class="w-full text-sm text-left text-gray-600">
                    <thead class="text-xs text-gray-700 uppercase bg-indigo-50/70 border-b border-indigo-200">
                        <tr>
                            <th scope="col" class="px-6 py-3 min-w-[250px] font-bold text-indigo-800">Fixture</th>
                            <th scope="col" class="px-6 py-3 font-bold text-indigo-800">Pick</th>
                            <th scope="col" class="px-6 py-3 text-center font-bold text-indigo-800">AI Confidence</th>
                            <th scope="col" class="px-6 py-3 text-center font-bold text-indigo-800">OLBG Confidence</th>
                            <th scope="col" class="px-6 py-3 text-center font-bold text-indigo-800">Oddspedia Confidence</th>
                        </tr>
                    </thead>
                    <tbody>
                        {all_rows if all_rows else '<tr><td colspan="5" class="text-center p-8 text-gray-500">No data found in the data file. Please ensure the file contains data.</td></tr>'}
                    </tbody>
                </table>
            </div>
        </div>
    </div>
    
    <footer class="text-center p-4 mt-auto text-sm text-gray-500 bg-white shadow-inner border-t border-gray-200">
        <p>This report was automatically generated by a Python script using Pandas for robust file processing.</p>
    </footer>

</body>
</html>
"""

    # 5. Write the final HTML content to the output file
    try:
        # Always write HTML using 'utf-8' encoding
        with open(SCRIPT_DIR / HTML_OUTPUT_PATH, 'w', encoding='utf-8') as f:
            f.write(html_template)
        print(f"Successfully generated HTML report: '{HTML_OUTPUT_PATH}'")
    except Exception as e:
        print(f"An error occurred while writing the HTML file: {e}")

def push_to_github():
    print("\nStarting Git push process...")
    
    try:
        # 1. Add all changes (index.html and any new/modified daily files)
        subprocess.run(["git", "add", f"{SCRIPT_DIR / HTML_OUTPUT_PATH}"], check=True, capture_output=True, text=True)
        print("Git: Staged index.html.")
        
        # 2. Commit changes with a date-stamped message
        today = datetime.now().strftime("%d")
        commit_message = f"Auto-generated p file update {today}"
        
        # Check if there's anything to commit before attempting the commit
        result = subprocess.run(["git", "diff", "--cached", "--exit-code"], capture_output=True, text=True)
        if result.returncode == 0:
            print("Git: No changes to commit.")
            return

        subprocess.run(["git", "commit", "-m", commit_message], check=True, capture_output=True, text=True)
        print(f"Git: Committed changes: '{commit_message}'")
        
        # 3. Push to remote (assuming 'origin' remote and 'main' branch)
        subprocess.run(["git", "push", "origin", "main"], check=True, capture_output=True, text=True)
        print("Git: Successfully pushed to GitHub.")

    except subprocess.CalledProcessError as e:
        print(f"\nERROR: Git command failed.")
        print(f"Command '{e.cmd}' returned non-zero exit status {e.returncode}.")
        print("Please ensure you have Git installed, are in a Git repository, and are logged in to push.")
        print(f"Stdout: {e.stdout}")
        print(f"Stderr: {e.stderr}")
    except FileNotFoundError:
        print("\nERROR: Git executable not found. Please ensure Git is installed and in your system's PATH.")


# This allows the script to be run from the command line
if __name__ == "__main__":
    # Ensure pandas is available when running in an environment like Colab
    try:
        generate_html_file()
        push_to_github()
    except ImportError:
        print("Error: The 'pandas' library is required but not installed.")
        print("Please run: pip install pandas openpyxl")
