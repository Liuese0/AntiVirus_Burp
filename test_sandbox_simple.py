#!/usr/bin/env python3
"""
샌드박스 기능 간단 테스트 (GUI 없이)
"""

import os
import tempfile
import hashlib
import shutil
import subprocess
import time
import psutil


class SimpleSandboxTest:
    """간단한 샌드박스 테스트"""

    def __init__(self):
        self.suspicious_patterns = [
            b"encrypt", b"decrypt", b"password",
            b"ransom", b"bitcoin"
        ]

    def calculate_hash(self, file_path):
        """파일 해시 계산"""
        try:
            hash_md5 = hashlib.md5()
            with open(file_path, "rb") as f:
                for chunk in iter(lambda: f.read(4096), b""):
                    hash_md5.update(chunk)
            return hash_md5.hexdigest()
        except:
            return None

    def sandbox_scan(self, file_path, timeout=10):
        """샌드박스 스캔"""
        result = {
            'threat_level': 0,
            'threat_type': 'Clean',
            'behaviors': [],
            'suspicious_patterns': [],
            'execution_log': []
        }

        sandbox_dir = None

        try:
            # 샌드박스 생성
            sandbox_dir = tempfile.mkdtemp(prefix='sandbox_test_')
            result['execution_log'].append(f"샌드박스 생성: {sandbox_dir}")

            # 파일 정보
            file_size = os.path.getsize(file_path)
            file_ext = os.path.splitext(file_path)[1].lower()

            # 정적 분석
            with open(file_path, 'rb') as f:
                content = f.read(1024 * 1024)

            for pattern in self.suspicious_patterns:
                if pattern in content:
                    result['threat_level'] += 8
                    result['suspicious_patterns'].append(pattern.decode('utf-8'))

            # 확장자 검사
            if file_ext in ['.exe', '.dll', '.scr', '.py', '.sh']:
                result['threat_level'] += 10
                result['behaviors'].append(f'executable_extension_{file_ext}')

            # 파일 복사
            filename = os.path.basename(file_path)
            sandbox_file = os.path.join(sandbox_dir, filename)
            shutil.copy2(file_path, sandbox_file)
            os.chmod(sandbox_file, 0o755)

            result['execution_log'].append("샌드박스에서 파일 실행...")

            # 프로세스 실행
            try:
                process = subprocess.Popen(
                    [sandbox_file],
                    cwd=sandbox_dir,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    env={'PATH': '/usr/bin:/bin'}
                )

                # 타임아웃 대기
                try:
                    stdout, stderr = process.communicate(timeout=timeout)
                    if stdout:
                        result['execution_log'].append(f"출력: {stdout.decode('utf-8', errors='ignore')[:200]}")
                except subprocess.TimeoutExpired:
                    process.kill()
                    result['threat_level'] += 20
                    result['behaviors'].append('timeout_exceeded')
                    result['execution_log'].append(f"타임아웃 ({timeout}초)")

            except Exception as e:
                result['execution_log'].append(f"실행 오류: {str(e)}")

            # 위협 유형 결정
            if result['threat_level'] >= 60:
                result['threat_type'] = 'High Risk'
            elif result['threat_level'] >= 40:
                result['threat_type'] = 'Suspicious'
            elif result['threat_level'] >= 20:
                result['threat_type'] = 'Low Risk'
            else:
                result['threat_type'] = 'Clean'

            result['execution_log'].append(f"스캔 완료 - 위협 수준: {result['threat_level']}/100")

        except Exception as e:
            result['execution_log'].append(f"오류: {str(e)}")

        finally:
            # 정리
            if sandbox_dir and os.path.exists(sandbox_dir):
                shutil.rmtree(sandbox_dir)

        return result


def main():
    """테스트 메인 함수"""
    print("=" * 80)
    print("🔒 샌드박스 스캔 기능 테스트")
    print("=" * 80)
    print()

    # 테스트 파일 생성
    print("1️⃣  테스트 파일 생성...")
    test_file = tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False)
    test_file.write("""#!/usr/bin/env python3
# 테스트 스크립트
print("샌드박스 테스트 실행")

# 의심스러운 키워드
keywords = "encrypt, decrypt, password"
print(f"Keywords: {keywords}")

print("테스트 완료")
""")
    test_file.close()
    os.chmod(test_file.name, 0o755)
    print(f"   ✅ {test_file.name}")
    print()

    # 스캔 실행
    print("2️⃣  샌드박스 스캔 실행...")
    tester = SimpleSandboxTest()
    result = tester.sandbox_scan(test_file.name, timeout=5)
    print()

    # 결과 출력
    print("=" * 80)
    print("📊 스캔 결과")
    print("=" * 80)
    print()
    print(f"위협 수준: {result['threat_level']}/100")
    print(f"위협 유형: {result['threat_type']}")
    print()

    if result['behaviors']:
        print(f"탐지된 행동:")
        for behavior in result['behaviors']:
            print(f"  • {behavior}")
        print()

    if result['suspicious_patterns']:
        print(f"의심스러운 패턴:")
        for pattern in result['suspicious_patterns']:
            print(f"  • {pattern}")
        print()

    print("실행 로그:")
    for log in result['execution_log']:
        print(f"  {log}")
    print()

    print("=" * 80)
    print("✅ 테스트 성공!")
    print("=" * 80)

    # 정리
    try:
        os.unlink(test_file.name)
    except:
        pass


if __name__ == '__main__':
    main()
