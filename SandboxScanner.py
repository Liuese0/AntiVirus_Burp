#!/usr/bin/env python3
"""
샌드박스 바이러스 스캐너
격리된 환경에서 의심스러운 파일을 실행하고 행동을 분석합니다.
"""

import os
import sys
import subprocess
import tempfile
import shutil
import time
import json
import hashlib
import threading
import queue
from datetime import datetime
from pathlib import Path
import psutil
import signal

class SandboxScanner:
    """
    샌드박스 환경에서 파일을 안전하게 실행하고 분석하는 클래스
    """

    def __init__(self, timeout=30, monitor_interval=0.5):
        """
        Args:
            timeout: 샌드박스 실행 최대 시간 (초)
            monitor_interval: 모니터링 간격 (초)
        """
        self.timeout = timeout
        self.monitor_interval = monitor_interval
        self.sandbox_dir = None
        self.process = None
        self.monitoring_active = False

        # 탐지 결과 저장
        self.detection_results = {
            'threat_level': 0,  # 0-100
            'behaviors': [],
            'file_operations': [],
            'process_created': [],
            'network_activity': [],
            'registry_changes': [],
            'suspicious_patterns': [],
            'execution_log': []
        }

    def create_sandbox_environment(self):
        """격리된 샌드박스 환경 생성"""
        try:
            # 임시 샌드박스 디렉토리 생성
            self.sandbox_dir = tempfile.mkdtemp(prefix='sandbox_', suffix='_av')

            # 읽기 전용 시스템 디렉토리 마운트 (시뮬레이션)
            sandbox_paths = {
                'bin': os.path.join(self.sandbox_dir, 'bin'),
                'lib': os.path.join(self.sandbox_dir, 'lib'),
                'tmp': os.path.join(self.sandbox_dir, 'tmp'),
                'home': os.path.join(self.sandbox_dir, 'home'),
                'logs': os.path.join(self.sandbox_dir, 'logs')
            }

            for path in sandbox_paths.values():
                os.makedirs(path, exist_ok=True)

            self.log_event(f"샌드박스 환경 생성: {self.sandbox_dir}")
            return True

        except Exception as e:
            self.log_event(f"샌드박스 생성 실패: {e}", level='error')
            return False

    def cleanup_sandbox(self):
        """샌드박스 환경 정리"""
        if self.sandbox_dir and os.path.exists(self.sandbox_dir):
            try:
                shutil.rmtree(self.sandbox_dir)
                self.log_event(f"샌드박스 정리 완료: {self.sandbox_dir}")
            except Exception as e:
                self.log_event(f"샌드박스 정리 실패: {e}", level='error')

    def log_event(self, message, level='info'):
        """이벤트 로깅"""
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]
        log_entry = {
            'timestamp': timestamp,
            'level': level,
            'message': message
        }
        self.detection_results['execution_log'].append(log_entry)
        print(f"[{timestamp}] [{level.upper()}] {message}")

    def copy_file_to_sandbox(self, file_path):
        """파일을 샌드박스로 복사"""
        try:
            if not os.path.exists(file_path):
                self.log_event(f"파일이 존재하지 않음: {file_path}", level='error')
                return None

            filename = os.path.basename(file_path)
            sandbox_file = os.path.join(self.sandbox_dir, 'home', filename)

            shutil.copy2(file_path, sandbox_file)
            self.log_event(f"파일 복사 완료: {filename}")

            return sandbox_file

        except Exception as e:
            self.log_event(f"파일 복사 실패: {e}", level='error')
            return None

    def analyze_file_metadata(self, file_path):
        """파일 메타데이터 분석"""
        try:
            stat_info = os.stat(file_path)
            file_hash = self.calculate_file_hash(file_path)

            metadata = {
                'size': stat_info.st_size,
                'created': datetime.fromtimestamp(stat_info.st_ctime).isoformat(),
                'modified': datetime.fromtimestamp(stat_info.st_mtime).isoformat(),
                'permissions': oct(stat_info.st_mode),
                'md5': file_hash['md5'],
                'sha256': file_hash['sha256']
            }

            self.log_event(f"파일 메타데이터 분석 완료: {file_path}")
            return metadata

        except Exception as e:
            self.log_event(f"메타데이터 분석 실패: {e}", level='error')
            return {}

    def calculate_file_hash(self, file_path):
        """파일 해시 계산"""
        md5_hash = hashlib.md5()
        sha256_hash = hashlib.sha256()

        try:
            with open(file_path, 'rb') as f:
                while chunk := f.read(8192):
                    md5_hash.update(chunk)
                    sha256_hash.update(chunk)

            return {
                'md5': md5_hash.hexdigest(),
                'sha256': sha256_hash.hexdigest()
            }
        except Exception as e:
            self.log_event(f"해시 계산 실패: {e}", level='error')
            return {'md5': '', 'sha256': ''}

    def monitor_file_system(self):
        """파일 시스템 변경 모니터링"""
        initial_files = set()

        if self.sandbox_dir:
            for root, dirs, files in os.walk(self.sandbox_dir):
                for file in files:
                    initial_files.add(os.path.join(root, file))

        while self.monitoring_active:
            time.sleep(self.monitor_interval)

            current_files = set()
            if self.sandbox_dir:
                for root, dirs, files in os.walk(self.sandbox_dir):
                    for file in files:
                        current_files.add(os.path.join(root, file))

            # 새로 생성된 파일
            new_files = current_files - initial_files
            if new_files:
                for file in new_files:
                    self.detection_results['file_operations'].append({
                        'action': 'created',
                        'path': file,
                        'timestamp': datetime.now().isoformat()
                    })
                    self.log_event(f"파일 생성 감지: {file}")
                    self.detection_results['threat_level'] += 5

            # 삭제된 파일
            deleted_files = initial_files - current_files
            if deleted_files:
                for file in deleted_files:
                    self.detection_results['file_operations'].append({
                        'action': 'deleted',
                        'path': file,
                        'timestamp': datetime.now().isoformat()
                    })
                    self.log_event(f"파일 삭제 감지: {file}")
                    self.detection_results['threat_level'] += 10

            initial_files = current_files.copy()

    def monitor_process(self, pid):
        """프로세스 행동 모니터링"""
        try:
            process = psutil.Process(pid)
            initial_connections = set()

            while self.monitoring_active and process.is_running():
                try:
                    # CPU 및 메모리 사용량
                    cpu_percent = process.cpu_percent(interval=0.1)
                    memory_info = process.memory_info()

                    if cpu_percent > 80:
                        self.log_event(f"높은 CPU 사용률 감지: {cpu_percent}%", level='warning')
                        self.detection_results['threat_level'] += 3

                    # 네트워크 연결
                    try:
                        connections = process.connections()
                        for conn in connections:
                            conn_key = (conn.laddr, conn.raddr if conn.raddr else None, conn.status)
                            if conn_key not in initial_connections:
                                self.detection_results['network_activity'].append({
                                    'local_addr': str(conn.laddr),
                                    'remote_addr': str(conn.raddr) if conn.raddr else None,
                                    'status': conn.status,
                                    'timestamp': datetime.now().isoformat()
                                })
                                self.log_event(f"네트워크 연결 감지: {conn.laddr} -> {conn.raddr}")
                                self.detection_results['threat_level'] += 15
                                initial_connections.add(conn_key)
                    except (psutil.AccessDenied, AttributeError):
                        pass

                    # 자식 프로세스
                    try:
                        children = process.children(recursive=True)
                        for child in children:
                            child_info = {
                                'pid': child.pid,
                                'name': child.name(),
                                'cmdline': ' '.join(child.cmdline()),
                                'timestamp': datetime.now().isoformat()
                            }
                            if child_info not in self.detection_results['process_created']:
                                self.detection_results['process_created'].append(child_info)
                                self.log_event(f"자식 프로세스 생성: {child.name()} (PID: {child.pid})")
                                self.detection_results['threat_level'] += 10
                    except (psutil.AccessDenied, psutil.NoSuchProcess):
                        pass

                    time.sleep(self.monitor_interval)

                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    break

        except Exception as e:
            self.log_event(f"프로세스 모니터링 오류: {e}", level='error')

    def detect_suspicious_patterns(self, file_path):
        """파일 내용에서 의심스러운 패턴 탐지"""
        suspicious_keywords = [
            b'encrypt', b'decrypt', b'ransom', b'bitcoin', b'payload',
            b'backdoor', b'keylog', b'password', b'credential', b'rootkit',
            b'shell', b'cmd.exe', b'powershell', b'/bin/sh', b'/bin/bash',
            b'registry', b'regedit', b'HKEY_', b'CreateProcess',
            b'VirtualAlloc', b'WriteProcessMemory', b'CreateRemoteThread'
        ]

        try:
            with open(file_path, 'rb') as f:
                content = f.read()

            for keyword in suspicious_keywords:
                if keyword in content:
                    pattern = {
                        'pattern': keyword.decode('utf-8', errors='ignore'),
                        'timestamp': datetime.now().isoformat()
                    }
                    self.detection_results['suspicious_patterns'].append(pattern)
                    self.log_event(f"의심스러운 패턴 발견: {pattern['pattern']}")
                    self.detection_results['threat_level'] += 8

        except Exception as e:
            self.log_event(f"패턴 분석 오류: {e}", level='error')

    def execute_in_sandbox(self, file_path, args=None):
        """샌드박스에서 파일 실행"""
        try:
            sandbox_file = self.copy_file_to_sandbox(file_path)
            if not sandbox_file:
                return False

            # 실행 권한 부여
            os.chmod(sandbox_file, 0o755)

            # 실행 명령 구성
            cmd = [sandbox_file]
            if args:
                cmd.extend(args)

            self.log_event(f"샌드박스에서 파일 실행: {' '.join(cmd)}")

            # 모니터링 시작
            self.monitoring_active = True

            # 파일 시스템 모니터링 스레드
            fs_monitor_thread = threading.Thread(target=self.monitor_file_system)
            fs_monitor_thread.daemon = True
            fs_monitor_thread.start()

            # 프로세스 실행
            try:
                self.process = subprocess.Popen(
                    cmd,
                    cwd=os.path.join(self.sandbox_dir, 'home'),
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    env={'PATH': '/usr/bin:/bin', 'HOME': os.path.join(self.sandbox_dir, 'home')}
                )

                # 프로세스 모니터링 스레드
                process_monitor_thread = threading.Thread(
                    target=self.monitor_process,
                    args=(self.process.pid,)
                )
                process_monitor_thread.daemon = True
                process_monitor_thread.start()

                # 타임아웃 대기
                try:
                    stdout, stderr = self.process.communicate(timeout=self.timeout)

                    if stdout:
                        self.log_event(f"프로세스 출력: {stdout.decode('utf-8', errors='ignore')[:500]}")
                    if stderr:
                        self.log_event(f"프로세스 에러: {stderr.decode('utf-8', errors='ignore')[:500]}", level='warning')

                except subprocess.TimeoutExpired:
                    self.log_event(f"실행 타임아웃 ({self.timeout}초)", level='warning')
                    self.process.kill()
                    self.detection_results['threat_level'] += 20
                    self.detection_results['behaviors'].append('timeout_exceeded')

            except Exception as e:
                self.log_event(f"프로세스 실행 오류: {e}", level='error')
                self.detection_results['threat_level'] += 25
                return False

            finally:
                self.monitoring_active = False
                time.sleep(1)  # 모니터링 스레드 종료 대기

            return True

        except Exception as e:
            self.log_event(f"샌드박스 실행 실패: {e}", level='error')
            return False

    def analyze_static(self, file_path):
        """정적 분석 수행"""
        self.log_event("정적 분석 시작...")

        # 메타데이터 분석
        metadata = self.analyze_file_metadata(file_path)

        # 의심스러운 패턴 탐지
        self.detect_suspicious_patterns(file_path)

        # 파일 크기 검사
        if metadata.get('size', 0) > 100 * 1024 * 1024:  # 100MB 초과
            self.log_event("대용량 파일 감지", level='warning')
            self.detection_results['threat_level'] += 5

        # 파일 확장자 검사
        ext = os.path.splitext(file_path)[1].lower()
        dangerous_exts = ['.exe', '.dll', '.scr', '.bat', '.cmd', '.vbs', '.ps1', '.sh']
        if ext in dangerous_exts:
            self.log_event(f"위험한 확장자 감지: {ext}", level='warning')
            self.detection_results['threat_level'] += 10
            self.detection_results['behaviors'].append(f'dangerous_extension_{ext}')

        return metadata

    def scan_file(self, file_path, execute=True):
        """
        파일 전체 스캔 (정적 + 동적 분석)

        Args:
            file_path: 스캔할 파일 경로
            execute: True면 샌드박스에서 실행, False면 정적 분석만

        Returns:
            dict: 스캔 결과
        """
        self.log_event("=" * 60)
        self.log_event(f"샌드박스 스캔 시작: {file_path}")
        self.log_event("=" * 60)

        scan_start_time = time.time()

        # 샌드박스 환경 생성
        if not self.create_sandbox_environment():
            return None

        try:
            # 정적 분석
            metadata = self.analyze_static(file_path)

            # 동적 분석 (실행)
            if execute:
                self.log_event("\n동적 분석 시작 (샌드박스 실행)...")
                self.execute_in_sandbox(file_path)

            # 최종 위협 수준 계산
            threat_level = min(self.detection_results['threat_level'], 100)

            # 위협 등급 결정
            if threat_level >= 80:
                threat_category = 'CRITICAL'
                recommendation = '즉시 격리 및 삭제 권장'
            elif threat_level >= 60:
                threat_category = 'HIGH'
                recommendation = '격리 권장'
            elif threat_level >= 40:
                threat_category = 'MEDIUM'
                recommendation = '주의 필요'
            elif threat_level >= 20:
                threat_category = 'LOW'
                recommendation = '의심스러운 행동 감지'
            else:
                threat_category = 'SAFE'
                recommendation = '정상 파일로 판단'

            scan_duration = time.time() - scan_start_time

            # 결과 정리
            result = {
                'file_path': file_path,
                'metadata': metadata,
                'threat_level': threat_level,
                'threat_category': threat_category,
                'recommendation': recommendation,
                'scan_duration': round(scan_duration, 2),
                'detection_details': self.detection_results,
                'timestamp': datetime.now().isoformat()
            }

            self.log_event("=" * 60)
            self.log_event(f"스캔 완료")
            self.log_event(f"위협 수준: {threat_level}/100 ({threat_category})")
            self.log_event(f"권장사항: {recommendation}")
            self.log_event(f"스캔 시간: {scan_duration:.2f}초")
            self.log_event("=" * 60)

            return result

        finally:
            # 샌드박스 정리
            self.cleanup_sandbox()

    def save_report(self, result, output_path=None):
        """스캔 결과를 JSON 파일로 저장"""
        if not output_path:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            output_path = f"sandbox_report_{timestamp}.json"

        try:
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(result, f, indent=2, ensure_ascii=False)

            self.log_event(f"보고서 저장 완료: {output_path}")
            return output_path

        except Exception as e:
            self.log_event(f"보고서 저장 실패: {e}", level='error')
            return None


def main():
    """메인 함수 - CLI 인터페이스"""
    import argparse

    parser = argparse.ArgumentParser(description='샌드박스 바이러스 스캐너')
    parser.add_argument('file', help='스캔할 파일 경로')
    parser.add_argument('--timeout', type=int, default=30, help='실행 타임아웃 (초)')
    parser.add_argument('--no-execute', action='store_true', help='정적 분석만 수행 (실행 안 함)')
    parser.add_argument('--output', help='보고서 출력 경로')

    args = parser.parse_args()

    if not os.path.exists(args.file):
        print(f"❌ 파일을 찾을 수 없습니다: {args.file}")
        return 1

    # 스캐너 생성
    scanner = SandboxScanner(timeout=args.timeout)

    # 스캔 실행
    result = scanner.scan_file(args.file, execute=not args.no_execute)

    if result:
        # 보고서 저장
        report_path = scanner.save_report(result, args.output)

        print("\n" + "=" * 60)
        print("📊 스캔 결과 요약")
        print("=" * 60)
        print(f"파일: {result['file_path']}")
        print(f"위협 수준: {result['threat_level']}/100")
        print(f"위협 등급: {result['threat_category']}")
        print(f"권장사항: {result['recommendation']}")
        print(f"스캔 시간: {result['scan_duration']}초")

        if result['detection_details']['behaviors']:
            print(f"\n탐지된 행동: {', '.join(result['detection_details']['behaviors'])}")

        if result['detection_details']['file_operations']:
            print(f"\n파일 작업: {len(result['detection_details']['file_operations'])}건")

        if result['detection_details']['network_activity']:
            print(f"네트워크 활동: {len(result['detection_details']['network_activity'])}건")

        if result['detection_details']['process_created']:
            print(f"프로세스 생성: {len(result['detection_details']['process_created'])}건")

        if report_path:
            print(f"\n보고서: {report_path}")

        print("=" * 60)

        return 0
    else:
        print("❌ 스캔 실패")
        return 1


if __name__ == '__main__':
    sys.exit(main())
