Remove-Item Alias:curl -Force -ErrorAction SilentlyContinue

curl -s -X POST http://localhost:8000/api/auth/register -H "Content-Type: application/json" -d "{""email"":""test2@test.com"",""username"":""testuser2"",""password"":""password123""}"

Write-Host ""

curl -s -X POST http://localhost:8000/api/auth/login -H "Content-Type: application/json" -d "{""email"":""test@test.com"",""password"":""password123""}" -c "$env:USERPROFILE\cookies.txt"

Write-Host ""

curl -s http://localhost:8000/api/auth/me -b "$env:USERPROFILE\cookies.txt"

Write-Host ""

curl -s -X POST http://localhost:8000/api/games -H "Content-Type: application/json" -d "{""nba_game_id"":""0052000121"",""q1_start_seconds"":120.0}" -b "$env:USERPROFILE\cookies.txt"

Write-Host ""

curl -s http://localhost:8000/api/games -b "$env:USERPROFILE\cookies.txt"
