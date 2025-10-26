@echo off
echo Setting up Text Humanizer API...
echo.

echo Activating virtual environment...
call venv\Scripts\activate.bat

echo Installing dependencies...
pip install -r requirements.txt

echo Downloading spaCy language model...
python -m spacy download en_core_web_sm

echo.
echo Setup complete!
echo.
echo To run the server:
echo   uvicorn main:app --reload
echo.
echo Don't forget to create a .env file with your Winston AI token!
echo   WINSTON_AI_TOKEN=your_token_here

pause

