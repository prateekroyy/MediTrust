Create file:

notepad SETUP.md


Paste instructions:

# MediTrust – Local Setup Instructions

This project is a hackathon MVP.

## Prerequisites
- Python 3.10+
- Git

## Setup
1. Clone repo


git clone https://github.com/prateekroyy/MediTrust.git

cd MediTrust


2. Create virtual environment


python -m venv venv


3. Activate
- Windows
  ```
  .\venv\Scripts\Activate.ps1
  ```
- macOS/Linux
  ```
  source venv/bin/activate
  ```

4. Install dependencies


pip install -r requirements.txt


5. Create `.env`:


MASTER_KEY=your64hexkey


6. Run tests


python test_integration.py


7. Run API


uvicorn app:app --reload

Save & close.