#!/usr/bin/env python3
"""
샌드박스 스캐너 테스트 스크립트
다양한 테스트 케이스로 샌드박스 기능을 검증합니다.
"""

import os
import tempfile
import time
from SandboxScanner import SandboxScanner


def create_test_files():
    """테스트용 파일 생성"""
    test_dir = tempfile.mkdtemp(prefix='sandbox_test_')
    print(f"\n📁 테스트 디렉토리: {test_dir}\n")

    test_cases = []

    # 테스트 케이스 1: 정상 파일
    print("1️⃣  정상 파일 생성...")
    safe_file = os.path.join(test_dir, "safe_script.py")
    with open(safe_file, 'w') as f:
        f.write("""#!/usr/bin/env python3
print("Hello, World!")
print("This is a safe script.")
x = 1 + 1
print(f"1 + 1 = {x}")
""")
    os.chmod(safe_file, 0o755)
    test_cases.append(('정상 파일', safe_file, False))
    print(f"   ✅ {safe_file}")

    # 테스트 케이스 2: 파일 생성 스크립트
    print("\n2️⃣  파일 생성 스크립트...")
    file_creator = os.path.join(test_dir, "file_creator.py")
    with open(file_creator, 'w') as f:
        f.write("""#!/usr/bin/env python3
import os
import tempfile

# 여러 파일 생성
for i in range(5):
    temp_file = tempfile.NamedTemporaryFile(mode='w', delete=False, prefix=f'test_{i}_')
    temp_file.write(f"Test file {i}")
    temp_file.close()
    print(f"Created: {temp_file.name}")

print("File creation test completed")
""")
    os.chmod(file_creator, 0o755)
    test_cases.append(('파일 생성 스크립트', file_creator, True))
    print(f"   ✅ {file_creator}")

    # 테스트 케이스 3: 프로세스 생성 스크립트
    print("\n3️⃣  프로세스 생성 스크립트...")
    process_creator = os.path.join(test_dir, "process_creator.py")
    with open(process_creator, 'w') as f:
        f.write("""#!/usr/bin/env python3
import subprocess
import sys

# 자식 프로세스 생성
try:
    result = subprocess.run(['echo', 'Hello from subprocess'],
                          capture_output=True, text=True, timeout=5)
    print(f"Subprocess output: {result.stdout}")

    result = subprocess.run(['ls', '-la'],
                          capture_output=True, text=True, timeout=5)
    print(f"Directory listing completed")
except Exception as e:
    print(f"Error: {e}")

print("Process creation test completed")
""")
    os.chmod(process_creator, 0o755)
    test_cases.append(('프로세스 생성 스크립트', process_creator, True))
    print(f"   ✅ {process_creator}")

    # 테스트 케이스 4: 의심스러운 키워드 포함
    print("\n4️⃣  의심스러운 키워드 포함 파일...")
    suspicious_file = os.path.join(test_dir, "suspicious.py")
    with open(suspicious_file, 'w') as f:
        f.write("""#!/usr/bin/env python3
# This is a test file with suspicious keywords
# for antivirus testing purposes only

import os

# Fake malware simulation (not real malware)
keywords = ['encrypt', 'decrypt', 'ransom', 'bitcoin', 'payload']
keywords += ['backdoor', 'keylog', 'password', 'credential']

print("Suspicious keyword test file")
print("This file contains suspicious patterns for testing")
print("Keywords:", keywords)

# Simulate some operations
data = "Test data for encryption simulation"
print(f"Data: {data}")
print("This is NOT real malware - just a test file")
""")
    os.chmod(suspicious_file, 0o755)
    test_cases.append(('의심스러운 키워드', suspicious_file, True))
    print(f"   ✅ {suspicious_file}")

    # 테스트 케이스 5: 무한 루프 (타임아웃 테스트)
    print("\n5️⃣  타임아웃 테스트 파일...")
    timeout_file = os.path.join(test_dir, "timeout_test.py")
    with open(timeout_file, 'w') as f:
        f.write("""#!/usr/bin/env python3
import time

print("Starting infinite loop test...")
counter = 0

while True:
    counter += 1
    if counter % 10 == 0:
        print(f"Loop iteration: {counter}")
    time.sleep(0.1)
""")
    os.chmod(timeout_file, 0o755)
    test_cases.append(('타임아웃 테스트', timeout_file, True))
    print(f"   ✅ {timeout_file}")

    # 테스트 케이스 6: 높은 CPU 사용
    print("\n6️⃣  CPU 집약적 스크립트...")
    cpu_intensive = os.path.join(test_dir, "cpu_test.py")
    with open(cpu_intensive, 'w') as f:
        f.write("""#!/usr/bin/env python3
import time

print("Starting CPU intensive operation...")

# CPU 집약적 계산
result = 0
for i in range(1000000):
    result += i ** 2
    if i % 100000 == 0:
        print(f"Progress: {i}")

print(f"Final result: {result}")
print("CPU test completed")
""")
    os.chmod(cpu_intensive, 0o755)
    test_cases.append(('CPU 집약적', cpu_intensive, True))
    print(f"   ✅ {cpu_intensive}")

    return test_dir, test_cases


def run_tests():
    """테스트 실행"""
    print("=" * 80)
    print("🧪 샌드박스 바이러스 스캐너 테스트")
    print("=" * 80)

    # 테스트 파일 생성
    test_dir, test_cases = create_test_files()

    results = []

    # 각 테스트 케이스 실행
    for idx, (name, file_path, execute) in enumerate(test_cases, 1):
        print("\n" + "=" * 80)
        print(f"🔍 테스트 {idx}/{len(test_cases)}: {name}")
        print("=" * 80)

        # 스캐너 생성
        scanner = SandboxScanner(timeout=10, monitor_interval=0.5)

        # 스캔 실행
        start_time = time.time()
        result = scanner.scan_file(file_path, execute=execute)
        duration = time.time() - start_time

        if result:
            print(f"\n✅ 테스트 완료")
            print(f"   위협 수준: {result['threat_level']}/100")
            print(f"   위협 등급: {result['threat_category']}")
            print(f"   스캔 시간: {duration:.2f}초")

            results.append({
                'name': name,
                'threat_level': result['threat_level'],
                'threat_category': result['threat_category'],
                'duration': duration,
                'success': True
            })
        else:
            print(f"\n❌ 테스트 실패")
            results.append({
                'name': name,
                'success': False
            })

        time.sleep(1)

    # 최종 결과 요약
    print("\n" + "=" * 80)
    print("📊 테스트 결과 요약")
    print("=" * 80)

    print(f"\n{'테스트 케이스':<30} {'위협 수준':<15} {'위협 등급':<15} {'시간':<10}")
    print("-" * 80)

    for result in results:
        if result['success']:
            print(f"{result['name']:<30} {result['threat_level']:>3}/100      "
                  f"{result['threat_category']:<15} {result['duration']:>6.2f}초")
        else:
            print(f"{result['name']:<30} {'실패':<15}")

    print("\n" + "=" * 80)

    # 통계
    successful = sum(1 for r in results if r['success'])
    print(f"\n✅ 성공: {successful}/{len(results)}")
    print(f"❌ 실패: {len(results) - successful}/{len(results)}")

    if successful > 0:
        avg_threat = sum(r['threat_level'] for r in results if r['success']) / successful
        avg_time = sum(r['duration'] for r in results if r['success']) / successful
        print(f"📊 평균 위협 수준: {avg_threat:.1f}/100")
        print(f"⏱️  평균 스캔 시간: {avg_time:.2f}초")

    print("\n" + "=" * 80)
    print(f"🗑️  테스트 디렉토리: {test_dir}")
    print("   (테스트 후 수동으로 삭제하거나 자동 정리됩니다)")
    print("=" * 80)


def quick_test():
    """빠른 테스트 - 정상 파일 하나만"""
    print("🚀 빠른 테스트 시작...\n")

    # 간단한 테스트 파일 생성
    test_file = tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False)
    test_file.write("""#!/usr/bin/env python3
print("Quick test script")
print("This is a simple test")
""")
    test_file.close()
    os.chmod(test_file.name, 0o755)

    print(f"테스트 파일: {test_file.name}\n")

    # 스캔
    scanner = SandboxScanner(timeout=5)
    result = scanner.scan_file(test_file.name, execute=True)

    if result:
        print(f"\n✅ 빠른 테스트 완료")
        print(f"   위협 수준: {result['threat_level']}/100")
        print(f"   위협 등급: {result['threat_category']}")
    else:
        print("\n❌ 테스트 실패")

    # 정리
    try:
        os.unlink(test_file.name)
    except:
        pass


if __name__ == '__main__':
    import sys

    if len(sys.argv) > 1 and sys.argv[1] == '--quick':
        quick_test()
    else:
        run_tests()
