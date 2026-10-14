"""Kivy Android chat interface for Chouhan Myra."""

from __future__ import annotations

import math
import threading
from pathlib import Path
from typing import Any

from kivy.app import App
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.graphics import Color, Ellipse, RoundedRectangle
from kivy.metrics import dp, sp
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.scrollview import ScrollView
from kivy.uix.spinner import Spinner
from kivy.uix.textinput import TextInput
from kivy.uix.widget import Widget

from myra.ai.providers import get_assistant_response
from myra.mobile_config import (
    VALID_PROVIDERS,
    load_mobile_settings,
    save_mobile_settings,
)

BACKGROUND = (0.035, 0.055, 0.105, 1)
SURFACE = (0.075, 0.105, 0.18, 1)
SURFACE_LIGHT = (0.11, 0.15, 0.24, 1)
ACCENT = (0.31, 0.76, 0.96, 1)
TEXT = (0.91, 0.95, 1, 1)
MUTED = (0.61, 0.68, 0.8, 1)
GREEN = (0.36, 0.88, 0.71, 1)


def _button(text: str, *, color: tuple[float, float, float, float] = ACCENT) -> Button:
    return Button(
        text=text,
        size_hint_y=None,
        height=dp(48),
        background_normal="",
        background_down="",
        background_color=color,
        color=(0.025, 0.05, 0.09, 1),
        font_size=sp(15),
        bold=True,
    )


def _label(
    text: str,
    *,
    size: float = 15,
    color: tuple[float, float, float, float] = TEXT,
    height: float | None = None,
    bold: bool = False,
) -> Label:
    return Label(
        text=text,
        color=color,
        font_size=sp(size),
        bold=bold,
        halign="left",
        valign="middle",
        size_hint_y=None if height is not None else 1,
        height=dp(height) if height is not None else 0,
        text_size=(None, None),
    )


class Orb(Widget):
    """A small animated glow used as the assistant mark."""

    def __init__(self, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self.phase = 0.0
        self.bind(pos=self._draw, size=self._draw)
        Clock.schedule_interval(self._pulse, 1 / 24)

    def _pulse(self, dt: float) -> None:
        self.phase += dt * 2.1
        self._draw()

    def _draw(self, *_args: Any) -> None:
        self.canvas.clear()
        if self.width <= 0 or self.height <= 0:
            return
        radius = min(self.width, self.height) * (0.29 + 0.025 * (1 + math.sin(self.phase)))
        center_x = self.x + self.width / 2
        center_y = self.y + self.height / 2
        with self.canvas:
            Color(0.1, 0.62, 0.95, 0.13)
            Ellipse(pos=(center_x - radius * 1.55, center_y - radius * 1.55), size=(radius * 3.1, radius * 3.1))
            Color(0.14, 0.78, 0.98, 0.55)
            Ellipse(pos=(center_x - radius * 1.18, center_y - radius * 1.18), size=(radius * 2.36, radius * 2.36))
            Color(0.55, 0.91, 1, 1)
            Ellipse(pos=(center_x - radius, center_y - radius), size=(radius * 2, radius * 2))
            Color(0.15, 0.49, 0.83, 1)
            Ellipse(
                pos=(center_x - radius * 0.49, center_y - radius * 0.49),
                size=(radius * 0.98, radius * 0.98),
            )


class MessageBubble(BoxLayout):
    def __init__(self, speaker: str, message: str, *, user: bool = False, **kwargs: Any) -> None:
        super().__init__(
            orientation="vertical",
            padding=(dp(13), dp(10)),
            size_hint=(1, None),
            **kwargs,
        )
        background = (0.09, 0.19, 0.28, 1) if user else SURFACE
        with self.canvas.before:
            Color(*background)
            self.background_shape = RoundedRectangle(
                pos=self.pos,
                size=self.size,
                radius=[dp(14)],
            )
        self.bind(pos=self._sync_background, size=self._sync_background)
        self.message_label = Label(
            text=f"{speaker}\n{message}",
            color=TEXT,
            font_size=sp(14),
            halign="left",
            valign="top",
            size_hint=(1, None),
            text_size=(None, None),
        )
        self.message_label.bind(width=self._set_text_width)
        self.message_label.bind(texture_size=self._set_height)
        self.add_widget(self.message_label)

    def _set_text_width(self, _instance: Label, width: float) -> None:
        self.message_label.text_size = (max(0, width), None)

    def _set_height(self, _instance: Label, texture_size: tuple[float, float]) -> None:
        self.message_label.height = max(dp(28), texture_size[1])
        self.height = self.message_label.height + dp(20)
        self._sync_background()

    def _sync_background(self, *_args: Any) -> None:
        self.background_shape.pos = self.pos
        self.background_shape.size = self.size


class MyraMobileApp(App):
    title = "Chouhan Myra"

    def build(self) -> BoxLayout:
        Window.clearcolor = BACKGROUND
        Window.softinput_mode = "pan"
        self.settings_path = Path(self.user_data_dir) / "assistant-settings.json"
        self.root_layout = BoxLayout(
            orientation="vertical",
            padding=(dp(16), dp(12)),
            spacing=dp(10),
        )
        try:
            self.settings = load_mobile_settings(self.settings_path)
        except RuntimeError as exc:
            self.root_layout.add_widget(
                _label(f"Settings could not be opened.\n{exc}", size=15)
            )
            return self.root_layout

        self.history: list[dict[str, str]] = []
        if self.settings["groq_api_key"] and self.settings["gemini_api_key"]:
            self._show_chat()
        else:
            self._show_keys(editing=False)
        return self.root_layout

    def _show_keys(self, *, editing: bool) -> None:
        self.root_layout.clear_widgets()
        self.root_layout.add_widget(Widget(size_hint_y=None, height=dp(6)))
        title = _label("Set up your assistant" if not editing else "API key settings", size=25, bold=True)
        self.root_layout.add_widget(title)
        self.root_layout.add_widget(
            _label(
            "Enter both provider keys. They are stored only in this app's private data.",
                size=14,
                color=MUTED,
                height=48,
            )
        )

        provider_row = BoxLayout(
            orientation="horizontal",
            spacing=dp(10),
            size_hint_y=None,
            height=dp(48),
        )
        provider_row.add_widget(_label("Preferred provider", size=14, color=MUTED))
        self.setup_provider = Spinner(
            text=self.settings.get("provider", "Groq"),
            values=sorted(VALID_PROVIDERS),
            size_hint_x=0.55,
            background_normal="",
            background_color=SURFACE_LIGHT,
            color=TEXT,
            font_size=sp(14),
        )
        provider_row.add_widget(self.setup_provider)
        self.root_layout.add_widget(provider_row)

        self.groq_key_input = TextInput(
            hint_text="Groq API key" + (" (blank keeps saved key)" if editing else ""),
            password=True,
            multiline=False,
            size_hint_y=None,
            height=dp(52),
            padding=(dp(12), dp(14)),
            background_color=SURFACE,
            foreground_color=TEXT,
            hint_text_color=MUTED,
            cursor_color=ACCENT,
            font_size=sp(14),
        )
        self.gemini_key_input = TextInput(
            hint_text="Gemini API key" + (" (blank keeps saved key)" if editing else ""),
            password=True,
            multiline=False,
            size_hint_y=None,
            height=dp(52),
            padding=(dp(12), dp(14)),
            background_color=SURFACE,
            foreground_color=TEXT,
            hint_text_color=MUTED,
            cursor_color=ACCENT,
            font_size=sp(14),
        )
        self.root_layout.add_widget(self.groq_key_input)
        self.root_layout.add_widget(self.gemini_key_input)

        self.key_status = _label("", size=13, color=MUTED, height=38)
        self.root_layout.add_widget(self.key_status)
        save_button = _button("Save keys and continue")
        save_button.bind(on_release=self._save_keys)
        self.root_layout.add_widget(save_button)
        if editing:
            back_button = _button("Back to chat", color=SURFACE_LIGHT)
            back_button.color = TEXT
            back_button.bind(on_release=lambda *_: self._show_chat())
            self.root_layout.add_widget(back_button)

    def _save_keys(self, *_args: Any) -> None:
        groq_key = self.groq_key_input.text.strip() or self.settings["groq_api_key"]
        gemini_key = self.gemini_key_input.text.strip() or self.settings["gemini_api_key"]
        if not groq_key or not gemini_key:
            self.key_status.text = "Both Groq and Gemini keys are required."
            return

        settings = {
            "provider": self.setup_provider.text,
            "groq_api_key": groq_key,
            "gemini_api_key": gemini_key,
        }
        try:
            save_mobile_settings(self.settings_path, settings)
        except (OSError, RuntimeError, ValueError) as exc:
            self.key_status.text = str(exc)
            return
        self.settings = settings
        self._show_chat()

    def _show_chat(self) -> None:
        self.root_layout.clear_widgets()
        header = BoxLayout(
            orientation="horizontal",
            spacing=dp(8),
            size_hint_y=None,
            height=dp(48),
        )
        header.add_widget(_label("CHOUHAN MYRA", size=19, bold=True))
        self.provider_spinner = Spinner(
            text=self.settings.get("provider", "Groq"),
            values=sorted(VALID_PROVIDERS),
            size_hint_x=0.35,
            background_normal="",
            background_color=SURFACE_LIGHT,
            color=TEXT,
            font_size=sp(13),
        )
        self.provider_spinner.bind(text=self._provider_changed)
        header.add_widget(self.provider_spinner)
        keys_button = _button("Keys", color=SURFACE_LIGHT)
        keys_button.color = TEXT
        keys_button.size_hint_x = 0.23
        keys_button.bind(on_release=lambda *_: self._show_keys(editing=True))
        header.add_widget(keys_button)
        self.root_layout.add_widget(header)

        identity = BoxLayout(
            orientation="horizontal",
            spacing=dp(8),
            size_hint_y=None,
            height=dp(72),
        )
        identity.add_widget(Orb(size_hint=(None, 1), width=dp(68)))
        identity.add_widget(
            _label(
                "AI chat with Groq and Gemini\nGroq requests fall back to Gemini if needed",
                size=13,
                color=MUTED,
            )
        )
        self.root_layout.add_widget(identity)

        self.message_list = GridLayout(
            cols=1,
            spacing=dp(9),
            size_hint_y=None,
            padding=(0, dp(4)),
        )
        self.message_list.bind(minimum_height=self.message_list.setter("height"))
        self.chat_scroll = ScrollView(
            do_scroll_x=False,
            bar_width=dp(3),
            scroll_type=["bars", "content"],
        )
        self.chat_scroll.add_widget(self.message_list)
        self.root_layout.add_widget(self.chat_scroll)

        self.chat_status = _label(
            "Keys stay in this app's private storage.",
            size=12,
            color=MUTED,
            height=28,
        )
        self.root_layout.add_widget(self.chat_status)
        composer = BoxLayout(
            orientation="horizontal",
            spacing=dp(8),
            size_hint_y=None,
            height=dp(52),
        )
        self.message_input = TextInput(
            hint_text="Message Chouhan Myra",
            multiline=False,
            size_hint_x=0.77,
            padding=(dp(12), dp(14)),
            background_color=SURFACE,
            foreground_color=TEXT,
            hint_text_color=MUTED,
            cursor_color=ACCENT,
            font_size=sp(14),
        )
        self.message_input.bind(on_text_validate=self._send_message)
        self.send_button = _button("Send")
        self.send_button.size_hint_x = 0.23
        self.send_button.bind(on_release=self._send_message)
        composer.add_widget(self.message_input)
        composer.add_widget(self.send_button)
        self.root_layout.add_widget(composer)

        self._append_message(
            "CHOUHAN MYRA",
            "Hi! Choose Groq or Gemini above and send a message.",
            user=False,
        )

    def _provider_changed(self, _spinner: Spinner, provider: str) -> None:
        if provider not in VALID_PROVIDERS:
            return
        self.settings["provider"] = provider
        try:
            save_mobile_settings(self.settings_path, self.settings)
        except (OSError, RuntimeError, ValueError):
            self.chat_status.text = "Could not save the provider choice."
            return
        if hasattr(self, "chat_status"):
            self.chat_status.text = f"Using {provider}. Groq falls back to Gemini on failure."

    def _send_message(self, *_args: Any) -> None:
        prompt = self.message_input.text.strip()
        if not prompt or self.send_button.disabled:
            return
        self.message_input.text = ""
        self.history.append({"role": "user", "content": prompt})
        self._append_message("You", prompt, user=True)
        self.send_button.disabled = True
        preferred = self.provider_spinner.text
        history = list(self.history[:-1][-20:])
        keys = (
            self.settings["groq_api_key"],
            self.settings["gemini_api_key"],
        )
        self.chat_status.text = f"Contacting {preferred}…"

        def worker() -> None:
            try:
                answer, used_provider, fell_back = get_assistant_response(
                    prompt,
                    provider=preferred,
                    groq_api_key=keys[0],
                    gemini_api_key=keys[1],
                    history=history,
                )
                Clock.schedule_once(
                    lambda _dt: self._finish_response(
                        answer,
                        used_provider=used_provider,
                        fell_back=fell_back,
                    ),
                    0,
                )
            except Exception:
                Clock.schedule_once(
                    lambda _dt: self._finish_response(
                        None,
                        used_provider=preferred,
                        fell_back=False,
                    ),
                    0,
                )

        threading.Thread(target=worker, daemon=True).start()

    def _finish_response(
        self,
        answer: str | None,
        *,
        used_provider: str,
        fell_back: bool,
    ) -> None:
        self.send_button.disabled = False
        if answer is None:
            self.chat_status.text = (
                "Request failed. Check both saved keys and your internet connection."
            )
            return
        self.history.append({"role": "assistant", "content": answer})
        self._append_message("CHOUHAN MYRA", answer, user=False)
        self.chat_status.text = (
            "Groq failed; replied with Gemini fallback."
            if fell_back
            else f"Answered by {used_provider}."
        )

    def _append_message(self, speaker: str, message: str, *, user: bool) -> None:
        bubble = MessageBubble(speaker, message, user=user)
        self.message_list.add_widget(bubble)
        Clock.schedule_once(lambda _dt: self.chat_scroll.scroll_to(bubble), 0.1)
