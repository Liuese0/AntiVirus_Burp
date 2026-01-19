#!/usr/bin/env python3
"""
CloudAntivirusAI.py 샌드박스 기능 테스트
"""

import sys
import os
import tempfile

# VirtualAIScanner만 import해서 테스트
sys.path.insert(0, '/home/user/AntiVirus_Burp')

from CloudAntivirusAI import VirtualAIScanner


def test_sandbox_scan():
    """샌드박스 스캔 기능 테스트"""
    print("=" * 80)
    print("🔒 샌드박스 스캔 기능 테스트")
    print("=" * 80)
    print()

    # 테스트 파일 생성
    print("1️⃣  테스트 파일 생성 중...")
    test_file = tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False)
    test_file.write("""#!/usr/bin/env python3
# 테스트 파일
import os

print("샌드박스 테스트 파일 실행")
print(f"현재 디렉토리: {os.getcwd()}")

# 의심스러운 키워드 (탐지 테스트)
keywords = ['encrypt', 'decrypt', 'password']
print(f"키워드: {keywords}")

print("테스트 완료!")
""")
    test_file.close()
    os.chmod(test_file.name, 0o755)
    print(f"   ✅ {test_file.name}")
    print()

    # VirtualAIScanner 생성
    print("2️⃣  VirtualAIScanner 초기화...")
    scanner = VirtualAIScanner()
    print("   ✅ 초기화 완료")
    print()

    # 샌드박스 스캔 실행
    print("3️⃣  샌드박스 스캔 시작...")
    result = scanner.sandbox_scan(test_file.name, timeout=10, execute=True)
    print()

    # 결과 출력
    if result:
        print("=" * 80)
        print("📊 스캔 결과")
        print("=" * 80)
        print()
        print(f"파일: {test_file.name}")
        print(f"위협 수준: {result['threat_level']}/100")
        print(f"위협 유형: {result['threat_type']}")
        print(f"신뢰도: {result['confidence']}%")
        print()

        if result['behaviors']:
            print(f"탐지된 행동 ({len(result['behaviors'])}건):")
            for behavior in result['behaviors']:
                print(f"  • {behavior}")
            print()

        if result['suspicious_patterns']:
            print(f"의심스러운 패턴 ({len(result['suspicious_patterns'])}건):")
            for pattern in result['suspicious_patterns']:
                print(f"  • {pattern}")
            print()

        if result['execution_log']:
            print("실행 로그:")
            for log in result['execution_log']:
                print(f"  • {log}")
            print()

        print("=" * 80)
        print("✅ 테스트 성공!")
        print("=" * 80)

        return True

    else:
        print("❌ 스캔 실패")
        return False

    # 정리
    try:
        os.unlink(test_file.name)
    except:
        pass


if __name__ == '__main__':
    success = test_sandbox_scan()
    sys.exit(0 if success else 1)
