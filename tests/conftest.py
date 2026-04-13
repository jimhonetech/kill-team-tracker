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
            self._bindings: dict[str, object] = {}
            for key, value in kwargs.items():
                setattr(self, key, value)

        def add_widget(self, widget: object) -> None:
            self.children.append(widget)

        def bind(self, **kwargs: object) -> None:
            self._bindings.update(kwargs)

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

    kivy_module = types.ModuleType("kivy")
    app_module = types.ModuleType("kivy.app")
    uix_module = types.ModuleType("kivy.uix")
    boxlayout_module = types.ModuleType("kivy.uix.boxlayout")
    button_module = types.ModuleType("kivy.uix.button")
    label_module = types.ModuleType("kivy.uix.label")

    app_module.App = _App
    boxlayout_module.BoxLayout = _BoxLayout
    button_module.Button = _Button
    label_module.Label = _Label

    sys.modules["kivy"] = kivy_module
    sys.modules["kivy.app"] = app_module
    sys.modules["kivy.uix"] = uix_module
    sys.modules["kivy.uix.boxlayout"] = boxlayout_module
    sys.modules["kivy.uix.button"] = button_module
    sys.modules["kivy.uix.label"] = label_module


if os.environ.get("CI"):
    _install_kivy_test_doubles()
