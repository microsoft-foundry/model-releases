"""Offline regression checks for the MAI-Transcribe-2 notebook's request definition.

Run: python -m unittest discover -s 1-scripts -p test_mai_transcribe.py -v
Uses the installed transcription SDK; never reads .env or calls Azure.
"""
from __future__ import annotations

import ast
import json
import re
import unittest
from pathlib import Path

from azure.ai.transcription.models import (
    EnhancedModeProperties,
    PhraseListProperties,
    TranscriptionOptions,
)

NOTEBOOK = Path(__file__).resolve().parent.parent / "4-models/mai-transcribe-2/mai-transcribe-2.ipynb"


class TranscriptionOptionsTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.cells = json.loads(NOTEBOOK.read_text(encoding="utf-8"))["cells"]
        source = next(
            "".join(cell["source"])
            for cell in cls.cells
            if cell["cell_type"] == "code" and "def make_options(" in "".join(cell["source"])
        )
        function = next(
            node for node in ast.parse(source).body
            if isinstance(node, ast.FunctionDef) and node.name == "make_options"
        )
        namespace = {
            "EnhancedModeProperties": EnhancedModeProperties,
            "PhraseListProperties": PhraseListProperties,
            "TranscriptionOptions": TranscriptionOptions,
        }
        exec(compile(ast.Module(body=[function], type_ignores=[]), str(NOTEBOOK), "exec"), namespace)
        cls.make_options = staticmethod(namespace["make_options"])

    def test_comparison_models_explicitly_enable_enhanced_mode(self):
        for model in ("mai-transcribe-1.5", "MAI-Transcribe-2"):
            with self.subTest(model=model):
                self.assertEqual(
                    self.make_options(model).as_dict(),
                    {"enhancedMode": {"enabled": True, "model": model}},
                )

    def test_preview_options_serialize_inside_enhanced_mode(self):
        for style in ("verbatim", "clean"):
            with self.subTest(style=style):
                definition = self.make_options(
                    "MAI-Transcribe-2", locales=["en-US"], phrases=["DevOps"],
                    biasing_weight=1.5, diarization=True, timestamps="word",
                    transcribe_style=style,
                ).as_dict()
                self.assertEqual(definition, {
                    "locales": ["en-US"],
                    "phraseList": {"phrases": ["DevOps"], "biasingWeight": 1.5},
                    "diarization": {"enabled": True},
                    "enhancedMode": {
                        "enabled": True,
                        "model": "MAI-Transcribe-2",
                        "modelOptions": {"timestamps": "word", "transcribeStyle": style},
                    },
                })

    def test_documented_rest_definition_matches_required_wire_shape(self):
        markdown = next(
            "".join(cell["source"]) for cell in self.cells
            if cell["cell_type"] == "markdown" and "### API surface" in "".join(cell["source"])
        )
        definition = json.loads(re.search(r"```json\n(.*?)\n```", markdown, re.DOTALL).group(1))
        self.assertEqual(definition["enhancedMode"], {
            "enabled": True,
            "model": "MAI-Transcribe-2",
            "modelOptions": {"timestamps": "word", "transcribeStyle": "verbatim"},
        })
        self.assertNotIn("modelOptions", definition)


if __name__ == "__main__":
    unittest.main()
