# 从需求到网页：操作指南

## 1 需求入口

Idea：提取已知类型、用途、风格、性格、配色，只问缺项。Existing image：检查原图，确认必须保留和允许优化。Real pet：保留可观察花纹与轮廓，再决定风格，不臆造照片看不见的标志。

init生成character/*.json作为源，views生成同名MD供审阅。先确认Brief，再整理Bible与定妆，最后Lock。Agent写数据，用户确认内容。

## 2 身份与确认

Bible包含identity、visual_identity、web_readability、body_topology。每个运动部件独立ID，不固定四爪、尾巴或翅膀。

正式原图放reference/，计算文件SHA-256填Lock.canonical。运行views，把Bible页Content hash填Lock.bible_sha256，再运行views得到最终Lock hash。

只有用户明确确认后，才填写approval的decision=approved、revision、approved_at、evidence_ref、payload_sha256。Brief与Lock分别确认，hash不包含approval字段。不要把计算hash当成用户批准。身份变化需要新版本和重审；这不是签名或证据真实性认证。

## 3 外部生成与动作

填写REFERENCE_SHEET_REQUEST、GENERATION_HANDOFF与ACTION_BRIEF。参考图按身体结构选视角，不强制三视图。每个动作写准备、重心、主动作/接触、反应、恢复与支撑部件。接触必须真的碰到指定目标。

返回原图，不用聊天截图。先检查视觉，再外部透明化和裁切。原图与RGBA帧分别留存。工具不会抠图、补画或判断美感。

## 4 配置例子

准备240×320的真RGBA PNG，四边至少1px透明余量，写actions/idle/clip.json：

```json
{"id":"idle","lock_version":1,"width":240,"height":320,"anchor":{"x":120,"y":304},"frames":[{"id":"f0","path":"actions/idle/frames/000.png"}],"sequence":["f0"],"durationsMs":[500],"reduced_motion_frame":"f0"}
```

这仅示范格式，一张图不是完整动画。真实动作增加源帧和时序；sequence可以重复ID，但时长必须等长、正整数毫秒。project.actions加入 `"idle":{"single":"idle"}`，default_action设idle。

等待型创建rest-enter/rest-loop/rest-exit三个clip，再加入 `"rest":{"enter":"rest-enter","loop":"rest-loop","exit":"rest-exit"}`。

不同clip可不同尺寸；每clip一个手动anchor。绘制位置是host.anchor减clip.anchor。不要逐帧按包围盒居中造成滑步。

## 5 观看与QA

validate通过后build，按README启动本地HTTP服务。Play complete action once播放完整一轮；Play / wait保持等待；Finish and return播完当前段再退出。检查三背景、80/120/160px、循环衔接。

QA/REVIEW.json绑定build_id。视觉检查身份、肢体、接触、支撑、连续性、附件和小尺寸识别。未评审保持not_reviewed，用户没看完整播放就保持pending。源、时序或播放器变动会改变build，不能继承旧批准。

## 常见问题

- Pillow缺失：用激活环境后的同一个python运行pip和脚本。
- 假透明：确认RGBA和实际alpha，棋盘格图片不等于透明。
- 触碰边界：检查裁切，补合理余量，不能切掉耳朵或翅膀。
- Bible changed：资料与锁不匹配，重审，不只是重算批准hash。
- 动画像幻灯片：补真实中间姿势、修接地锚点，而非单纯放慢。
- 无法加载预览：使用HTTP路径，查看页面错误；不要直接双击HTML。
- 已存在预览被改：保留证据，用新源版本构建，不覆盖已审阅内容。
