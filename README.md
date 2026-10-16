# Lower-cost PPT Master images

<!-- TOAPIS-MODEL-COST-UPDATE-20261016 -->
## Tested model types, presets and costs

Updated October 16, 2026. These are tested historical presets/prices; this addition does not relabel the original batch below.

| Model (API ID) | Type | Tested preset | Unit quote | Confirmed unit charge | Count |
|---|---|---|---:|---:|---:|
| gpt-image-2(VIP) (`gpt-image-2-vip`) | Image | low / 1K / n=1 | $0.0019/image | $0.0019 | 3 |

Confirmed original image/video example subtotal: **$0.0057**.

Community-fork image_gen.py CLI path validated; full agent/PPTX workflow unvalidated. Upstream does not accept gateway-specific backends.

gpt-image-2(VIP), **from $0.0019/image**; the tested low/1K preset here is **$0.0019/image**. Different models, qualities and resolutions do not imply equivalent results.
<!-- /TOAPIS-MODEL-COST-UPDATE-20261016 -->

[中文](README_zh-CN.md)

ToAPIs `gpt-image-2-vip / low / 1K / n=1` for PPT Master workflows. 3 image-2(vip) images: **$0.0057 actually charged**.

Original image_gen.py CLI → new ToAPIs backend → async image outputs. Full agent-driven decks and native PPTX export were not validated.

> Community tutorial; no upstream endorsement. “Lower-cost” describes this API tier, not total software or all-model costs.

## Demo

![API case overview](assets/overview-en.png)

| Case | Original image | Output pixels |
|---|---|---|
| 01-resort | [PNG](assets/01-resort.png) | 1536 × 864 |
| 02-solar | [PNG](assets/02-solar.png) | 1536 × 864 |
| 03-interior | [PNG](assets/03-interior.png) | 1536 × 864 |

## Model price and this demo’s cost

| Model | Configuration | API unit quote |
|---|---|---|
| `gpt-image-2-vip` | `low / 1K / n=1` | **$0.0019** |

3 image-2(vip) images: **$0.0057 actually charged**。

[API pricing snapshot](evidence/pricing.json) · [Cost record](evidence/costs.json) · [Original requests](evidence/runs.json)

Quote checked on 2026-10-14. Other tiers, resolutions, models, agents and machine costs are excluded.

[ToAPIs model landing page](https://go2v.toapis.com/1014_pptmaster_lowercost_gh_en)

## Reproduce

Set `TOAPIS_API_KEY` privately in your local environment. Keep it out of source code and chats. Use `TOAPIS_BASE_URL=https://toapis.cn` or `https://toapis.com`.

```bash
python -m pip install -r skills/ppt-master/requirements.txt
python skills/ppt-master/scripts/image_gen.py "A coastal eco-resort, no text" --backend toapis --model gpt-image-2-vip --aspect_ratio 16:9 --image_size 1K --output results --filename resort
```

This fork adds backend_toapis and CLI registration, preserving upstream MIT, skill identity and sponsor attribution. Single-image CLI generation was validated; manifest concurrency, complete PPTX workflows and agent hosts were not.

```bash
# Inspect without paid calls
python scripts/run_demo.py
# Generate the original cases (charged; exact quote checked first)
python scripts/run_demo.py --live --output results
```

The generic script is an external asset runner. Original PPT Master CLI runs are separately identified in the evidence.

## API mapping

```text
Authorization: Bearer TOAPIS_API_KEY
POST /v1/uploads/images             # reference PNG -> HTTPS URL
POST /v1/images/generations         # model,prompt,size,resolution,quality,n,reference_images
GET  /v1/images/generations/{id}    # poll the SAME task
completed -> result.data[0].url -> download PNG without the API key
```

Generation POST is never automatically retried. Preserve .toapis-state or results/private-state to resume the same task. Reference editing is not masked inpainting. Masks, transparency, audio and cloud video were not tested.

## Upstream and licenses

[hugohe3/ppt-master](https://github.com/hugohe3/ppt-master) · [pinned `b6843645`](https://github.com/hugohe3/ppt-master/tree/b6843645766c9ab63a7f1486cfd330d6ad337e99)

[Third-party notices](THIRD_PARTY_NOTICES.md)

[Preserved upstream documentation](README_UPSTREAM.md)
