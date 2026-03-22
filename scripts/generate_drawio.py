#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
生成论文图片对应的 Draw.io XML 文件，尽量还原原图样式。
输出到 images/drawio/ 目录。
"""
import os

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(SCRIPT_DIR)
OUT_DIR = os.path.join(PROJECT_ROOT, 'images', 'drawio')
os.makedirs(OUT_DIR, exist_ok=True)

# 统一配色（与原图一致）
BLUE_FILL = '#e3f2fd'
BLUE_EDGE = '#1565c0'
ORANGE_FILL = '#fff3e0'
ORANGE_EDGE = '#e65100'
GRAY = '#e8e8e8'
TEXT = '#333333'

# 中文学术期刊配图规范：宋体（中文）/ Arial（英文图表）
FONT = "Arial"
FONT_CN = "SimSun"   # 宋体，用于中文标题与图注
FONT_TITLE = 12      # 主标题 12–14pt
FONT_LARGE = 14      # 大图主标题（如框架图）
FONT_SUBTITLE = 11   # 副标题/图注 9–11pt
FONT_BODY = 10       # 正文/标签 8–10pt
FONT_SMALL = 9       # 小标注 ≥8pt
FONT_COLOR = '#333333'

# GNN 图专用配色（User: 103,146,199 / Item: 236,131,57）
GNN_USER_FILL = '#6792c7'
GNN_USER_EDGE = '#4a6fa5'
GNN_ITEM_FILL = '#ec8339'
GNN_ITEM_EDGE = '#c96b24'
GNN_PROCESS_FILL = '#f5f5f5'
GNN_PROCESS_EDGE = '#666666'


def mxfile_header(page_w=1100, page_h=850):
    return f'''<?xml version="1.0" encoding="UTF-8"?>
<mxfile host="app.diagrams.net" modified="2025-01-01" agent="5.0" version="22.1.0" etag="x" type="device">
  <diagram name="Page-1" id="page1">
    <mxGraphModel dx="1422" dy="794" grid="1" gridSize="10" guides="1" tooltips="1" connect="1" arrows="1" fold="1" page="1" pageScale="1" pageWidth="{page_w}" pageHeight="{page_h}" background="#ffffff" math="0" shadow="0">
      <root>
        <mxCell id="0"/>
        <mxCell id="1" parent="0"/>'''


def mxfile_footer():
    return '''
      </root>
    </mxGraphModel>
  </diagram>
</mxfile>'''


def rect(id_, x, y, w, h, text, fill=BLUE_FILL, stroke=BLUE_EDGE, rounded=1, font_size=None, dashed=0):
    fs = font_size if font_size is not None else FONT_BODY
    dash = "dashed=1;" if dashed else ""
    style = f"rounded={rounded};whiteSpace=wrap;html=1;fillColor={fill};strokeColor={stroke};strokeWidth=1;fontFamily={FONT};fontColor={FONT_COLOR};fontSize={fs};align=center;verticalAlign=middle;{dash}"
    return f'''        <mxCell id="{id_}" value="{_xml_escape(text)}" style="{style}" parent="1" vertex="1">
          <mxGeometry x="{x}" y="{y}" width="{w}" height="{h}" as="geometry"/>
        </mxCell>'''


def ellipse(id_, x, y, w, h, text, fill=BLUE_FILL, stroke=BLUE_EDGE):
    style = f"ellipse;whiteSpace=wrap;html=1;fillColor={fill};strokeColor={stroke};strokeWidth=1;fontFamily={FONT};fontColor={FONT_COLOR};fontSize={FONT_BODY};align=center;verticalAlign=middle;"
    return f'''        <mxCell id="{id_}" value="{_xml_escape(text)}" style="{style}" parent="1" vertex="1">
          <mxGeometry x="{x}" y="{y}" width="{w}" height="{h}" as="geometry"/>
        </mxCell>'''


def square(id_, x, y, s, text, fill=ORANGE_FILL, stroke=ORANGE_EDGE):
    """正方形（Item 节点用）"""
    style = f"shape=rectangle;perimeter=rectanglePerimeter;whiteSpace=wrap;html=1;fillColor={fill};strokeColor={stroke};strokeWidth=1;fontFamily={FONT};fontColor={FONT_COLOR};fontSize={FONT_BODY};align=center;verticalAlign=middle;"
    return f'''        <mxCell id="{id_}" value="{_xml_escape(text)}" style="{style}" parent="1" vertex="1">
          <mxGeometry x="{x}" y="{y}" width="{s}" height="{s}" as="geometry"/>
        </mxCell>'''


def block_arrow(id_, x, y, w, h):
    """空心块箭头（section 间过渡）"""
    style = "shape=flexArrow;endArrow=block;html=1;fillColor=#ffffff;strokeColor=#333333;strokeWidth=1;endSize=8;"
    return f'''        <mxCell id="{id_}" value="" style="{style}" parent="1" vertex="1">
          <mxGeometry x="{x}" y="{y}" width="{w}" height="{h}" as="geometry"/>
        </mxCell>'''


def edge(id_, source, target, dashed=0):
    ds = ";dashed=1" if dashed else ""
    style = f"endArrow=classic;html=1;rounded=0;strokeWidth=1;strokeColor=#333333{ds};exitX=1;exitY=0.5;exitDx=0;exitDy=0;entryX=0;entryY=0.5;entryDx=0;entryDy=0;"
    return f'''        <mxCell id="{id_}" style="{style}" parent="1" source="{source}" target="{target}" edge="1">
          <mxGeometry relative="1" as="geometry"/>
        </mxCell>'''


def edge_undirected(id_, source, target, dashed=0):
    """无向边（无箭头），用于同构图等"""
    ds = ";dashed=1" if dashed else ""
    style = f"endArrow=none;html=1;rounded=0;strokeWidth=1;strokeColor=#333333{ds};exitX=1;exitY=0.5;exitDx=0;exitDy=0;entryX=0;entryY=0.5;entryDx=0;entryDy=0;"
    return f'''        <mxCell id="{id_}" style="{style}" parent="1" source="{source}" target="{target}" edge="1">
          <mxGeometry relative="1" as="geometry"/>
        </mxCell>'''


def edge_curved(id_, source, target):
    """高阶连接弧形边（从节点顶部弧过）"""
    style = "endArrow=classic;html=1;curved=1;strokeWidth=1;exitX=0.5;exitY=0;exitDx=0;exitDy=0;entryX=0.5;entryY=0;entryDx=0;entryDy=0;"
    return f'''        <mxCell id="{id_}" style="{style}" parent="1" source="{source}" target="{target}" edge="1">
          <mxGeometry relative="1" as="geometry"/>
        </mxCell>'''


def _xml_escape(s):
    """转义 XML 属性中的特殊字符（保留 HTML 标签供 Draw.io 渲染）"""
    s = str(s).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace('"', "&quot;")
    return s


def text(id_, x, y, w, h, content, font_size=None, bold=0, font_family=None):
    fsz = font_size if font_size is not None else FONT_BODY
    ff = font_family if font_family else FONT
    fstyle = f";fontStyle={bold}" if bold else ""
    style = f"text;html=1;strokeColor=none;fillColor=none;align=center;verticalAlign=middle;fontFamily={ff};fontColor={FONT_COLOR};fontSize={fsz}{fstyle}"
    return f'''        <mxCell id="{id_}" value="{_xml_escape(content)}" style="{style}" parent="1" vertex="1">
          <mxGeometry x="{x}" y="{y}" width="{w}" height="{h}" as="geometry"/>
        </mxCell>'''


def gen_paper_structure():
    """论文结构图"""
    cells = []
    cid = 2
    # 标题
    cells.append(text(cid, 350, 20, 400, 30, "本文研究框架", FONT_LARGE, 1))
    cid += 1
    # 六章
    chapters = [
        ("第一章 绪论", 80, 70),
        ("第二章 相关理论与技术", 220, 70),
        ("第三章 FedASCL框架", 450, 70),
        ("第四章 语义感知压缩", 680, 70),
        ("第五章 系统实现", 850, 70),
        ("第六章 总结与展望", 980, 70),
    ]
    ids = []
    for ch, x, y in chapters:
        cells.append(rect(cid, x, y, 120, 50, ch.replace(" ", "\n"), BLUE_FILL, BLUE_EDGE, 1, FONT_SMALL))
        ids.append(cid)
        cid += 1
    for i in range(len(ids) - 1):
        cells.append(edge(cid, ids[i], ids[i + 1]))
        cid += 1
    return mxfile_header() + "\n" + "\n".join(cells) + mxfile_footer()


def gen_compression_flow():
    """压缩流程示意图：评估-剪枝-量化-补偿-上传"""
    cells = []
    cid = 2
    steps = [
        ("评估", 80, 100),
        ("剪枝", 260, 100),
        ("量化", 440, 100),
        ("补偿", 620, 100),
        ("上传", 800, 100),
    ]
    ids = []
    for name, x, y in steps:
        cells.append(rect(cid, x, y, 140, 50, name, GRAY, TEXT, 1, FONT_TITLE))
        ids.append(cid)
        cid += 1
    for i in range(len(ids) - 1):
        cells.append(edge(cid, ids[i], ids[i + 1]))
        cid += 1
    # 底部说明
    cells.append(text(cid, 80, 180, 500, 30, "从结构视图提取元路径注意力权重 α^(t)，以 Top-K 方式屏蔽低贡献元路径", FONT_SMALL))
    cid += 1
    cells.append(text(cid, 80, 210, 600, 30, "对保留通道的梯度执行低比特随机量化，并将量化误差在本地累积用于下一轮补偿", FONT_SMALL))
    cid += 1
    cells.append(text(cid, 350, 50, 400, 25, "语义感知压缩流程", FONT_TITLE, 1))
    cid += 1
    return mxfile_header() + "\n" + "\n".join(cells) + mxfile_footer()


def gen_bipartite_matrix():
    """用户-物品二部图与交互矩阵"""
    cells = []
    cid = 2
    # 标题
    cells.append(text(cid, 250, 10, 500, 25, "用户-物品二部图与交互矩阵对应关系", FONT_TITLE, 1))
    cid += 1
    # 左侧：物品
    cells.append(text(cid, 80, 45, 60, 20, "物品", FONT_SUBTITLE, 1))
    cid += 1
    for j in range(5):
        cells.append(text(cid, 120 + j * 45, 45, 30, 20, f"v{j+1}", FONT_BODY))
        cid += 1
    cells.append(text(cid, 15, 100, 20, 200, "用户", FONT_SUBTITLE, 1))
    cid += 1
    # 矩阵 4x5
    filled = [(0,0),(0,2),(0,3), (1,1),(1,3),(1,4), (2,0),(2,1),(2,2), (3,2),(3,3),(3,4)]  # (row,col) 0-based
    for i in range(4):
        cells.append(text(cid, 85, 80 + i * 45, 25, 20, f"u{i+1}", FONT_BODY))
        cid += 1
        for j in range(5):
            fill = BLUE_FILL if (i, j) in filled else "#ffffff"
            stroke = BLUE_EDGE if (i, j) in filled else "#cccccc"
            cells.append(rect(cid, 115 + j * 45, 75 + i * 45, 35, 35, "", fill, stroke, 1))
            cid += 1
    # 等价映射
    cells.append(rect(cid, 355, 110, 80, 50, "等价映射", "#ffffff", TEXT, 0, FONT_BODY))
    cid += 1
    # 右侧：二部图节点
    u_ids, v_ids = [], []
    for i in range(4):
        cells.append(ellipse(cid, 490, 70 + i * 45, 35, 35, f"u{i+1}", BLUE_FILL, BLUE_EDGE))
        u_ids.append(cid)
        cid += 1
    for j in range(5):
        cells.append(ellipse(cid, 620, 50 + j * 40, 35, 35, f"v{j+1}", ORANGE_FILL, ORANGE_EDGE))
        v_ids.append(cid)
        cid += 1
    # 边 u_i -> v_j
    for (ui, vj) in [(0,0),(0,2),(0,3), (1,1),(1,3),(1,4), (2,0),(2,1),(2,2), (3,2),(3,3),(3,4)]:
        cells.append(edge(cid, u_ids[ui], v_ids[vj]))
        cid += 1
    return mxfile_header() + "\n" + "\n".join(cells) + mxfile_footer()


def gen_homo_hetero():
    """同构图与异构图对比（按中文学术期刊规范：宋体、RGB 配色、下标、虚实边）"""
    cells = []
    cid = 2
    # 主标题
    cells.append(text(cid, 300, 8, 400, 28, "同构图与异构图对比", FONT_TITLE, 1, FONT_CN))
    cid += 1
    # ----- 左侧：同构图 -----
    s1_title = "同构图<br>Homogeneous Graph"
    cells.append(text(cid, 80, 45, 200, 36, s1_title, FONT_SUBTITLE, 1, FONT_CN))
    cid += 1
    # 5 个蓝色节点，五边形布局，RGB(103,146,199)
    nodes1 = [(120, 95), (215, 65), (280, 115), (245, 175), (140, 165)]
    ids1 = []
    for i, (x, y) in enumerate(nodes1):
        lbl = f"U<sub>{i+1}</sub>"
        cells.append(ellipse(cid, x, y, 36, 36, lbl, GNN_USER_FILL, GNN_USER_EDGE))
        ids1.append(cid)
        cid += 1
    # 完全图：10 条无向实线边
    for i in range(5):
        for j in range(i + 1, 5):
            cells.append(edge_undirected(cid, ids1[i], ids1[j]))
            cid += 1
    cells.append(text(cid, 110, 218, 240, 22, "单一节点类型，单一边类型", FONT_SMALL, 0, FONT_CN))
    cid += 1
    # ----- 右侧：异构图 -----
    s2_title = "异构图<br>Heterogeneous Graph"
    cells.append(text(cid, 480, 45, 220, 36, s2_title, FONT_SUBTITLE, 1, FONT_CN))
    cid += 1
    # 2 个 User 节点（蓝）+ 4 个 Item 节点（橙）
    u_pos = [(455, 95), (455, 145)]
    i_pos = [(575, 82), (645, 118), (610, 172), (530, 155)]  # 菱形
    ids_u, ids_i = [], []
    for i, (x, y) in enumerate(u_pos):
        lbl = f"U<sub>{i+1}</sub>"
        cells.append(ellipse(cid, x, y, 34, 34, lbl, GNN_USER_FILL, GNN_USER_EDGE))
        ids_u.append(cid)
        cid += 1
    for i, (x, y) in enumerate(i_pos):
        lbl = f"I<sub>{i+1}</sub>"
        cells.append(ellipse(cid, x, y, 34, 34, lbl, GNN_ITEM_FILL, GNN_ITEM_EDGE))
        ids_i.append(cid)
        cid += 1
    # 实线：U-U, U-I
    cells.append(edge_undirected(cid, ids_u[0], ids_u[1]))
    cid += 1
    cells.append(edge_undirected(cid, ids_u[0], ids_i[0]))
    cid += 1
    cells.append(edge_undirected(cid, ids_u[0], ids_i[1]))
    cid += 1
    cells.append(edge_undirected(cid, ids_u[1], ids_i[1]))
    cid += 1
    cells.append(edge_undirected(cid, ids_u[1], ids_i[3]))
    cid += 1
    # 虚线：I-I（I1-I2, I1-I3, I2-I3, I2-I4, I3-I4）
    cells.append(edge_undirected(cid, ids_i[0], ids_i[1], dashed=1))
    cid += 1
    cells.append(edge_undirected(cid, ids_i[0], ids_i[2], dashed=1))
    cid += 1
    cells.append(edge_undirected(cid, ids_i[1], ids_i[2], dashed=1))
    cid += 1
    cells.append(edge_undirected(cid, ids_i[1], ids_i[3], dashed=1))
    cid += 1
    cells.append(edge_undirected(cid, ids_i[2], ids_i[3], dashed=1))
    cid += 1
    cells.append(text(cid, 500, 218, 260, 22, "多种节点类型，多种边/关系类型", FONT_SMALL, 0, FONT_CN))
    cid += 1
    return mxfile_header(page_w=920, page_h=260) + "\n" + "\n".join(cells) + mxfile_footer()


def gen_meta_path():
    """元路径示意图 U->A->P"""
    cells = []
    cid = 2
    cells.append(text(cid, 250, 10, 200, 25, "元路径语义建模", FONT_SUBTITLE, 1))
    cid += 1
    cells.append(ellipse(cid, 80, 90, 50, 50, "U", BLUE_FILL, BLUE_EDGE))
    uid = cid
    cid += 1
    cells.append(ellipse(cid, 220, 80, 45, 45, "A", ORANGE_FILL, ORANGE_EDGE))
    aid = cid
    cid += 1
    cells.append(ellipse(cid, 360, 90, 45, 45, "P", "#e8f5e9", "#2e7d32"))
    pid = cid
    cid += 1
    cells.append(edge(cid, uid, aid))
    cid += 1
    cells.append(edge(cid, aid, pid))
    cid += 1
    cells.append(text(cid, 150, 60, 120, 20, "R₁", FONT_SMALL))
    cid += 1
    cells.append(text(cid, 290, 60, 120, 20, "R₂", FONT_SMALL))
    cid += 1
    cells.append(text(cid, 220, 150, 200, 20, "Meta-path: U → A → P", FONT_SMALL))
    cid += 1
    return mxfile_header() + "\n" + "\n".join(cells) + mxfile_footer()


def gen_selector_logic():
    """动态元路径选择器"""
    cells = []
    cid = 2
    cells.append(text(cid, 250, 20, 450, 25, "动态元路径选择器（基于注意力权重 α 的 Top-K 筛选）", FONT_SUBTITLE, 1))
    cid += 1
    boxes = [
        ("输入：元路径集合 P={p₁,...,pₘ} 与权重 α^(t)", 100, 80),
        ("Top-K 筛选：保留权重最大的 K 条元路径，生成掩码 m^(t)∈{0,1}^M", 100, 180),
        ("输出：仅上传 mᵢ^(t)=1 对应子网络的梯度更新；服务端按位聚合", 100, 280),
    ]
    ids = []
    for txt, x, y in boxes:
        cells.append(rect(cid, x, y, 600, 70, txt, BLUE_FILL, BLUE_EDGE, 1, FONT_BODY))
        ids.append(cid)
        cid += 1
    cells.append(edge(cid, ids[0], ids[1]))
    cid += 1
    cells.append(edge(cid, ids[1], ids[2]))
    cid += 1
    return mxfile_header() + "\n" + "\n".join(cells) + mxfile_footer()


# FedASCL 框架图配色（与 draw_fedascl_framework.py 一致）
FEDASCL_BLUE = '#e3f2fd'
FEDASCL_BLUE_EDGE = '#1976d2'
FEDASCL_ORANGE = '#fff3e0'
FEDASCL_ORANGE_EDGE = '#e65100'
FEDASCL_GREEN = '#e8f5e9'
FEDASCL_GREEN_EDGE = '#2e7d32'
FEDASCL_GRAY = '#e8e8e8'
FEDASCL_PANEL = '#eeeeee'


def gen_fedascl_framework():
    """FedASCL 算法总体架构图（服务端-客户端联邦异构图学习）"""
    cells = []
    cid = 2
    # ----- 服务端 (Global) -----
    cells.append(rect(cid, 20, 15, 960, 75, "", FEDASCL_PANEL, "#999999", 1, dashed=0))
    cid += 1
    cells.append(text(cid, 40, 25, 300, 24, "服务端 (Global / Server)", FONT_SUBTITLE, 1, FONT_CN))
    cid += 1
    cells.append(rect(cid, 80, 40, 220, 42, "全局语义原型聚合<br>Prototypes Aggregation", FEDASCL_BLUE, FEDASCL_BLUE_EDGE, 1, FONT_BODY))
    agg = cid
    cid += 1
    cells.append(rect(cid, 420, 40, 280, 42, "模型聚合 (加权平均)<br>Model Aggregation (Weighted Average)", FEDASCL_ORANGE, FEDASCL_ORANGE_EDGE, 1, FONT_BODY))
    model_agg = cid
    cid += 1
    cells.append(edge(cid, agg, model_agg))
    cid += 1
    # ----- 客户端 (Local) 外框 -----
    cells.append(rect(cid, 20, 105, 960, 475, "", FEDASCL_PANEL, "#888888", 1, dashed=0))
    cid += 1
    cells.append(text(cid, 500, 115, 300, 22, "客户端 (Local / Client) — Iterative Local Training", FONT_SUBTITLE, 1, FONT_CN))
    cid += 1
    # 虚线内框
    cells.append(rect(cid, 40, 148, 920, 420, "", "#ffffff", "#999999", 1, FONT_BODY, dashed=1))
    cid += 1
    # ----- 1. 输入 & 图构建 -----
    cells.append(rect(cid, 50, 168, 140, 48, "用户/物品 Raw 原始属性", FEDASCL_GRAY, TEXT, 1, FONT_BODY))
    raw_attr = cid
    cid += 1
    cells.append(rect(cid, 50, 240, 140, 48, "本地 Interaction 数据", FEDASCL_GRAY, TEXT, 1, FONT_BODY))
    raw_int = cid
    cid += 1
    cells.append(rect(cid, 230, 168, 130, 52, "属性语义图<br>Semantic Graph", FEDASCL_BLUE, FEDASCL_BLUE_EDGE, 1, FONT_BODY))
    sem_graph = cid
    cid += 1
    cells.append(rect(cid, 230, 240, 130, 52, "交互结构图<br>Structural Graph", FEDASCL_ORANGE, FEDASCL_ORANGE_EDGE, 1, FONT_BODY))
    stru_graph = cid
    cid += 1
    cells.append(text(cid, 295, 218, 120, 18, "1. Graph Construction", FONT_SMALL))
    cid += 1
    cells.append(edge(cid, raw_attr, sem_graph))
    cid += 1
    cells.append(edge(cid, raw_int, stru_graph))
    cid += 1
    # ----- 2. 双视图编码 -----
    cells.append(rect(cid, 400, 168, 140, 48, "异构GNN编码器<br>GNN Encoder", FEDASCL_GREEN, FEDASCL_GREEN_EDGE, 1, FONT_BODY))
    enc_sem = cid
    cid += 1
    cells.append(rect(cid, 400, 240, 140, 48, "异构GNN编码器<br>GNN Encoder", FEDASCL_ORANGE, FEDASCL_ORANGE_EDGE, 1, FONT_BODY))
    enc_stru = cid
    cid += 1
    cells.append(edge(cid, sem_graph, enc_sem))
    cid += 1
    cells.append(edge(cid, stru_graph, enc_stru))
    cid += 1
    # ----- 3. 跨视图对比 -----
    cells.append(rect(cid, 580, 195, 180, 56, "3. 跨视图对比 Contrastive<br>(最大化互信息)", GRAY, TEXT, 1, FONT_BODY))
    contrast = cid
    cid += 1
    cells.append(edge(cid, enc_sem, contrast))
    cid += 1
    cells.append(edge(cid, enc_stru, contrast))
    cid += 1
    # ----- 4. 原型对齐 -----
    cells.append(rect(cid, 800, 195, 140, 56, "4. 原型对齐 (修正偏差)<br>Prototype Alignment", FEDASCL_GREEN, FEDASCL_GREEN_EDGE, 1, FONT_BODY))
    proto = cid
    cid += 1
    cells.append(edge(cid, contrast, proto))
    cid += 1
    # ----- 元路径 & 推荐 -----
    cells.append(rect(cid, 580, 280, 140, 48, "元路径挖掘 Mining &<br>注意力融合", FEDASCL_BLUE, FEDASCL_BLUE_EDGE, 1, FONT_BODY))
    mining = cid
    cid += 1
    cells.append(rect(cid, 800, 280, 140, 48, "Recommendation<br>Prediction", FEDASCL_BLUE, FEDASCL_BLUE_EDGE, 1, FONT_BODY))
    pred = cid
    cid += 1
    cells.append(edge(cid, enc_sem, mining))
    cid += 1
    cells.append(edge(cid, proto, mining))
    cid += 1
    cells.append(edge(cid, mining, pred))
    cid += 1
    # ----- 5. 损失计算 -----
    cells.append(rect(cid, 580, 355, 200, 50, "5. 损失计算 Loss Calculation<br>Rec Loss (Main) + CL Loss (Aux)", FEDASCL_GRAY, TEXT, 1, FONT_BODY))
    loss = cid
    cid += 1
    cells.append(edge(cid, pred, loss))
    cid += 1
    cells.append(edge(cid, proto, loss))
    cid += 1
    # ----- 6. 联合优化 -----
    cells.append(rect(cid, 580, 430, 220, 50, "6. 联合反向传播与参数更新<br>6. Joint Optimization", FEDASCL_BLUE, FEDASCL_BLUE_EDGE, 1, FONT_BODY))
    joint = cid
    cid += 1
    cells.append(edge(cid, loss, joint))
    cid += 1
    # ----- 端云箭头标注 -----
    cells.append(text(cid, 170, 340, 100, 20, "Global Prototypes", FONT_SMALL))
    cid += 1
    cells.append(text(cid, 780, 130, 120, 20, "Updated Model Parameters", FONT_SMALL))
    cid += 1
    cells.append(text(cid, 350, 95, 120, 20, "Global Model Update", FONT_SMALL))
    cid += 1
    return mxfile_header(page_w=1000, page_h=610) + "\n" + "\n".join(cells) + mxfile_footer()


def gen_system_architecture():
    """系统总体设计架构图"""
    cells = []
    cid = 2
    cells.append(text(cid, 300, 20, 500, 30, "系统总体设计架构图", FONT_LARGE, 1))
    cid += 1
    layers = [
        ("业务展示层\n(React, Web UI)", 100, 80),
        ("业务服务层\n(推荐 API, 冷启动)", 100, 180),
        ("算法引擎层\n(FedASCL, 压缩器, 聚合器)", 100, 280),
        ("数据存储层\n(客户端: SQLite; 服务端: MySQL/Redis)", 100, 380),
    ]
    ids = []
    for txt, x, y in layers:
        cells.append(rect(cid, x, y, 600, 70, txt, BLUE_FILL, BLUE_EDGE, 1, FONT_BODY))
        ids.append(cid)
        cid += 1
    for i in range(len(ids) - 1):
        cells.append(edge(cid, ids[i], ids[i + 1]))
        cid += 1
    return mxfile_header() + "\n" + "\n".join(cells) + mxfile_footer()


def gen_cross_view_cl():
    """跨视图对比机制"""
    cells = []
    cid = 2
    cells.append(text(cid, 250, 20, 300, 25, "跨视图对比学习机制", FONT_SUBTITLE, 1))
    cid += 1
    cells.append(rect(cid, 80, 80, 150, 60, "属性视图\nz^attr", BLUE_FILL, BLUE_EDGE, 1))
    cid += 1
    c1 = cid - 1
    cells.append(rect(cid, 80, 180, 150, 60, "结构视图\nz^stru", ORANGE_FILL, ORANGE_EDGE, 1))
    cid += 1
    c2 = cid - 1
    cells.append(rect(cid, 350, 120, 200, 80, "InfoNCE / 最大化互信息", GRAY, TEXT, 1))
    cid += 1
    c3 = cid - 1
    cells.append(edge(cid, c1, c3))
    cid += 1
    cells.append(edge(cid, c2, c3))
    cid += 1
    return mxfile_header() + "\n" + "\n".join(cells) + mxfile_footer()


def gen_prototype_alignment():
    """基于原型的语义对齐策略"""
    cells = []
    cid = 2
    cells.append(text(cid, 250, 20, 350, 25, "基于原型的语义对齐策略", FONT_SUBTITLE, 1))
    cid += 1
    cells.append(rect(cid, 80, 100, 150, 50, "本地嵌入 zᵢ", ORANGE_FILL, ORANGE_EDGE, 1))
    cid += 1
    c1 = cid - 1
    cells.append(rect(cid, 350, 100, 150, 50, "全局原型 cₖ", BLUE_FILL, BLUE_EDGE, 1))
    cid += 1
    c2 = cid - 1
    cells.append(rect(cid, 280, 220, 130, 40, "L_proto 约束", GRAY, TEXT, 1))
    cid += 1
    c3 = cid - 1
    cells.append(edge(cid, c1, c2))
    cid += 1
    cells.append(edge(cid, c2, c3))
    cid += 1
    return mxfile_header() + "\n" + "\n".join(cells) + mxfile_footer()


def gen_gnn():
    """图神经网络三阶段流程（紧凑布局、L-hop 高阶弧线、三阶段靠拢）"""
    cells = []
    cid = 2
    # 三阶段靠拢：S1: 0-195, 箭头 202-218, S2: 225-450, 箭头 458-474, S3: 482-750
    # ----- Section 1 -----
    s1_title = "(1) 图结构定义与初始化<br>Graph Definition & Initialization"
    cells.append(text(cid, 8, 5, 190, 44, s1_title, FONT_SUBTITLE))
    cid += 1
    cells.append(text(cid, 50, 48, 120, 20, "G = (U ∪ V, E)", FONT_SUBTITLE))
    cid += 1
    u_pos = [(25, 78), (25, 128), (25, 178)]
    u_ids = []
    for i, (x, y) in enumerate(u_pos):
        cells.append(ellipse(cid, x, y, 34, 34, f"u{i+1}", GNN_USER_FILL, GNN_USER_EDGE))
        u_ids.append(cid)
        cid += 1
    cells.append(text(cid, 8, 130, 18, 16, "U", FONT_SUBTITLE, 1))
    cid += 1
    v_pos = [(125, 70), (125, 120), (125, 170), (125, 220)]
    v_ids = []
    for i, (x, y) in enumerate(v_pos):
        cells.append(square(cid, x, y, 32, f"v{i+1}", GNN_ITEM_FILL, GNN_ITEM_EDGE))
        v_ids.append(cid)
        cid += 1
    cells.append(text(cid, 168, 136, 18, 16, "V", FONT_SUBTITLE, 1))
    cid += 1
    cells.append(edge(cid, u_ids[0], v_ids[0]))
    cid += 1
    cells.append(edge(cid, u_ids[0], v_ids[1]))
    cid += 1
    cells.append(edge(cid, u_ids[1], v_ids[1]))
    cid += 1
    cells.append(edge(cid, u_ids[1], v_ids[2]))
    cid += 1
    cells.append(edge(cid, u_ids[2], v_ids[2]))
    cid += 1
    cells.append(edge(cid, u_ids[2], v_ids[3]))
    cid += 1
    cells.append(text(cid, 88, 58, 12, 14, "E", FONT_BODY, 1))
    cid += 1
    e_u = lambda i: f"e<sub>u{i}</sub><sup>(0)</sup>"
    e_v = lambda i: f"e<sub>v{i}</sub><sup>(0)</sup>"
    cells.append(text(cid, 5, 86, 28, 16, e_u(1), FONT_BODY))
    cid += 1
    cells.append(text(cid, 5, 136, 28, 16, e_u(2), FONT_BODY))
    cid += 1
    cells.append(text(cid, 5, 186, 28, 16, e_u(3), FONT_BODY))
    cid += 1
    cells.append(text(cid, 158, 78, 28, 16, e_v(1), FONT_BODY))
    cid += 1
    cells.append(text(cid, 158, 128, 28, 16, e_v(2), FONT_BODY))
    cid += 1
    cells.append(text(cid, 158, 178, 28, 16, e_v(3), FONT_BODY))
    cid += 1
    cells.append(text(cid, 158, 228, 28, 16, e_v(4), FONT_BODY))
    cid += 1
    cells.append(text(cid, 25, 265, 170, 18, "Initial embeddings e<sup>(0)</sup> assigned.", FONT_BODY))
    cid += 1
    cells.append(block_arrow(cid, 200, 95, 18, 75))
    cid += 1
    # ----- Section 2 -----
    s2_title = "(2) 消息传递与聚合<br>Message Passing & Aggregation"
    cells.append(text(cid, 225, 5, 230, 44, s2_title, FONT_SUBTITLE))
    cid += 1
    i_pos = [(235, 75), (248, 128), (235, 181)]
    i_ids = []
    for i, (x, y) in enumerate(i_pos):
        cells.append(square(cid, x, y, 30, f"i{i+1}", GNN_ITEM_FILL, GNN_ITEM_EDGE))
        i_ids.append(cid)
        cid += 1
    e_i = lambda i: f"e<sub>i{i}</sub><sup>(l-1)</sup>"
    cells.append(text(cid, 278, 82, 42, 16, e_i(1), FONT_BODY))
    cid += 1
    cells.append(text(cid, 291, 135, 42, 16, e_i(2), FONT_BODY))
    cid += 1
    cells.append(text(cid, 278, 188, 42, 16, e_i(3), FONT_BODY))
    cid += 1
    cells.append(text(cid, 248, 228, 55, 16, "i ∈ N<sub>u</sub>", FONT_BODY))
    cid += 1
    cells.append(rect(cid, 360, 112, 85, 36, "AGGREGATE<sup>(l)</sup>", GNN_PROCESS_FILL, GNN_PROCESS_EDGE, 1, FONT_BODY))
    agg_id = cid
    cid += 1
    for iid in i_ids:
        cells.append(edge(cid, iid, agg_id))
        cid += 1
    cells.append(text(cid, 348, 90, 52, 16, "Messages", FONT_BODY))
    cid += 1
    cells.append(text(cid, 455, 118, 60, 18, "m<sub>N<sub>u</sub></sub><sup>(l)</sup>", FONT_SUBTITLE, 1))
    cid += 1
    f2 = "m<sub>N<sub>u</sub></sub><sup>(l)</sup> = AGGREGATE<sup>(l)</sup>({e<sub>i</sub><sup>(l-1)</sup> : i ∈ N<sub>u</sub>})"
    cells.append(text(cid, 225, 255, 230, 20, f2, FONT_BODY))
    cid += 1
    cells.append(block_arrow(cid, 466, 95, 18, 75))
    cid += 1
    # ----- Section 3 -----
    s3_title = "(3) 特征更新与高阶协同<br>Feature Update & High-order Connectivity"
    cells.append(text(cid, 482, 5, 270, 44, s3_title, FONT_SUBTITLE))
    cid += 1
    cells.append(ellipse(cid, 498, 48, 32, 32, "u", GNN_USER_FILL, GNN_USER_EDGE))
    u_node = cid
    cid += 1
    cells.append(ellipse(cid, 566, 48, 32, 32, "u", GNN_USER_FILL, GNN_USER_EDGE))
    m_node = cid
    cid += 1
    cells.append(text(cid, 493, 85, 44, 16, "e<sub>u</sub><sup>(l-1)</sup>", FONT_BODY))
    cid += 1
    cells.append(text(cid, 563, 85, 52, 16, "m<sub>N<sub>u</sub></sub><sup>(l)</sup>", FONT_BODY))
    cid += 1
    cells.append(rect(cid, 625, 46, 72, 36, "UPDATE<sup>(l)</sup>", GNN_PROCESS_FILL, GNN_PROCESS_EDGE, 1, FONT_BODY))
    upd_id = cid
    cid += 1
    cells.append(edge(cid, u_node, upd_id))
    cid += 1
    cells.append(edge(cid, m_node, upd_id))
    cid += 1
    cells.append(text(cid, 710, 58, 40, 16, "e<sub>u</sub><sup>(l)</sup>", FONT_BODY))
    cid += 1
    f3 = "e<sub>u</sub><sup>(l)</sup> = UPDATE<sup>(l)</sup>(e<sub>u</sub><sup>(l-1)</sup>, m<sub>N<sub>u</sub></sub><sup>(l)</sup>)"
    cells.append(text(cid, 482, 92, 240, 20, f3, FONT_BODY))
    cid += 1
    # L-hop 虚线框（节点紧凑 + 高阶弧形边）
    cells.append(rect(cid, 482, 118, 250, 78, "", "#fafafa", "#666666", 1, FONT_BODY, dashed=1))
    cid += 1
    ha_x, h1_x, hb_x, h2_x = 502, 555, 608, 661
    hy = 132
    cells.append(ellipse(cid, ha_x, hy, 32, 32, "User A", GNN_USER_FILL, GNN_USER_EDGE))
    ha_id = cid
    cid += 1
    cells.append(square(cid, h1_x, hy, 30, "Item 1", GNN_ITEM_FILL, GNN_ITEM_EDGE))
    h1_id = cid
    cid += 1
    cells.append(ellipse(cid, hb_x, hy, 32, 32, "User B", GNN_USER_FILL, GNN_USER_EDGE))
    hb_id = cid
    cid += 1
    cells.append(square(cid, h2_x, hy, 30, "Item 2", GNN_ITEM_FILL, GNN_ITEM_EDGE))
    h2_id = cid
    cid += 1
    cells.append(edge(cid, ha_id, h1_id))
    cid += 1
    cells.append(edge(cid, h1_id, hb_id))
    cid += 1
    cells.append(edge(cid, hb_id, h2_id))
    cid += 1
    cells.append(edge_curved(cid, ha_id, hb_id))
    cid += 1
    cells.append(edge_curved(cid, h1_id, h2_id))
    cid += 1
    cells.append(edge_curved(cid, ha_id, h2_id))
    cid += 1
    cells.append(text(cid, 558, 173, 180, 18, "L-hop High-order Connectivity", FONT_BODY))
    cid += 1
    cells.append(text(cid, 482, 208, 250, 20, "Stacking L layers captures L-hop neighbors", FONT_BODY))
    cid += 1
    return mxfile_header(page_w=770, page_h=250) + "\n" + "\n".join(cells) + mxfile_footer()


def gen_attr_sem_graph():
    """属性语义图构建流程"""
    cells = []
    cid = 2
    cells.append(text(cid, 300, 15, 400, 25, "属性语义图构建流程", FONT_SUBTITLE, 1))
    cid += 1
    steps = [
        ("A. 原始属性\nOne-Hot / Min-Max", 80, 80),
        ("B. 相似度计算\ncos(xi, xj)", 350, 80),
        ("C. k-NN 超图构建\n关联矩阵 H", 620, 80),
    ]
    ids = []
    for txt, x, y in steps:
        cells.append(rect(cid, x, y, 200, 70, txt, BLUE_FILL, BLUE_EDGE, 1, FONT_BODY))
        ids.append(cid)
        cid += 1
    for i in range(len(ids) - 1):
        cells.append(edge(cid, ids[i], ids[i + 1]))
        cid += 1
    cells.append(text(cid, 450, 180, 150, 25, "→ 图神经网络输入", FONT_BODY))
    cid += 1
    return mxfile_header() + "\n" + "\n".join(cells) + mxfile_footer()


def gen_hypergraph_compare():
    """超图与普通图对比"""
    cells = []
    cid = 2
    cells.append(text(cid, 300, 10, 350, 25, "超图与普通图对比", FONT_SUBTITLE, 1))
    cid += 1
    cells.append(text(cid, 150, 50, 250, 20, "普通图（边连2点）", FONT_BODY, 1))
    cid += 1
    pts1 = [(100, 100), (180, 80), (180, 120)]
    ids1 = []
    for i, (x, y) in enumerate(pts1):
        cells.append(ellipse(cid, x, y, 30, 30, f"n{i+1}", BLUE_FILL, BLUE_EDGE))
        ids1.append(cid)
        cid += 1
    cells.append(edge(cid, ids1[0], ids1[1]))
    cid += 1
    cells.append(edge(cid, ids1[0], ids1[2]))
    cid += 1
    cells.append(text(cid, 550, 50, 250, 20, "超图（超边连多点）", FONT_BODY, 1))
    cid += 1
    pts2 = [(480, 100), (560, 80), (560, 120), (520, 140)]
    for i, (x, y) in enumerate(pts2):
        cells.append(ellipse(cid, x, y, 30, 30, f"n{i+1}", ORANGE_FILL, ORANGE_EDGE))
        cid += 1
    cells.append(rect(cid, 500, 95, 100, 50, "超边 e", "#e8f5e9", "#2e7d32", 1, 9))
    cid += 1
    return mxfile_header() + "\n" + "\n".join(cells) + mxfile_footer()


def gen_federated_learning():
    """联邦学习架构"""
    cells = []
    cid = 2
    cells.append(text(cid, 300, 20, 350, 25, "联邦学习架构", FONT_SUBTITLE, 1))
    cid += 1
    cells.append(ellipse(cid, 400, 80, 80, 60, "服务器\nServer", BLUE_FILL, BLUE_EDGE))
    server = cid
    cid += 1
    clients = []
    for i, x in enumerate([100, 300, 500, 700]):
        cells.append(ellipse(cid, x, 220, 60, 50, f"客户端{i+1}", ORANGE_FILL, ORANGE_EDGE))
        clients.append(cid)
        cid += 1
    for cl in clients:
        cells.append(edge(cid, cl, server))
        cid += 1
        cells.append(edge(cid, server, cl))
        cid += 1
    return mxfile_header() + "\n" + "\n".join(cells) + mxfile_footer()


def gen_horizontal_vertical_fl():
    """横向联邦与纵向联邦对比"""
    cells = []
    cid = 2
    cells.append(text(cid, 300, 15, 400, 25, "横向联邦与纵向联邦数据分布对比", FONT_SUBTITLE, 1))
    cid += 1
    cells.append(rect(cid, 80, 80, 200, 120, "横向联邦\n同构特征、不同用户\n(样本划分)", BLUE_FILL, BLUE_EDGE, 1, FONT_BODY))
    cid += 1
    cells.append(rect(cid, 400, 80, 200, 120, "纵向联邦\n同用户、异特征\n(特征划分)", ORANGE_FILL, ORANGE_EDGE, 1, FONT_BODY))
    cid += 1
    cells.append(text(cid, 200, 230, 100, 20, "Client A", 9))
    cid += 1
    cells.append(text(cid, 200, 260, 100, 20, "Client B", 9))
    cid += 1
    cells.append(text(cid, 500, 230, 100, 20, "Client A", 9))
    cid += 1
    cells.append(text(cid, 500, 260, 100, 20, "Client B", 9))
    cid += 1
    return mxfile_header() + "\n" + "\n".join(cells) + mxfile_footer()


def gen_fed_prototype():
    """联邦原型聚合与语义对齐"""
    cells = []
    cid = 2
    cells.append(text(cid, 250, 15, 400, 25, "联邦原型聚合与语义对齐", FONT_SUBTITLE, 1))
    cid += 1
    cells.append(rect(cid, 80, 80, 120, 50, "客户端1\n本地原型", ORANGE_FILL, ORANGE_EDGE, 1, 9))
    c1 = cid
    cid += 1
    cells.append(rect(cid, 80, 160, 120, 50, "客户端2\n本地原型", ORANGE_FILL, ORANGE_EDGE, 1, 9))
    c2 = cid
    cid += 1
    cells.append(rect(cid, 350, 100, 150, 70, "服务器\n全局原型聚合", BLUE_FILL, BLUE_EDGE, 1, FONT_BODY))
    server = cid
    cid += 1
    cells.append(rect(cid, 600, 110, 130, 50, "下发全局原型", GRAY, TEXT, 1, 9))
    down = cid
    cid += 1
    cells.append(edge(cid, c1, server))
    cid += 1
    cells.append(edge(cid, c2, server))
    cid += 1
    cells.append(edge(cid, server, down))
    cid += 1
    return mxfile_header() + "\n" + "\n".join(cells) + mxfile_footer()


def gen_coldstart_flow():
    """冷启动推荐策略流程"""
    cells = []
    cid = 2
    cells.append(text(cid, 250, 20, 450, 25, "基于属性-结构双通路的冷启动推荐策略", FONT_SUBTITLE, 1))
    cid += 1
    cells.append(rect(cid, 80, 100, 150, 50, "用户请求", GRAY, TEXT, 1))
    rq = cid
    cid += 1
    cells.append(rect(cid, 320, 100, 120, 50, "有交互?", GRAY, TEXT, 1))
    chk = cid
    cid += 1
    cells.append(rect(cid, 520, 60, 180, 50, "结构优先\n(元路径聚合)", BLUE_FILL, BLUE_EDGE, 1))
    stru = cid
    cid += 1
    cells.append(rect(cid, 520, 140, 180, 50, "属性优先\n(原型映射)", ORANGE_FILL, ORANGE_EDGE, 1))
    attr = cid
    cid += 1
    cells.append(edge(cid, rq, chk))
    cid += 1
    cells.append(edge(cid, chk, stru))
    cid += 1
    cells.append(edge(cid, chk, attr))
    cid += 1
    return mxfile_header() + "\n" + "\n".join(cells) + mxfile_footer()


def main():
    files = [
        ("01_论文结构.drawio", gen_paper_structure),
        ("02_压缩流程示意图.drawio", gen_compression_flow),
        ("03_二部图与矩阵.drawio", gen_bipartite_matrix),
        ("04_同构图与异构图对比.drawio", gen_homo_hetero),
        ("05_元路径.drawio", gen_meta_path),
        ("06_动态元路径选择器.drawio", gen_selector_logic),
        ("07_系统架构.drawio", gen_system_architecture),
        ("08_跨视图对比机制.drawio", gen_cross_view_cl),
        ("09_基于原型的语义对齐.drawio", gen_prototype_alignment),
        ("10_图神经网络.drawio", gen_gnn),
        ("11_属性语义图构建.drawio", gen_attr_sem_graph),
        ("12_超图对比.drawio", gen_hypergraph_compare),
        ("13_联邦学习架构.drawio", gen_federated_learning),
        ("14_冷启动推荐策略.drawio", gen_coldstart_flow),
        ("15_横向纵向联邦对比.drawio", gen_horizontal_vertical_fl),
        ("16_联邦原型对齐.drawio", gen_fed_prototype),
        ("17_FedASCL框架.drawio", gen_fedascl_framework),
    ]
    for fname, gen in files:
        path = os.path.join(OUT_DIR, fname)
        with open(path, 'w', encoding='utf-8') as f:
            f.write(gen())
        print(f"Saved: {path}")
    print(f"\nAll {len(files)} Draw.io files saved to: {OUT_DIR}")


if __name__ == '__main__':
    main()
