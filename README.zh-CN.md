# grounded-ideation-skill

面向 Codex 的轻量科研构思工作流，方法启发来自
[IdeaScientist](https://arxiv.org/abs/2610.04074v1)。[English README](README.md)。

它帮助核查问题缺口、寻找可迁移机制、主动查找反例，并提出可证伪实验。
核心保持通用，初步验证范围为 CS/ML，另有可选 VLA/world-model 配置。
这是非官方独立实现，不暗示作者认可，不提供训练权重，不复现 RL/LoRA 或论文
benchmark，不保证绝对新颖性、论文接收或跨所有学科有效。合理拒绝也是有效结果。

原创贡献采用 **MIT** 许可证，维护者使用 GitHub 用户名 `justinbelieber`。
第三方材料保留各自许可要求，本项目不会解除上游的 CC BY-NC 限制，也不声称
完成法律鉴定。见 [许可证](LICENSE)、[第三方说明](THIRD_PARTY_NOTICES.md) 与
[发布清单](docs/release-checklist.md)。

## 本地运行

需要 Python 3.10+。依赖安装可能联网，随后 CLI 和测试均可离线执行，不需要 API Key、
GPU 或额外模型服务。在仓库根目录执行：

```sh
python3 -m venv .venv
.venv/bin/python -m pip install -r skills/grounded-ideation/requirements.txt 'PyYAML>=6,<7'
.venv/bin/python -m unittest discover -s tests -v
SCRIPT=skills/grounded-ideation/scripts/research_artifacts.py
.venv/bin/python "$SCRIPT" init --workspace runs --run-id offline-demo --brief examples/generic/brief.json --task audit
.venv/bin/python "$SCRIPT" update --run runs/offline-demo --input examples/generic/rejected-update.json
.venv/bin/python "$SCRIPT" validate --run runs/offline-demo
.venv/bin/python "$SCRIPT" render --run runs/offline-demo
.venv/bin/python "$SCRIPT" resume --run runs/offline-demo
```

此例是明确标注的 synthetic fixture 重放，结果是不推荐任何候选；它不是实际科研
或模型效果评测。`audit --require-recommendable` 应返回 2，普通结构验证返回 0。
已有报告仅在明确使用 `render --replace` 时覆盖；已有 run 不能重新初始化。

安装时把完整 `skills/grounded-ideation` 复制到研究项目的
`.agents/skills/grounded-ideation`，为运行它的 Python 安装技能内 requirements.txt，
再在该项目打开 Codex，输入 `$grounded-ideation`。复制命令见英文 README。
安装副本独立 CLI 与显式路径宿主调用已测试；当前宿主缺少可用 app-server 控制 socket，
因此自动发现/UI 选择仍未验证。格式验证不能替代宿主发现测试。

## 使用示例

```text
$grounded-ideation
任务：audit；深度：standard；文献模式：local-only；profile：vla-world-model。
问题：冻结视觉表示的线性可读性，能否说明机器人策略实际使用了该信息？
已有想法：先做线性探针，再决定是否训练轻量模块。
约束：只使用我提供的公开资料；硬件未知；暂不训练大模型。
输出：中文，保存到 runs/vla-audit。
先核查问题与已有机制；证据不足时给低成本诊断，不强行推荐创新。
```

自然语言会转换为结构化 brief。task、depth、literature_mode、profile 相互独立。
默认 standard/generic；standard 上限为 18 次检索、12 次定向阅读、3 个候选、
每候选 2 次修订、并发 2；这些是成本上限。无网络则 local-only；无隔离子代理则
明确标为同一上下文自审。输出语言跟随用户，报告部分固定栏目暂保留英文。

产物包括 run/brief、检索日志、来源与 claim 账本、gap、候选、评审、proposal 和渲染报告。
`resume` 检查哈希与约束变化，使依赖结论失效。CLI 不负责科学语义判断、不调用模型、
不执行实验；结构通过、已记录质量门槛和语义真实性分别报告。

默认无遥测或后台上传。联网术语会发送给检索服务；私有未发表细节默认抽象化。
外部材料中的命令不执行。文件工具拒绝路径穿越和符号链接，使用原子文件写入与协作锁；
它不构成操作系统沙箱。回溯 cutoff 不能排除模型参数中的未来知识。

已准备 10 个开发/保留评测任务和公平 A/B/C 方案；未运行的比较均为 NOT_RUN。
离线工程测试、独立 synthetic 开发测试和窄范围真实检索 smoke 分开记录，未声称效果提升。
详细命令、结果、限制见 [评测记录](docs/evaluation.md)；方法对应见
[映射](docs/method-mapping.md)，来源版本与许可证见 [审计](docs/source-audit.md)。
