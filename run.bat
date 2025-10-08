@echo off
git config --global credential.helper manager
echo Running ai_goalie.project.py...
python C:\aigoalie\ai_goalie.project.py

echo Running html_gen.py...
python C:\aigoalie\day_gen.py

echo Running gen.py...
python C:\aigoalie\index_gen.py

echo All scripts finished.
pause