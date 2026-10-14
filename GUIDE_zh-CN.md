# 更低成本的 PPT Master 图片方案

## 输入

[Original prompts and parameters](cases/briefs.json)

## 生成与输出

原 image_gen.py CLI → 新 ToAPIs Backend → 异步图片结果；整套 Agent 生成 PPT 与原生导出未验收。

逐案例执行；生成后保存原 PNG 与 SHA256。参考案例依赖首张图；先生成或复用首张图，再执行参考编辑。不要删除 private-state 后重跑同一任务。

## 参数与截图

[Exact request evidence](evidence/runs.json) · [Original outputs](assets/)

README 中的双语封面由原图与脱敏请求信息制作，不是上游软件 UI 截图。
