from __future__ import annotations

import shutil
import subprocess
import time
from pathlib import Path

from playwright.sync_api import Page, sync_playwright


APP_URL = "http://127.0.0.1:8765"
ROOT = Path(__file__).resolve().parents[1]
DEMO_DIR = ROOT / "demo_assets"
RAW_DIR = DEMO_DIR / "raw_video"
MP4_PATH = DEMO_DIR / "medtutor_demo_captioned.mp4"
WEBM_PATH = DEMO_DIR / "medtutor_demo_captioned.webm"


def main() -> None:
    DEMO_DIR.mkdir(exist_ok=True)
    if RAW_DIR.exists():
        shutil.rmtree(RAW_DIR)
    RAW_DIR.mkdir(parents=True)

    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(headless=True)
        context = browser.new_context(
            viewport={"width": 1280, "height": 720},
            record_video_dir=str(RAW_DIR),
            record_video_size={"width": 1280, "height": 720},
        )
        page = context.new_page()
        page.goto(APP_URL, wait_until="domcontentloaded")
        page.wait_for_selector("text=MedTutor Agent", timeout=30000)
        install_caption(page)

        caption(page, "MedTutor Agent turns static lecture notes into active medical exam practice.")
        pause(3)

        caption(page, "Step 1: The sample respiratory lecture is loaded. No patient data or API key is required.")
        page.mouse.wheel(0, 220)
        pause(3)
        page.mouse.wheel(0, -220)

        caption(page, "Step 2: We focus the workflow on COPD diagnosis and acute dyspnea.")
        page.get_by_label("Topic focus").fill("COPD diagnosis and acute dyspnea")
        pause(2)

        caption(page, "Step 3: The coordinator routes the request to retrieval, exam generation, validation, and export agents.")
        page.get_by_role("button", name="Run workflow").click()
        page.wait_for_selector("text=Agent Trace", timeout=60000)
        pause(5)

        caption(page, "The trace makes the multi-agent workflow auditable for judges: each specialist step is visible.")
        pause(4)

        caption(page, "The output includes MCQs, one best answer, explanations, and lecture source references.")
        first_mcq = page.locator("text=mcq_001").first
        if first_mcq.count():
            first_mcq.click()
        pause(4)

        caption(page, "The blueprint tab shows high-yield topics, clinical conditions, and likely exam angles.")
        page.get_by_role("tab", name="Blueprint").click()
        pause(4)

        caption(page, "Step 4: Switch to OSCE mode for oral, case-based clinical exam practice.")
        page.get_by_text("Generate OSCE cases").click()
        page.get_by_role("button", name="Run workflow").click()
        page.wait_for_selector("text=OSCE", timeout=60000)
        pause(5)

        caption(page, "OSCE stations include a stem, examiner questions, expected answers, common mistakes, and a checklist.")
        pause(4)

        caption(page, "Step 5: The export agent creates downloadable JSON, Markdown, and CSV study assets.")
        page.get_by_role("tab", name="Downloads").click()
        pause(5)

        caption(page, "Safety guardrails scan for prompt injection and possible PHI, and every output is educational-only.")
        page.get_by_role("tab", name="Output").click()
        pause(4)

        caption(page, "MedTutor Agent is a responsible multi-agent medical study system, not just a generic quiz bot.")
        pause(4)

        video = page.video
        context.close()
        browser.close()

        if video is None:
            raise RuntimeError("Playwright did not produce a video artifact.")
        raw_path = Path(video.path())

    if WEBM_PATH.exists():
        WEBM_PATH.unlink()
    shutil.copy2(raw_path, WEBM_PATH)
    convert_to_mp4(WEBM_PATH, MP4_PATH)
    print(MP4_PATH)


def install_caption(page: Page) -> None:
    page.evaluate(
        """
        () => {
          const style = document.createElement('style');
          style.textContent = `
            #demo-caption {
              position: fixed;
              left: 32px;
              right: 32px;
              bottom: 28px;
              z-index: 2147483647;
              background: rgba(15, 23, 42, 0.94);
              color: white;
              border: 1px solid rgba(255, 255, 255, 0.2);
              border-radius: 8px;
              box-shadow: 0 16px 36px rgba(0, 0, 0, 0.28);
              padding: 18px 22px;
              font-family: Inter, Segoe UI, Arial, sans-serif;
              font-size: 24px;
              line-height: 1.28;
              font-weight: 650;
              letter-spacing: 0;
            }
          `;
          document.head.appendChild(style);
          const caption = document.createElement('div');
          caption.id = 'demo-caption';
          caption.textContent = '';
          document.body.appendChild(caption);
        }
        """
    )


def caption(page: Page, text: str) -> None:
    page.evaluate(
        """
        (text) => {
          const caption = document.getElementById('demo-caption');
          if (caption) caption.textContent = text;
        }
        """,
        text,
    )


def pause(seconds: float) -> None:
    time.sleep(seconds)


def convert_to_mp4(source: Path, target: Path) -> None:
    if target.exists():
        target.unlink()
    command = [
        "ffmpeg",
        "-y",
        "-i",
        str(source),
        "-c:v",
        "libx264",
        "-pix_fmt",
        "yuv420p",
        "-movflags",
        "+faststart",
        str(target),
    ]
    subprocess.run(command, check=True)


if __name__ == "__main__":
    main()
