@echo off
call .venv\Scripts\activate
python scripts/sectors/pharmacy/pharmacy_skill.py
python scripts/gen_strategic_report.py --tenant demo-saas
pause.

