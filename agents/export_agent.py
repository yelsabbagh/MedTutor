from __future__ import annotations

from typing import Any

from tools.export_tools import (
    blueprint_to_markdown,
    generate_output_file,
    mcqs_to_csv,
    mcqs_to_markdown,
    osce_to_markdown,
    to_pretty_json,
)


class ExportAgent:
    name = "Export Agent"

    def export_mcqs(self, mcqs: list[dict[str, Any]]) -> dict[str, str]:
        json_content = to_pretty_json(mcqs)
        markdown_content = mcqs_to_markdown(mcqs)
        csv_content = mcqs_to_csv(mcqs)
        return {
            "questions.json": generate_output_file("questions.json", json_content),
            "mcqs.md": generate_output_file("mcqs.md", markdown_content),
            "mcqs.csv": generate_output_file("mcqs.csv", csv_content),
            "_questions_json": json_content,
            "_mcqs_markdown": markdown_content,
            "_mcqs_csv": csv_content,
        }

    def export_osce(self, cases: list[dict[str, Any]]) -> dict[str, str]:
        json_content = to_pretty_json(cases)
        markdown_content = osce_to_markdown(cases)
        return {
            "osce_cases.json": generate_output_file("osce_cases.json", json_content),
            "osce_cases.md": generate_output_file("osce_cases.md", markdown_content),
            "_osce_json": json_content,
            "_osce_markdown": markdown_content,
        }

    def export_blueprint(self, blueprint: dict[str, Any]) -> dict[str, str]:
        json_content = to_pretty_json(blueprint)
        markdown_content = blueprint_to_markdown(blueprint)
        return {
            "study_blueprint.json": generate_output_file("study_blueprint.json", json_content),
            "study_plan.md": generate_output_file("study_plan.md", markdown_content),
            "_blueprint_json": json_content,
            "_blueprint_markdown": markdown_content,
        }
