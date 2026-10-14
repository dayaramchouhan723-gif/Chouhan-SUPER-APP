"""Optional Tkinter chat window with an animated assistant orb."""

from __future__ import annotations

import threading
import tkinter as tk
from tkinter import scrolledtext

from myra.main import handle_message
from myra.voice.stt import listen_once
from myra.voice.tts import speak

BACKGROUND = "#101522"
PANEL = "#171f30"
TEXT = "#eff4ff"
ACCENT = "#85e2ff"
MUTED = "#a6b3c9"


class OrbWindow:
    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.speak_next = False
        self.root.title("Chouhan Myra")
        self.root.geometry("390x590")
        self.root.minsize(330, 460)
        self.root.configure(bg=BACKGROUND)

        title = tk.Label(
            root,
            text="CHOUHAN MYRA",
            bg=BACKGROUND,
            fg=TEXT,
            font=("TkDefaultFont", 13, "bold"),
        )
        title.pack(pady=(16, 2))

        self.status = tk.StringVar(value="Ready · microphone is off")
        tk.Label(root, textvariable=self.status, bg=BACKGROUND, fg=MUTED).pack(pady=(0, 8))

        self.canvas = tk.Canvas(
            root, width=100, height=100, bg=BACKGROUND, highlightthickness=0
        )
        self.canvas.pack()
        self.orb = self.canvas.create_oval(
            25, 25, 75, 75, fill="#5bbdde", outline=ACCENT, width=2
        )
        self.canvas.create_oval(35, 35, 65, 65, fill="#b5f4ff", outline="")

        self.transcript = scrolledtext.ScrolledText(
            root,
            wrap=tk.WORD,
            bg=PANEL,
            fg=TEXT,
            insertbackground=TEXT,
            relief=tk.FLAT,
            padx=12,
            pady=10,
            font=("TkDefaultFont", 10),
        )
        self.transcript.pack(fill=tk.BOTH, expand=True, padx=16, pady=(6, 10))
        self.transcript.insert(tk.END, "Ask a question or choose a command.\nType /help to see commands.\n")
        self.transcript.configure(state=tk.DISABLED)

        input_row = tk.Frame(root, bg=BACKGROUND)
        input_row.pack(fill=tk.X, padx=16, pady=(0, 16))
        self.entry = tk.Entry(
            input_row,
            bg=PANEL,
            fg=TEXT,
            insertbackground=TEXT,
            relief=tk.FLAT,
            font=("TkDefaultFont", 11),
        )
        self.entry.pack(side=tk.LEFT, fill=tk.X, expand=True, ipady=10, padx=(0, 8))
        self.entry.bind("<Return>", lambda _event: self.send())

        tk.Button(
            input_row,
            text="Send",
            command=self.send,
            bg="#276b89",
            fg="white",
            activebackground="#3985a5",
            relief=tk.FLAT,
            padx=12,
            pady=8,
        ).pack(side=tk.LEFT, padx=(0, 6))
        tk.Button(
            input_row,
            text="Mic",
            command=self.listen,
            bg="#33415c",
            fg="white",
            activebackground="#455575",
            relief=tk.FLAT,
            padx=10,
            pady=8,
        ).pack(side=tk.LEFT)
        self._animate(0)

    def _append(self, text: str) -> None:
        self.transcript.configure(state=tk.NORMAL)
        self.transcript.insert(tk.END, text + "\n\n")
        self.transcript.see(tk.END)
        self.transcript.configure(state=tk.DISABLED)

    def _set_status(self, value: str) -> None:
        self.status.set(value)

    def _animate(self, tick: int) -> None:
        offset = tick % 14
        expansion = offset if offset <= 7 else 14 - offset
        margin = 25 - expansion // 2
        self.canvas.coords(self.orb, margin, margin, 100 - margin, 100 - margin)
        self.root.after(70, self._animate, tick + 1)

    def send(self) -> None:
        text = self.entry.get().strip()
        if not text:
            return
        self.entry.delete(0, tk.END)
        self._append(f"You: {text}")
        self._set_status("Thinking…")
        speak_response = self.speak_next
        self.speak_next = False
        threading.Thread(
            target=self._respond, args=(text, speak_response), daemon=True
        ).start()

    def _respond(self, text: str, speak_response: bool) -> None:
        response, _should_speak = handle_message(text)

        def update() -> None:
            self._append(f"Chouhan Myra: {response}")
            self._set_status("Ready · microphone is off")

        self.root.after(0, update)
        if speak_response:
            try:
                speak(response)
            except RuntimeError:
                pass

    def listen(self) -> None:
        self._set_status("Listening once…")
        self.canvas.itemconfigure(self.orb, fill="#efad5e")
        threading.Thread(target=self._listen_worker, daemon=True).start()

    def _listen_worker(self) -> None:
        try:
            text = listen_once()
        except RuntimeError as exc:
            self.root.after(0, self._append, str(exc))
            self.root.after(0, self._set_status, "Ready · microphone is off")
            self.root.after(0, self.canvas.itemconfigure, self.orb, "fill", "#5bbdde")
            return

        def submit() -> None:
            self.entry.delete(0, tk.END)
            self.entry.insert(0, text)
            self.speak_next = True
            self._set_status("Speech recognized · review, then press Send")
            self.canvas.itemconfigure(self.orb, fill="#5bbdde")

        self.root.after(0, submit)


def run_orb() -> None:
    root = tk.Tk()
    OrbWindow(root)
    root.mainloop()
