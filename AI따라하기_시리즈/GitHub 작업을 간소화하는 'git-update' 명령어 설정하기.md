# Git Update PowerShell Script 사용 가이드

## 스크립트 생성 및 실행

1. 다음 내용으로 `Git-Update.ps1` 파일을 생성합니다:

```powershell
# Pull the latest changes
git pull

# Add all changes
git add .

# Get current date in YYMMDD format
$current_date = Get-Date -Format "yyMMdd"

# Commit with the current date
git commit -m "${current_date}_update_wooseok"

# Push changes
git push

Write-Host "Git update completed successfully!" -ForegroundColor Green
```

2. PowerShell을 관리자 권한으로 실행합니다.

3. 실행 정책을 변경하여 스크립트 실행을 허용합니다:

```powershell
Set-ExecutionPolicy Bypass -Scope Process -Force
```

4. 스크립트를 실행합니다:

```powershell
.\Git-Update.ps1
```

## 편리한 사용을 위한 설정

### 방법 1: PowerShell 프로필에 함수 추가

1. PowerShell 프로필이 없다면 생성합니다:

```powershell
if (!(Test-Path -Path $PROFILE)) {
    New-Item -ItemType File -Path $PROFILE -Force
}
notepad $PROFILE
```

2. 프로필에 다음 함수를 추가합니다:

```powershell
function git-update {
    Set-ExecutionPolicy Bypass -Scope Process -Force
    & "$HOME\Git-Update.ps1"
}
```

3. PowerShell을 재시작하거나 `.$PROFILE` 명령어로 프로필을 다시 로드합니다.

4. 이제 PowerShell에서 어디서든 `git-update` 명령어로 스크립트를 실행할 수 있습니다.

### 방법 2: PATH에 스크립트 추가

1. `$env:PATH`를 확인하여 PATH에 포함된 디렉토리를 확인합니다.

2. 스크립트를 PATH에 포함된 디렉토리 중 하나로 이동시킵니다 (예: `C:\Windows\System32\`).

3. 이제 PowerShell에서 어디서든 `Git-Update.ps1` 명령어로 스크립트를 실행할 수 있습니다.

## 주의사항

- 실행 정책을 변경하면 시스템의 보안에 영향을 줄 수 있으므로, 신중하게 결정해야 합니다.
- 항상 신뢰할 수 있는 소스의 스크립트만 실행하세요.
- `Set-ExecutionPolicy Bypass -Scope Process -Force` 명령은 현재 PowerShell 세션에서만 적용됩니다. 영구적인 변경을 원한다면 `Set-ExecutionPolicy RemoteSigned` 명령을 사용하는 것을 고려해보세요.
