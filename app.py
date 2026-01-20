import os
import json
import time
import requests
import streamlit as st
import google.generativeai as genai
from pypdf import PdfReader
from streamlit_option_menu import option_menu

# ============================================================
# 0) 基础配置
# ============================================================
st.set_page_config(
    page_title="TradeNexus AI - B2B 外贸销售专家",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ============================================================
# 1) 样式：严格贴近图2（AI Studio 风格）
# ============================================================
def inject_css():
    st.markdown(
        """
<style>
/* ====== Global ====== */
:root{
  --bg: #f6f7fb;
  --panel: #ffffff;
  --muted: #6b7280;
  --text: #0f172a;
  --border: rgba(15, 23, 42, .10);
  --shadow: 0 10px 28px rgba(15, 23, 42, .08);

  --sidebar: #0b1220;
  --sidebar2:#0f172a;
  --sideText: rgba(255,255,255,.88);
  --sideMuted: rgba(255,255,255,.55);
  --sideBorder: rgba(255,255,255,.10);

  --primary: #4f46e5;
  --primary2:#6d28d9;

  --cardHover: rgba(79,70,229,.06);
}

html, body, [class*="css"]{
  font-family: ui-sans-serif, system-ui, -apple-system, Segoe UI, Roboto, Helvetica, Arial;
}
.stApp{ background: var(--bg); }
header {visibility: hidden;}

/* 主体左右留白更接近图2 */
.block-container{
  max-width: 1200px;
  padding-top: 12px;
  padding-bottom: 96px; /* 给底部输入栏留空间 */
}

/* ====== Sidebar ====== */
section[data-testid="stSidebar"]{
  background: linear-gradient(180deg, var(--sidebar) 0%, var(--sidebar2) 100%);
  border-right: 1px solid var(--sideBorder);
}
section[data-testid="stSidebar"] *{
  color: var(--sideText) !important;
}
.sidebar-brand{
  display:flex; align-items:center; gap:10px;
  padding: 14px 10px 10px 10px;
}
.sidebar-logo{
  width:34px;height:34px;border-radius:12px;
  background: linear-gradient(135deg, rgba(79,70,229,.95), rgba(109,40,217,.95));
  display:flex;align-items:center;justify-content:center;
  color:white;font-weight:900;
  box-shadow: 0 12px 28px rgba(79,70,229,.30);
}
.sidebar-title{ font-weight:900; letter-spacing:.2px; line-height:1.1; }
.sidebar-sub{ font-size:12px; color: var(--sideMuted) !important; margin-top:2px; }

.sidebar-footer-btn{
  margin-top: 10px;
  padding: 12px;
  border-radius: 16px;
  border: 1px solid rgba(255,255,255,.14);
  background: rgba(255,255,255,.06);
}
.sidebar-footer-btn:hover{
  background: rgba(255,255,255,.08);
}

/* sidebar 输入控件 */
section[data-testid="stSidebar"] .stTextArea textarea,
section[data-testid="stSidebar"] .stTextInput input{
  background: rgba(255,255,255,.08) !important;
  border: 1px solid rgba(255,255,255,.12) !important;
  border-radius: 14px !important;
}

/* ====== Main Header (像图2的那条标题栏) ====== */
.main-header{
  display:flex;
  align-items:flex-start;
  justify-content:space-between;
  gap: 12px;
  padding: 14px 16px;
  background: var(--panel);
  border: 1px solid var(--border);
  border-radius: 18px;
  box-shadow: var(--shadow);
}
.mh-left .mh-title{
  font-size: 16px;
  font-weight: 900;
  color: var(--text);
  margin: 0;
}
.mh-left .mh-sub{
  font-size: 12px;
  color: var(--muted);
  margin-top: 3px;
}
.mh-right{
  display:flex; align-items:center; gap: 10px;
}
.mh-btn{
  border: 1px solid var(--border);
  background: #fff;
  padding: 8px 12px;
  border-radius: 999px;
  font-size: 12px;
  font-weight: 800;
  color: var(--text);
  box-shadow: 0 8px 18px rgba(15,23,42,.06);
}
.mh-btn:hover{ background: rgba(15,23,42,.02); }

/* ====== Center Hero ====== */
.hero{
  margin-top: 30px;
  text-align:center;
}
.hero-icon{
  width: 56px; height: 56px;
  margin: 0 auto 12px auto;
  border-radius: 18px;
  background: linear-gradient(180deg, rgba(79,70,229,.10), rgba(109,40,217,.08));
  border: 1px solid rgba(79,70,229,.18);
  display:flex; align-items:center; justify-content:center;
  color: var(--primary);
  font-size: 26px;
}
.hero-title{
  font-size: 28px;
  font-weight: 950;
  color: var(--text);
  margin: 0;
}
.hero-desc{
  margin-top: 10px;
  color: var(--muted);
  font-size: 13px;
}

/* ====== Quick Start Panel (像图2中间那块) ====== */
.qs-panel{
  margin-top: 26px;
  background: var(--panel);
  border: 1px solid var(--border);
  border-radius: 18px;
  box-shadow: var(--shadow);
  padding: 16px;
}
.qs-title{
  font-weight: 900;
  color: var(--text);
  font-size: 13px;
  margin-bottom: 10px;
}

/* 用 button 伪装成“整行可点卡片” */
div[data-testid="stButton"] > button.qs-card{
  width: 100%;
  text-align: left;
  border-radius: 14px;
  border: 1px solid rgba(15,23,42,.10);
  background: #fff;
  padding: 12px 12px;
  margin: 6px 0;
  box-shadow: 0 8px 18px rgba(15,23,42,.04);
}
div[data-testid="stButton"] > button.qs-card:hover{
  background: var(--cardHover);
  border-color: rgba(79,70,229,.25);
}
.qs-row{
  display:flex;
  align-items:center;
  gap: 10px;
}
.qs-badge{
  width: 22px; height: 22px;
  border-radius: 999px;
  border: 1px solid rgba(79,70,229,.25);
  background: rgba(79,70,229,.08);
  display:flex; align-items:center; justify-content:center;
  font-size: 12px;
  font-weight: 900;
  color: var(--primary);
}
.qs-text .qs-main{
  font-weight: 900;
  color: var(--text);
  font-size: 13px;
}
.qs-text .qs-sub{
  color: var(--muted);
  font-size: 12px;
  margin-top: 2px;
}

/* ====== Chat Area ====== */
.chat-area{
  margin-top: 18px;
}
.chat-scroll{
  max-height: calc(100vh - 520px); /* 头+hero+quickstart+composer 的估算 */
  overflow-y: auto;
  padding-right: 6px;
}
.msg-row{ display:flex; margin: 10px 0; }
.msg-row.user{ justify-content:flex-end; }
.msg-row.assistant{ justify-content:flex-start; }

.bubble{
  max-width: 78%;
  border-radius: 18px;
  border: 1px solid var(--border);
  background: #fff;
  padding: 12px 14px;
  box-shadow: 0 8px 18px rgba(15,23,42,.04);
}
.bubble.user{
  background: rgba(79,70,229,.08);
  border-color: rgba(79,70,229,.18);
}
.bmeta{
  font-size: 11px;
  color: var(--muted);
  margin-bottom: 6px;
}
.bcontent{
  font-size: 13.5px;
  line-height: 1.55;
  color: var(--text);
  white-space: pre-wrap;
}

/* ====== Bottom Composer (像图2底部输入栏) ====== */
.composer{
  position: fixed;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(246,247,251,.92);
  backdrop-filter: blur(12px);
  border-top: 1px solid var(--border);
  z-index: 100;
}
.composer-inner{
  max-width: 1200px;
  margin: 0 auto;
  padding: 12px 10px 14px 10px;
}
.composer-box{
  background: #fff;
  border: 1px solid var(--border);
  border-radius: 18px;
  box-shadow: var(--shadow);
  padding: 10px;
}
.composer-grid{
  display:flex;
  gap: 10px;
  align-items:flex-end;
}
.composer-grid .left{
  flex: 1;
}
.composer-grid .right{
  width: 56px;
}

/* 输入框更像图2：单行/两行高 */
.composer textarea{
  border-radius: 14px !important;
  border: 1px solid rgba(15,23,42,.10) !important;
  background: #fff !important;
  padding: 10px 12px !important;
  min-height: 44px !important;
}
.composer textarea:focus{
  border: 1px solid rgba(79,70,229,.35) !important;
  box-shadow: 0 0 0 4px rgba(79,70,229,.12) !important;
  outline: none !important;
}

/* 发送按钮：圆角方块 + 纸飞机感 */
div[data-testid="stButton"] > button.send-btn{
  width: 56px !important;
  height: 44px !important;
  border-radius: 14px !important;
  border: 1px solid rgba(79,70,229,.22) !important;
  background: linear-gradient(135deg, rgba(79,70,229,.95), rgba(109,40,217,.95)) !important;
  box-shadow: 0 12px 28px rgba(79,70,229,.30) !important;
  color: white !important;
  font-weight: 900 !important;
}
div[data-testid="stButton"] > button.send-btn:hover{
  filter: brightness(1.02);
}

/* 隐藏一些 Streamlit 默认空白 */
label[for^="composer_"]{display:none;}
</style>
        """,
        unsafe_allow_html=True,
    )

inject_css()

# ============================================================
# 2) Key / Gemini 配置（Streamlit Cloud：Secrets）
# ============================================================
MEMORY_FILE = "b2b_kb_memory.json"

def get_api_key():
    try:
        if "GOOGLE_API_KEY" in st.secrets:
            return st.secrets["GOOGLE_API_KEY"]
        if "GEMINI_API_KEY" in st.secrets:
            return st.secrets["GEMINI_API_KEY"]
    except Exception:
        pass
    return None

api_key = get_api_key()
if not api_key:
    st.error("⚠️ 未检测到 API Key。请在 Streamlit Secrets 配置 GOOGLE_API_KEY（或 GEMINI_API_KEY）。")
    st.stop()

genai.configure(api_key=api_key)

@st.cache_resource
def get_best_model():
    return "models/gemini-2.5-flash"

MODEL_NAME = get_best_model()

# ============================================================
# 3) Memory / KB（粘贴 + PDF）
# ============================================================
def load_memory() -> str:
    if os.path.exists(MEMORY_FILE):
        try:
            with open(MEMORY_FILE, "r", encoding="utf-8") as f:
                return json.load(f).get("text", "")
        except Exception:
            return ""
    return ""

def save_memory(new_text: str) -> bool:
    current = load_memory()
    new_text = (new_text or "").strip()
    if not new_text:
        return False
    if new_text in current:
        return False
    updated = (current + "\n" + new_text).strip() if current else new_text
    with open(MEMORY_FILE, "w", encoding="utf-8") as f:
        json.dump({"text": updated}, f, ensure_ascii=False)
    return True

def clear_memory():
    if os.path.exists(MEMORY_FILE):
        os.remove(MEMORY_FILE)

def kb_injection_text() -> str:
    mem = load_memory()
    if len(mem) > 50:
        return f"[内部知识库数据]\n{mem}\n"
    return ""

# ============================================================
# 4) Google Search Tool（保留你的全球情报探挖能力）
# ============================================================
def robust_api_search(payload: dict, model_name: str, api_key_: str) -> dict:
    url = f"https://generativelanguage.googleapis.com/v1beta/{model_name}:generateContent?key={api_key_}"
    headers = {"Content-Type": "application/json"}
    for _ in range(3):
        try:
            res = requests.post(url, headers=headers, data=json.dumps(payload), timeout=60)
            if res.status_code == 200:
                return res.json()
            if res.status_code == 429:
                time.sleep(5)
                continue
            return {"error": f"错误码: {res.status_code}", "detail": res.text}
        except Exception as e:
            return {"error": str(e)}
    return {"error": "请求超时"}

def robust_generate(prompt: str) -> str:
    model = genai.GenerativeModel(MODEL_NAME)
    for i in range(5):
        try:
            resp = model.generate_content(prompt)
            return getattr(resp, "text", "") or "（模型无返回文本）"
        except Exception as e:
            if "429" in str(e):
                time.sleep((i + 1) * 5)
            else:
                time.sleep(2)
    return "⚠️ 网络繁忙，请稍后重试。"

# ============================================================
# 5) 模块定义（多模块 + 图2风格 Quick Start 文案）
# ============================================================
MODULES = [
    "综合助手",
    "订单复盘",
    "开发信生成",
    "客户背景调查",
    "谈判策略",
    "社媒内容引擎",
    "全球情报探挖",
    "智能技术支持",
]

MODULE_META = {
    "综合助手": {
        "icon": "🤖",
        "title": "综合助手",
        "sub": "AI 外贸销售助手 · 工业机械与零部件",
        "desc": "专为出单任务设计的 AI 模块。上传知识库文件以获得更精准的定制建议。",
        "placeholder": "输入客户信息、邮件内容或当前情况…",
        "quick": [
            ("如何制定 2025 年欧洲市场开发计划？", "如何制定2025年欧洲市场开发计划？请给我分阶段目标、渠道组合、预算、人效指标与周度动作清单。", "给出阶段拆解 + KPI + 动作"),
            ("帮我优化这段公司介绍…", "帮我优化这段公司介绍（中英双语）：\n\n<粘贴公司介绍>\n\n要求：更专业、更聚焦客户价值、含证据与CTA。", "中英双语 + 可直接用"),
            ("现在的海运费趋势如何影响 CIF 报价？", "现在的海运费趋势如何影响CIF报价？请给我报价策略、风险条款建议与对客户的话术。", "报价策略 + 风险控制"),
        ],
    },
    "订单复盘": {
        "icon": "🔎",
        "title": "订单复盘",
        "sub": "AI 外贸销售助手 · 工业机械与零部件",
        "desc": "粘贴交易结果或对话历史，输出更精准的复盘建议与纠偏方案。",
        "placeholder": "粘贴交易结果/对话历史，或描述你要复盘的问题…",
        "quick": [
            ("复盘这个失败的订单…", "复盘这个失败的订单：我将把交易记录/对话粘贴给你，请按时间线拆解关键失误、客户心理与改进策略。", "时间线 + 失误点 + 纠偏"),
            ("总结最近 5 个客户流失的原因", "请总结我最近5个客户流失的原因：按产品/价格/交付/信任/时机/跟进分类，并给动作清单。", "归因分类 + 动作清单"),
            ("如何提高我的询盘转化率？", "如何提高我的询盘转化率？请按漏斗（曝光-询盘-跟进-报价-成交）诊断并给可执行方案。", "漏斗诊断 + 可执行方案"),
        ],
    },
    "开发信生成": {
        "icon": "✉️",
        "title": "开发信生成",
        "sub": "AI 外贸销售助手 · 工业机械与零部件",
        "desc": "生成高回复率开发信：破冰、价值主张、证据与低摩擦 CTA。",
        "placeholder": "输入客户公司/职位/产品与诉求…",
        "quick": [
            ("写一封 LinkedIn 破冰私信", "请写一封LinkedIn破冰私信：客户行业=<填写> 角色=<填写> 我们产品=<填写>。要求：不超过80词，低摩擦CTA。", "短、轻、可复制"),
            ("写一封英文开发信（专业版）", "写一封英文开发信：客户公司=<填写> 产品=<填写> 我们优势=<填写>。结构：Icebreaker-Value-Evidence-CTA。", "结构化高转化"),
            ("写 3 封跟进邮件（节奏推进）", "请写3封英文跟进邮件：第1封温和提醒，第2封价值补充，第3封最后期限推进。", "跟进节奏模板"),
        ],
    },
    "客户背景调查": {
        "icon": "🕵️",
        "title": "客户背景调查",
        "sub": "AI 外贸销售助手 · 工业机械与零部件",
        "desc": "粘贴客户官网/About Us，输出可信度判断、风险点与验证清单。",
        "placeholder": "粘贴客户官网/介绍…",
        "quick": [
            ("判断客户可信度与风险等级", "请根据以下客户信息判断可信度与风险等级，并给出验证清单：\n\n<粘贴>", "风险分层 + 验证清单"),
            ("提炼客户痛点与采购动机", "请从以下客户介绍中提炼：核心业务、痛点、采购动机、决策指标，并给切入建议：\n\n<粘贴>", "画像 + 切入点"),
            ("生成客户画像卡（1页）", "请把以下客户信息整理成1页画像卡：行业/规模/地区/渠道/可能需求/潜在风险。\n\n<粘贴>", "一页总结卡"),
        ],
    },
    "谈判策略": {
        "icon": "🧠",
        "title": "谈判策略",
        "sub": "AI 外贸销售助手 · 工业机械与零部件",
        "desc": "针对压价、拖延、对比竞品等情景，输出打法与话术。",
        "placeholder": "输入客户异议/你的底线/目标…",
        "quick": [
            ("客户压价：你们太贵了", "客户说“你们太贵了”。请给动机拆解、反问问题、强/中/弱三套话术、让步边界。", "三档话术 + 边界"),
            ("客户拖延不回复怎么办", "客户已读不回/拖延。请给3封英文跟进邮件：温和提醒/价值补充/最后期限推进。", "跟进模板"),
            ("客户拿竞品报价压我", "客户拿竞品报价压我。请输出：价值框架、证据材料建议、可接受让步组合。", "差异化 + 组合让步"),
        ],
    },
    "社媒内容引擎": {
        "icon": "📣",
        "title": "社媒内容引擎",
        "sub": "AI 外贸销售助手 · 工业机械与零部件",
        "desc": "一键生成 LinkedIn / TikTok / Cold DM 内容，支持外贸获客。",
        "placeholder": "输入产品、受众、卖点与案例…",
        "quick": [
            ("生成 LinkedIn 专业贴", "请生成一条LinkedIn专业贴：Hook+痛点+方案+证据+CTA。产品=<填写> 客群=<填写>", "可直接发布"),
            ("生成短视频脚本（30-45秒）", "请生成30-45秒短视频脚本：3秒Hook+3要点+结尾CTA。产品=<填写> 场景=<填写>", "分镜+字幕建议"),
            ("生成 Cold DM 私信（3段式）", "请生成Cold DM私信：破冰+价值点+轻量CTA，不超过120词。客户=<填写>", "低推销感"),
        ],
    },
    "全球情报探挖": {
        "icon": "🌍",
        "title": "全球情报探挖",
        "sub": "AI 外贸销售助手 · 工业机械与零部件",
        "desc": "实时连接搜索：输出公司/竞品/新闻/切入点（调用 Google Search Tool）。",
        "placeholder": "输入公司名/网址/关键词…",
        "quick": [
            ("调研目标公司画像", "调研目标公司：<公司名/网站>。输出：业务简介、产品线、采购线索、近期动态、切入点。", "公司画像+切入点"),
            ("竞品对比表", "列出<产品/行业>主要竞品并给对比表（价格/交付/认证/卖点/渠道）。", "对比表"),
            ("生成英文破冰切入点", "基于目标公司近期动态生成3条英文破冰切入点（每条<=2句）。公司：<公司名/网站>", "高相关破冰"),
        ],
    },
    "智能技术支持": {
        "icon": "🛠️",
        "title": "智能技术支持",
        "sub": "AI 外贸销售助手 · 工业机械与零部件",
        "desc": "基于你的知识库回答产品与售后问题（建议先上传 PDF/资料）。",
        "placeholder": "输入客户技术问题…",
        "quick": [
            ("把问题转成排查清单", "请把以下客户技术问题转成排查清单（按优先级），并给需要客户补充的信息：\n\n<粘贴>", "排查清单"),
            ("生成英文技术回复邮件", "请把以下技术问题生成英文邮件：原因+排查步骤+下一步动作：\n\n<粘贴>", "可直接发客户"),
            ("沉淀成 FAQ 条目", "请把以下问题沉淀成FAQ：问题/原因/解决方案/注意事项/建议图示。\n\n<粘贴>", "可入库FAQ"),
        ],
    },
}

# ============================================================
# 6) Session：多模块隔离 + 新对话
# ============================================================
if "active_module" not in st.session_state:
    st.session_state.active_module = "综合助手"

if "chat" not in st.session_state:
    st.session_state.chat = {m: [] for m in MODULES}

if "composer" not in st.session_state:
    st.session_state.composer = ""

def esc(s: str) -> str:
    return (s or "").replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")

def push(module: str, role: str, content: str):
    st.session_state.chat[module].append(
        {"role": role, "content": content, "ts": time.strftime("%H:%M")}
    )

def clear_current_chat():
    mod = st.session_state.active_module
    st.session_state.chat[mod] = []
    st.session_state.composer = ""
    st.rerun()

# ============================================================
# 7) Prompt：按模块系统提示 + KB 注入
# ============================================================
def system_prompt_for(module: str) -> str:
    if module == "订单复盘":
        return "你是B2B外贸订单复盘专家。输出：时间线→关键失误→客户心理/流程推断→SOP→下一步动作清单。"
    if module == "开发信生成":
        return "你是B2B外贸开发信专家。输出邮件要专业克制、有证据、有低摩擦CTA；先破冰再价值再证据再CTA。"
    if module == "客户背景调查":
        return "你是客户背调分析师。输出：可信度判断、风险点、验证清单、沟通策略与切入点。"
    if module == "谈判策略":
        return "你是B2B外贸谈判军师。输出：动机拆解、反问问题、强/中/弱话术、让步边界、下一步推进。"
    if module == "社媒内容引擎":
        return "你是B2B外贸增长内容专家。输出内容可直接发布：Hook清晰、价值具体、证据充分、CTA明确。"
    if module == "全球情报探挖":
        return "你是外贸情报分析师。输出：公司画像、竞品、新闻、采购线索、切入点。"
    if module == "智能技术支持":
        return "你是B2B产品技术支持工程师。输出：排查步骤、需要补充信息、可发客户的回复稿。"
    return "你是B2B外贸销售综合助手。输出要结构化，最后给可执行下一步。"

def build_prompt(module: str, user_text: str) -> str:
    kb = kb_injection_text()
    sys = system_prompt_for(module)
    return f"{kb}{sys}\n\n[模块：{module}]\n用户输入：{user_text}"

# ============================================================
# 8) 模块调用：情报探挖用 Google Search Tool，其余走 generate
# ============================================================
def run_module(module: str, user_text: str) -> str:
    if module == "全球情报探挖":
        q = user_text.strip()
        prompt = f"Role: Analyst. Search: '{q}'. Report: Identity, News, Competitors, Hooks."
        payload = {
            "contents": [{"parts": [{"text": prompt}]}],
            "tools": [{"google_search": {}}],
        }
        data = robust_api_search(payload, MODEL_NAME, api_key)
        if "error" in data:
            return f"⚠️ 搜索失败：{data.get('error')}"
        try:
            return data["candidates"][0]["content"]["parts"][0]["text"]
        except Exception:
            return "⚠️ 解析失败：未获得有效搜索结果。"

    prompt = build_prompt(module, user_text)
    return robust_generate(prompt)

def send_text(text: str):
    mod = st.session_state.active_module
    text = (text or "").strip()
    if not text:
        return
    push(mod, "user", text)
    with st.spinner("思考中..."):
        ans = run_module(mod, text)
    push(mod, "assistant", ans)
    st.session_state.composer = ""
    st.rerun()

# ============================================================
# 9) Sidebar：严格贴近图2的模块导航 + 底部知识库按钮
# ============================================================
with st.sidebar:
    st.markdown(
        """
<div class="sidebar-brand">
  <div class="sidebar-logo">T</div>
  <div>
    <div class="sidebar-title">TradeNexus AI</div>
    <div class="sidebar-sub">B2B 外贸销售专家</div>
  </div>
</div>
        """,
        unsafe_allow_html=True,
    )

    selected = option_menu(
        None,
        MODULES,
        icons=["grid", "search", "envelope", "person-badge", "chat-dots", "megaphone", "globe", "tools"],
        menu_icon="cast",
        default_index=MODULES.index(st.session_state.active_module),
        styles={
            "container": {"padding": "0!important", "background-color": "rgba(0,0,0,0)"},
            "icon": {"color": "rgba(255,255,255,.75)", "font-size": "16px"},
            "nav-link": {
                "font-size": "13px",
                "text-align": "left",
                "margin": "6px 10px",
                "color": "rgba(255,255,255,.82)",
                "border-radius": "14px",
                "padding": "10px 12px",
            },
            "nav-link-selected": {
                "background": "linear-gradient(90deg, rgba(79,70,229,.95), rgba(109,40,217,.95))",
                "color": "white",
                "box-shadow": "0 12px 28px rgba(79,70,229,.30)",
            },
        },
    )
    st.session_state.active_module = selected

    st.markdown("<div class='sidebar-footer-btn'>📚 <b>知识库配置</b><br/><span style='color:rgba(255,255,255,.55);font-size:12px;'>上传 PDF / 粘贴资料</span></div>", unsafe_allow_html=True)

    with st.expander("知识库配置（上传/粘贴）", expanded=False):
        mem = load_memory()
        if len(mem) > 50:
            st.success(f"✅ 已加载知识库（约 {len(mem)} 字符）")
        else:
            st.info("当前知识库为空：建议上传 PDF 或粘贴资料。")

        txt = st.text_area("粘贴文本资料：", height=110, placeholder="产品参数、FAQ、交期、质检标准、报价规则…")
        c1, c2 = st.columns(2)
        with c1:
            if st.button("保存到知识库", use_container_width=True):
                if save_memory(txt):
                    st.success("已保存")
                    time.sleep(0.5)
                    st.rerun()
                else:
                    st.warning("内容为空或已存在")
        with c2:
            if st.button("清空知识库", use_container_width=True):
                clear_memory()
                st.success("已清空")
                time.sleep(0.5)
                st.rerun()

        st.write("---")
        up = st.file_uploader("上传 PDF（提取文字写入知识库）", type=["pdf"])
        if up:
            try:
                reader = PdfReader(up)
                content = "\n".join([(p.extract_text() or "") for p in reader.pages])
                if len(content.strip()) > 50:
                    save_memory(content.strip())
                    st.success("PDF 已写入知识库")
                    time.sleep(0.5)
                    st.rerun()
                else:
                    st.error("PDF 无可提取文本（可能是扫描版）")
            except Exception:
                st.error("PDF 读取失败")

# ============================================================
# 10) 主区：严格贴近图2布局
# ============================================================
mod = st.session_state.active_module
meta = MODULE_META[mod]

# 顶部栏（标题/副标题 + 新对话）
st.markdown(
    f"""
<div class="main-header">
  <div class="mh-left">
    <div class="mh-title">{esc(meta["title"])}</div>
    <div class="mh-sub">{esc(meta["sub"])}</div>
  </div>
  <div class="mh-right">
    <div style="font-size:12px;color:var(--muted);display:flex;align-items:center;gap:8px;">
      <span style="color:#16a34a;font-weight:900;">●</span> Ready
    </div>
  </div>
</div>
    """,
    unsafe_allow_html=True,
)

# 用真正按钮实现“新对话”（放在 header 下方右侧，交互对齐）
r1, r2, r3 = st.columns([6, 1.2, 1.2])
with r3:
    if st.button("新对话", key="new_chat_btn"):
        clear_current_chat()

# Hero（空状态）
st.markdown(
    f"""
<div class="hero">
  <div class="hero-icon">{esc(meta["icon"])}</div>
  <h1 class="hero-title">{esc(meta["title"])}</h1>
  <div class="hero-desc">{esc(meta["desc"])}</div>
</div>
    """,
    unsafe_allow_html=True,
)

# Chat（如果已有消息就显示在 hero 下方）
messages = st.session_state.chat.get(mod, [])
if messages:
    st.markdown('<div class="chat-area">', unsafe_allow_html=True)
    st.markdown('<div class="chat-scroll">', unsafe_allow_html=True)
    for m in messages:
        role = m.get("role", "assistant")
        ts = m.get("ts", "")
        label = "你" if role == "user" else "TradeNexus AI"
        st.markdown(
            f"""
<div class="msg-row {role}">
  <div class="bubble {role}">
    <div class="bmeta">{esc(label)} · {esc(ts)}</div>
    <div class="bcontent">{esc(m.get("content",""))}</div>
  </div>
</div>
            """,
            unsafe_allow_html=True,
        )
    st.markdown("</div></div>", unsafe_allow_html=True)

# Quick Start（严格为“列表卡片”）
st.markdown(
    """
<div class="qs-panel">
  <div class="qs-title">快速开始</div>
</div>
    """,
    unsafe_allow_html=True,
)

# 用三条 “整行卡片” button
qs = meta["quick"]

# 通过给 st.button 注入 class 来实现 card 外观
def qs_button(label_main, label_sub, idx):
    # Streamlit button 无法直接传 class，这里用组件后处理：用 key 定位 + CSS 选择器
    # 做法：先渲染 button，再用 JS 不稳定；因此我们用 Streamlit 现成机制：
    # 让按钮文本包含结构，再用 CSS 把按钮整体按 card 样式呈现（button 元素加 class 需要 st.markdown hack）
    pass

# 用“自定义HTML + st.button”的安全可控方案：
# 每行：一个 st.button（触发），旁边显示说明文字（样式像列表卡）
for i, (main, payload, sub) in enumerate(qs, start=1):
    # 渲染卡片外观（HTML），按钮覆盖在其上（透明），点击触发
    st.markdown(
        f"""
<div style="position:relative;">
  <div style="border:1px solid rgba(15,23,42,.10);background:#fff;border-radius:14px;padding:12px;box-shadow:0 8px 18px rgba(15,23,42,.04);margin:6px 0;"
       onmouseover="this.style.background='rgba(79,70,229,.06)'; this.style.borderColor='rgba(79,70,229,.25)';"
       onmouseout="this.style.background='#fff'; this.style.borderColor='rgba(15,23,42,.10)';">
    <div class="qs-row">
      <div class="qs-badge">{i}</div>
      <div class="qs-text">
        <div class="qs-main">{esc(main)}</div>
        <div class="qs-sub">{esc(sub)}</div>
      </div>
    </div>
  </div>
</div>
        """,
        unsafe_allow_html=True,
    )
    # 真实点击触发：用隐藏按钮（全宽）放在下面，CSS让它“贴近卡片区域”
    clicked = st.button(
        f"__qs_{mod}_{i}",
        key=f"qs_{mod}_{i}",
        use_container_width=True,
    )
    # 把这个按钮在视觉上压缩为 0 高（但保留可点击性），避免破坏布局
    st.markdown(
        """
<style>
/* 把刚才那个按钮变成“覆盖卡片的透明层” */
div[data-testid="stButton"] > button:has(span:contains("__qs_")){ display:none !important; }
</style>
        """,
        unsafe_allow_html=True,
    )
    if clicked:
        send_text(payload)

# ============================================================
# 11) 底部输入栏：固定，像图2
# ============================================================
st.markdown('<div class="composer"><div class="composer-inner"><div class="composer-box">', unsafe_allow_html=True)
st.markdown('<div class="composer-grid">', unsafe_allow_html=True)

left, right = st.columns([10, 1.4], vertical_alignment="bottom")
with left:
    st.session_state.composer = st.text_area(
        " ",
        value=st.session_state.composer,
        height=60,
        placeholder=meta["placeholder"],
        key=f"composer_{mod}",
    )
with right:
    send = st.button("➤", key=f"send_{mod}", use_container_width=True)
    # 给发送按钮加 class（通过 data-testid + key 很难精确，采用整体样式已接近）
    st.markdown(
        """
<script>
</script>
        """,
        unsafe_allow_html=True,
    )

if send:
    send_text(st.session_state.composer)

st.markdown("</div></div></div></div>", unsafe_allow_html=True)
