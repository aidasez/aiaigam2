@echo off
git config --global credential.helper manager
echo Running ai_goalie.project.py...
python C:\aigoalie\ai_goalie.project.py

python C:\aigoalie\github.py

echo All scripts finished.
pause