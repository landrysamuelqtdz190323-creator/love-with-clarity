# 安装：Codex 与 WorkBuddy

文档核对日期：2026-10-01。两个安装包由同一个 Skill 正文和同一套参考资料生成，区别是目录形式与平台元数据。入口名称可能随平台版本变化。

## 先选对文件

| 平台 | 下载包 | 解压后的关键结构 |
| --- | --- | --- |
| Codex | `love-with-clarity-codex-1.0.0.zip` | `love-with-clarity/SKILL.md` 及同目录的 `references/` |
| WorkBuddy | `love-with-clarity-workbuddy-1.0.0.zip` | ZIP 根目录直接有 `SKILL.md` 和 `references/` |

文件位于网页的“安装 Skill”入口，或仓库 `site/downloads/`。整个项目 ZIP 用于阅读与维护，不能代替 WorkBuddy 的专用技能包。

## WorkBuddy：导入本地 ZIP

1. 打开 WorkBuddy，进入“技能”或“专家·技能·连接器 → 技能”。
2. 选择“添加技能 → 上传技能”。
3. 选择 `love-with-clarity-workbuddy-1.0.0.zip`，保持原包，不必自行解压再压缩。
4. 在“已安装”列表确认出现“看清关系，也照顾自己”，并确认处于启用状态。
5. 新建对话，选择该技能或明确说“使用看清关系，也照顾自己这个技能”，尝试下方的虚构事件。

如果没有识别，检查上传的是技能包、ZIP 根目录有 `SKILL.md`，以及当前版本的技能开关和导入提示。包已按官方文件与元数据说明检查；实际导入与调用状态以你的 WorkBuddy 为准，不把文件校验当作平台已安装。

[WorkBuddy 官方安装说明](https://www.workbuddy.cn/docs/workbuddy/From-Beginner-to-Expert-Guide/Function-Description/Skills-Market) · [官方技能结构与元数据](https://open.workbuddy.cn/docs/skill)

## Codex：安装文件夹

解压 Codex 包后，保留完整的 `love-with-clarity` 文件夹。不要只复制 `SKILL.md`，否则会缺少场景与练习。

**只在一个项目使用**：将文件夹复制到项目里的 `.agents/skills/`，形成：

```text
你的项目/
└── .agents/skills/
    └── love-with-clarity/
        ├── SKILL.md
        ├── agents/openai.yaml
        └── references/
```

**在多个项目使用**：复制到个人目录的 `.agents/skills/`。macOS、Linux 路径为 `~/.agents/skills/love-with-clarity/`；Windows 本地环境通常是 `%USERPROFILE%\.agents\skills\love-with-clarity\`。如果使用 WSL，应安装在运行 Codex 的 Linux 用户目录，而不是另一个 Windows 用户目录。

macOS 可在 Finder 的“前往文件夹”中输入 `~/.agents/skills/`；文件夹不存在时先创建。Windows 可在文件资源管理器地址栏输入 `%USERPROFILE%\.agents\skills`，再创建缺少的目录。

Codex 官方说明支持自动发现新技能；若列表没有更新，重新打开相应项目或重启 Codex。CLI/IDE 可通过 `/skills` 或输入 `$love-with-clarity` 明确调用；桌面界面可从技能选择入口选中它。不要同时在多个扫描目录重复安装同名技能。

[OpenAI 官方技能与本地发现说明](https://developers.openai.com/codex/skills)

## 第一次试用

先使用虚构事件，确认已调用该 Skill，且能够读取场景资料：

```text
请使用 love-with-clarity（看清关系，也照顾自己）整理这个虚构事件：
我们约好周六见面，周五被取消，之后没有新的安排。
我有点失落，担心自己不重要。
请分开事实、感受和猜测，并给出一个可以调整的下一步。
```

应看到：承认情境和动机未知、整理你的需要、给出可调整的行动与参考场景；不应看到爱情分数、人格诊断或替你决定关系。宿主模型的输出会有差异，发现问题可反馈到项目贡献渠道，省略私密信息。

## 更新、停用与移除

更新前记录版本并保留需要的旧包。在相同安装范围替换同名文件夹或使用平台提供的更新/重新导入功能，确认只启用一个版本。不要删除宿主配置或其他技能。

WorkBuddy 可在已安装列表关闭技能；Codex 的启用/停用方式以当前界面或官方说明为准。手动移除时只移除你安装的 `love-with-clarity` 文件夹，再确认技能列表变化。

## 输入资料前

阅读 [隐私说明](privacy.md)。本包没有执行脚本、没有项目服务器，但宿主 AI 会按该平台的机制处理对话内容。自行选择是否分享概括事件、是否复制结果和是否保存报告。
