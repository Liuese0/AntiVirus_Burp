#!/usr/bin/env python3
"""
샌드박스 바이러스 스캐너 GUI
사용자 친화적인 인터페이스로 샌드박스 스캔을 수행합니다.
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import threading
import json
from datetime import datetime
from SandboxScanner import SandboxScanner


class SandboxGUI:
    """샌드박스 스캐너 GUI 클래스"""

    def __init__(self):
        self.root = tk.Tk()
        self.root.title("🔒 샌드박스 바이러스 스캐너")
        self.root.geometry("1000x800")
        self.root.configure(bg='#0d1421')

        self.scanner = None
        self.current_scan_result = None

        self.create_ui()

    def create_ui(self):
        """UI 생성"""
        # 헤더
        header_frame = tk.Frame(self.root, bg='#1a252f', height=100)
        header_frame.pack(fill='x', padx=10, pady=10)
        header_frame.pack_propagate(False)

        title_label = tk.Label(
            header_frame,
            text="🔒 샌드박스 바이러스 스캐너",
            font=('Arial', 24, 'bold'),
            fg='#00ff88',
            bg='#1a252f'
        )
        title_label.pack(pady=10)

        subtitle_label = tk.Label(
            header_frame,
            text="격리된 환경에서 안전하게 파일 분석",
            font=('Arial', 12),
            fg='#64ffda',
            bg='#1a252f'
        )
        subtitle_label.pack()

        # 메인 컨테이너
        main_container = tk.Frame(self.root, bg='#0d1421')
        main_container.pack(fill='both', expand=True, padx=10, pady=10)

        # 좌측 패널 (설정)
        left_panel = tk.Frame(main_container, bg='#1a252f', width=300)
        left_panel.pack(side='left', fill='y', padx=(0, 10))
        left_panel.pack_propagate(False)

        # 파일 선택
        tk.Label(
            left_panel,
            text="📂 파일 선택",
            font=('Arial', 14, 'bold'),
            fg='#00ff88',
            bg='#1a252f'
        ).pack(pady=(20, 10))

        self.file_path_var = tk.StringVar()
        file_entry = tk.Entry(
            left_panel,
            textvariable=self.file_path_var,
            font=('Arial', 10),
            bg='#2d3748',
            fg='white',
            insertbackground='white'
        )
        file_entry.pack(padx=20, pady=5, fill='x')

        browse_btn = tk.Button(
            left_panel,
            text="파일 찾기",
            command=self.browse_file,
            bg='#3182ce',
            fg='white',
            font=('Arial', 11, 'bold'),
            relief='flat',
            pady=8
        )
        browse_btn.pack(padx=20, pady=5, fill='x')

        # 설정
        tk.Label(
            left_panel,
            text="⚙️ 스캔 설정",
            font=('Arial', 14, 'bold'),
            fg='#00ff88',
            bg='#1a252f'
        ).pack(pady=(30, 10))

        # 타임아웃 설정
        timeout_frame = tk.Frame(left_panel, bg='#1a252f')
        timeout_frame.pack(padx=20, pady=10, fill='x')

        tk.Label(
            timeout_frame,
            text="실행 타임아웃 (초):",
            font=('Arial', 10),
            fg='white',
            bg='#1a252f'
        ).pack(anchor='w')

        self.timeout_var = tk.IntVar(value=30)
        timeout_spinbox = tk.Spinbox(
            timeout_frame,
            from_=5,
            to=300,
            textvariable=self.timeout_var,
            font=('Arial', 10),
            bg='#2d3748',
            fg='white',
            buttonbackground='#3182ce'
        )
        timeout_spinbox.pack(fill='x', pady=5)

        # 실행 옵션
        self.execute_var = tk.BooleanVar(value=True)
        execute_check = tk.Checkbutton(
            left_panel,
            text="샌드박스에서 실행 (동적 분석)",
            variable=self.execute_var,
            font=('Arial', 10),
            fg='white',
            bg='#1a252f',
            selectcolor='#2d3748',
            activebackground='#1a252f',
            activeforeground='white'
        )
        execute_check.pack(padx=20, pady=10)

        # 스캔 버튼
        scan_btn = tk.Button(
            left_panel,
            text="🔍 스캔 시작",
            command=self.start_scan,
            bg='#27ae60',
            fg='white',
            font=('Arial', 14, 'bold'),
            relief='flat',
            pady=15
        )
        scan_btn.pack(padx=20, pady=20, fill='x')

        # 보고서 저장 버튼
        save_report_btn = tk.Button(
            left_panel,
            text="💾 보고서 저장",
            command=self.save_report,
            bg='#2c3e50',
            fg='white',
            font=('Arial', 11, 'bold'),
            relief='flat',
            pady=10
        )
        save_report_btn.pack(padx=20, pady=5, fill='x')

        # 우측 패널 (결과)
        right_panel = tk.Frame(main_container, bg='#1a252f')
        right_panel.pack(side='right', fill='both', expand=True)

        # 결과 탭
        notebook = ttk.Notebook(right_panel)
        notebook.pack(fill='both', expand=True, padx=10, pady=10)

        # 스타일 설정
        style = ttk.Style()
        style.configure('TNotebook', background='#1a252f')
        style.configure('TNotebook.Tab', background='#2d3748', foreground='white', padding=[10, 5])
        style.map('TNotebook.Tab', background=[('selected', '#3182ce')])

        # 요약 탭
        summary_frame = tk.Frame(notebook, bg='#2d3748')
        notebook.add(summary_frame, text='📊 스캔 요약')

        self.summary_text = scrolledtext.ScrolledText(
            summary_frame,
            font=('Consolas', 11),
            bg='#1e2936',
            fg='white',
            insertbackground='white',
            wrap=tk.WORD
        )
        self.summary_text.pack(fill='both', expand=True, padx=10, pady=10)

        # 로그 탭
        log_frame = tk.Frame(notebook, bg='#2d3748')
        notebook.add(log_frame, text='📝 실행 로그')

        self.log_text = scrolledtext.ScrolledText(
            log_frame,
            font=('Consolas', 10),
            bg='#1e2936',
            fg='#a0aec0',
            insertbackground='white',
            wrap=tk.WORD
        )
        self.log_text.pack(fill='both', expand=True, padx=10, pady=10)

        # 상세 탭
        detail_frame = tk.Frame(notebook, bg='#2d3748')
        notebook.add(detail_frame, text='🔍 상세 분석')

        self.detail_text = scrolledtext.ScrolledText(
            detail_frame,
            font=('Consolas', 10),
            bg='#1e2936',
            fg='white',
            insertbackground='white',
            wrap=tk.WORD
        )
        self.detail_text.pack(fill='both', expand=True, padx=10, pady=10)

        # 상태바
        status_frame = tk.Frame(self.root, bg='#1a252f', height=30)
        status_frame.pack(fill='x', side='bottom')
        status_frame.pack_propagate(False)

        self.status_label = tk.Label(
            status_frame,
            text="준비",
            font=('Arial', 10),
            fg='#64ffda',
            bg='#1a252f',
            anchor='w'
        )
        self.status_label.pack(fill='x', padx=10)

    def browse_file(self):
        """파일 선택 다이얼로그"""
        filename = filedialog.askopenfilename(
            title="스캔할 파일 선택",
            filetypes=[
                ("모든 파일", "*.*"),
                ("실행 파일", "*.exe"),
                ("스크립트", "*.py *.sh *.bat *.cmd"),
                ("문서", "*.pdf *.doc *.docx")
            ]
        )
        if filename:
            self.file_path_var.set(filename)

    def update_status(self, message, color='#64ffda'):
        """상태 업데이트"""
        self.status_label.config(text=message, fg=color)

    def append_log(self, message):
        """로그 추가"""
        self.log_text.insert(tk.END, message + '\n')
        self.log_text.see(tk.END)
        self.root.update_idletasks()

    def scan_thread(self, file_path, timeout, execute):
        """스캔 스레드"""
        try:
            self.update_status("스캔 진행 중...", '#ffa500')

            # 스캐너 생성
            self.scanner = SandboxScanner(timeout=timeout)

            # 스캔 실행
            result = self.scanner.scan_file(file_path, execute=execute)

            if result:
                self.current_scan_result = result
                self.display_results(result)
                self.update_status("스캔 완료", '#27ae60')
            else:
                self.update_status("스캔 실패", '#e74c3c')
                messagebox.showerror("스캔 오류", "파일 스캔 중 오류가 발생했습니다.")

        except Exception as e:
            self.update_status(f"오류: {str(e)}", '#e74c3c')
            messagebox.showerror("스캔 오류", f"스캔 중 오류 발생:\n{str(e)}")

    def start_scan(self):
        """스캔 시작"""
        file_path = self.file_path_var.get()

        if not file_path:
            messagebox.showwarning("경고", "스캔할 파일을 선택해주세요.")
            return

        # 로그 초기화
        self.log_text.delete(1.0, tk.END)
        self.summary_text.delete(1.0, tk.END)
        self.detail_text.delete(1.0, tk.END)

        timeout = self.timeout_var.get()
        execute = self.execute_var.get()

        # 스캔 스레드 시작
        scan_thread = threading.Thread(
            target=self.scan_thread,
            args=(file_path, timeout, execute)
        )
        scan_thread.daemon = True
        scan_thread.start()

    def display_results(self, result):
        """결과 표시"""
        # 요약 탭
        self.summary_text.delete(1.0, tk.END)

        threat_level = result['threat_level']
        threat_category = result['threat_category']

        # 색상 코드
        if threat_level >= 80:
            color_code = '🔴'
        elif threat_level >= 60:
            color_code = '🟠'
        elif threat_level >= 40:
            color_code = '🟡'
        elif threat_level >= 20:
            color_code = '🟢'
        else:
            color_code = '✅'

        summary = f"""
╔══════════════════════════════════════════════════════════════╗
║                     스캔 결과 요약                            ║
╚══════════════════════════════════════════════════════════════╝

📁 파일: {result['file_path']}

{color_code} 위협 수준: {threat_level}/100
📊 위협 등급: {threat_category}
💡 권장사항: {result['recommendation']}
⏱️  스캔 시간: {result['scan_duration']}초

──────────────────────────────────────────────────────────────

📋 탐지 상세:
"""

        details = result['detection_details']

        if details['behaviors']:
            summary += f"\n🔍 탐지된 행동 ({len(details['behaviors'])}건):\n"
            for behavior in details['behaviors']:
                summary += f"  • {behavior}\n"

        if details['file_operations']:
            summary += f"\n📂 파일 작업 ({len(details['file_operations'])}건):\n"
            for op in details['file_operations'][:5]:
                summary += f"  • {op['action']}: {op['path']}\n"
            if len(details['file_operations']) > 5:
                summary += f"  ... 외 {len(details['file_operations']) - 5}건\n"

        if details['network_activity']:
            summary += f"\n🌐 네트워크 활동 ({len(details['network_activity'])}건):\n"
            for net in details['network_activity'][:5]:
                summary += f"  • {net['local_addr']} -> {net.get('remote_addr', 'N/A')}\n"
            if len(details['network_activity']) > 5:
                summary += f"  ... 외 {len(details['network_activity']) - 5}건\n"

        if details['process_created']:
            summary += f"\n⚙️  프로세스 생성 ({len(details['process_created'])}건):\n"
            for proc in details['process_created'][:5]:
                summary += f"  • {proc['name']} (PID: {proc['pid']})\n"
            if len(details['process_created']) > 5:
                summary += f"  ... 외 {len(details['process_created']) - 5}건\n"

        if details['suspicious_patterns']:
            summary += f"\n⚠️  의심스러운 패턴 ({len(details['suspicious_patterns'])}건):\n"
            for pattern in details['suspicious_patterns'][:5]:
                summary += f"  • {pattern['pattern']}\n"
            if len(details['suspicious_patterns']) > 5:
                summary += f"  ... 외 {len(details['suspicious_patterns']) - 5}건\n"

        summary += f"\n──────────────────────────────────────────────────────────────\n"
        summary += f"🕐 스캔 시간: {result['timestamp']}\n"

        self.summary_text.insert(tk.END, summary)

        # 로그 탭
        self.log_text.delete(1.0, tk.END)
        for log_entry in details['execution_log']:
            log_line = f"[{log_entry['timestamp']}] [{log_entry['level'].upper()}] {log_entry['message']}\n"
            self.log_text.insert(tk.END, log_line)

        # 상세 탭
        self.detail_text.delete(1.0, tk.END)
        detail_json = json.dumps(result, indent=2, ensure_ascii=False)
        self.detail_text.insert(tk.END, detail_json)

    def save_report(self):
        """보고서 저장"""
        if not self.current_scan_result:
            messagebox.showwarning("경고", "저장할 스캔 결과가 없습니다.")
            return

        filename = filedialog.asksaveasfilename(
            defaultextension=".json",
            filetypes=[("JSON 파일", "*.json"), ("텍스트 파일", "*.txt"), ("모든 파일", "*.*")],
            initialfile=f"sandbox_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        )

        if filename:
            try:
                with open(filename, 'w', encoding='utf-8') as f:
                    json.dump(self.current_scan_result, f, indent=2, ensure_ascii=False)

                messagebox.showinfo("저장 완료", f"보고서가 저장되었습니다:\n{filename}")
                self.update_status(f"보고서 저장: {filename}", '#27ae60')

            except Exception as e:
                messagebox.showerror("저장 오류", f"보고서 저장 중 오류 발생:\n{str(e)}")

    def run(self):
        """GUI 실행"""
        self.root.mainloop()


def main():
    """메인 함수"""
    app = SandboxGUI()
    app.run()


if __name__ == '__main__':
    main()
