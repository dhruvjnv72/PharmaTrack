@echo off
title PharmaTrack - Import Excel Data
echo ================================================
echo   PharmaTrack - Excel Data Importer
echo ================================================
echo.
echo Installing required packages...
pip install openpyxl --quiet
echo.
echo Starting import...
echo.
python import_excel.py
