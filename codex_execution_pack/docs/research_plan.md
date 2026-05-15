# ReVision-Context++ 顶会潜力评测与优化版研究方案

> 目标：在已有 **Fidelity-Aware Hybrid Visual-Text Context Compression for Long-Context LLMs / ReVision-Context / HiVT** idea 基础上，进一步提高 NeurIPS / ICLR / ICML / ACL / EMNLP 主会录用概率。  
> 建议新定位：**从“VIST/Glyph 上加文本锚点”升级为“固定预算下的可验证保真度分配问题”**。  
> 推荐标题：**ReVision-Context++: Verifiable Budgeted Fidelity Allocation for Hybrid Visual-Text Long-Context Compression**

---

## 0. 一句话结论

这个 idea **值得继续推进，但必须升级论文叙事**。

当前版本的核心模块（text anchors、query-aware router、adaptive re-read）方向正确，直接命中了视觉上下文压缩的最大短板：**视觉表示保覆盖，但精确符号保真不足**。不过，如果论文只是把 VIST / Glyph / DeepSeek-OCR 与若干启发式文本锚点拼起来，顶会审稿人很容易判定为 **incremental engineering**。

为了显著提高主会概率，建议将贡献重构为：

> **在固定 token / latency / memory 预算下，如何为不同上下文信息类型自适应选择视觉、文本锚点、文本 latent、局部重读或丢弃，从而获得 coverage–fidelity Pareto improvement？**

换言之，论文不应主打“我们加了 anchors”，而应主打：

1. 提出一个新的问题定义：**Budgeted Fidelity Allocation**；
2. 提出一个可学习分配器：**把 context span 分配到不同表示模态**；
3. 提出一个可复现 benchmark：**专测 exactness-sensitive compression failure**；
4. 提出一个可验证推理机制：**先压缩，再验证，必要时局部 re-read**；
5. 用强 ablation 和 oracle upper bound 证明增益来自“保真度分配”，不是简单多给文本 token。

---

## 1. 当前 idea 顶会潜力评估

### 1.1 当前版本评分

| 维度 | 当前版本评分 | 优化后目标评分 | 判断 |
|---|---:|---:|---|
| 问题重要性 | 8.5 / 10 | 9.0 / 10 | 长上下文成本、视觉压缩、符号保真都是 2025–2026 高热方向。 |
| Novelty | 6.0 / 10 | 8.0 / 10 | 当前 anchors/router/reread 单看偏组合；升级为 budgeted fidelity allocation 后 novelty 明显增强。 |
| 技术深度 | 6.5 / 10 | 8.0–8.5 / 10 | 需要从启发式升级到可学习分配、oracle 监督、verification-triggered reread。 |
| 实验说服力 | 6.5 / 10 | 8.5 / 10 | 必须补 fidelity benchmark、真实任务、Pareto 曲线、强 baseline 和 error taxonomy。 |
| 工程可行性 | 8.0 / 10 | 7.5 / 10 | 新方案稍复杂，但可以分阶段落地，第一版不必端到端大训。 |
| 主会概率 | 35–45% | 60–72% | 前提是 benchmark + learning allocator + oracle analysis 做扎实。 |

### 1.2 当前 idea 最大优点

它抓住了视觉压缩路线最容易被攻击的点：**视觉 token 能保留全局结构，但对数字、变量名、公式、URL、表格 cell、代码符号这类 exact symbols 容易失真**。

这正好与近期工作形成互补：

- **VIST** 已经证明 long text → rendered image → visual tokens → LLM cross-attention 是有效路线，并用 PVE / frequency-based masking 提升语义密度；但它的目标更偏平均任务表现和效率，不专门解决 exactness-sensitive failure。
- **Glyph** 已经把“渲染长文本为图片 + VLM 处理”做到 3–4× 压缩，并加入 LLM-driven rendering search；因此单纯做视觉文本压缩已经不够新。
- **DeepSeek-OCR** 证明 optical compression 在 OCR 重建上 9–10× 压缩仍可高精度，但在 20× 高压缩下 precision 明显下降，说明 fidelity bottleneck 是真实存在的。
- **LongCodeOCR** 明确指出视觉代码压缩有 coverage–fidelity trade-off：全局覆盖强，但 exactness-critical code task 有 symbol-level bottleneck。
- **C3** 则从纯文本 latent compression 方向给出强反驳：文本 latent 在重建任务上可达到更高压缩和更高保真，因此 ReVision-Context++ 必须清楚说明自己不是要在纯重建任务上打败 C3，而是要解决视觉结构覆盖与文本精确保真之间的预算分配。

### 1.3 当前 idea 最大风险

当前版本容易被审稿人质疑：

> “这是不是 VIST/Glyph + regex anchors + second-pass retrieval？”

为了避免这个评价，需要把模块从“功能拼装”改造成统一框架：

- Fidelity anchors 不是人工补丁，而是分配器选择的一种表示动作；
- query-aware router 不是 heuristic ranker，而是 budgeted decision policy；
- adaptive re-read 不是简单二阶段推理，而是 verifier 触发的可控预算机制；
- benchmark 不是 synthetic demo，而是系统刻画视觉压缩在 exactness-sensitive 信息上的失效边界。

---

## 2. 推荐的新论文定位

### 2.1 新标题候选

1. **ReVision-Context++: Verifiable Budgeted Fidelity Allocation for Hybrid Visual-Text Long-Context Compression**
2. **Fidelis-Context: Fidelity-Aware Modality Allocation for Long-Context Compression**
3. **Hybrid Fidelity Routing: When Should Long-Context LLMs See Text, Pixels, or Both?**
4. **Coverage is Not Fidelity: Verifiable Hybrid Compression for Exact Long-Context Reasoning**

最推荐第 1 个，因为继承已有 ReVision-Context，又突出三个关键词：**Verifiable、Budgeted、Fidelity Allocation**。

### 2.2 新核心 claim

> 视觉上下文压缩可以低成本保留长上下文覆盖和二维结构，但在 exactness-sensitive 信息上存在可系统刻画的保真度瓶颈。ReVision-Context++ 将长上下文压缩建模为固定预算下的 fidelity allocation 问题，为不同 span 自适应选择视觉压缩、文本锚点、文本 latent 或局部重读，并通过 verifier 控制二次读取预算，从而在相同总预算下显著提升 coverage–fidelity Pareto frontier。

### 2.3 最强卖点

这篇论文应该让审稿人记住一句话：

> **视觉压缩解决 coverage，文本锚点解决 fidelity，可验证分配解决二者的预算冲突。**

---

## 3. 与已有工作的差异化定位

| 相关工作 | 已解决什么 | 未解决什么 | ReVision-Context++ 应强调的差异 |
|---|---|---|---|
| VIST | 视觉路径压缩 long context，PVE 提升语义密度 | 不专门处理数字、代码、公式、表格 cell 等精确信息 | 在 VIST 类视觉压缩上加 fidelity-aware allocation，而不是仅做视觉 token compression。 |
| CEPE | 小 encoder 分块并行编码长上下文，通过 cross-attention 接入 LLM | 输入仍是文本 token encoder，缺少视觉结构压缩；没有 fidelity 类型分配 | 将 CEPE 作为 text-encoder baseline，证明 hybrid allocation 更适合结构 + exactness 混合任务。 |
| LLaVolta / Visual Context Compressor | 证明视觉 token 有冗余，简单 pooling 可有效压缩 | 面向自然图像/视频 MLLM，非 text-rendered exactness | 借鉴 staged compression，但关注 rendered text 的 symbol fidelity。 |
| DeepSeek-OCR | 证明 optical compression 可行，并给出 7–20× OCR 压缩实证 | 高压缩下 precision 下降；主要是 OCR/解析，不是下游 reasoning allocation | 用 OCR risk 作为分配器特征，给高风险 span 保留 text anchors 或 reread。 |
| Text or Pixels | off-the-shelf MLLM 可用图片替代长文本，节省约一半 decoder tokens | 不训练，不处理复杂 exactness-sensitive failure | 在 zero-shot text-as-image 基础上加入可学习分配与 verifier。 |
| Glyph | 大规模视觉文本压缩，rendering search，3–4× 压缩 | 更关注整体长上下文能力和渲染配置，不强调精确信息类型分配 | Glyph 可作为视觉 backbone / strong baseline；ReVision-Context++ 解决 Glyph 的 fidelity failure mode。 |
| LongCodeOCR | 证明视觉代码压缩保留全局依赖，减少 selective filtering 的 dependency breakage | exactness-critical code task 仍有 symbol-level bottleneck | 以 LongCodeOCR 的 trade-off 为直接动机：视觉覆盖 + 文本符号锚点。 |
| C3 | 纯文本 latent compression 在重建任务上很强 | 难保留二维布局/表格/代码结构；需要训练文本 autoencoder；不解决视觉结构优势 | 把 C3 作为纯文本 latent upper baseline，证明 hybrid 在结构化下游任务和可插拔性上的价值。 |

---

## 4. 方法重构：从三个模块升级为统一框架

### 4.1 问题定义：Budgeted Fidelity Allocation

给定长上下文 \(C = \{s_i\}_{i=1}^{n}\)、查询 \(q\)、总预算 \(B\)，每个 span \(s_i\) 可选择一种或多种表示动作：

- \(a_i = \text{VIS-LOW}\)：低分辨率视觉压缩，低成本，适合背景与全局结构；
- \(a_i = \text{VIS-HIGH}\)：高分辨率视觉压缩，中成本，适合表格、公式、代码密集区域；
- \(a_i = \text{TEXT-ANCHOR}\)：保留原文短 span，高成本但高保真，适合数字、变量、URL、日期、实体；
- \(a_i = \text{TEXT-LATENT}\)：用小文本 encoder / latent compressor 表示，适合语义段落；
- \(a_i = \text{DROP}\)：丢弃低价值 span；
- \(a_i = \text{REREAD}\)：推理后按需读取原文或局部 crop。

目标函数：

\[
\max_{a_1,\dots,a_n} \; \mathbb{E}[S(y, y^*)] - \lambda \sum_i \text{Cost}(a_i)
\]

其中 \(S\) 是下游任务分数，可包含 exact match、F1、edit distance、pass@1、table-cell EM 等；Cost 同时统计 text tokens、visual tokens、KV cache、latency、reread expected cost。

### 4.2 模块 1：Fidelity-Sensitive Span Detector

不要只做 regex。建议做两级 detector：

**Level 1：高召回候选抽取**

- regex：数字、日期、百分比、货币、ID、URL、email、版本号、路径、代码 identifier、LaTeX symbol；
- tokenizer 特征：罕见 token、BPE 切分很碎的 token、非自然语言字符密集 span；
- layout 特征：表格 header/cell、公式块、代码块、列表项、脚注；
- query overlap：query 中实体、属性、时间、变量名与 span 的 overlap；
- answer-type prior：问题问 “how many / when / which function / what value / where in table”。

**Level 2：risk scoring**

为每个 span 预测视觉压缩后的错误风险：

\[
r_i = P(\text{visual compression corrupts } s_i \mid q, s_i, layout_i, \rho_i)
\]

特征包括：

- 字符相似风险：0/O、1/l/I、-/_、{}/()、;/:、小数点、负号；
- 渲染密度：font size、DPI、line height、tokens-per-image；
- 语义关键度：query relevance、IDF、是否在 answer candidate 周围；
- 类型关键度：number/date/code/formula/table/URL 权重更高；
- 视觉不确定度：OCR head confidence、vision-token entropy、cross-attention dispersion。

### 4.3 模块 2：Budgeted Modality Allocator

这是从 heuristic 走向顶会 novelty 的关键。

#### 4.3.1 Heuristic 版，用于快速跑通

得分：

\[
U_i(a) = \alpha \cdot \text{Relevance}_i + \beta \cdot \text{Risk}_i + \gamma \cdot \text{TypeWeight}_i - \lambda \cdot \text{Cost}(a)
\]

用 knapsack / greedy 在预算内选 anchors、VIS-HIGH 和 reread candidates。

#### 4.3.2 Trainable 版，用于主实验

输入：

- span embedding；
- query embedding；
- layout embedding；
- token density / OCR risk；
- type embedding；
- visual preview embedding；
- current budget state。

输出：

\[
P(a_i \in \{\text{VIS-LOW}, \text{VIS-HIGH}, \text{TEXT-ANCHOR}, \text{TEXT-LATENT}, \text{DROP}, \text{REREAD}\})
\]

训练方式建议三阶段：

1. **Oracle distillation**：用小规模 exhaustive / beam search 找到最小预算下能答对的 modality set，训练 allocator 模仿 oracle；
2. **Differentiable relaxation**：Gumbel-Softmax / Soft top-k，在预算约束下端到端优化；
3. **Verifier-aware fine-tuning**：用下游任务 reward 和 reread cost 做 policy gradient 或 DPO-style preference learning。

### 4.4 模块 3：Anchor-Aware Visual Alignment

原来的 Weighted PVE 可以保留，但需要升级为更像“贡献”的 loss。

建议加入三个 loss：

#### 4.4.1 Page-to-anchor contrastive alignment

让每个 visual page token 与该页 critical anchors 对齐，而不是只做全局图文平均池化。

\[
\mathcal{L}_{p2a} = -\log \frac{\exp(v_p \cdot e_{a^+}/\tau)}{\exp(v_p \cdot e_{a^+}/\tau)+\sum_{a^-}\exp(v_p \cdot e_{a^-}/\tau)}
\]

#### 4.4.2 Type-aware copy loss

对 exactness-sensitive span 施加更大权重：

\[
\mathcal{L}_{copy} = \sum_{t \in C} w_{type(t)} \cdot \text{CE}(\hat{x}_t, x_t)
\]

权重示例：code token / number / formula / URL > entity > normal words > stopwords。

#### 4.4.3 Hard negative loss

构造相似但错误的负样本：

- 2024 vs 2025；
- `user_id` vs `userID`；
- `foo_bar` vs `foo-bar`；
- `0.001` vs `0.01`；
- `<=` vs `<`；
- `O(n log n)` vs `O(n)`。

这样能让视觉 token 不只学语义，还学对符号差异敏感。

### 4.5 模块 4：Verification-Triggered Adaptive Re-read

二次读取必须避免被批评为“无限开后门”。建议严格建模为 expected budget：

\[
B_{total}=B_{visual}+B_{anchor}+p_{trigger} \cdot B_{reread}
\]

Verifier 输入：

- 生成答案；
- answer span 类型；
- cross-attention 是否集中到高风险 visual page；
- 输出中是否包含数字/代码/公式；
- 视觉 OCR confidence；
- answer consistency：visual-only answer vs anchor-only answer 是否一致。

触发条件：

- 低置信度；
- exact answer 但无 text anchor 支持；
- visual-only 与 anchor-only 不一致；
- 生成了高风险类型，例如数字、代码片段、表格 cell；
- verifier 判定可能 hallucination。

Reread 动作：

1. 读取原文 page-line span；
2. 读取局部 high-res crop；
3. 读取附近 ±k 行；
4. 读取依赖闭包，例如代码定义、表格 header、公式上下文。

---

## 5. Benchmark 设计：FidBench-Long

顶会概率能否提高，很大程度取决于 benchmark 是否足够干净、有说服力。建议把 benchmark 作为论文第二大贡献。

### 5.1 为什么需要新 benchmark

现有评测常见问题：

- Needle-in-a-haystack 偏检索，不足以证明 fidelity；
- OCR benchmark 偏重建，不等价于下游 reasoning；
- LongBench 等通用 benchmark 的平均分掩盖 exact symbol failure；
- 代码 benchmark 能体现 exactness，但不覆盖数字、表格、公式、URL、实体绑定等文档场景。

### 5.2 FidBench-Long 的任务族

建议至少 6 类，每类都要求模型在压缩上下文中保留精确信息。

| 子任务 | 核心考察 | 示例问题 | 指标 |
|---|---|---|---|
| Numeric QA | 数字、单位、比较、聚合 | “2023 年 Q4 revenue 是多少？” | exact match、relative error |
| Temporal / Date QA | 日期、顺序、时间窗口 | “合同在什么日期终止？” | date EM |
| Entity Binding | 多跳实体绑定 | “与 Alice 同时出现在 Table 3 的公司是哪家？” | EM / F1 |
| Table Cell QA | 表格 header-cell 对齐 | “第 4 行 EBITDA margin 是多少？” | cell EM |
| Formula / Math | 公式符号、变量、上下标 | “公式中 beta_2 的定义是什么？” | normalized edit distance |
| Code Symbol QA | 函数名、参数、类型、调用依赖 | “哪个 constructor 接受 ILayerCell？” | exact match / pass@1 |
| URL / Path / Config | 路径、URL、版本号、配置项 | “配置文件里 timeout_ms 的值是多少？” | string EM |
| Multi-hop Mixed | 视觉结构 + exact answer | “根据图表标题和表格脚注，最终答案是多少？” | task-specific EM |

### 5.3 数据构造建议

**Synthetic split：用于可控诊断**

- 自动生成文档、表格、代码片段、配置文件、公式块；
- 控制 context length：8K / 32K / 128K / 512K；
- 控制干扰强度：相似数字、相似变量、重复实体、错位表头；
- 控制压缩比：2× / 4× / 8× / 16×；
- 保留 oracle answer span 和页面坐标。

**Real split：用于主实验说服力**

- LongBench / NarrativeQA / Qasper：长文档问答；
- HotpotQA / 2WikiMultihopQA：多跳实体绑定；
- FinQA / TAT-QA / WikiTableQuestions：表格与数字推理；
- arXiv / ProofPile：公式和科学文本；
- RepoBench-P / LongCodeQA / Long Module Summarization：代码理解；
- DocVQA / InfographicsVQA / ChartQA：保留二维结构的文档图像任务。

### 5.4 新指标：Fidelity-Aware Pareto Score

不能只报告 average accuracy。建议报告：

1. **Task Score**：原任务准确率；
2. **Exactness Score**：只在 exact symbols 上评估 EM / edit distance；
3. **Compression Ratio**：raw text tokens / total consumed tokens；
4. **Expected Latency**：包含 render、vision encode、LLM prefill、reread；
5. **Memory / KV Cost**；
6. **Pareto AUC**：在不同预算下 accuracy–cost 曲线面积；
7. **Fidelity Failure Rate**：数字错、变量错、单位错、表头错、依赖缺失等错误率。

建议引入主指标：

\[
\text{FAPS} = \text{AUC}_{B \in \mathcal{B}} \left( \text{ExactScore}(B), -\log \text{Cost}(B) \right)
\]

即 **Fidelity-Aware Pareto Score**。

---

## 6. 实验设计

### 6.1 Baselines 必须足够强

| 类别 | Baseline | 用途 |
|---|---|---|
| Full text | 原始长上下文 LLM / long-context LLM | upper bound，但成本最高。 |
| Pure visual | VIST、Glyph、Text-or-Pixels、DeepSeek-OCR-style rendering | 证明纯视觉在 exactness 上的瓶颈。 |
| Pure text compression | CEPE、LLMLingua、Selective Context、LongCodeZip、C3 | 证明文本路线的优势和不足。 |
| Retrieval | BM25 / dense retriever top-k chunks | 证明不是普通 RAG 就能解决。 |
| Hybrid heuristic | random anchors、regex anchors、query anchors | 证明学习式 allocator 不是普通规则。 |
| Oracle | oracle anchors、oracle reread、oracle modality allocation | 估计问题上限。 |
| Ablated variants | no anchor、no verifier、no alignment、no trainable router | 证明每个模块贡献。 |


### 6.1.1 开源项目代码链接与使用说明

为了避免“idea 没有代码基线支撑”的问题，实验实现应明确以 **VIST 为主代码基线**，并把 Glyph、CEPE、Text-or-Pixels、DeepSeek-OCR、C3、LongCodeZip 等作为强对照或诊断工具。建议按下面优先级接入。

| 优先级 | 开源项目 | 代码链接 | 在本课题中的角色 | 具体使用说明 |
|---:|---|---|---|---|
| P0 | **VIST: Vision-centric Token Compression** | https://github.com/CSU-JPG/VIST | **主 baseline / 主改造对象** | 作为 ReVision-Context++ 的第一实现底座。直接复用其 long text rendering、vision encoder、Perceiver Resampler、cross-attention 接入 LLM、PVE 训练与下游评测框架；在其 pipeline 中加入 fidelity anchor extractor、budgeted allocator、anchor-aware alignment 和 verifier-triggered reread。论文叙事应写成“we build upon VIST and extend it with fidelity-aware budgeted allocation”。 |
| P0 | **Glyph: Scaling Context Windows via Visual-Text Compression** | https://github.com/thu-coai/Glyph | **强视觉压缩 baseline / 渲染搜索参考** | 作为 VIST 之外的 strongest visual-text compression baseline。重点复用或参考其 rendering configuration、LLM-driven rendering search、长上下文视觉压缩评测设置。若算力不足，不建议完整重训 Glyph，可优先跑其公开推理或复现其 rendering-style baseline。 |
| P0 | **CEPE: Context Expansion with Parallel Encoding** | https://github.com/princeton-nlp/CEPE | **纯文本 encoder 压缩 baseline** | 用于回答 reviewer 的核心问题：“为什么不用 text encoder compression？”将 CEPE 作为 text-only parallel encoder + cross-attention baseline，与 VIST/Glyph/Ours 在 same-budget 下比较 accuracy、exactness、latency、memory。 |
| P0 | **Text or Pixels? It Takes Half** | https://github.com/yanhong-lbh/text_or_pixels | **轻量 zero-shot text-as-image baseline** | 适合作为最小可复现视觉压缩 baseline。其代码包含 `text_to_image.py`、GPT/Qwen 推理脚本，可用于快速建立 render→VLM→answer 的 sanity check，并作为“不训练、不加 anchors”的对照。 |
| P1 | **DeepSeek-OCR** | https://github.com/deepseek-ai/DeepSeek-OCR | **OCR fidelity 诊断 / 高压缩风险估计器** | 不建议直接作为主下游 reasoning baseline，而应作为 OCR reconstruction 与 visual fidelity diagnostic。可用它评估不同字体、DPI、压缩比、表格/公式/代码渲染下的 OCR precision，并把 OCR confidence / edit distance 作为 allocator 的 risk feature。 |
| P1 | **C3: Context Cascade Compression** | https://github.com/liufanfanlff/C3-Context-Cascade-Compression | **纯文本 latent upper baseline / TEXT-LATENT 动作参考** | 用于正面回应“纯文本 latent compression 比 optical compression 更强”的质疑。实验中可将 C3 作为 text-latent upper baseline；方法上也可以把 C3 类 latent 表示纳入 action space，即 \(a_i=\text{TEXT-LATENT}\)。 |
| P1 | **LongCodeZip** | https://github.com/YerbaPage/LongCodeZip | **长代码文本压缩 baseline** | 在 RepoBench-P、LongCodeQA、Long Module Summarization 等代码任务中使用。它代表 selective filtering / textual code compression 路线，可用于对比 ReVision-Context++ 是否在保留全局依赖的同时修复视觉符号保真问题。 |
| P1 | **LLMLingua** | https://github.com/microsoft/LLMLingua | **通用 prompt compression baseline** | 用作通用纯文本压缩 baseline，特别适合文档 QA、摘要、RAG context 压缩场景。要注意它不是专门为视觉渲染或 exact symbol fidelity 设计，因此应重点比较 exactness failure rate。 |
| P1 | **Selective Context** | https://github.com/liyucheng09/Selective_Context | **轻量文本裁剪 baseline** | 用作简单信息量裁剪 baseline。它能帮助证明 ReVision-Context++ 的收益不是来自普通上下文删减，而是来自视觉 coverage + 文本 fidelity 的预算分配。 |
| P2 | **LLaVolta / Visual Context Compressor** | https://github.com/Beckschen/LLaVolta | **视觉 token 压缩模块参考** | 不是 text-rendered long-context 主线，但可借鉴其 average pooling visual compressor 和 staged compression training。适合在后续版本中作为 VIS-LOW / VIS-HIGH 的视觉 token budget 控制模块。 |
| P2 | **LongCodeOCR** | 暂未找到稳定官方代码仓库；论文页：https://arxiv.org/abs/2602.00746 | **代码视觉压缩动机 / 复现实验参考** | 当前先作为动机和实验设计参考，不作为必须跑通的代码依赖。若后续官方开源，应补充为代码视觉压缩 baseline；在此之前，可用 Glyph/VIST + code-specific rendering 自行复现其 global-preserving visual code compression 思路。 |

#### 推荐代码接入顺序

1. **先 fork VIST**：把 ReVision-Context++ 的核心模块直接接到 VIST 的 rendering、Resampler、cross-attention 和 eval pipeline 上。
2. **同时跑 Text-or-Pixels**：快速得到 zero-shot text-as-image baseline，用于早期 sanity check。
3. **接入 CEPE / LLMLingua / Selective Context**：建立纯文本压缩对照，确保 same-budget 实验公平。
4. **接入 Glyph**：作为强视觉压缩 baseline，优先复用其 rendering/search 配置，而不是一开始完整重训。
5. **接入 DeepSeek-OCR**：专门做 fidelity 诊断，输出 OCR risk / edit distance / confidence 给 allocator。
6. **接入 C3**：作为 TEXT-LATENT baseline 或 action，回应纯文本 latent compression 的强反驳。
7. **代码任务再接 LongCodeZip**：专门用于代码 exactness 与 dependency closure 对比。
8. **最后考虑 LLaVolta**：用于进一步压缩 visual tokens 或做 staged compression，不作为第一版必要依赖。

#### 建议仓库组织方式

```text
revision-context-plus/
  third_party/
    VIST/                  # 主 baseline，建议 fork 后深度修改
    Glyph/                 # 强视觉 baseline / rendering search
    CEPE/                  # 纯文本 encoder baseline
    text_or_pixels/        # zero-shot text-as-image baseline
    DeepSeek-OCR/          # OCR fidelity 诊断
    C3-Context-Cascade-Compression/
    LongCodeZip/
    LLMLingua/
    Selective_Context/
    LLaVolta/
  revision_context/
    anchor_extractor/
    allocator/
    renderer/
    verifier/
    reread/
    eval/
```

#### 最小可跑命令清单

```bash
git clone https://github.com/CSU-JPG/VIST.git third_party/VIST
git clone https://github.com/thu-coai/Glyph.git third_party/Glyph
git clone https://github.com/princeton-nlp/CEPE.git third_party/CEPE
git clone https://github.com/yanhong-lbh/text_or_pixels.git third_party/text_or_pixels
git clone https://github.com/deepseek-ai/DeepSeek-OCR.git third_party/DeepSeek-OCR
git clone https://github.com/liufanfanlff/C3-Context-Cascade-Compression.git third_party/C3-Context-Cascade-Compression
git clone https://github.com/YerbaPage/LongCodeZip.git third_party/LongCodeZip
git clone https://github.com/microsoft/LLMLingua.git third_party/LLMLingua
git clone https://github.com/liyucheng09/Selective_Context.git third_party/Selective_Context
git clone https://github.com/Beckschen/LLaVolta.git third_party/LLaVolta
```

#### 写进论文时的表述建议

论文中不要说“我们从零实现一个系统”，而应明确写：

> Our implementation is built on top of VIST, a vision-centric long-context compression framework. We extend its visual rendering and resampler pipeline with fidelity-sensitive span detection, budgeted modality allocation, anchor-aware visual alignment, and verification-triggered local rereading. We compare against strong open-source visual, textual, and hybrid baselines including Glyph, CEPE, Text-or-Pixels, DeepSeek-OCR, C3, LLMLingua, Selective Context, and LongCodeZip under the same token/latency/memory budget.

这样可以显著降低工程可行性风险，也能让 reviewer 清楚看到：本工作不是空想 idea，而是有明确可复现代码路径和强 baseline 对齐。


### 6.2 关键实验 1：Same Budget Pareto Frontier

对每个方法在相同总预算下比较：

- visual tokens + text anchor tokens + latent tokens + expected reread tokens；
- latency 包括 render 和二次读取；
- memory 包括 KV cache 和 vision encoder 激活。

必须画出：

- Accuracy vs Total Tokens；
- Exactness Score vs Total Tokens；
- Accuracy vs Latency；
- Fidelity Failure Rate vs Compression Ratio。

审稿人最想看的图：

> 在 4×、8×、16× 压缩下，ReVision-Context++ 是否始终位于 VIST/Glyph、text-only compression、RAG 的 Pareto frontier 外侧？

### 6.3 关键实验 2：Oracle Gap Analysis

做四条曲线：

1. Pure visual；
2. Heuristic anchors；
3. Trainable allocator；
4. Oracle allocation；
5. Full raw text upper bound。

解释方式：

- 如果 pure visual 与 oracle 差距大：说明 fidelity allocation 问题真实存在；
- 如果 trainable allocator 接近 oracle：说明方法有效；
- 如果 full text 比 oracle 只高一点：说明压缩几乎不损失下游性能；
- 如果 heuristic 与 trainable 差距大：说明 novelty 不只是 regex。

### 6.4 关键实验 3：Exactness Type Breakdown

按类型报告错误率：

| 类型 | Pure Visual | Regex Anchor | Trainable Allocator | +Verifier Reread | Full Text |
|---|---:|---:|---:|---:|---:|
| Number | 高 | 中 | 低 | 更低 | 最低 |
| Date | 高 | 中 | 低 | 更低 | 最低 |
| Code identifier | 很高 | 中 | 低 | 更低 | 最低 |
| Formula | 很高 | 高 | 中 | 低 | 最低 |
| Table cell | 高 | 中 | 低 | 更低 | 最低 |
| URL / Path | 很高 | 中 | 低 | 更低 | 最低 |

如果能展示“数字/代码/公式/表格 cell 的错误率显著下降”，论文说服力会比只报平均 accuracy 强很多。

### 6.5 关键实验 4：Stress Test

测试 reviewer 会关心的极端情况：

- 字体变小；
- 低分辨率；
- 多列排版；
- 表格 header 与 cell 分离；
- 相似变量名；
- 重复实体；
- 多语言；
- 长上下文中间位置 needle；
- 代码依赖跨文件；
- rerender style shift。

### 6.6 关键实验 5：Reread Budget Sensitivity

报告 trigger rate：

| Trigger Rate | Extra Tokens | Accuracy | Exactness | Latency |
|---:|---:|---:|---:|---:|
| 0% | 0 | baseline | baseline | lowest |
| 5% | low | + | + | slight |
| 10% | medium | ++ | ++ | medium |
| 25% | high | +++ | +++ | high |
| 100% | huge | near full text | best | too slow |

目标是证明：**很少的 reread 就能修复大量 high-risk exactness error**。

---

## 7. Ablation 设计

### 7.1 方法模块 ablation

| Variant | 目的 |
|---|---|
| Pure visual only | 证明视觉压缩 baseline。 |
| +Random anchors | 排除“多给文本 token 就好”的质疑。 |
| +Regex anchors | 检验简单规则上限。 |
| +Query-aware anchors | 检验 query relevance。 |
| +Trainable allocator | 证明学习式分配有效。 |
| +Anchor-aware alignment | 证明训练视觉 token 对 critical spans 更敏感。 |
| +Verifier reread | 证明二阶段可控修复。 |
| Full ReVision-Context++ | 完整方法。 |

### 7.2 预算 ablation

- anchor budget：0 / 64 / 128 / 256 / 512 tokens；
- visual budget：low / medium / high resolution；
- reread budget：0 / 5% / 10% / 25% trigger；
- total budget：2× / 4× / 8× / 16× compression。

### 7.3 allocator training ablation

- heuristic only；
- supervised by oracle；
- supervised + downstream fine-tuning；
- supervised + verifier-aware RL；
- no layout feature；
- no type feature；
- no query feature；
- no OCR risk feature。

### 7.4 visual alignment ablation

- original PVE；
- type-weighted PVE；
- page-to-anchor contrastive；
- hard negatives；
- OCR reconstruction auxiliary；
- all losses。

---

## 8. 建议的系统实现

### 8.1 第一版最小闭环

第一版不要一开始就做完整训练。先做 plug-in inference 框架：

1. long context 渲染为 image pages；
2. 同时保留 text-page-line mapping；
3. 用 regex + query overlap 提取 candidate anchors；
4. 用预算 packer 放入 prompt；
5. 模型输入：visual pages + anchor block + query；
6. answer 后 verifier 判断是否 reread；
7. 记录 token、latency、VRAM、accuracy、exactness。

### 8.2 Anchor block 格式

建议固定格式，便于模型使用：

```text
[Critical Text Anchors]
A1 | page=03 | line=12 | type=number | text="Revenue: 12.7M USD"
A2 | page=08 | line=04 | type=code | text="def parse_user_id(raw_id: str) -> int"
A3 | page=11 | table=2 | row=4 | col=EBITDA | text="18.3%"
[/Critical Text Anchors]
```

注意：anchor 必须有 page/line/table 坐标，方便 visual grounding 和 reread。

### 8.3 Reread prompt 格式

```text
The previous answer may depend on an exact symbol. Re-read only the following raw span:
[Re-read Span]
page=08, lines=02-09
...
[/Re-read Span]
Now answer again. Preserve exact strings, numbers, and symbols.
```

### 8.4 Render 策略

结合 Glyph 与 DeepSeek-OCR 经验，render 不应固定单一格式。建议：

- normal text：小字号多列，追求压缩；
- table：保留 header、网格线、行列编号；
- code：monospace、syntax highlight、行号；
- formula：较高 DPI、公式块单独渲染；
- high-risk page：VIS-HIGH；
- low-risk background：VIS-LOW。

---

## 9. 论文贡献写法

### 9.1 推荐贡献列表

论文贡献建议写成四点：

1. **Problem**：首次系统提出 long-context compression 中的 **Budgeted Fidelity Allocation** 问题，指出视觉压缩的 coverage 与 exactness fidelity 存在可量化冲突。
2. **Method**：提出 ReVision-Context++，一个可验证混合视觉-文本压缩框架，在固定预算下为 span 自适应选择 visual / text-anchor / text-latent / reread 表示。
3. **Benchmark**：构建 FidBench-Long，覆盖数字、日期、表格、公式、代码符号、URL/path、多跳实体绑定等 exactness-sensitive 长上下文任务。
4. **Findings**：在相同 token/latency/memory 预算下，ReVision-Context++ 在 coverage–fidelity Pareto frontier 上优于纯视觉压缩、纯文本压缩、RAG 和 heuristic hybrid，并通过 oracle gap、type-wise error breakdown、reread budget sensitivity 解释收益来源。

### 9.2 Abstract 草稿

> Visual long-context compression has recently emerged as a promising alternative to token-based context extension, converting long text into compact visual representations. However, our study shows that visual compression suffers from a systematic fidelity bottleneck on exactness-sensitive information such as numbers, dates, code identifiers, formulas, URLs, and table cells. We propose ReVision-Context++, a verifiable hybrid compression framework that formulates long-context compression as budgeted fidelity allocation. Given a fixed token/latency budget, our model learns to allocate each span to low-resolution visual compression, high-resolution visual compression, text anchors, text latents, or verification-triggered re-reading. We further introduce FidBench-Long, a benchmark targeting exactness-sensitive reasoning under compression. Experiments across document QA, table reasoning, scientific text, and long-context code show that ReVision-Context++ consistently improves the coverage–fidelity Pareto frontier over pure visual compression, text compression, and retrieval baselines, while reducing symbol-level errors with limited additional rereading cost.

### 9.3 Introduction 结构

建议 intro 采用如下逻辑：

1. Long context 成本高，压缩必要；
2. 视觉压缩是新趋势：把长文本渲染成图像，用 visual tokens 获得高信息密度；
3. 但是平均 accuracy 掩盖了 exactness failure；
4. 举例：`0.01` 变 `0.1`，`user_id` 变 `userid`，表格 header 错位，公式下标丢失；
5. 观察：视觉保 coverage，文本保 fidelity；二者不是替代关系，而是预算分配关系；
6. 提出 ReVision-Context++；
7. 贡献与结果。

### 9.4 论文图建议

至少需要 5 张关键图：

1. **Figure 1：Coverage–Fidelity Failure Example**  
   左：纯文本 selective filtering 删除依赖；中：纯视觉压缩看得到全局但变量/数字错；右：ReVision-Context++ 用视觉全局 + text anchors + reread 修复。

2. **Figure 2：Framework**  
   Context → span detector → modality allocator → visual rendering + anchors + latent + verifier reread → LLM。

3. **Figure 3：Pareto Frontier**  
   Accuracy / Exactness vs budget，展示 ReVision-Context++ 在 frontier 外侧。

4. **Figure 4：Oracle Gap**  
   pure visual、heuristic、trainable、oracle、full text 曲线。

5. **Figure 5：Type-wise Error Breakdown**  
   数字、日期、代码、公式、表格、URL 错误率柱状图。

---

## 10. 投稿 venue 策略

### 10.1 NeurIPS / ICLR

适合版本：

- 有清楚的问题定义；
- 有 learning allocator；
- 有 benchmark；
- 有 oracle / Pareto / verifier analysis；
- 不只是工程系统。

主打关键词：

- budgeted inference；
- adaptive computation；
- multimodal representation allocation；
- reliable compression；
- Pareto optimization。

### 10.2 ACL / EMNLP / NAACL

适合版本：

- FidBench-Long 很完整；
- 长文档 QA、表格 QA、代码 QA、公式问答做扎实；
- error analysis 丰富。

主打关键词：

- long-context NLP；
- context compression；
- document understanding；
- exactness-sensitive evaluation。

### 10.3 ICML

适合版本：

- allocator 建模足够数学化；
- budgeted optimization / bandit / RL 训练扎实；
- 有理论或 oracle regret 分析。

### 10.4 MLSys

适合版本：

- latency、throughput、VRAM、KV cache、render pipeline、serving system 做得很扎实；
- 1M token 级实验；
- 工程优化明显。

---

## 11. 预期审稿问题与防御

### Q1：这不就是 VIST/Glyph 加了一些文本 token？

**防御方式：**

- same total budget 对比 random anchors / regex anchors / query anchors；
- trainable allocator 显著优于 heuristic；
- oracle gap 证明 allocation 是核心；
- type-wise error 证明增益集中在 exactness-sensitive span。

### Q2：为什么不用 C3 这种纯文本 latent compression？

**防御方式：**

- C3 在重建任务上强，但 ReVision-Context++ 目标不是纯重建，而是结构化下游 reasoning；
- 视觉保留二维 layout、表格结构、代码全局形态、页面位置；
- hybrid 可以把 C3/text-latent 作为动作之一，而不是与其竞争；
- 对表格、文档布局、代码跨文件依赖展示 hybrid 优势。

### Q3：reread 是不是作弊？

**防御方式：**

- 把 reread 计入 expected budget；
- 报告 trigger rate 和额外 latency；
- 与 retrieval top-k / full reread / oracle reread 公平比较；
- 证明少量 reread 带来大幅 exactness 修复。

### Q4：benchmark 是否过于 synthetic？

**防御方式：**

- synthetic 只用于可控诊断；
- 主结果必须包含真实任务：table QA、doc QA、code QA、scientific formula、config/path；
- 所有生成数据公开脚本和 templates；
- 报告跨数据集泛化。

### Q5：allocator 训练是否成本太高？

**防御方式：**

- 第一版用 oracle 小样本蒸馏，不需要大规模端到端训练；
- LLM 和 vision encoder 可冻结，只训练小 router / LoRA / resampler；
- inference-time 也支持 heuristic fallback；
- 展示训练成本与收益。

---

## 12. 工程路线图

### Phase 0：1 周，复现与诊断

- 跑通 VIST / text-as-image / Glyph-style baseline 至少一个；
- 建立 render + page-line mapping；
- 构建 1K synthetic exactness samples；
- 得到纯视觉错误类型初步统计。

产出：第一张 failure taxonomy 图。

### Phase 1：1–2 周，Heuristic Hybrid

- regex + query overlap anchor extractor；
- budget packer；
- random / regex / query anchors 对比；
- 初版 verifier + reread；
- 记录 token、latency、accuracy。

产出：证明方向有增益的 Pareto 曲线。

### Phase 2：2–3 周，FidBench-Long

- synthetic 10K–100K；
- real tasks 接入；
- 统一 evaluator；
- type-wise metrics；
- stress tests。

产出：benchmark section 和诊断实验。

### Phase 3：2–4 周，Trainable Allocator

- oracle allocation 数据生成；
- router supervised training；
- Gumbel / knapsack constrained inference；
- ablation：no type / no query / no OCR risk / no layout。

产出：核心方法提升。

### Phase 4：2–3 周，Visual Alignment

- type-aware PVE；
- page-to-anchor contrastive；
- hard negatives；
- OCR / copy auxiliary loss。

产出：证明不是只靠 text anchors，视觉 token 本身也更 fidelity-aware。

### Phase 5：2 周，整理论文

- 主图；
- ablation；
- error cases；
- reviewer defense；
- 开源 benchmark 与代码。

---

## 13. 最小可投版本与强版本

### 13.1 最小可投版本

适合 ACL Findings / EMNLP Findings / workshop-to-main-track borderline：

- Heuristic anchors；
- FidBench synthetic + 2 个 real tasks；
- pure visual vs anchors vs reread；
- 详细 error analysis。

风险：novelty 不够，容易被认为 engineering。

### 13.2 主会强版本

适合 ACL/EMNLP main、ICLR/NeurIPS borderline-to-accept：

- FidBench-Long 完整；
- trainable allocator；
- oracle gap；
- verifier-triggered reread；
- anchor-aware visual alignment；
- 真实任务覆盖文档、表格、代码、公式；
- 与 VIST/Glyph/CEPE/C3/LongCodeZip 等强 baseline 对齐预算比较。

### 13.3 最高竞争力版本

适合 NeurIPS/ICLR/ICML 更强提交：

- allocator 有清晰优化框架；
- 有理论分析，例如 budgeted allocation 的 oracle regret / Pareto optimality；
- verifier 有 calibration；
- benchmark 被包装成长期可用评测；
- 1M token 级系统实验；
- 支持 text latent as action，将 C3 类方法纳入统一框架。

---

## 14. 具体改进建议清单

### 必做

1. 把标题和叙事从 “Hybrid Visual-Text Compression” 改成 **Budgeted Fidelity Allocation**。
2. 引入 **FidBench-Long**，不要只靠现有 benchmark。
3. 做 **same total budget** 实验，严格计入 anchors 和 reread。
4. 做 **oracle allocation**，否则无法证明问题上限和方法有效性。
5. 做 **type-wise exactness error breakdown**，这是最能打动审稿人的证据。
6. 至少实现一个 **trainable allocator**，否则 novelty 偏弱。
7. 把 reread 设计成 **verifier-triggered expected budget**，避免“作弊”质疑。
8. 把 C3 放进讨论或 baseline，正面回应纯文本 latent compression。

### 强烈建议

1. 加入 **hard negatives**，让模型对相似符号敏感。
2. 加入 **page-to-anchor alignment**，让视觉 token 可定位 critical anchors。
3. 对表格和代码做专用 rendering。
4. 做 render robustness：字体、DPI、列数变化。
5. 报告 latency breakdown：render、vision encoder、LLM prefill、decode、reread。

### 可以后续做

1. 多语言 exactness；
2. 低质量扫描文档；
3. handwritten notes；
4. agent memory / conversation history；
5. 与 KV cache compression 联合。

---

## 15. 最终推荐版本摘要

**ReVision-Context++** 应该被包装为一个 **reliable long-context compression** 论文，而不是单纯的视觉压缩论文。

推荐最终贡献闭环：

1. 发现并系统量化视觉上下文压缩的 fidelity failure；
2. 将 hybrid compression 形式化为 budgeted fidelity allocation；
3. 提出可学习 modality allocator；
4. 提出 anchor-aware visual alignment 与 verifier-triggered reread；
5. 发布 FidBench-Long；
6. 在强 baseline 和严格预算下证明 Pareto frontier 改善。

最关键的实验结论应该是：

> 在相同总预算下，ReVision-Context++ 保留了纯视觉压缩的全局覆盖优势，同时显著降低数字、表格、公式、代码符号、URL/path 等 exactness-sensitive 错误；少量 verifier-triggered reread 即可进一步逼近 full-text upper bound。

如果能够做到上述版本，主会概率可以从当前约 **35–45%** 提升到 **60–72%**。若 benchmark、oracle analysis 和 trainable allocator 都做得非常干净，并且覆盖 1M token 级系统实验，则有机会冲击更高档次的 NeurIPS / ICLR / ACL / EMNLP 主会。

---

## 16. 参考依据

本方案基于以下已上传材料综合评估：

- `ReVision_Context_TopConf_Evaluation.md`
- `vist_vision_centric_token_compression_in_llm.pdf`
- `cepe_parallel_context_encoding.pdf`
- `efficient_large_multimodal_models_via_visual_context_compression.pdf`
- `deepseek_ocr_contexts_optical_compression.pdf`
- `text_or_pixels_it_takes_half.pdf`
- `glyph_scaling_context_windows_via_visual_text_compression.pdf`
- `longcodeocr_visual_compression_for_long_context_code.pdf`
- `context_cascade_compression_upper_limits_of_text_compression.pdf`
- `视觉上下文压缩_挑战与方向.md`
