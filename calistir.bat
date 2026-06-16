@echo off
chcp 65001 >nul
cd /d "%~dp0"

echo.
echo  ============================================
echo    APEXDRIVE PRO - PROJE YONETIM SISTEMI
echo  ============================================
echo.

python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo  [HATA] Python bulunamadi!
    echo  Lutfen https://www.python.org adresinden Python yukleyin.
    pause
    exit /b 1
)

echo  [1/3] Gerekli kutuphaneler yukleniyor...
python -m pip install streamlit pandas plotly --quiet

echo  [2/3] Veritabani hazirlaniyor...
if not exist "proje_yonetim.db" (
    python build_db.py
)

echo  [3/3] Uygulama baslatiliyor...
echo.
echo  Tarayicinizda su adres acilacak: http://localhost:8501
echo  Durdurmak icin bu pencerede Ctrl+C basin.
echo.

python -m streamlit run "%~dp0app.py" --server.port 8501

pause
