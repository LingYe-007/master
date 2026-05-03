import type { Paper, TrainingState } from '@/types'

/** 演示用论文列表：中英标题、常见刊会与作者格式，贴近 CNKI / DBLP 展示习惯 */
export const mockPapers: Paper[] = [
  {
    id: '10.3778/j.issn.1000-9825.2024.0012',
    title: '面向论文推荐的异质图联邦表示学习与隐私保护机制',
    authors: ['刘志远', 'Chen Yifan', '王磊', 'Zhou Lin'],
    venue: '软件学报',
    year: 2024,
    abstract:
      '针对科研合作网络中用户—论文二部图在联邦场景下的异构性与数据孤岛问题，提出分层聚合与原型对齐策略，在保护本地梯度隐私的前提下提升冷启动推荐效果。',
    keywords: ['联邦学习', '异质图神经网络', '论文推荐'],
    recommendationReason:
      '与当前画像「联邦学习 / 图神经网络」及 FedASCL 双视图设定一致性高；推荐理由含结构视图协同信号与全局语义原型。',
    metaPaths: ['U—P—A—P', 'U—P—K—P'],
    metaPathExplanation:
      '结构视图：您历史交互过的论文与本文通过「共同作者」形成二跳路径（U—P—A—P）；同时两篇论文在「关键词」节点上共现，经由 U—P—K—P 强化语义一致性，故排序靠前。',
    strategy: 'structure',
  },
  {
    id: 'arXiv:2311.08452',
    title: 'FedProtoAlign: Prototype-Guided Contrastive Learning for Non-IID Federated Recommendation',
    authors: ['Ming Zhang', 'S. Kumar', '刘洋'],
    venue: 'AAAI',
    year: 2025,
    abstract:
      'We align client-level user/item prototypes in a contrastive objective to mitigate semantic drift under heterogeneous partitions, with applications to academic recommender systems.',
    keywords: ['federated learning', 'contrastive learning', 'prototype'],
    recommendationReason:
      '方法路径与您论文第三章「全局语义原型 + 对比对齐」可直接对照；适合作为 Related Work 中近邻工作。',
    metaPaths: ['U—P—P—P', 'U—P—V—P'],
    metaPathExplanation:
      '依据引用/阅读行为扩展：您曾交互的论文与被引工作构成 U—P—P—P（引用链）关联；另通过同一顶级会议/期刊廊道 U—P—V—P 将本文与您的阅读历史对齐。',
    strategy: 'structure',
  },
  {
    id: '10.1109/ICDE56745.2023.00189',
    title: 'Semantic-Aware Gradient Compression for Cross-Silo Federated Graph Training',
    authors: ['Aria Patel', '吴晓东', 'James Cook'],
    venue: 'ICDE',
    year: 2023,
    abstract:
      'Residual quantization of structure-view gradients with error feedback; reports wall-clock and uplink reduction on hierarchical federated setups.',
    keywords: ['gradient compression', 'federated GNN'],
    recommendationReason: '与第四章语义感知压缩、残差量化与通信开销评估叙事高度契合。',
    metaPaths: ['U—P—K—P', 'U—P—A—P'],
    metaPathExplanation:
      '以关键词「梯度压缩 / 联邦图」为桥：U—P—K—P 连接您关切的主题与本文；辅路径 U—P—A—P 捕获与合作者网络重叠的高置信关联。',
    strategy: 'structure',
  },
  {
    id: '10.1360/SSI-2024-0156',
    title: '非独立同分布条件下联邦对比学习的表示漂移与对齐方法',
    authors: ['赵敏', 'Sun Hao', '李伟'],
    venue: '中国科学: 信息科学',
    year: 2024,
    abstract:
      '从优化视角分析 Non-IID 下对比学习目标中的客户端漂移，并提出跨客户端语义锚定机制，在公开引用与推荐数据集上验证稳定性。',
    keywords: ['Non-IID', '对比学习', '联邦优化'],
    recommendationReason: '第五章 Non-IID 鲁棒性实验的同类中文工作，可支撑讨论与 baseline 说明。',
    metaPaths: ['U—P—U—P', 'U—P—K—P'],
    metaPathExplanation:
      '协同信号路径 U—P—U—P：与您行为相似的用户群体共同感兴趣的论文廊道指向本文；并叠加主题关键词路径 U—P—K—P 作为语义锚定。',
    strategy: 'structure',
  },
  {
    id: '10.1145/3580305.3599856',
    title: 'Cold-Start Paper Recommendation with Attribute-Conditioned Hypergraph Encoders',
    authors: ['Elena Rossi', '林志', 'Noah Berger'],
    venue: 'SIGIR',
    year: 2024,
    abstract:
      'Hypergraph message passing over author–venue–keyword tuples when interaction counts are sparse; evaluated on AMiner-style corpora.',
    keywords: ['cold start', 'hypergraph', 'scholarly'],
    recommendationReason: '冷启动场景与属性视图路由说明一致，可作属性侧对照实验引用。',
    metaPaths: ['研究方向—K—P', 'I—A—P'],
    metaPathExplanation:
      '属性视图：您在个人设置中的「研究方向 / 兴趣词」与论文关键词在 K 类节点上对齐（研究方向—K—P）；机构画像经 I—A—P 与作者署名弱关联至本文。',
    strategy: 'attribute',
  },
  {
    id: '10.1109/TKDE.2023.3269120',
    title: 'Heterogeneous Information Network Embedding for Explainable Citation Recommendation',
    authors: ['Yang Liu', '陈晨', 'Daniel Frost'],
    venue: 'IEEE TKDE',
    year: 2024,
    abstract:
      'Meta-path-aware attention with explainable path weights for citation link prediction in large-scale digital libraries.',
    keywords: ['HIN', 'explainability', 'citation'],
    recommendationReason: '异质网络元路径与可解释引用推荐，便于与「结构—属性」双视图解释材料衔接。',
    metaPaths: ['U—P—A—P', 'P—V—P', 'P—K—P'],
    metaPathExplanation:
      '可解释引用场景：U—P—A—P 共享权威作者；P—V—P 同 venue/Corpus 廊道；P—K—P 在引用预测任务中与您的主题偏好一致，多条元路径融合打分。',
    strategy: 'structure',
  },
  {
    id: 'arXiv:2402.11809',
    title: 'Vertical vs. Horizontal Partitioning in Federated Academic Recommenders: A System Study',
    authors: ['Karim Ali', '周宁'],
    venue: 'WWW Companion',
    year: 2024,
    abstract:
      'Benchmarks client-side feature heterogeneity versus sample heterogeneity in federated paper recommendation pipelines.',
    keywords: ['vertical FL', 'horizontal FL', 'benchmark'],
    recommendationReason: '与论文中「横向 / 纵向联邦」示意图及系统章节叙述可并列引用。',
    metaPaths: ['U—P—K—P', 'U—P—V—P'],
    metaPathExplanation:
      '系统类论文以主题与出版语境为主：U—P—K—P 对齐「联邦 / 划分」等关键词；U—P—V—P 与您常读的 Workshop/会议类型一致。',
    strategy: 'structure',
  },
  {
    id: '10.1613/jair.1.14322',
    title: 'Federated Matrix Factorization with Differential Privacy for Digital Libraries',
    authors: ['Thomas Weber', '韩梅'],
    venue: 'JAIR',
    year: 2023,
    abstract:
      'Combines DP noise calibration with secure aggregation for matrix factorization in distributed library deployments.',
    keywords: ['differential privacy', 'matrix factorization'],
    recommendationReason: '隐私与聚合机制经典线路，可用于与语义原型方案的对比讨论。',
    metaPaths: ['兴趣—K—P', 'U—P—K—P'],
    metaPathExplanation:
      '弱交互时启用属性路径：画像兴趣词与 MF/DP 相关关键词经 K 节点连到本文；若有少量历史则并入 U—P—K—P 提升置信度。',
    strategy: 'attribute',
  },
  {
    id: '10.1145/3690624.3709250',
    title: 'Layer-wise Sparsification and Error Compensation in Federated GNN Backpropagation',
    authors: ['Lucia Marin', '王强', 'P. Zhou'],
    venue: 'The Web Conference (WWW)',
    year: 2025,
    abstract:
      'Layer-adaptive sparsity schedules for GNN backpropagation under constrained bandwidth in cross-device FL.',
    keywords: ['sparsification', 'GNN', 'bandwidth'],
    recommendationReason: '与压缩章节中按层/按视图的比特分配思路形成技术对照。',
    metaPaths: ['U—P—A—P', 'U—P—P—P'],
    metaPathExplanation:
      'GNN 梯度主题通过 U—P—A—P 与您的合作者/关注作者重叠；引用层面 U—P—P—P 将近期您阅读的稀疏化工作与本文衔接。',
    strategy: 'structure',
  },
  {
    id: '10.13328/j.cnki.jos.006789',
    title: '基于对比学习与图注意力网络的学术文献多视角推荐',
    authors: ['孙洁', 'Ma Jun', '高鹏'],
    venue: '计算机学报',
    year: 2023,
    abstract:
      '在论文—作者—机构图上构建多视角对比目标，缓解长尾与噪声标签对推荐排序的影响。',
    keywords: ['对比学习', '图注意力', '多视角'],
    recommendationReason: '国内主流刊会表述与术语习惯与本系统中文界面一致，适合答辩演示。',
    metaPaths: ['U—P—K—P', 'U—P—V—P'],
    metaPathExplanation:
      '中文计算机类刊会语境：U—P—V—P（《计算机学报》等）匹配您的阅读习惯；对比学习与 GAT 相关 K 节点经 U—P—K—P 连至本文。',
    strategy: 'structure',
  },
  {
    id: '10.24963/ijcai.2024/472',
    title: 'Cross-View Regularization for Federated Hypergraph Recommenders',
    authors: ['Olivia Chen', '张涛'],
    venue: 'IJCAI',
    year: 2024,
    abstract:
      'Dual-view regularization losses shared via auxiliary servers in a hierarchical federation topology.',
    keywords: ['hypergraph', 'cross-view', 'hierarchical FL'],
    recommendationReason: '分层联邦 + 跨视图正则，与仿真引擎「副服务器」配置面板叙事一致。',
    metaPaths: ['U—P—U—P', 'U—P—K—P'],
    metaPathExplanation:
      '跨客户端语义：相似用户子图上的 U—P—U—P 将本文推至与您同频的科研社群；超图/跨视图关键词经 U—P—K—P 汇合。',
    strategy: 'structure',
  },
  {
    id: 'arXiv:2305.04014',
    title: 'Benchmarking Recommendation under Non-IID Shards: Datasets, Protocols, and Pitfalls',
    authors: ['Alex Boone', '李娜', 'Kim S.-H.'],
    venue: 'RecSys Workshop',
    year: 2023,
    abstract:
      'Proposes evaluation protocols for shard-level Non-IID in federated recommendation, including citation and co-author induced skew.',
    keywords: ['benchmark', 'Non-IID', 'evaluation'],
    recommendationReason: '实验设置与指标话术可套用到第五章消融与鲁棒性小节。',
    metaPaths: ['研究方向—K—P', 'U—P—K—P'],
    metaPathExplanation:
      '评测协议类文献：以「Non-IID / benchmark」关键词经研究方向—K—P 对接；若有交互历史则 U—P—K—P 进一步确认主题 shard 一致性。',
    strategy: 'attribute',
  },
  {
    id: '10.1145/3637528.3671456',
    title: 'Efficient Broadcast of Model Updates in Tree-Structured Federated Aggregation',
    authors: ['R. Singh', '陈曦'],
    venue: 'KDD',
    year: 2024,
    abstract:
      'Tree-structured parameter broadcast reducing straggler impact in hierarchical aggregation trees.',
    keywords: ['aggregation tree', 'straggler'],
    recommendationReason: '与监控页「Broadcast / FedAvg 聚合」日志风格一致，可作系统实现参考。',
    metaPaths: ['U—P—V—P', 'U—P—A—P'],
    metaPathExplanation:
      '系统路线：KDD 等数据挖掘顶会廊道 U—P—V—P；树形聚合与联邦训练作者圈通过 U—P—A—P 与您的近期阅读产生关联。',
    strategy: 'structure',
  },
  {
    id: '10.1016/j.inffus.2024.102567',
    title: 'Information Fusion for Multi-Modal Scholar Profiles in Privacy-Preserving Recommender Services',
    authors: ['Marc Dubois', '黄伟'],
    venue: 'Information Fusion',
    year: 2024,
    abstract:
      'Fuses textual abstracts, co-authorship, and venue embeddings under homomorphic encryption constraints at inference.',
    keywords: ['multi-modal', 'privacy'],
    recommendationReason: '属性模态融合与「个人信息/研究方向」表单在业务语义上呼应。',
    metaPaths: ['研究方向—K—P', 'I—A—P'],
    metaPathExplanation:
      '多模态学者画像：表单中的研究方向与摘要主题词在 K 上对齐；机构字段经 I—A—P 连接到本文署名作者，用于冷启动补全。',
    strategy: 'attribute',
  },
]

function makeLossHistory(rounds: number): { round: number; value: number }[] {
  return Array.from({ length: rounds }, (_, i) => {
    const r = i + 1
    const decay = 1 - 0.62 * (1 - Math.exp(-r / 28))
    const noise = 0.018 * Math.sin(r * 0.47) + 0.008 * ((r * 7) % 3)
    const value = Math.max(0.32, 1.18 * decay + noise)
    return { round: r, value: Math.round(value * 10000) / 10000 }
  })
}

function makeMetricHistory(rounds: number, start: number, end: number): { round: number; value: number }[] {
  return Array.from({ length: rounds }, (_, i) => {
    const r = i + 1
    const t = r / rounds
    const smooth = start + (end - start) * (1 - Math.exp(-t * 3.2))
    const noise = 0.004 * Math.sin(r * 0.35)
    const value = Math.min(1, Math.max(0, smooth + noise))
    return { round: r, value: Math.round(value * 10000) / 10000 }
  })
}

/** 当前演示轮次：未跑满，便于进度条与「运行中」状态同时成立 */
const ROUNDS = 73
const LOSS = makeLossHistory(ROUNDS)
const HIT5 = makeMetricHistory(ROUNDS, 0.052, 0.124)
const NDCG5 = makeMetricHistory(ROUNDS, 0.031, 0.079)

const LOG_TEMPLATES: readonly string[] = [
  '127.0.0.1:8000 - "GET /api/admin/training/status HTTP/1.1" 200 482',
  'Worker-3 | round=73 | local_epoch=1/1 | train_loss=0.4012 | bs=32 | lr=1.00e-2',
  'Aggregator | FedAvg | merged 10/10 clients | aux_servers=5 | wall_ms=1847',
  'FedASCL | prototype_bank sync | dim=256 | L2 clip=1.0 | NaN check OK',
  'Compression | structure_grad | ratio=8.2:1 | residual_norm=0.014 | bpp_est=2.31',
  'Scheduler | job_id=fedascl-prod-v2 | queue=gpu-a100-01 | cuda_driver=12.2',
  'Client region-cn-north-004 | uploaded encrypted delta | bytes=1.28MB | sig verified',
  'Client region-cn-west-002 | status=training | epoch progress 72%',
  'Broadcast | global_state v=73 | targets=10 | multicast tree depth=3',
  'SecureAgg | round_secret refreshed | participants=10 | dropout tolerated=1',
  'Monitor | Hit@5=0.1184 NDCG@5=0.0749 eval_holdout=val_core_v3',
  'Warning | client region-cn-south-008 straggler | slack_wait_ms=3200',
  'NVML | GPU0 util=68%/mem=41.2GiB temp=61C | batch latency p50=112ms',
  'checkpoint | saved ./runs/fedascl_ckpt_r073.pt | sha256=9f3a…c21e',
  'uvicorn | INFO | Waiting for next client uploads (hierarchical round 73/100)',
]

function formatLogTime(baseHour: number, index: number): string {
  const totalSec = index * 23 + (index % 5) * 7
  const h = baseHour + Math.floor(totalSec / 3600)
  const m = Math.floor((totalSec % 3600) / 60)
  const s = totalSec % 60
  const ms = (index * 37) % 1000
  return `2026-03-28 ${String(h % 24).padStart(2, '0')}:${String(m).padStart(2, '0')}:${String(s).padStart(2, '0')}.${String(ms).padStart(3, '0')}`
}

export const mockTrainingState: TrainingState = {
  currentRound: ROUNDS,
  totalRounds: 100,
  clientCount: 10,
  trainingStatus: 'running',
  trainingType: 'FedASCL · 语义原型对齐 · 分层 FedAvg',
  auxServerCount: 5,
  clients: [
    { id: 'region-cn-north-001', status: 'online' },
    { id: 'region-cn-north-002', status: 'training' },
    { id: 'region-cn-east-001', status: 'online' },
    { id: 'region-cn-east-002', status: 'online' },
    { id: 'region-cn-south-001', status: 'offline' },
    { id: 'region-cn-south-002', status: 'training' },
    { id: 'region-cn-west-001', status: 'online' },
    { id: 'region-cn-west-002', status: 'online' },
    { id: 'region-lab-gpu-619', status: 'online' },
    { id: 'region-backup-cpu-01', status: 'offline' },
  ],
  lossHistory: LOSS,
  aucHistory: HIT5,
  hitHistory: HIT5,
  ndcgHistory: NDCG5,
  logEntries: Array.from({ length: 56 }, (_, i) => ({
    time: formatLogTime(9, i),
    level: i === 11 || i === 34 ? 'WARN' : 'INFO',
    message: LOG_TEMPLATES[i % LOG_TEMPLATES.length],
  })),
}
