# 🔒 샌드박스 바이러스 스캐너

격리된 샌드박스 환경에서 의심스러운 파일을 안전하게 실행하고 분석하는 고급 바이러스 검사 도구입니다.

## 📋 목차

- [특징](#특징)
- [시스템 요구사항](#시스템-요구사항)
- [설치](#설치)
- [사용법](#사용법)
  - [CLI 사용](#cli-사용)
  - [GUI 사용](#gui-사용)
  - [Python 모듈로 사용](#python-모듈로-사용)
- [기능 설명](#기능-설명)
- [테스트](#테스트)
- [보안 주의사항](#보안-주의사항)

## ✨ 특징

### 🛡️ 격리된 샌드박스 환경
- 임시 격리 디렉토리에서 파일 실행
- 시스템 리소스 제한
- 실행 타임아웃 설정

### 🔍 다층 분석
- **정적 분석**: 파일 메타데이터, 해시, 의심스러운 패턴 탐지
- **동적 분석**: 실제 실행하여 행동 모니터링

### 📊 실시간 모니터링
- 파일 시스템 변경 감지
- 프로세스 생성 추적
- 네트워크 활동 모니터링
- CPU/메모리 사용량 분석

### 🎯 위협 탐지
- 의심스러운 키워드 및 패턴
- 파일 생성/삭제 행위
- 자식 프로세스 생성
- 네트워크 연결 시도
- 높은 리소스 사용

### 📝 상세 보고서
- JSON 형식의 스캔 결과
- 실행 로그
- 위협 수준 및 권장사항

## 💻 시스템 요구사항

### 필수 요구사항
- Python 3.7 이상
- Linux/Unix 환경 (Ubuntu, Debian, macOS 등)

### 필요한 Python 패키지
```bash
pip install psutil
```

### 선택적 패키지 (GUI 사용 시)
- tkinter (대부분의 Python 설치에 기본 포함)

## 🔧 설치

### 1. 저장소 클론 또는 파일 다운로드
```bash
git clone <repository-url>
cd AntiVirus_Burp
```

### 2. 의존성 설치
```bash
pip install -r requirements.txt
```

또는 수동 설치:
```bash
pip install psutil
```

### 3. 실행 권한 부여
```bash
chmod +x SandboxScanner.py
chmod +x SandboxGUI.py
chmod +x test_sandbox.py
```

## 📖 사용법

### CLI 사용

#### 기본 스캔
```bash
python SandboxScanner.py /path/to/suspicious/file
```

#### 타임아웃 설정
```bash
python SandboxScanner.py /path/to/file --timeout 60
```

#### 정적 분석만 (실행 안 함)
```bash
python SandboxScanner.py /path/to/file --no-execute
```

#### 보고서 저장
```bash
python SandboxScanner.py /path/to/file --output report.json
```

#### 전체 옵션
```bash
python SandboxScanner.py --help
```

### GUI 사용

#### GUI 실행
```bash
python SandboxGUI.py
```

#### GUI 사용 방법
1. **파일 선택**: "파일 찾기" 버튼으로 스캔할 파일 선택
2. **설정 조정**:
   - 실행 타임아웃 설정 (기본: 30초)
   - 동적 분석 활성화/비활성화
3. **스캔 시작**: "🔍 스캔 시작" 버튼 클릭
4. **결과 확인**:
   - **스캔 요약**: 전체 결과 요약
   - **실행 로그**: 상세 실행 로그
   - **상세 분석**: JSON 형식의 전체 데이터
5. **보고서 저장**: "💾 보고서 저장" 버튼으로 결과 저장

### Python 모듈로 사용

```python
from SandboxScanner import SandboxScanner

# 스캐너 생성
scanner = SandboxScanner(timeout=30, monitor_interval=0.5)

# 파일 스캔 (동적 분석 포함)
result = scanner.scan_file('/path/to/file', execute=True)

# 결과 확인
if result:
    print(f"위협 수준: {result['threat_level']}/100")
    print(f"위협 등급: {result['threat_category']}")
    print(f"권장사항: {result['recommendation']}")

    # 보고서 저장
    scanner.save_report(result, 'scan_report.json')
```

#### 정적 분석만
```python
result = scanner.scan_file('/path/to/file', execute=False)
```

#### 커스텀 설정
```python
scanner = SandboxScanner(
    timeout=60,           # 60초 타임아웃
    monitor_interval=1.0  # 1초마다 모니터링
)
```

## 🎯 기능 설명

### 위협 수준 계산

샌드박스 스캐너는 다음 항목을 기반으로 위협 수준을 계산합니다:

| 행동 | 위협 점수 |
|------|-----------|
| 파일 생성 | +5점 |
| 파일 삭제 | +10점 |
| 높은 CPU 사용 (>80%) | +3점 |
| 네트워크 연결 | +15점 |
| 자식 프로세스 생성 | +10점 |
| 의심스러운 패턴 (각) | +8점 |
| 위험한 확장자 | +10점 |
| 실행 타임아웃 | +20점 |
| 대용량 파일 (>100MB) | +5점 |

### 위협 등급

| 위협 수준 | 등급 | 설명 |
|-----------|------|------|
| 0-19 | SAFE | 정상 파일 |
| 20-39 | LOW | 의심스러운 행동 감지 |
| 40-59 | MEDIUM | 주의 필요 |
| 60-79 | HIGH | 격리 권장 |
| 80-100 | CRITICAL | 즉시 격리 및 삭제 권장 |

### 탐지 패턴

샌드박스는 다음 키워드를 탐지합니다:
- 암호화/복호화: `encrypt`, `decrypt`, `ransom`, `bitcoin`
- 백도어: `backdoor`, `payload`, `rootkit`
- 정보 탈취: `keylog`, `password`, `credential`
- 시스템 조작: `shell`, `cmd.exe`, `powershell`, `registry`
- 프로세스 조작: `CreateProcess`, `VirtualAlloc`, `WriteProcessMemory`

## 🧪 테스트

### 전체 테스트 실행
```bash
python test_sandbox.py
```

테스트 케이스:
1. ✅ 정상 파일
2. 📂 파일 생성 스크립트
3. ⚙️  프로세스 생성 스크립트
4. ⚠️  의심스러운 키워드
5. ⏱️  타임아웃 테스트
6. 💻 CPU 집약적 스크립트

### 빠른 테스트
```bash
python test_sandbox.py --quick
```

### 기존 테스트 파일 사용
```bash
# crack.py로 테스트 파일 생성
python crack.py

# 생성된 파일 스캔
python SandboxScanner.py ~/Downloads/crack_keygen_tool.pdf.exe
```

## 🔐 보안 주의사항

### ⚠️ 중요 경고

1. **실제 악성코드 처리 시 주의**
   - 이 샌드박스는 완벽한 격리를 보장하지 않습니다
   - 프로덕션 환경에서는 가상 머신이나 컨테이너 사용 권장
   - 의심스러운 파일은 격리된 네트워크에서만 실행

2. **권한 관리**
   - 샌드박스를 일반 사용자 권한으로 실행
   - root 권한으로 실행하지 마세요
   - 중요한 시스템 파일 경로에서 실행하지 마세요

3. **네트워크 격리**
   - 실제 악성코드 분석 시 네트워크 연결 차단 권장
   - 방화벽 규칙 설정
   - 가상 네트워크 환경 사용

4. **데이터 백업**
   - 중요한 데이터는 백업
   - 샌드박스 테스트 전 시스템 스냅샷 권장

### 🛡️ 권장 사용 환경

- **가상 머신**: VirtualBox, VMware, KVM
- **컨테이너**: Docker, LXC
- **격리된 네트워크**: 오프라인 또는 격리된 VLAN
- **백업 시스템**: 정기적인 스냅샷

### 🔒 제한사항

이 샌드박스는 다음을 완전히 방지하지 못할 수 있습니다:
- 커널 레벨 공격
- 하드웨어 기반 공격
- 샌드박스 탈출 (sandbox escape)
- 타이밍 기반 공격
- 네트워크를 통한 전파

## 📊 출력 예시

### CLI 출력
```
============================================================
[2024-01-19 10:30:45.123] [INFO] 샌드박스 스캔 시작: /path/to/file
============================================================
[2024-01-19 10:30:45.234] [INFO] 샌드박스 환경 생성: /tmp/sandbox_abc123
[2024-01-19 10:30:45.345] [INFO] 정적 분석 시작...
[2024-01-19 10:30:45.456] [INFO] 파일 메타데이터 분석 완료
[2024-01-19 10:30:45.567] [WARNING] 위험한 확장자 감지: .exe
[2024-01-19 10:30:45.678] [INFO] 의심스러운 패턴 발견: encrypt
[2024-01-19 10:30:45.789] [INFO] 동적 분석 시작 (샌드박스 실행)...
============================================================
스캔 완료
위협 수준: 65/100 (HIGH)
권장사항: 격리 권장
스캔 시간: 12.34초
============================================================
```

### JSON 보고서
```json
{
  "file_path": "/path/to/file",
  "threat_level": 65,
  "threat_category": "HIGH",
  "recommendation": "격리 권장",
  "scan_duration": 12.34,
  "detection_details": {
    "behaviors": ["dangerous_extension_.exe"],
    "file_operations": [
      {
        "action": "created",
        "path": "/tmp/sandbox_abc123/test.txt",
        "timestamp": "2024-01-19T10:30:46.123"
      }
    ],
    "suspicious_patterns": [
      {"pattern": "encrypt", "timestamp": "2024-01-19T10:30:45.678"}
    ]
  }
}
```

## 🤝 기여

버그 리포트, 기능 제안, 코드 기여를 환영합니다!

## 📄 라이선스

이 프로젝트는 교육 및 연구 목적으로 제공됩니다.

## 📞 지원

문제가 발생하거나 질문이 있으시면 이슈를 등록해주세요.

---

**⚠️ 면책 조항**: 이 도구는 교육 및 연구 목적으로 제공됩니다. 실제 악성코드 분석 시 전문적인 보안 환경에서 사용하시기 바랍니다. 도구 사용으로 인한 모든 책임은 사용자에게 있습니다.
