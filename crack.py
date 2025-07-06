import os
import hashlib
import time

def create_suspicious_test_file():
    """
    백신 프로그램 테스트용 의심스러운 파일 생성
    실제 악성코드가 아닌 테스트 목적의 파일입니다.
    """
    
    # 테스트 파일 경로 (빠른 스캔 대상인 Downloads 폴더)
    downloads_path = os.path.expanduser("~/Downloads")
    test_filename = "crack_keygen_tool.pdf.exe"  # 의심스러운 이중 확장자
    test_file_path = os.path.join(downloads_path, test_filename)
    
    # 의심스러운 콘텐츠 생성 (실제 악성코드 아님)
    suspicious_content = b"""
This is a TEST FILE for antivirus testing purposes only.
=======================================================

FAKE CONTENT FOR TESTING:
Your files have been encrypted by a test simulator!
This is NOT real malware - just for testing detection.

Send Bitcoin to: TEST-ADDRESS-123456789 (FAKE)
DECRYPT_INSTRUCTION: This is a test file only!

Features of this test file:
- Suspicious filename with double extension (.pdf.exe)
- Contains ransomware-like keywords
- Located in Downloads folder
- Small file size to trigger detection

This file is completely safe and created for testing purposes.
The antivirus should detect this as suspicious based on:
1. Filename patterns (crack, keygen)
2. Double extension (.pdf.exe) 
3. Suspicious content keywords
4. Location in Downloads folder

Total expected score: 70-90 points
- Filename analysis: 30 points (crack + keygen patterns)
- Double extension: 25 points
- Dangerous extension (.exe): 15 points  
- Content signatures: 40 points
- Location bonus: 25 points

DELETE THIS FILE AFTER TESTING!
"""
    
    # 파일 생성
    try:
        with open(test_file_path, 'wb') as f:
            f.write(suspicious_content)
        
        print(f"✅ 테스트 파일이 생성되었습니다:")
        print(f"📍 경로: {test_file_path}")
        print(f"📊 파일 크기: {len(suspicious_content)} bytes")
        print(f"🔍 예상 탐지 점수: 70-90점")
        print()
        print("🎯 이 파일은 다음 패턴으로 탐지될 예정입니다:")
        print("  • 파일명: 'crack', 'keygen' 패턴 (30점)")
        print("  • 이중 확장자: .pdf.exe (25점)")
        print("  • 실행파일 확장자: .exe (15점)")
        print("  • 의심스러운 콘텐츠 (40점)")
        print("  • Downloads 폴더 위치 (25점)")
        print()
        print("⚠️  주의: 테스트 완료 후 반드시 파일을 삭제하세요!")
        print("🧪 이제 백신 프로그램에서 '빠른 스캔'을 실행해보세요.")
        
        return test_file_path
        
    except Exception as e:
        print(f"❌ 파일 생성 실패: {e}")
        return None

def create_additional_test_files():
    """추가 테스트 파일들 생성"""
    downloads_path = os.path.expanduser("~/Downloads")
    
    test_files = [
        {
            "name": "virus_scanner.txt.exe",
            "content": b"This is a test file with virus keywords for antivirus testing.",
            "expected_score": "75-85점"
        },
        {
            "name": "hack_tool_2024.scr", 
            "content": b"Hacking tool simulation - completely safe test file for AV testing.",
            "expected_score": "60-70점"
        },
        {
            "name": "malware_sample.doc.exe",
            "content": b"Your files have been encrypted! Send Bitcoin to test-address! DECRYPT_INSTRUCTION: fake",
            "expected_score": "90-100점"
        }
    ]
    
    created_files = []
    
    for file_info in test_files:
        file_path = os.path.join(downloads_path, file_info["name"])
        try:
            with open(file_path, 'wb') as f:
                f.write(file_info["content"])
            created_files.append(file_path)
            print(f"✅ {file_info['name']} - 예상 점수: {file_info['expected_score']}")
        except Exception as e:
            print(f"❌ {file_info['name']} 생성 실패: {e}")
    
    return created_files

def cleanup_test_files():
    """테스트 파일들 정리"""
    downloads_path = os.path.expanduser("~/Downloads")
    test_patterns = ['crack_keygen_tool.pdf.exe', 'virus_scanner.txt.exe', 
                    'hack_tool_2024.scr', 'malware_sample.doc.exe']
    
    cleaned = 0
    for pattern in test_patterns:
        file_path = os.path.join(downloads_path, pattern)
        try:
            if os.path.exists(file_path):
                os.remove(file_path)
                print(f"🗑️ 삭제됨: {pattern}")
                cleaned += 1
        except Exception as e:
            print(f"❌ 삭제 실패 {pattern}: {e}")
    
    print(f"✅ 총 {cleaned}개 테스트 파일이 정리되었습니다.")

if __name__ == "__main__":
    print("🧪 백신 테스트 파일 생성기")
    print("=" * 50)
    print()
    print("다음 중 선택하세요:")
    print("1. 메인 테스트 파일 생성 (신뢰도 70-90점)")
    print("2. 추가 테스트 파일들 생성")
    print("3. 모든 테스트 파일 생성")
    print("4. 테스트 파일 정리/삭제")
    print()
    
    choice = input("선택 (1-4): ").strip()
    
    if choice == "1":
        create_suspicious_test_file()
    elif choice == "2":
        print("\n📁 추가 테스트 파일들 생성 중...")
        create_additional_test_files()
    elif choice == "3":
        print("\n📁 모든 테스트 파일 생성 중...")
        create_suspicious_test_file()
        print()
        create_additional_test_files()
    elif choice == "4":
        print("\n🗑️ 테스트 파일 정리 중...")
        cleanup_test_files()
    else:
        print("❌ 잘못된 선택입니다.")
    
    print("\n" + "=" * 50)
    print("🔍 백신 테스트 방법:")
    print("1. 백신 프로그램 실행")
    print("2. '빠른 스캔' 선택")
    print("3. 신뢰도 임계값을 70으로 설정")
    print("4. 스캔 시작")
    print("5. Downloads 폴더의 테스트 파일들이 탐지되는지 확인")
    print("\n⚠️ 테스트 완료 후 반드시 파일들을 삭제하세요!")