"""ToAPIs async image backend for the original PPT Master CLI (MIT)."""
import base64
import os
from contextlib import ExitStack
from pathlib import Path

from .backend_common import report_resolution, resolve_output_path, save_image_bytes
from .toapis_async import ToAPIsClient

DEFAULT_MODEL = "gpt-image-2-vip"
DEFAULT_IMAGE_SIZE = "1K"
VALID_ASPECT_RATIOS = ["1:1", "16:9", "9:16", "4:3", "3:4", "3:2", "2:3"]
PIXELS = {"1:1": "1024x1024", "16:9": "1024x576", "9:16": "576x1024", "4:3": "1024x768", "3:4": "768x1024", "3:2": "1152x768", "2:3": "768x1152"}


def generate(prompt: str, aspect_ratio: str = "1:1", image_size: str = "1K",
             output_dir: str = None, filename: str = None, model: str = None,
             max_retries: int = 0, reference_image: str = None) -> str:
    """Generate or reference-edit one PNG; persist the task and never retry POST.

    Args:
        prompt: Image prompt or reference-edit instruction.
        aspect_ratio: One supported explicit ratio; mapped to ToAPIs ratio.
        image_size: This preview accepts only 1K.
        output_dir: Directory for the saved PNG.
        filename: Basename accepted by the original CLI.
        model: The tested model, gpt-image-2-vip.
        max_retries: Kept for the CLI contract; generation POST is never retried.
        reference_image: Optional local PNG/JPEG/WebP to upload.

    Returns:
        Validated PNG path saved through the original backend helper.
    """
    if aspect_ratio not in PIXELS or image_size.upper() != "1K":
        raise ValueError("This preview requires a supported ratio and 1K")
    chosen = model or os.environ.get("TOAPIS_MODEL", DEFAULT_MODEL)
    if chosen != DEFAULT_MODEL:
        raise ValueError("This preview is validated only for gpt-image-2-vip")
    client = ToAPIsClient(os.environ.get("TOAPIS_API_KEY"),
                          os.environ.get("TOAPIS_BASE_URL", "https://toapis.cn"),
                          "1K", os.environ.get("TOAPIS_STATE_DIR"))
    with ExitStack() as stack:
        params = dict(model=chosen, prompt=prompt, size=PIXELS[aspect_ratio],
                      quality="low", n=1, output_format="png")
        if reference_image:
            params["image"] = [stack.enter_context(open(reference_image, "rb"))]
        result = client.edit(**params) if reference_image else client.generate(**params)
    path = resolve_output_path(prompt, output_dir, filename, ext=".png")
    saved = save_image_bytes(base64.b64decode(result.data[0].b64_json), str(path))
    report_resolution(saved)
    return saved
