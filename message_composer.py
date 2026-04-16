import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
import threading
import json
import urllib.request
import urllib.error


OLLAMA_URL = "http://localhost:11434/api/generate"


class MessageComposer(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("AI 격식 메시지 작성기 (Ollama)")
        self.geometry("900x700")
        self.configure(bg="#f5f0eb")

        style = ttk.Style()
        style.configure("Title.TLabel", font=("맑은 고딕", 16, "bold"), background="#f5f0eb")
        style.configure("Section.TLabel", font=("맑은 고딕", 10, "bold"), background="#f5f0eb")
        style.configure("TLabel", font=("맑은 고딕", 10), background="#f5f0eb")
        style.configure("TButton", font=("맑은 고딕", 10))
        style.configure("TRadiobutton", font=("맑은 고딕", 10), background="#f5f0eb")
        style.configure("TFrame", background="#f5f0eb")

        self.create_widgets()

    def create_widgets(self):
        main = ttk.Frame(self, padding=20)
        main.pack(fill=tk.BOTH, expand=True)

        ttk.Label(main, text="AI 격식 메시지 작성기", style="Title.TLabel").pack(pady=(0, 10))

        # === 격식 수준 ===
        level_frame = ttk.LabelFrame(main, text=" 격식 수준 ", padding=8)
        level_frame.pack(fill=tk.X, pady=5)

        self.formality = tk.StringVar(value="최고")
        levels = [("최고 (스님, 어르신)", "최고"), ("높음 (직장 상사, 선배)", "높음"), ("보통 (동료, 지인)", "보통")]
        level_row = ttk.Frame(level_frame)
        level_row.pack(fill=tk.X)
        for text, val in levels:
            ttk.Radiobutton(level_row, text=text, variable=self.formality, value=val).pack(side=tk.LEFT, padx=8)

        # === 메시지 길이 ===
        len_frame = ttk.LabelFrame(main, text=" 메시지 길이 ", padding=8)
        len_frame.pack(fill=tk.X, pady=5)

        self.msg_length = tk.StringVar(value="보통")
        lengths = [("짧게 (3~5줄)", "짧게"), ("보통 (7~12줄)", "보통"), ("길게 (15줄 이상)", "길게")]
        len_row = ttk.Frame(len_frame)
        len_row.pack(fill=tk.X)
        for text, val in lengths:
            ttk.Radiobutton(len_row, text=text, variable=self.msg_length, value=val).pack(side=tk.LEFT, padx=8)

        # === 상황 설명 ===
        situation_frame = ttk.LabelFrame(main, text=" 상황 설명 (자유롭게 입력) ", padding=8)
        situation_frame.pack(fill=tk.X, pady=5)

        self.situation_text = scrolledtext.ScrolledText(
            situation_frame, wrap=tk.WORD, font=("맑은 고딕", 11), height=6,
            bg="white", relief=tk.FLAT, padx=8, pady=8)
        self.situation_text.pack(fill=tk.X)
        self.situation_text.insert("1.0",
            "오늘 오전 태영 형님과 함께 스님을 찾아뵙고 인사드렸음. "
            "귀한 시간 내어 좋은 가르침을 주심. "
            "태영 형님의 앞날도 축원해달라는 뜻을 담고 싶음. "
            "스님이 곧 전국 방생 길을 떠나심. "
            "스님이 다니시는 지역(서울, 대전, 인천, 영흥, 당진, 평택, 태안, 대산, 보령, 서천, 통영, 강릉, 삼척)에 "
            "우리 회사가 있어서 도움 드릴 수 있음. "
            "보내는 사람: 김경호")

        # === 버튼 ===
        btn_frame = ttk.Frame(main)
        btn_frame.pack(fill=tk.X, pady=10)

        self.gen_btn = ttk.Button(btn_frame, text="메시지 생성", command=self.generate_message)
        self.gen_btn.pack(side=tk.LEFT, padx=5)

        ttk.Button(btn_frame, text="다시 생성", command=self.generate_message).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="클립보드 복사", command=self.copy_to_clipboard).pack(side=tk.LEFT, padx=5)

        self.char_label = ttk.Label(btn_frame, text="글자 수: 0", style="Section.TLabel")
        self.char_label.pack(side=tk.RIGHT, padx=10)

        self.status_label = ttk.Label(btn_frame, text="", style="Section.TLabel")
        self.status_label.pack(side=tk.RIGHT, padx=10)

        # === 결과 ===
        result_frame = ttk.LabelFrame(main, text=" 생성된 메시지 ", padding=10)
        result_frame.pack(fill=tk.BOTH, expand=True, pady=5)

        self.result_text = scrolledtext.ScrolledText(
            result_frame, wrap=tk.WORD, font=("맑은 고딕", 12), height=12,
            bg="white", relief=tk.FLAT, padx=10, pady=10)
        self.result_text.pack(fill=tk.BOTH, expand=True)

    def build_prompt(self):
        formality = self.formality.get()
        length = self.msg_length.get()
        situation = self.situation_text.get("1.0", tk.END).strip()

        formality_desc = {
            "최고": "최고 수준의 격식. 스님, 어르신, 큰 은인에게 보내는 수준. 존칭과 한자어 표현 적절히 사용. 겸양의 표현 사용.",
            "높음": "높은 격식. 직장 상사, 선배, 은사님 등에게. 정중하되 약간 편한 느낌.",
            "보통": "보통 격식. 동료, 지인에게. 존댓말이지만 자연스럽고 따뜻한 느낌."
        }

        length_desc = {
            "짧게": "3~5줄 분량. 핵심만 간결하게.",
            "보통": "7~12줄 분량. 적당한 길이로 정성이 느껴지게.",
            "길게": "15줄 이상. 충분히 마음을 담아 정성스럽게."
        }

        return f"""당신은 한국어 격식 메시지 작성 전문가입니다.
아래 상황을 바탕으로 문자메시지나 카카오톡으로 보낼 메시지를 작성해 주세요.

[격식 수준] {formality_desc[formality]}
[메시지 길이] {length_desc[length]}

[상황 설명]
{situation}

작성 규칙:
1. 상황을 파악하여 적절한 인사 메시지를 자연스럽게 작성
2. 문자/카톡에 바로 복사해서 보낼 수 있는 형태로 작성
3. 과도한 수식어는 피하되, 진심이 느껴지는 문체
4. 적절한 줄바꿈으로 가독성 확보
5. 서명이나 날짜는 넣지 않음
6. 메시지 본문만 출력 (설명이나 부가 안내 없이)
7. 반드시 한국어로만 작성"""

    def generate_message(self):
        situation = self.situation_text.get("1.0", tk.END).strip()
        if not situation:
            messagebox.showwarning("입력 필요", "상황 설명을 입력해 주세요.")
            return

        self.gen_btn.config(state=tk.DISABLED)
        self.status_label.config(text="생성 중... (최초 실행 시 모델 로딩으로 시간이 걸릴 수 있습니다)")
        self.result_text.delete("1.0", tk.END)
        self.result_text.insert("1.0", "AI가 메시지를 작성하고 있습니다...")

        def run():
            try:
                prompt = self.build_prompt()
                payload = json.dumps({
                    "model": "gemma3:4b",
                    "prompt": prompt,
                    "stream": False,
                    "options": {
                        "temperature": 0.7,
                        "num_predict": 2000,
                    }
                }).encode("utf-8")

                req = urllib.request.Request(
                    OLLAMA_URL,
                    data=payload,
                    headers={"Content-Type": "application/json"},
                    method="POST"
                )
                with urllib.request.urlopen(req, timeout=120) as resp:
                    data = json.loads(resp.read().decode("utf-8"))
                    result = data.get("response", "").strip()

                if not result:
                    self.after(0, lambda: self.show_error("모델이 빈 응답을 반환했습니다. 다시 시도해 주세요."))
                else:
                    self.after(0, lambda: self.show_result(result))

            except urllib.error.URLError:
                self.after(0, lambda: self.show_error(
                    "Ollama 서버에 연결할 수 없습니다.\n"
                    "작업 표시줄에서 Ollama가 실행 중인지 확인해 주세요."))
            except Exception as e:
                self.after(0, lambda: self.show_error(f"오류 발생: {str(e)}"))

        threading.Thread(target=run, daemon=True).start()

    def show_result(self, text):
        self.result_text.delete("1.0", tk.END)
        self.result_text.insert("1.0", text)
        char_count = len(text.replace("\n", "").replace(" ", ""))
        self.char_label.config(text=f"글자 수: {char_count}")
        self.status_label.config(text="생성 완료")
        self.gen_btn.config(state=tk.NORMAL)

    def show_error(self, msg):
        self.result_text.delete("1.0", tk.END)
        self.result_text.insert("1.0", msg)
        self.status_label.config(text="오류")
        self.gen_btn.config(state=tk.NORMAL)
        messagebox.showerror("오류", msg)

    def copy_to_clipboard(self):
        msg = self.result_text.get("1.0", tk.END).strip()
        if not msg or msg.startswith("AI가 메시지를"):
            messagebox.showwarning("복사 불가", "먼저 메시지를 생성해 주세요.")
            return
        self.clipboard_clear()
        self.clipboard_append(msg)
        messagebox.showinfo("복사 완료", "메시지가 클립보드에 복사되었습니다.\n카톡이나 문자에 붙여넣기 하세요.")


if __name__ == "__main__":
    app = MessageComposer()
    app.mainloop()
