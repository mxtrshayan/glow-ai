Set-Location $PSScriptRoot
if (-not (Test-Path ".env")) {
    Write-Error "Missing .env — add GEMINI_API_KEY=your_key"
    exit 1
}
python -m pip install -r requirements.txt -q
python -m uvicorn api.index:app --host 127.0.0.1 --port 8080 --reload
