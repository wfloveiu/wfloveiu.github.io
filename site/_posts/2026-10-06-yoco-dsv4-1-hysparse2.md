---
layout: post
title: "YOCO、DSV4.1、HySparse2"
date: 2026-10-06 00:00:00 +0800
permalink: /2026/10/06/yoco-dsv4-1-hysparse2/
description: "整理 YOCO、DeepSeek-V4.1 与 HySparse2 的架构，关注跨层 KV 共享、SWA 重放与 prefill 计算优化。"
published: true
math: true
categories: [模型架构]
tags: [Attention, KV Cache, YOCO, DeepSeek, HySparse2]
---

## 一、YOCO

1.  KV Cache 随序列长度和层数增长。普通 Transformer 每层都要保存一套 KV Cache，显存开销约为 $O(LND)$ 
2. 降低长输入的 prefill 延迟。普通 Transformer 需要让整个 prompt 经过所有层的注意力计算，长输入会导致首个 token 的等待时间很长。

![image-20261006003257743](/assets/images/posts/yoco-dsv4-1-hysparse2/yoco-architecture.png)

YOCO 的架构非常简单易懂：把多层 decoder-only Transformer 分成两部分。
**前半部分是 Self-Decoder。** 正常计算，生成各个token的K/V。
**后半部分是 Cross-Decoder。** 每一层不再各自保存历史 K/V，而是用自己的 Query 去 cross-attend 前半部分对应layer KV。

这样做的好处是：**从存储角度考虑，KV节省一半**；从prefill计算角度考虑，经过Self- Decoder后，已经拿到了所有token的KV Cache，除了最后一个token外，其余token 不需要做后面的Cross-Decoder，而最后一个token继续走Cross-Decoder，generate第一个token，**近似于prefill计算减半**



## 二、DeepSeek-V4.1

V4 的全局注意力采用 CSA 与 HCA 混合结构，V4.1 统一为 CSA2，再按层分配不同的计算与复用职责。语言主干共 40 层，前 20 层组成 causal encoder，后 20 层组成 decoder。

![image-20261005105624567](/assets/images/posts/yoco-dsv4-1-hysparse2/deepseek-v4-1-architecture.png)

| 层范围                 | 全局注意力配置 | 分组方式                              |
| ---------------------- | -------------- | ------------------------------------- |
| Encoder 第 1 至 2 层   | 纯 SWA         | 只处理局部窗口                        |
| Encoder 第 3 至 20 层  | CSA2，压缩率 2 | 3 组，每组 1 个 Full 加 5 个 Reuse    |
| Decoder 第 21 至 24 层 | CSA2，压缩率 1 | 1 个 Full 加 3 个 Reuse               |
| Decoder 第 25 至 40 层 | CSA2，压缩率 1 | 4 组，每组 1 个 Reindex 加 3 个 Reuse |

全模型只有 4 层生成独立的全局 KV，另外 4 层重新做索引，30 层直接复用 KV 和索引。所有层仍有自己的局部 SWA，窗口为 128 tokens。

### CED

Causal Encoder-Decoder（CED）基于YOCO发展来：YOCO前半部分构建共享 KV，后半部分通过 cross-attention复用它，允许 prefill 提前结束。CED 改变了 decoder 全局 KV 的来源。它先让输入经过 20 层 causal encoder，得到第20层的隐藏状态 ，再通过投影生成 decoder 需要的全局 KV。

$$
C_l = H_{20}W_l^{KV}, \qquad Z_l = H_{20}W_l^{Z}, \qquad l > 20
$$

$C_l$ 表示 KV 条目，$Z_l$ 表示压缩权重。结合实际 CSA2 配置，**decoder 的第一个 Full 层负责生成全局 KV，后面的层共享这份KV**。

生成新 token 时，模型仍然执行完整的 40 层。CED 的收益集中在读取输入这一阶段，尤其适合工具结果很长、输入量显著高于输出量的 Agent 工作负载。

### SWA重放

Decoder 还保留每层独立的 SWA KV。它们依赖各层自己的隐藏状态，需要额外计算。前面提到，CED使用第20层的隐藏状态计算decoder的full KV（即第21层的KV），这里SWA KV是decoder的其它层，用它自己的隐藏状态计算得到的。

设输入长度为 $N$、总层数为 $L$、窗口长度为 $W$，报告给出的层计算量近似为：


$$
O(NL) \;\longrightarrow\; O\left(\frac{NL}{2}+\frac{WL}{2}\right)
$$


当 $N \gg W$ 时，后面的回放开销相对很小，总体 prefill 计算接近减半。这里描述的是层计算量的变化；实际延迟还取决于输入长度、缓存命中、并行策略和硬件利用率。

### CSA2 与跨层复用

CSA2 由CSA（Compress Sparse Attention）发展来，个人理解，**CSA为了解决Sparse Attention的Indexer在超长上下文下成为瓶颈的问题**。

![image-20261005112955662](/assets/images/posts/yoco-dsv4-1-hysparse2/csa-attention.png)

CSA2是对CSA的进一步优化，**引入了跨层的KV 复用/Index Key复用/Topk Index复用**。有 Full、Reindex、Reuse 三种模式。

![image-20261005113448430](/assets/images/posts/yoco-dsv4-1-hysparse2/csa2-reuse-modes.png)

- Full Mode：该层会自行计算其Main KV和Indexer Q，从Main KV投影出Indexer K，并生成新的 Top-K 索引。它执行了完整的 CSA2 计算路径，与 DeepSeek-V4 中完整 CSA 层一样。
- Reindex Mode：该层**复用最近的某一完整层的Main KV和Index K**，省了Indexer projection的计算，但计算新的Topk Indices。（即**KV复用，但topk不复用，可以减少缓存存储**）
- Reuse Mode：该层复用前一层在Full Mode或Reindex Mode下计算出的最新可用的 Main KV 及对应的最新 Top-K 索引，直接做Sparse Attention（**减少Indexer相关的计算**）



## 三、HySparse2

Agentic 工作负载需要更紧凑的 KV 缓存。KV 缓存压缩涵盖四个维度：头、序列、层和精度。头级别方法通过 GQA/MQA共享 KV 头，或如 MLA将 KV 表示压缩为潜在状态。序列级别方法将多个 token 压缩为更少的缓存条目。层级别方法如YOCO在层间共享 KV 缓存。精度级别方法降低缓存中键和值的数值精度。先前工作聚焦于沿头、序列和精度轴的层内压缩。HySparse2 则通过 KV 桥接和 KV 重用推动跨层共享。

HySparse2是两级KV共享

第一级是cross-decoder和self-decoder 中，Full Attention层间的KV bridge（这里不是KV reuse，而是hidden state的复用，目的不是减少layer的KV Cache，而是让prefill除尾token，在self-decoder后exit，尾token继续cross-decoder）。cross-decoder复用self-decoder对应FA layer的input hidden。

第二级是cross-decoder内，一个块（1FA+5SA）内，SA复用FA的KV Cache和Topk KV indices（减少了KV Cache存储和Topk Indixer计算）

![image-20261005133635758](/assets/images/posts/yoco-dsv4-1-hysparse2/hysparse2-architecture.png)

self-decoder是SWA+FA的混合（self-decoder本身是有KV Cache的）

cross-decoder 分成4个块，每个块包含1个FA 层和5个Sparse FA层，如上右图。对于FA，它的KV从self-decoder的hidden state，重新做KV proj得到，而不是像YOCO直接复用self-decoder的KV，在FA layer，还要额外做Tok-K token的selection，**并保存Topk Indices和KV。块内的5个SFA，用FA layer的Topk KV做稀疏attention。**
