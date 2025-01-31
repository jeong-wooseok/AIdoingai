# 포괄적인 SSH 설정 가이드: Windows 클라이언트 및 Ubuntu 서버

## Windows 클라이언트 설정

### 1. SSH 키 생성

1. PowerShell을 관리자 권한으로 실행합니다.

2. SSH 키 생성:
   ```powershell
   ssh-keygen -t rsa -b 4096 -f C:\Users\masta\.ssh\id_rsa
   ```
   - 암호 설정은 선택사항입니다.

3. 공개 키를 서버에 복사:
   ```powershell
   type C:\Users\masta\.ssh\id_rsa.pub | ssh tw@towoo.iptime.org -p 2222 "mkdir -p ~/.ssh && cat >> ~/.ssh/authorized_keys"
   ```

### 2. SSH 설정 파일 구성

1. `C:\Users\masta\.ssh\config` 파일 편집:
   ```powershell
   notepad C:\Users\masta\.ssh\config
   ```

2. 파일에 다음 내용 추가:
   ```
   Host towoo.iptime.org
     HostName towoo.iptime.org
     User tw
     Port 2222
     IdentityFile C:\Users\masta\.ssh\id_rsa
   ```

### 3. PowerShell 프로필에 단축 명령어 추가

1. PowerShell 프로필 파일 열기:
   ```powershell
   if (!(Test-Path -Path $PROFILE)) {
       New-Item -ItemType File -Path $PROFILE -Force
   }
   notepad $PROFILE
   ```

2. 프로필에 함수 추가:
   ```powershell
   function sshtw {
       ssh tw@towoo.iptime.org -p 2222
   }
   ```

3. 프로필 다시 로드:
   ```powershell
   . $PROFILE
   ```

## Ubuntu 서버 설정

### 1. SSH 서버 설치 및 구성

1. SSH 서버 설치 (이미 설치되어 있을 수 있음):
   ```bash
   sudo apt update
   sudo apt install openssh-server
   ```

2. SSH 서비스 상태 확인:
   ```bash
   sudo systemctl status ssh
   ```

3. SSH 설정 파일 편집:
   ```bash
   sudo nano /etc/ssh/sshd_config
   ```
   - `Port 2222`로 변경
   - `PasswordAuthentication no`로 설정 (키 기반 인증만 허용)
   - `PubkeyAuthentication yes`로 설정

4. SSH 서비스 재시작:
   ```bash
   sudo systemctl restart ssh
   ```

### 2. 방화벽 설정

1. UFW (Uncomplicated Firewall) 설치 및 활성화:
   ```bash
   sudo apt install ufw
   sudo ufw enable
   ```

2. SSH 포트 개방:
   ```bash
   sudo ufw allow 2222/tcp
   ```

3. 방화벽 상태 확인:
   ```bash
   sudo ufw status
   ```

### 3. 포트 포워딩 설정

1. 라우터 관리 페이지 접속 (일반적으로 192.168.0.1, id및 pw 입력 / 처음에는 보통 admin/admin)

2. 포트 포워딩 또는 가상 서버 설정 찾기

3. 새 규칙 추가:
   - 외부 포트: 2222
   - 내부 포트: 2222
   - 프로토콜: TCP
   - 내부 IP 주소: Ubuntu 서버의 내부 IP

4. 설정 저장 및 적용

### 4. 동적 DNS 설정 (선택사항): IPTIME 공유기에서는 DNS설정도 공유기에서 가능합니다.

1. 동적 DNS 서비스 가입 (예: No-IP, DynDNS)

2. Ubuntu 서버에 DDNS 클라이언트 설치:
   ```bash
   sudo apt install ddclient
   ```

3. DDNS 클라이언트 설정:
   ```bash
   sudo nano /etc/ddclient.conf
   ```
   - DDNS 제공자의 지침에 따라 설정

4. DDNS 클라이언트 시작:
   ```bash
   sudo systemctl start ddclient
   sudo systemctl enable ddclient
   ```

## 사용 방법

Windows PowerShell에서:
```powershell
sshtw
```

## 보안 주의사항

- 정기적으로 SSH 키 및 비밀번호 변경
- 로그인 시도 제한 설정 고려 (예: fail2ban)
- 서버의 소프트웨어를 최신 상태로 유지
- 불필요한 서비스 비활성화
- 정기적인 보안 감사 수행
