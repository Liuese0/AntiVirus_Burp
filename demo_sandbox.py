#!/usr/bin/env python3
"""
샌드박스 스캐너 데모
빠른 시작을 위한 간단한 데모 스크립트
"""

import os
import tempfile
from SandboxScanner import SandboxScanner


def demo():
    """샌드박스 스캐너 데모"""
    print("=" * 80)
    print("🔒 샌드박스 바이러스 스캐너 데모")
    print("=" * 80)
    print()

    # 데모 파일 생성
    print("1️⃣  데모 테스트 파일 생성 중...")
    test_file = tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False)
    test_file.write("""#!/usr/bin/env python3
\"\"\"
데모 테스트 파일
샌드박스에서 실행될 간단한 스크립트
\"\"\"

import os
import tempfile
import time

print("샌드박스 데모 스크립트 시작")
print(f"현재 디렉토리: {os.getcwd()}")
print(f"프로세스 ID: {os.getpid()}")

# 파일 생성 (파일 시스템 모니터링 테스트)
temp_file = tempfile.NamedTemporaryFile(mode='w', delete=False, prefix='demo_')
temp_file.write("This is a test file created by sandbox demo")
temp_file.close()
print(f"테스트 파일 생성: {temp_file.name}")

# 약간의 CPU 사용
print("계산 수행 중...")
result = sum(i ** 2 for i in range(10000))
print(f"계산 결과: {result}")

# 의심스러운 키워드 (탐지 테스트)
keywords = ['encrypt', 'decrypt', 'password']
print(f"키워드 목록: {keywords}")

print("데모 스크립트 완료!")
""")
    test_file.close()
    os.chmod(test_file.name, 0o755)
    print(f"   ✅ 테스트 파일: {test_file.name}")
    print()

    # 스캐너 생성
    print("2️⃣  샌드박스 스캐너 초기화...")
    scanner = SandboxScanner(timeout=15, monitor_interval=0.5)
    print("   ✅ 스캐너 준비 완료")
    print()

    # 스캔 실행
    print("3️⃣  샌드박스 스캔 시작...")
    print("   (격리된 환경에서 파일 실행 및 분석 중...)")
    print()

    result = scanner.scan_file(test_file.name, execute=True)

    # 결과 출력
    if result:
        print()
        print("=" * 80)
        print("📊 스캔 결과")
        print("=" * 80)
        print()

        # 기본 정보
        print(f"📁 파일: {result['file_path']}")
        print(f"🔍 스캔 시간: {result['scan_duration']}초")
        print()

        # 위협 수준
        threat_level = result['threat_level']
        if threat_level >= 80:
            color = '🔴'
        elif threat_level >= 60:
            color = '🟠'
        elif threat_level >= 40:
            color = '🟡'
        elif threat_level >= 20:
            color = '🟢'
        else:
            color = '✅'

        print(f"{color} 위협 수준: {threat_level}/100")
        print(f"📊 위협 등급: {result['threat_category']}")
        print(f"💡 권장사항: {result['recommendation']}")
        print()

        # 탐지 상세
        details = result['detection_details']

        if details['behaviors']:
            print(f"🔍 탐지된 행동 ({len(details['behaviors'])}건):")
            for behavior in details['behaviors']:
                print(f"   • {behavior}")
            print()

        if details['file_operations']:
            print(f"📂 파일 작업 ({len(details['file_operations'])}건):")
            for op in details['file_operations'][:3]:
                print(f"   • {op['action']}: {os.path.basename(op['path'])}")
            if len(details['file_operations']) > 3:
                print(f"   ... 외 {len(details['file_operations']) - 3}건")
            print()

        if details['suspicious_patterns']:
            print(f"⚠️  의심스러운 패턴 ({len(details['suspicious_patterns'])}건):")
            for pattern in details['suspicious_patterns'][:5]:
                print(f"   • {pattern['pattern']}")
            if len(details['suspicious_patterns']) > 5:
                print(f"   ... 외 {len(details['suspicious_patterns']) - 5}건")
            print()

        # 보고서 저장
        report_path = scanner.save_report(result)
        if report_path:
            print(f"💾 보고서: {report_path}")
            print()

        print("=" * 80)
        print()

        # 다음 단계 안내
        print("🎯 다음 단계:")
        print()
        print("1. CLI로 파일 스캔:")
        print(f"   python SandboxScanner.py <파일경로>")
        print()
        print("2. GUI 실행:")
        print(f"   python SandboxGUI.py")
        print()
        print("3. 전체 테스트 실행:")
        print(f"   python test_sandbox.py")
        print()
        print("4. 자세한 사용법:")
        print(f"   cat SANDBOX_README.md")
        print()

    else:
        print("❌ 스캔 실패")

    # 정리
    print("=" * 80)
    print(f"🗑️  테스트 파일 정리: {test_file.name}")
    try:
        os.unlink(test_file.name)
        print("   ✅ 정리 완료")
    except:
        print("   ⚠️  수동 삭제 필요")
    print("=" * 80)


if __name__ == '__main__':
    try:
        demo()
    except KeyboardInterrupt:
        print("\n\n⚠️  데모가 중단되었습니다.")
    except Exception as e:
        print(f"\n\n❌ 오류 발생: {e}")
        import traceback
        traceback.print_exc()
