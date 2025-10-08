import os
import datetime
import calendar
from datetime import datetime
import subprocess # NEW: Required to run external commands like 'git'
today_folder = datetime.now().strftime("%Y-%m-%d")
def get_save_path(source_name):
    os.makedirs(today_folder, exist_ok=True)
    return os.path.join(today_folder, f"{source_name}_fixtures.xlsx")
# --- Helper function to determine the current month's scope ---
def get_month_info():
    """Returns the current month's name and total number of days."""
    now = datetime.now()
    month_name = now.strftime("%B")  # e.g., "October"
    month_num = now.month
    year = now.year
    # calendar.monthrange returns (weekday_of_first_day, number_of_days)
    _, num_days = calendar.monthrange(year, month_num)
    return month_name, num_days

def generate_prediction_page(day_num, month_name):
    """
    Generates the content for a single day's prediction HTML page (e.g., 05_predictions.html).
    Checks if the file exists and skips generation if it does.
    
    NOTE: This function is currently not called in main() to prevent file generation.
    """
    # Formats the day number with leading zero (e.g., 1 becomes "01")
    day_str = f"{day_num:02d}"
    filename = f"{day_str}_predictions.html"
    filename = os.path.join(today_folder, f"{filename}")
    # CHECK 1: Check if the file already exists. If it does, skip generation.
    if os.path.exists(filename):
        print(f"Skipping {filename}: File already exists. (Not overwritten)")
        return
        
    # We use Tailwind CSS for a clean, responsive design
    content = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{month_name} {day_num} Predictions</title>
    <!-- Load Tailwind CSS -->
    <script src="https://cdn.tailwindcss.com"></script>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&display=swap" rel="stylesheet">
    <style>
        body {{ font-family: 'Inter', sans-serif; background-color: #f7f9fb; }}
    </style>
</head>
<body class="min-h-screen flex items-center justify-center p-4">
    <!-- Centered Prediction Card -->
    <div class="w-full max-w-2xl bg-white shadow-2xl rounded-xl p-8 transition-all duration-300 border border-gray-100">
        <h1 class="text-4xl font-extrabold text-blue-800 mb-6 text-center">Forecast for {month_name} {day_num}</h1>
        <p class="text-gray-700 text-lg mb-8 text-center border-b pb-4">
            Here are the specific insights for {month_name} {day_num}.
        </p>
        
        <!-- Placeholder Content Section -->
        <div class="bg-blue-50 border border-blue-200 rounded-lg p-6 mb-8 shadow-inner">
            <h2 class="text-2xl font-semibold text-blue-700 mb-3">Key Focus Area</h2>
            <p class="text-gray-600">
                The primary theme for {month_name} {day_num} involves clarity and focused execution. Prioritize your three most important tasks and defer less critical items until tomorrow.
            </p>
            <ul class="list-disc list-inside mt-4 text-gray-600">
                <li>Review all communication for potential misunderstandings.</li>
                <li>Allocate dedicated time for deep work.</li>
                <li>Seek expert advice before making major decisions.</li>
            </ul>
        </div>

        <!-- Back Button -->
        <a href="index.html" class="block w-full text-center py-3 px-6 bg-blue-600 hover:bg-blue-700 text-white font-bold rounded-xl shadow-md transition duration-300 transform hover:scale-[1.01] focus:outline-none focus:ring-4 focus:ring-blue-300">
            ← Back to Monthly Overview
        </a>
    </div>
</body>
</html>
"""
    # Specify UTF-8 encoding to prevent UnicodeEncodeError
    with open(filename, "w", encoding="utf-8") as f:
        f.write(content.strip())
    print(f"Generated {filename}")


def generate_index_file():
    """
    Generates the main index.html file.
    Only creates buttons for day files that already exist.
    """
    month_name, num_days = get_month_info()
    button_html = ""
    
    # Iterate through every possible day in the current month
    for day_num in range(1, num_days + 1):
        day_str = f"{day_num:02d}"
        filename = f"{day_str}_predictions.html"
        filename = os.path.join(today_folder, f"{filename}")
        
        # CHECK 2: Only create a button if the prediction file already exists
        if os.path.exists(filename):
            button_html += f"""
        <a href="{filename}" class="w-full py-4 px-6 bg-green-600 hover:bg-green-700 text-white font-bold text-lg rounded-xl shadow-lg transition duration-300 transform hover:scale-[1.03] focus:outline-none focus:ring-4 focus:ring-green-300 text-center">
            View {month_name} {day_num} Predictions
        </a>
"""

    index_content = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{month_name} Predictions Dashboard</title>
    <!-- Load Tailwind CSS -->
    <script src="https://cdn.tailwindcss.com"></script>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&display=swap" rel="stylesheet">
    <style>
        body {{ font-family: 'Inter', sans-serif; background-color: #eef2f6; }}
    </style>
</head>
<body class="min-h-screen flex items-center justify-center p-4">
    <!-- Main Card Container -->
    <div class="w-full max-w-5xl bg-white shadow-2xl rounded-3xl p-8 md:p-12 border border-gray-100">
        <header class="text-center mb-10">
            <h1 class="text-5xl font-extrabold text-gray-900 mb-3">Forecasts for {month_name}</h1>
            <p class="text-xl text-gray-600">Select a day below to view its detailed forecast.</p>
        </header>
        
        <!-- Responsive Button Grid (4 columns for desktop, 2 for tablet, 1 for mobile) -->
        <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
            {button_html if button_html else '<p class="text-center col-span-full text-gray-500 text-xl py-8">No prediction files found for this month.</p>'}
        </div>
        
        <footer class="mt-12 text-center text-sm text-gray-500 pt-6 border-t border-gray-100">
            Run the script to generate missing day files.
        </footer>
    </div>
</body>
</html>
"""
    # Specify UTF-8 encoding to prevent UnicodeEncodeError
    with open("index.html", "w", encoding="utf-8") as f:
        f.write(index_content.strip())
    print("Generated index.html")

def push_to_github():
    """Automatically adds, commits, and pushes generated files to GitHub."""
    print("\nStarting Git push process...")
    
    try:
        # 1. Add all changes (index.html and any new/modified daily files)
        subprocess.run(["git", "add", "index.html"], check=True, capture_output=True, text=True)
        print("Git: Staged index.html.")
        
        # 2. Commit changes with a date-stamped message
        today = datetime.now()
        commit_message = f"Auto-generated index file update {today}"
        
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


def main():
    month_name, num_days = get_month_info()
    print(f"Skipping generation of individual day files for {month_name}.")
    
    # Generate the index page with conditional buttons (only for existing files)
    generate_index_file()
    print("Index file generation complete. Only 'index.html' was updated/created.")
    
    # NEW: Automatically push the generated index file to GitHub
    push_to_github()

# To run this script locally, uncomment the following line:
if __name__ == '__main__':
     main()
