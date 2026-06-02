"""Floating tkinter window for vocabulary quiz — learn-all then quiz-all."""

import tkinter as tk
from quiz import QuizSession, WORDS_PER_DAY
from db import get_stats, get_today_log, get_wrong_words

C_PURPLE = "#7C3AED"
C_PURPLE_DARK = "#5B21B6"
C_PURPLE_LIGHT = "#EDE9FE"
C_GREEN = "#10B981"
C_RED = "#EF4444"
C_GRAY = "#6B7280"
C_WHITE = "#FFFFFF"
C_BG = "#F8F7FC"
C_ORANGE = "#F59E0B"
C_GRAY_BG = "#E5E7EB"

WIN_W, WIN_H = 420, 460


class VocabApp:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("IELTS 每日单词")
        self.root.geometry(f"{WIN_W}x{WIN_H}")
        self.root.overrideredirect(True)
        self.root.attributes("-topmost", True)
        self.root.configure(bg=C_BG)

        self.root.update_idletasks()
        sw = self.root.winfo_screenwidth()
        sh = self.root.winfo_screenheight()
        x = sw - WIN_W - 20
        y = sh - WIN_H - 80
        self.root.geometry(f"{WIN_W}x{WIN_H}+{x}+{y}")

        self._drag_x = 0
        self._drag_y = 0
        self.root.bind("<ButtonPress-1>", self._start_drag)
        self.root.bind("<B1-Motion>", self._do_drag)

        self.session = None
        self.learn_index = 0
        self.show_welcome()

    def _start_drag(self, event):
        self._drag_x = event.x
        self._drag_y = event.y

    def _do_drag(self, event):
        x = self.root.winfo_x() + event.x - self._drag_x
        y = self.root.winfo_y() + event.y - self._drag_y
        self.root.geometry(f"+{x}+{y}")

    def _clear(self):
        for w in self.root.winfo_children():
            w.destroy()

    def _top_bar(self):
        bar = tk.Frame(self.root, bg=C_PURPLE, height=36)
        bar.pack(fill=tk.X)
        bar.pack_propagate(False)
        tk.Label(bar, text="  IELTS 每日单词", bg=C_PURPLE, fg=C_WHITE,
                 font=("Microsoft YaHei UI", 11, "bold")).pack(side=tk.LEFT, padx=4)
        tk.Button(bar, text="—", bg=C_PURPLE, fg=C_WHITE, bd=0, font=("Arial", 12),
                  command=self._minimize, activebackground=C_PURPLE_DARK).pack(side=tk.RIGHT, padx=2)
        tk.Button(bar, text="×", bg=C_PURPLE, fg=C_WHITE, bd=0, font=("Arial", 14),
                  command=self._close, activebackground=C_RED).pack(side=tk.RIGHT, padx=2)

    def _minimize(self):
        self.root.withdraw()

    def _close(self):
        self.root.destroy()

    # ======== Welcome ========
    def show_welcome(self):
        self._clear()
        self._top_bar()
        body = tk.Frame(self.root, bg=C_BG)
        body.pack(fill=tk.BOTH, expand=True)

        tk.Label(body, text="雅思词汇练习", bg=C_BG, fg=C_PURPLE_DARK,
                 font=("Microsoft YaHei UI", 20, "bold")).pack(pady=(30, 4))
        tk.Label(body, text=f"每天 {WORDS_PER_DAY} 个单词 · 先学后测", bg=C_BG, fg=C_GRAY,
                 font=("Microsoft YaHei UI", 10)).pack(pady=(0, 20))

        stats = get_stats()
        card_row = tk.Frame(body, bg=C_BG)
        card_row.pack(pady=(0, 20))
        for label, value, color in [
            ("已学", str(stats["total_studied"]), C_PURPLE),
            ("掌握", str(stats["mastered"]), C_GREEN),
            ("错题", str(stats["total_wrong"]), C_ORANGE if stats["total_wrong"] > 0 else C_GRAY),
        ]:
            card = tk.Frame(card_row, bg=C_WHITE, padx=18, pady=10,
                            highlightbackground=C_PURPLE_LIGHT, highlightthickness=1)
            card.pack(side=tk.LEFT, padx=8)
            tk.Label(card, text=value, bg=C_WHITE, fg=color,
                     font=("Arial", 18, "bold")).pack()
            tk.Label(card, text=label, bg=C_WHITE, fg=C_GRAY,
                     font=("Microsoft YaHei UI", 9)).pack()

        tk.Button(body, text="开始今日学习", bg=C_PURPLE, fg=C_WHITE,
                  font=("Microsoft YaHei UI", 14, "bold"), bd=0, padx=50, pady=10,
                  command=self._start_learn, activebackground=C_PURPLE_DARK,
                  cursor="hand2").pack(pady=(0, 12))

        wrong_words = get_wrong_words()
        if wrong_words:
            tk.Button(body, text=f"错题集 ({len(wrong_words)} 词)", bg=C_ORANGE, fg=C_WHITE,
                      font=("Microsoft YaHei UI", 11, "bold"), bd=0, padx=30, pady=7,
                      command=lambda: self._show_wrong_list(),
                      activebackground="#D97706", cursor="hand2").pack()

    # ======== Learn Phase ========
    def _start_learn(self):
        self.session = QuizSession()
        self.learn_index = 0
        self._show_learn_card()

    def _show_learn_card(self):
        self._clear()
        self._top_bar()
        is_review = getattr(self.session, 'is_review', False)
        words = self.session.words

        body = tk.Frame(self.root, bg=C_BG)
        body.pack(fill=tk.BOTH, expand=True, padx=16, pady=5)

        pf = tk.Frame(body, bg=C_BG)
        pf.pack(fill=tk.X, pady=(5, 6))
        mode_label = "复习模式" if is_review else "学习阶段"
        tk.Label(pf, text=f"{mode_label}  {self.learn_index + 1} / {len(words)}",
                 bg=C_BG, fg=C_GRAY, font=("Microsoft YaHei UI", 9)).pack(side=tk.LEFT)
        tk.Label(pf, text="先学后测", bg=C_PURPLE_LIGHT, fg=C_PURPLE,
                 font=("Microsoft YaHei UI", 8, "bold")).pack(side=tk.RIGHT)

        bar_frame = tk.Frame(body, bg=C_GRAY_BG, height=5)
        bar_frame.pack(fill=tk.X, pady=(0, 10))
        bar_frame.pack_propagate(False)
        pct = (self.learn_index + 1) / len(words)
        fill = tk.Frame(bar_frame, bg=C_PURPLE, width=int((WIN_W - 32) * pct))
        fill.pack(side=tk.LEFT, fill=tk.Y)

        word = words[self.learn_index]
        card = tk.Frame(body, bg=C_WHITE, highlightbackground=C_PURPLE_LIGHT, highlightthickness=2)
        card.pack(fill=tk.X, ipady=12)

        tk.Label(card, text=word["word"], bg=C_WHITE, fg=C_PURPLE_DARK,
                 font=("Arial", 26, "bold")).pack(pady=(10, 2))
        tk.Label(card, text=word["phonetic"], bg=C_WHITE, fg=C_GRAY,
                 font=("Arial", 12)).pack(pady=(0, 6))
        tk.Frame(card, bg=C_PURPLE_LIGHT, height=1).pack(fill=tk.X, padx=25, pady=2)
        tk.Label(card, text=word["meaning"], bg=C_WHITE, fg="#333333",
                 font=("Microsoft YaHei UI", 14), wraplength=350, justify="center").pack(pady=(4, 10))

        level_text = {1: "基础", 2: "中级", 3: "高级"}.get(word.get("level", 1), "基础")
        level_colors = {1: C_GREEN, 2: C_ORANGE, 3: C_RED}
        level_color = level_colors.get(word.get("level", 1), C_GREEN)
        tk.Label(body, text=f"难度: {level_text}", bg=C_BG, fg=level_color,
                 font=("Microsoft YaHei UI", 9)).pack(pady=(8, 6))

        nav = tk.Frame(body, bg=C_BG)
        nav.pack(fill=tk.X, pady=5)

        if self.learn_index > 0:
            tk.Button(nav, text="< 上一个", bg=C_GRAY_BG, fg="#333",
                      font=("Microsoft YaHei UI", 10), bd=0, padx=14, pady=5,
                      cursor="hand2", command=self._learn_prev).pack(side=tk.LEFT)
        else:
            tk.Frame(nav, width=1).pack(side=tk.LEFT)

        if self.learn_index < len(words) - 1:
            tk.Button(nav, text="下一个 >", bg=C_PURPLE, fg=C_WHITE,
                      font=("Microsoft YaHei UI", 10, "bold"), bd=0, padx=14, pady=5,
                      cursor="hand2", activebackground=C_PURPLE_DARK,
                      command=self._learn_next).pack(side=tk.RIGHT)
        else:
            btn_text = "重新测试" if is_review else "学完了，开始测试!"
            tk.Button(nav, text=btn_text, bg=C_GREEN, fg=C_WHITE,
                      font=("Microsoft YaHei UI", 10, "bold"), bd=0, padx=14, pady=5,
                      cursor="hand2", activebackground="#059669",
                      command=self._start_quiz_phase).pack(side=tk.RIGHT)

    def _learn_prev(self):
        if self.learn_index > 0:
            self.learn_index -= 1
            self._show_learn_card()

    def _learn_next(self):
        if self.learn_index < len(self.session.words) - 1:
            self.learn_index += 1
            self._show_learn_card()

    def _start_quiz_phase(self):
        self.session.index = 0
        self.session.correct = 0
        self._show_question()

    # ======== Quiz Phase ========
    def _show_question(self):
        self._clear()
        self._top_bar()

        if self.session.is_done:
            self._show_result()
            return

        word = self.session.current
        body = tk.Frame(self.root, bg=C_BG)
        body.pack(fill=tk.BOTH, expand=True, padx=16, pady=5)

        pf = tk.Frame(body, bg=C_BG)
        pf.pack(fill=tk.X, pady=(5, 6))
        tk.Label(pf, text=f"测试阶段  {self.session.index + 1} / {self.session.total}",
                 bg=C_BG, fg=C_GRAY, font=("Microsoft YaHei UI", 9)).pack(side=tk.LEFT)
        tk.Label(pf, text=f"✓ {self.session.correct}", bg=C_BG, fg=C_GREEN,
                 font=("Microsoft YaHei UI", 9, "bold")).pack(side=tk.RIGHT)

        bar_frame = tk.Frame(body, bg=C_GRAY_BG, height=5)
        bar_frame.pack(fill=tk.X, pady=(0, 8))
        bar_frame.pack_propagate(False)
        pct = self.session.index / self.session.total
        fill = tk.Frame(bar_frame, bg=C_PURPLE, width=int((WIN_W - 32) * pct))
        fill.pack(side=tk.LEFT, fill=tk.Y)

        tk.Label(body, text=word["word"], bg=C_BG, fg=C_PURPLE_DARK,
                 font=("Arial", 22, "bold")).pack(pady=(5, 2))
        tk.Label(body, text=word["phonetic"], bg=C_BG, fg=C_GRAY,
                 font=("Arial", 11)).pack(pady=(0, 4))
        tk.Label(body, text="这个单词的意思是？", bg=C_BG, fg=C_GRAY,
                 font=("Microsoft YaHei UI", 9)).pack(pady=(0, 6))

        options = self.session.get_options()
        self._option_buttons = []
        for i, opt in enumerate(options):
            btn = tk.Button(body, text=f"  {chr(65 + i)}. {opt}", bg=C_WHITE, fg="#333333",
                            font=("Microsoft YaHei UI", 10), bd=1, relief=tk.GROOVE,
                            anchor="w", padx=12, pady=5, cursor="hand2", wraplength=370,
                            justify="left",
                            command=lambda o=opt: self._on_answer(o))
            btn.pack(fill=tk.X, pady=2)
            self._option_buttons.append((btn, opt))

        self._feedback = tk.Label(body, text="", bg=C_BG, font=("Microsoft YaHei UI", 10, "bold"))
        self._feedback.pack(pady=(4, 0))

    def _on_answer(self, chosen):
        result = self.session.answer(chosen)
        if result is None:
            return
        is_correct, correct_answer = result

        for btn, opt in self._option_buttons:
            btn.config(state="disabled", cursor="arrow")
            if opt == correct_answer:
                btn.config(bg="#D1FAE5", fg=C_GREEN)
            elif opt == chosen and not is_correct:
                btn.config(bg="#FEE2E2", fg=C_RED)

        if is_correct:
            self._feedback.config(text="正确!", fg=C_GREEN)
        else:
            self._feedback.config(text=f"正确答案: {correct_answer}", fg=C_RED)

        delay = 500 if is_correct else 1500
        self.root.after(delay, self._show_question)

    # ======== Result ========
    def _show_result(self):
        self._clear()
        self._top_bar()
        body = tk.Frame(self.root, bg=C_BG)
        body.pack(fill=tk.BOTH, expand=True)

        is_review = getattr(self.session, 'is_review', False)
        title = "复习完成!" if is_review else "今日完成!"
        tk.Label(body, text=title, bg=C_BG, fg=C_PURPLE_DARK,
                 font=("Microsoft YaHei UI", 18, "bold")).pack(pady=(30, 5))

        total = self.session.total
        correct = self.session.correct
        pct = int(correct / total * 100) if total > 0 else 0

        color = C_GREEN if pct >= 80 else (C_PURPLE if pct >= 60 else C_RED)
        tk.Label(body, text=f"{pct}%", bg=C_BG, fg=color,
                 font=("Arial", 36, "bold")).pack(pady=5)
        tk.Label(body, text=f"{correct}/{total} 正确", bg=C_BG, fg=C_GRAY,
                 font=("Microsoft YaHei UI", 11)).pack(pady=(0, 5))

        if pct >= 90:
            msg = "太棒了! 继续保持!"
        elif pct >= 70:
            msg = "不错! 明天继续加油!"
        elif pct >= 50:
            msg = "还需要多练习哦!"
        else:
            msg = "别灰心，多复习几遍!"
        tk.Label(body, text=msg, bg=C_BG, fg=C_GRAY,
                 font=("Microsoft YaHei UI", 10)).pack(pady=(0, 20))

        btn_frame = tk.Frame(body, bg=C_BG)
        btn_frame.pack(pady=5)

        wrong_words = get_wrong_words()
        if not is_review:
            tk.Button(btn_frame, text="再来一轮", bg=C_PURPLE, fg=C_WHITE,
                      font=("Microsoft YaHei UI", 10, "bold"), bd=0, padx=16, pady=6,
                      command=self._start_learn, activebackground=C_PURPLE_DARK,
                      cursor="hand2").pack(side=tk.LEFT, padx=5)
        if wrong_words:
            tk.Button(btn_frame, text=f"错题集 ({len(wrong_words)})", bg=C_ORANGE, fg=C_WHITE,
                      font=("Microsoft YaHei UI", 10, "bold"), bd=0, padx=16, pady=6,
                      command=lambda: self._show_wrong_list(),
                      activebackground="#D97706", cursor="hand2").pack(side=tk.LEFT, padx=5)
        tk.Button(btn_frame, text="首页", bg=C_GRAY_BG, fg="#333",
                  font=("Microsoft YaHei UI", 10), bd=0, padx=16, pady=6,
                  command=self.show_welcome, cursor="hand2").pack(side=tk.LEFT, padx=5)

    # ======== Wrong Words List ========
    def _show_wrong_list(self):
        self._clear()
        self._top_bar()
        wrong_words = get_wrong_words()

        body = tk.Frame(self.root, bg=C_BG)
        body.pack(fill=tk.BOTH, expand=True)

        header = tk.Frame(body, bg=C_BG)
        header.pack(fill=tk.X, padx=16, pady=(8, 5))
        tk.Button(header, text="< 返回", bg=C_BG, fg=C_PURPLE, bd=0,
                  font=("Microsoft YaHei UI", 9), cursor="hand2",
                  command=self.show_welcome).pack(side=tk.LEFT)
        tk.Label(header, text=f"错题集 ({len(wrong_words)} 词)", bg=C_BG, fg=C_ORANGE,
                 font=("Microsoft YaHei UI", 13, "bold")).pack(side=tk.LEFT, padx=15)

        if not wrong_words:
            tk.Label(body, text="没有错题，继续保持!", bg=C_BG, fg=C_GREEN,
                     font=("Microsoft YaHei UI", 12)).pack(pady=40)
            return

        list_outer = tk.Frame(body, bg=C_BG)
        list_outer.pack(fill=tk.BOTH, expand=True, padx=12)

        canvas = tk.Canvas(list_outer, bg=C_BG, highlightthickness=0)
        scrollbar = tk.Scrollbar(list_outer, orient="vertical", command=canvas.yview)
        scroll_inner = tk.Frame(canvas, bg=C_BG)

        scroll_inner.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=scroll_inner, anchor="nw", width=WIN_W - 50)
        canvas.configure(yscrollcommand=scrollbar.set)
        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        def _on_mousewheel(event):
            canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")
        canvas.bind_all("<MouseWheel>", _on_mousewheel)

        for w in wrong_words:
            row = tk.Frame(scroll_inner, bg=C_WHITE, cursor="hand2")
            row.pack(fill=tk.X, pady=2, padx=2)

            word_frame = tk.Frame(row, bg=C_WHITE)
            word_frame.pack(fill=tk.X, padx=10, pady=7)

            text_frame = tk.Frame(word_frame, bg=C_WHITE)
            text_frame.pack(side=tk.LEFT, fill=tk.X, expand=True)
            tk.Label(text_frame, text=w["word"], bg=C_WHITE, fg=C_PURPLE_DARK,
                     font=("Arial", 12, "bold")).pack(anchor="w")
            tk.Label(text_frame, text=w["meaning"], bg=C_WHITE, fg=C_GRAY,
                     font=("Microsoft YaHei UI", 9)).pack(anchor="w")

            badge = tk.Frame(word_frame, bg="#FEE2E2", padx=6, pady=1)
            badge.pack(side=tk.RIGHT)
            tk.Label(badge, text=f"错{w['wrong_count']}", bg="#FEE2E2", fg=C_RED,
                     font=("Microsoft YaHei UI", 8, "bold")).pack()

            row.bind("<Button-1>", lambda e, word=w: self._show_word_detail(word))
            for child in row.winfo_children():
                child.bind("<Button-1>", lambda e, word=w: self._show_word_detail(word))
                for sub in child.winfo_children():
                    sub.bind("<Button-1>", lambda e, word=w: self._show_word_detail(word))

        bottom = tk.Frame(body, bg=C_BG, height=50)
        bottom.pack(fill=tk.X, padx=16, pady=8)
        bottom.pack_propagate(False)
        tk.Button(bottom, text="重新练习错题", bg=C_ORANGE, fg=C_WHITE,
                  font=("Microsoft YaHei UI", 11, "bold"), bd=0, padx=20, pady=6,
                  command=lambda: self._start_review(wrong_words),
                  activebackground="#D97706", cursor="hand2").pack()

    # ======== Word Detail Popup ========
    def _show_word_detail(self, word):
        popup = tk.Toplevel(self.root)
        popup.title(word["word"])
        popup.geometry(f"320x250+{self.root.winfo_x() + 50}+{self.root.winfo_y() + 80}")
        popup.overrideredirect(True)
        popup.attributes("-topmost", True)
        popup.configure(bg=C_WHITE)

        bar = tk.Frame(popup, bg=C_ORANGE, height=32)
        bar.pack(fill=tk.X)
        bar.pack_propagate(False)
        tk.Label(bar, text=f"  {word['word']}", bg=C_ORANGE, fg=C_WHITE,
                 font=("Microsoft YaHei UI", 11, "bold")).pack(side=tk.LEFT)
        tk.Button(bar, text="×", bg=C_ORANGE, fg=C_WHITE, bd=0, font=("Arial", 13),
                  command=popup.destroy, activebackground=C_RED).pack(side=tk.RIGHT, padx=4)

        body = tk.Frame(popup, bg=C_WHITE)
        body.pack(fill=tk.BOTH, expand=True, padx=20, pady=12)

        tk.Label(body, text=word["word"], bg=C_WHITE, fg=C_PURPLE_DARK,
                 font=("Arial", 22, "bold")).pack(pady=(0, 2))
        tk.Label(body, text=word["phonetic"], bg=C_WHITE, fg=C_GRAY,
                 font=("Arial", 12)).pack(pady=(0, 8))
        tk.Frame(body, bg=C_PURPLE_LIGHT, height=1).pack(fill=tk.X, pady=4)
        tk.Label(body, text=word["meaning"], bg=C_WHITE, fg="#333",
                 font=("Microsoft YaHei UI", 13), wraplength=270, justify="center").pack(pady=6)

        level_text = {1: "基础", 2: "中级", 3: "高级"}.get(word.get("level", 1), "基础")
        level_colors = {1: C_GREEN, 2: C_ORANGE, 3: C_RED}
        lc = level_colors.get(word.get("level", 1), C_GREEN)
        tk.Label(body, text=f"难度: {level_text}  |  错 {word.get('wrong_count', '?')} 次",
                 bg=C_WHITE, fg=lc, font=("Microsoft YaHei UI", 9)).pack(pady=(5, 0))

    # ======== Review Mode ========
    def _start_review(self, words):
        self.session = QuizSession(words=words)
        self.learn_index = 0
        self._show_learn_card()

    def run(self):
        self.root.mainloop()

    def show_window(self):
        self.root.deiconify()
        self.show_welcome()


def run_ui():
    app = VocabApp()
    app.run()
