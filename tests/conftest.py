"""Pytest configuration for deterministic test behavior across environments."""

from __future__ import annotations

import os
import sys
import types
from typing import Any

os.environ.setdefault("KIVY_NO_ARGS", "1")


def _install_kivy_test_doubles() -> None:
    class _Widget:
        def __init__(self, **kwargs: Any) -> None:
            self.children: list[object] = []
            self.parent: object | None = None
            self.disabled = False
            self.opacity = 1
            self._bindings: dict[str, list[object]] = {}
            for key, value in kwargs.items():
                if key.startswith("on_") and callable(value):
                    self.bind(**{key: value})
                else:
                    setattr(self, key, value)

        def add_widget(self, widget: object) -> None:
            if hasattr(widget, "parent"):
                setattr(widget, "parent", self)
            self.children.append(widget)

        def bind(self, **kwargs: object) -> None:
            for key, value in kwargs.items():
                self._bindings.setdefault(key, []).append(value)

        def dispatch(self, event_name: str, *args: object) -> None:
            callbacks = self._bindings.get(event_name, [])
            for callback in callbacks:
                callback(self, *args)

    class _App:
        def run(self) -> object | None:
            build = getattr(self, "build", None)
            if callable(build):
                return build()
            return None

    class _BoxLayout(_Widget):
        pass

    class _Button(_Widget):
        pass

    class _Label(_Widget):
        pass

    class _Spinner(_Widget):
        pass

    class _Screen(_Widget):
        pass

    class _NoTransition:
        pass

    class _ScreenManager(_Widget):
        def __init__(self, **kwargs: Any) -> None:
            self.current = ""
            self.transition = None
            self.screens: dict[str, object] = {}
            super().__init__(**kwargs)

        def add_widget(self, widget: object) -> None:
            super().add_widget(widget)
            name = getattr(widget, "name", None)
            if isinstance(name, str):
                self.screens[name] = widget

    kivy_module = types.ModuleType("kivy")
    app_module = types.ModuleType("kivy.app")
    metrics_module = types.ModuleType("kivy.metrics")
    uix_module = types.ModuleType("kivy.uix")
    boxlayout_module = types.ModuleType("kivy.uix.boxlayout")
    button_module = types.ModuleType("kivy.uix.button")
    label_module = types.ModuleType("kivy.uix.label")
    screenmanager_module = types.ModuleType("kivy.uix.screenmanager")
    spinner_module = types.ModuleType("kivy.uix.spinner")
    widget_module = types.ModuleType("kivy.uix.widget")

    app_module.App = _App
    metrics_module.dp = lambda value: value
    boxlayout_module.BoxLayout = _BoxLayout
    button_module.Button = _Button
    label_module.Label = _Label
    screenmanager_module.NoTransition = _NoTransition
    screenmanager_module.Screen = _Screen
    screenmanager_module.ScreenManager = _ScreenManager
    spinner_module.Spinner = _Spinner
    widget_module.Widget = _Widget

    sys.modules["kivy"] = kivy_module
    sys.modules["kivy.app"] = app_module
    sys.modules["kivy.metrics"] = metrics_module
    sys.modules["kivy.uix"] = uix_module
    sys.modules["kivy.uix.boxlayout"] = boxlayout_module
    sys.modules["kivy.uix.button"] = button_module
    sys.modules["kivy.uix.label"] = label_module
    sys.modules["kivy.uix.screenmanager"] = screenmanager_module
    sys.modules["kivy.uix.spinner"] = spinner_module
    sys.modules["kivy.uix.widget"] = widget_module


if os.environ.get("CI"):
    _install_kivy_test_doubles()
