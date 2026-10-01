# 看清关系，也照顾自己 · Love With Clarity

从具体行为出发，整理感受与需求，选择自己的下一步。

这是一份中文公开指南、20 张场景卡、三份练习，以及可在 Codex、WorkBuddy 中使用的 AI Skill。适合成年用户思考现有伴侣关系，不限定性别、性取向或是否已婚。

**v0.1.0 是 AI 协助起草的公开草案；来源已核对，尚未经过独立心理专业审阅或真实用户效果评估。** 它提供个人反思与沟通支持，不是心理诊断、爱情评分工具或紧急援助服务。

## 从这里开始

| 你现在需要什么 | 入口 |
| --- | --- |
| 不知道从哪里想起 | [公开指南](skills/love-with-clarity/references/guide.md) |
| 有一件具体的事想梳理 | [20 个场景](skills/love-with-clarity/references/scenarios/index.md) |
| 想把事实、猜测与需求分开 | [事实与猜测练习](skills/love-with-clarity/references/exercises/facts-and-guesses.md) |
| 想清楚表达自己的需要 | [需求与边界练习](skills/love-with-clarity/references/exercises/needs-and-boundaries.md) |
| 想重新照顾自己的生活 | [七天自我关爱练习](skills/love-with-clarity/references/exercises/seven-day-care.md) |
| 想在 AI 对话里使用 | [Codex / WorkBuddy 安装说明](docs/install.md) |
| 出现威胁、强迫或暴力 | [安全支持](skills/love-with-clarity/references/safety.md) |

下载完整项目后，可直接打开 `site/index.html` 阅读网页、搜索场景并填写练习。网页无需注册或联网；表单内容不上传、不写入浏览器长期存储。导出文件和复制内容由你决定如何保存。

## 一个使用示例

输入：

> 昨天伴侣六小时没有回复消息。我很难受，担心自己不重要。请帮我整理这件事，看看下一步可以做什么。

Skill 会帮助整理：已经知道的行为、仍不清楚的情境、你的感受与需求、可观察的变化、一段可以调整的表达，以及一个今天就能完成的自我关爱行动。信息不足时会说明不足，不会判定对方内心、强迫你作决定或生成“爱你百分比”。

[查看五个完整虚构示例](skills/love-with-clarity/references/examples.md)。

## 第一版内容

- 20 张具体场景卡，覆盖联系与承诺、沟通与修复、边界与安全、自我关爱、选择与未来。
- 三份可打印、复制或在网页填写的练习。七天是便于开始的安排，不代表疗效周期。
- 一个共用 Skill；Codex 标准文件夹包与 WorkBuddy 本地导入 ZIP 由同一份正文和资料生成。
- 一个无外部字体、无分析追踪、无 AI 接口的静态阅读网页。
- [来源与证据边界](skills/love-with-clarity/references/sources.md)、[隐私说明](docs/privacy.md)、[实际验证记录](docs/validation.md)。

Skill 需要宿主平台的 AI 服务。平台可能处理你在对话中输入的信息；“文件装在本地”不代表“AI 推理完全离线”。本项目不自动读取聊天软件、联系人或账号，也不自动发送消息。

## 安装和更新

安装前先阅读 [安装说明](docs/install.md)。网页中的两个下载包分别对应 Codex 与 WorkBuddy；它们不是整个仓库的 ZIP。更新时保留需要的旧版本，避免重复安装同名 Skill。

[下载 WorkBuddy ZIP](site/downloads/love-with-clarity-workbuddy-0.1.0.zip) · [下载 Codex ZIP](site/downloads/love-with-clarity-codex-0.1.0.zip) · [SHA256 校验值](site/downloads/SHA256SUMS)

## 一起改进

欢迎贡献一个具体场景、核对一条出处、改善一句难以使用的表达，或反馈实际导入问题。请先看 [贡献方式](CONTRIBUTING.md)。公开 Issues 只讨论项目，不接收可识别个人的关系求助或私密聊天记录。

本项目的场景结构与练习为原创编辑内容。研究和机构资料只用于支持有限范围的说明；引用不表示来源机构认可本项目。

## 本地构建

阅读指南、打开网页和安装 Skill 都不需要 Python。维护者重新生成网页与安装包时使用 Python 3.9+：

```sh
python3 -m venv .build-venv
.build-venv/bin/python -m pip install -r requirements-build.txt
.build-venv/bin/python scripts/build.py
.build-venv/bin/python scripts/verify.py
```

Windows 可将 `.build-venv/bin/python` 换为 `.build-venv\Scripts\python.exe`。网页和安装包是生成结果；内容修改请从 `skills/love-with-clarity/references/` 开始。

## 许可

指南、场景、练习和 Skill 指令采用 [CC BY 4.0](LICENSE.md)，构建脚本与网页程序采用 [MIT](LICENSE-CODE)。外部链接材料保留各自的许可。再发布时保留署名、许可和来源，并说明修改。
