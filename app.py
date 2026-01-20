import os
import json
import time
import requests
import streamlit as st
import google.generativeai as genai
from pypdf import PdfReader
from streamlit_option_menu import option_menu

# ============================================================
# 1) 页面配置
# ============================================================
st.set_page_config(
    page_title="TradeNexus AI - B2B 外贸销售专家",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ============================================================
# 2) 全局 CSS（AI Studio 风格：深侧栏 + 浅主区 + sticky composer）
# ============================================================
def inject_ai_studio_css():
    st.markdown(
        """
<style>
:root{
  --bg: #f6f7fb;
  --panel: #ffffff;
  --panel-2: #fbfbfe;
  --text: #0b1220;
  --muted: #5b6475;
  --border: rgba(16, 24, 40, .10);
  --shadow: 0 10px 30px rgba(16, 24, 40, .08);

  --nav-bg: #0f172a;
  --nav-bg-2: #111c33;
  --nav-text: rgba(255,255,255,.86);
  --nav-muted: rgba(255,255,255,.55);
  --nav-border: rgba(255,255,255,.10);

  --primary: #4f46e5;
  --primary-2: #6d28d9;
  --success: #16a34a;
  --warn: #f59e0b;

  --bubble-user: #eef2ff;
  --bubble-assistant: #ffffff;

  --radius-lg: 18px;
}

html, body, [class*="css"]{
  font-family: ui-sans-serif, system-ui, -apple-system, Segoe UI, Roboto, Helvetica, Arial, "Apple Color Emoji","Segoe UI Emoji";
}
.stApp { background: var(--bg); }

header {visibility: hidden;}
.block-container{
  padding-top: 0.75rem;
  padding-bottom: 6.5rem; /* 给 sticky composer 留空间 */
  max-width: 1200px;
}

section[data-testid="stSidebar"]{
  background: linear-gradient(180deg, var(--nav-bg) 0%, var(--nav-bg-2) 100%);
  border-right: 1px solid var(--nav-border);
}
section[data-testid="stSidebar"] .stMarkdown,
section[data-testid="stSidebar"] label,
section[data-testid="stSidebar"] span,
section[data-testid="stSidebar"] div{
  color: var(--nav-text) !important;
}
section[data-testid="stSidebar"] .stTextInput input,
section[data-testid="stSidebar"] .stTextArea textarea,
section[data-testid="stSidebar"] .stSelectbox div[data-baseweb="select"]{
  background: rgba(255,255,255,.08) !important;
  border: 1px solid rgba(255,255,255,.12) !important;
  color: var(--nav-text) !important;
  border-radius: 12px !important;
}
section[data-testid="stSidebar"] hr{ border-color: var(--nav-border); }

.sidebar-brand{
  display:flex; align-items:center; gap:10px;
  padding: 16px 10px 8px 10px;
}
.sidebar-brand .logo{
  width: 36px; height: 36px; border-radius: 12px;
  background: radial-gradient(circle at 30% 30%, rgba(99,102,241,.9), rgba(109,40,217,.9));
  display:flex; align-items:center; justify-content:center;
  color:white; font-weight:800;
  box-shadow: 0 10px 25px rgba(79,70,229,.35);
}
.sidebar-brand .title{ font-weight: 800; letter-spacing: .2px; }
.sidebar-brand .subtitle{
  font-size: 12px;
  color: var(--nav-muted);
  margin-top: -2px;
}
.sidebar-status{
  margin: 10px 10px 12px 10px;
  padding: 10px 12px;
  border: 1px solid rgba(255,255,255,.12);
  border-radius: 14px;
  background: rgba(255,255,255,.06);
}
.badge{
  display:inline-flex; align-items:center; gap:6px;
  padding: 3px 10px;
  border-radius: 999px;
  border: 1px solid rgba(255,255,255,.16);
  font-size: 12px;
  color: rgba(255,255,255,.78);
}
.dot{
  width:8px; height:8px; border-radius:999px;
  background: #22c55e;
  box-shadow: 0 0 0 3px rgba(34,197,94,.20);
}

.ai-header{
  position: sticky;
  top: 0;
  z-index: 50;
  background: rgba(246,247,251,.85);
  backdrop-filter: blur(10px);
  border-bottom: 1px solid var(--border);
}
.ai-header-inner{
  max-width: 1200px;
  margin: 0 auto;
  padding: 14px 10px;
  display:flex;
  align-items:center;
  justify-content:space-between;
  gap: 10px;
}
.h-left{ display:flex; align-items:center; gap: 12px; }
.h-appmark{
  width: 34px; height: 34px; border-radius: 12px;
  background: #ffffff;
  border: 1px solid var(--border);
  display:flex; align-items:center; justify-content:center;
  box-shadow: 0 8px 22px rgba(16,24,40,.06);
}
.h-title{ font-size: 15px; font-weight: 800; color: var(--text); line-height: 1.1; }
.h-sub{ font-size: 12px; color: var(--muted); margin-top: 1px; }
.h-right{ display:flex; align-items:center; gap: 8px; }
.h-chip{
  display:inline-flex; align-items:center; gap: 8px;
  padding: 7px 10px;
  border-radius: 999px;
  background: #ffffff;
  border: 1px solid var(--border);
  box-shadow: 0 8px 22px rgba(16,24,40,.06);
  font-size: 12px;
  color: var(--muted);
}
.h-iconbtn{
  width: 34px; height: 34px;
  border-radius: 12px;
  background: #ffffff;
  border: 1px solid var(--border);
  display:flex; align-items:center; justify-content:center;
  box-shadow: 0 8px 22px rgba(16,24,40,.06);
  cursor: default;
}

.panel{
  background: var(--panel);
  border: 1px solid var(--border);
  border-radius: var(--radius-lg);
  box-shadow: var(--shadow);
}
.panel-pad{ padding: 18px 18px; }

.hero{
  text-align:center;
  padding: 34px 18px 18px 18px;
}
.hero .hero-icon{
  width: 58px; height: 58px; border-radius: 18px;
  background: linear-gradient(180deg, rgba(79,70,229,.12), rgba(109,40,217,.08));
  border: 1px solid rgba(79,70,229,.18);
  display:flex; align-items:center; justify-content:center;
  margin: 0 auto 12px auto;
  color: var(--primary);
  font-size: 26px;
}
.hero h2{ margin: 0; font-size: 22px; color: var(--text); font-weight: 900; }
.hero p{ margin: 8px 0 0 0; color: var(--muted); font-size: 13px; }

.quick-title{
  margin: 0 0 10px 0;
  font-weight: 800;
  color: var(--text);
  font-size: 13px;
}
.quick-hint{ color: var(--muted); font-size: 12px; margin-top: -6px; margin-bottom: 10px; }

.chat-wrap{ display:flex; flex-direction:column; gap: 10px; }
.msg-row{ display:flex; }
.msg-row.user { justify-content: flex-end; }
.msg-row.assistant { justify-content: flex-start; }

.bubble{
  max-width: 78%;
  border-radius: 18px;
  border: 1px solid var(--border);
  padding: 12px 14px;
  box-shadow: 0 8px 22px rgba(16,24,40,.04);
}
.bubble.user{ background: var(--bubble-user); }
.bubble.assistant{ background: var(--bubble-assistant); }
.bubble .meta{ font-size: 11px; color: var(--muted); margin-bottom: 6px; }
.bubble .content{
  color: var(--text);
  font-size: 13.5px;
  line-height: 1.55;
  white-space: pre-wrap;
}

.composer{
  position: fixed;
  left: 0;
  right: 0;
  bottom: 0;
  z-index: 60;
  background: rgba(246,247,251,.86);
  backdrop-filter: blur(12px);
  border-top: 1px solid var(--border);
}
.composer-inner{
  max-width: 1200px;
  margin: 0 auto;
  padding: 12px 10px 14px 10px;
}
.composer-note{
  font-size: 12px;
  color: var(--muted);
  margin-top: 8px;
  text-align: center;
}

.composer-inner textarea{
  border-radius: 16px !important;
  border: 1px solid var(--border) !important;
  background: #ffffff !important;
  color: var(--text) !important;
  padding: 10px 12px !important;
  min-height: 46px !important;
}
.composer-inner textarea:focus{
  outline: none !important;
  border: 1px solid rgba(79,70,229,.45) !important;
  box-shadow: 0 0 0 4px rgba(79,70,229,.12) !important;
}
.composer-inner button[kind="primary"]{
  border-radius: 16px !important;
  height: 46px !important;
  padding: 0 16px !important;
  font-weight: 800 !important;
  border: 1px solid rgba(79,70,229,.25) !important;
  background: linear-gradient(90deg, rgba(79,70,229,.95), rgba(109,40,217,.95)) !important;
  box-shadow: 0 10px 25px rgba(79,70,229,.25) !important;
}
.composer-inner button[kind="secondary"]{
  border-radius: 16px !important;
  height: 46px !important;
}
.composer-inner [data-testid="stVerticalBlock"]{ gap: 0.35rem; }
</style>
        """,
        unsafe_allow_html=True,
    )

inject_ai_studio_css()

# ============================================================
# 3) API Key 配置（与你原来一致）
# ============================================================
MEMORY_FILE = "b2b_kb_memory.json"

try:
    api_key = st.secrets["GOOGLE_API_KEY"]
    genai.configure(api_key=api_key)
except Exception:
    st.error("⚠️ 系统错误：GOOGLE_API_KEY 未配置（请检查 Streamlit Secrets）")
    st.stop()

# ============================================================
# 4) Memory / KB：读取、保存、清空（与你原来一致风格）
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
    if new_text.strip() and new_text.strip() in current:
        return False
    updated = (current + "\n" + new_text).strip() if current else new_text.strip()
    with open(MEMORY_FILE, "w", encoding="utf-8") as f:
        json.dump({"text": updated}, f, ensure_ascii=False)
    return True

def clear_memory():
    if os.path.exists(MEMORY_FILE):
        os.remove(MEMORY_FILE)

@st.cache_resource
def get_best_model():
    # 你截图里是返回 "models/gemini-2.5-flash"
    return "models/gemini-2.5-flash"

valid_model_name = get_best_model()

def robust_generate(prompt: str, model_name: str) -> str:
    model = genai.GenerativeModel(model_name)
    max_retries = 5
    for i in range(max_retries):
        try:
            resp = model.generate_content(prompt)
            return getattr(resp, "text", "") or "（模型无返回文本）"
        except Exception as e:
            # 429 等限流
            if "429" in str(e):
                time.sleep((i + 1) * 5)
                continue
            time.sleep(2)
            continue
    return "⚠️ 网络繁忙，请稍后重试。"

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

# ============================================================
# 5) 模块定义（多模块 + 每模块 Quick Start）
# ============================================================
ALL_MODULES = [
    "总控仪表盘",
    "订单复盘",
    "全球社媒营销",
    "深度询盘分析",
    "全球情报探挖",
    "客户背景调查",
    "谈判策略军师",
    "智能技术支持",
]

MODULE_META = {
    "总控仪表盘": {
        "icon": "📊",
        "title": "指挥官总控台",
        "desc": "聚合核心模块入口与关键指标，快速进入高频工作流。",
        "composer_ph": "描述你想看的指标、问题或要优化的流程…",
        "quick": [
            ("查看本周关键 KPI", "请给我本周外贸销售关键KPI看板：询盘数、有效询盘、报价数、跟进中、赢单、输单，并给出异常点提示。"),
            ("生成本周执行优先级", "基于外贸销售流程，为我生成本周执行优先级（80/20），并给出每日重点动作清单。"),
            ("沉淀我的 SOP 目录", "请帮我整理一套外贸销售SOP目录结构：获客-询盘-跟进-报价-谈判-成交-复购，并给出每部分需要沉淀的模板。"),
        ],
    },
    "订单复盘": {
        "icon": "🔎",
        "title": "订单复盘",
        "desc": "粘贴交易结果或对话历史，输出更精准的复盘与纠偏建议。",
        "composer_ph": "粘贴交易结果/对话历史，或描述你要复盘的问题…",
        "quick": [
            ("复盘这个失败的订单", "复盘这个失败的订单：我将把交易记录/对话粘贴给你，请按时间线拆解问题并给出改进策略。"),
            ("总结最近 5 个客户流失原因", "请总结我最近 5 个客户流失的原因：给出归因分类（产品/价格/交付/信任/时机/跟进）+ 我应该立刻做的动作清单。"),
            ("提升询盘转化率", "如何提高我的询盘转化率？请基于漏斗（曝光-询盘-跟进-报价-成交）给我诊断框架和可执行改进方案。"),
        ],
    },
    "全球社媒营销": {
        "icon": "📣",
        "title": "全球社媒营销",
        "desc": "一键生成 LinkedIn / TikTok / Cold DM 多平台内容，服务 B2B 外贸获客。",
        "composer_ph": "输入产品与受众，例如：solar panel / industrial buyer / EU…",
        "quick": [
            ("生成 LinkedIn 专业贴", "请为我的B2B产品生成一条LinkedIn专业贴：包含Hook、痛点、解决方案、证据、CTA。产品：<填写> 目标客户：<填写>"),
            ("生成 TikTok 短视频脚本", "请生成一条30-45秒TikTok短视频脚本：开头3秒强Hook，中段3个要点，结尾CTA。产品：<填写> 场景：<填写>"),
            ("生成 Cold DM 私信三段式", "请生成Cold DM三段式私信：破冰+价值点+轻量CTA。目标客户：<填写> 行业：<填写> 产品：<填写>"),
        ],
    },
    "深度询盘分析": {
        "icon": "✉️",
        "title": "深度询盘分析",
        "desc": "粘贴客户邮件/询盘内容，输出客户画像、意图评分、追问清单与回复草稿。",
        "composer_ph": "粘贴客户询盘/邮件内容…",
        "quick": [
            ("评估询盘质量与意图", "请对以下询盘做意图评分(0-10)并给出理由、风险点、下一步追问问题：\n\n<粘贴询盘>"),
            ("生成高转化回复邮件", "请基于以下询盘生成一封高转化英文回复：先确认需求，再给2-3个澄清问题，最后给明确下一步CTA：\n\n<粘贴询盘>"),
            ("推断决策链与竞品", "请根据以下询盘推断客户决策链角色、采购流程、可能对比的竞品方向，并给出应对策略：\n\n<粘贴询盘>"),
        ],
    },
    "全球情报探挖": {
        "icon": "🌍",
        "title": "全球情报探挖",
        "desc": "实时连接搜索，汇总目标公司/竞品/新闻与切入点（使用 Google Search Tool）。",
        "composer_ph": "输入公司名/网站/关键词，例如：ABB motor distributor Germany…",
        "quick": [
            ("调研目标公司画像", "调研目标公司：<公司名/网站>。输出：业务简介、产品线、采购线索、近期动态、合作切入点。"),
            ("竞品对比表", "列出<产品/行业>的主要竞品，并给出差异化对比表（价格/交付/认证/渠道/卖点）。"),
            ("生成破冰切入话术", "基于目标公司近期动态，生成3条英文破冰切入点（每条不超过2句话）。公司：<公司名/网站>"),
        ],
    },
    "客户背景调查": {
        "icon": "🕵️",
        "title": "客户背景调查",
        "desc": "分析客户官网/介绍，输出可信度判断、风险点与沟通策略。",
        "composer_ph": "粘贴客户 About Us / 官网介绍…",
        "quick": [
            ("判断客户可信度", "请根据以下客户信息判断可信度与风险等级，并给出验证清单：\n\n<粘贴官网/介绍>"),
            ("提炼采购动机与痛点", "请从以下客户介绍中提炼：核心业务、痛点、采购动机、关键决策指标，并给出切入建议：\n\n<粘贴>"),
            ("生成客户画像卡", "请把以下客户信息整理成1页客户画像卡：行业/规模/地区/产品/渠道/可能需求/潜在风险：\n\n<粘贴>"),
        ],
    },
    "谈判策略军师": {
        "icon": "🧠",
        "title": "谈判策略军师",
        "desc": "针对压价、拖延、对比竞品等情景，输出可执行谈判打法与话术。",
        "composer_ph": "描述客户当前的异议/话术/你想达成的目标…",
        "quick": [
            ("应对客户压价", "客户说：'你们太贵了'。请给：动机拆解、反问问题、3套应对话术（强/中/弱），以及让步边界建议。"),
            ("应对拖延不回复", "客户已读不回/拖延。请给3封英文跟进邮件模板：温和提醒/价值补充/最后期限推进。"),
            ("对比竞品报价", "客户拿竞品报价来压我。请输出：差异化价值框架、证据材料建议、可接受让步组合方案。"),
        ],
    },
    "智能技术支持": {
        "icon": "🛠️",
        "title": "智能技术支持",
        "desc": "基于你的知识库/资料回答产品与售后技术问题（建议先上传 PDF / 粘贴资料）。",
        "composer_ph": "输入客户技术问题或售后场景…",
        "quick": [
            ("转成排查清单", "请把以下客户技术问题转成排查清单（按优先级），并给出需要客户补充的信息：\n\n<粘贴问题>"),
            ("生成英文技术回复", "请把以下技术问题生成一封英文技术支持邮件：解释原因+排查步骤+下一步动作：\n\n<粘贴问题>"),
            ("沉淀成FAQ条目", "请把以下问题沉淀成FAQ：问题/原因/解决方案/注意事项/建议图示：\n\n<粘贴问题>"),
        ],
    },
}

# ============================================================
# 6) Session state：每模块对话隔离
# ============================================================
if "active_module" not in st.session_state:
    st.session_state.active_module = "订单复盘"
if "chat_messages" not in st.session_state:
    st.session_state.chat_messages = {m: [] for m in ALL_MODULES}
if "composer_text" not in st.session_state:
    st.session_state.composer_text = ""
if "social_platform" not in st.session_state:
    st.session_state.social_platform = "LinkedIn（专业贴）"

# ============================================================
# 7) 知识库注入（与你原来思路一致：从 memory 文件拼接）
# ============================================================
current_mem = load_memory()
mem_len = len(current_mem or "")
KB_INJECTION = f"[内部知识库数据]\n{current_mem}\n" if mem_len > 50 else ""

# ============================================================
# 8) 统一：Prompt 组装 + 模型调用（按模块分流）
# ============================================================
def build_prompt(module_name: str, user_text: str) -> str:
    base = ""
    # 你可以把“系统规则/输出结构”固化在这里（更像 AI Studio 的 system 指令）
    if module_name == "订单复盘":
        base = (
            "你是B2B外贸销售订单复盘专家。"
            "请按：1)时间线 2)关键失误 3)客户心理/采购流程推断 4)可复用SOP 5)下一步动作清单 输出。"
        )
    elif module_name == "深度询盘分析":
        base = (
            "你是B2B外贸询盘分析专家。"
            "请输出：意图评分(0-10)+理由、客户画像、风险点、追问问题清单、回复邮件草稿（中英可选）。"
        )
    elif module_name == "谈判策略军师":
        base = (
            "你是B2B外贸谈判军师。"
            "请输出：对方动机拆解、反问问题、话术（强/中/弱）、让步边界、推进成交的下一步。"
        )
    elif module_name == "全球社媒营销":
        base = (
            "你是B2B外贸增长内容专家。输出内容要可直接发布，避免空话，强调证据、场景、CTA。"
        )
    elif module_name == "客户背景调查":
        base = (
            "你是客户背调分析师。请输出：可信度判断、风险点、验证清单、沟通策略与切入点。"
        )
    elif module_name == "智能技术支持":
        base = (
            "你是B2B产品技术支持工程师。请给出排查步骤、所需补充信息、可发给客户的回复稿。"
        )
    elif module_name == "总控仪表盘":
        base = "你是B2B外贸销售运营负责人。请用结构化方式给KPI/优先级/行动清单。"
    else:
        base = "请结构化回答，并给出可执行的下一步动作。"

    # 注入知识库（如果有）
    prompt = ""
    if KB_INJECTION:
        prompt += KB_INJECTION + "\n"
    prompt += f"{base}\n\n[模块：{module_name}]\n用户输入：{user_text}"
    return prompt

def call_module(module_name: str, user_text: str) -> str:
    """
    按模块分流：
    - 全球情报探挖：走 Google Search Tool（与你原 app.py 一致逻辑）
    - 全球社媒营销：附带平台规则
    - 其他：robust_generate
    """
    if module_name == "全球情报探挖":
        query = user_text.strip()
        prompt = f"Role: Analyst. Search: '{query}'. Report: Identity, News, Competitors, Hook."
        payload = {
            "contents": [{"parts": [{"text": prompt}]}],
            "tools": [{"google_search": {}}],
        }
        data = robust_api_search(payload, valid_model_name, api_key)
        if "error" in data:
            return f"⚠️ 搜索失败：{data.get('error')}"
        try:
            return data["candidates"][0]["content"]["parts"][0]["text"]
        except Exception:
            return "⚠️ 解析失败：未获得有效搜索结果。"

    if module_name == "全球社媒营销":
        platform = st.session_state.get("social_platform", "LinkedIn（专业贴）")
        rules = ""
        if "LinkedIn" in platform:
            rules = "规则：LinkedIn专业贴结构=Hook(1-2句)+痛点+解决方案+证据/案例+CTA；语气专业克制；可加项目符号。"
        elif "TikTok" in platform:
            rules = "规则：短视频脚本=3秒Hook+场景+3个要点+结尾CTA；口语化；句子短；可加分镜/字幕建议。"
        else:
            rules = "规则：Cold DM=破冰(个性化)+价值主张(一句)+低摩擦CTA(一个问题)；避免推销感；不超过120词。"
        prompt = build_prompt(module_name, f"平台：{platform}\n{rules}\n\n主题/输入：{user_text}")
        return robust_generate(prompt, valid_model_name)

    # 其他模块
    prompt = build_prompt(module_name, user_text)
    return robust_generate(prompt, valid_model_name)

# ============================================================
# 9) UI 组件：顶部栏、聊天、Quick Start、发送逻辑、sticky composer
# ============================================================
def esc(s: str) -> str:
    return (s or "").replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")

def render_top_header(module_name: str):
    meta = MODULE_META[module_name]
    st.markdown(
        f"""
<div class="ai-header">
  <div class="ai-header-inner">
    <div class="h-left">
      <div class="h-appmark">{meta["icon"]}</div>
      <div>
        <div class="h-title">{esc(meta["title"])}</div>
        <div class="h-sub">TradeNexus AI · B2B 外贸销售工作台</div>
      </div>
    </div>
    <div class="h-right">
      <div class="h-chip"><span style="color:#16a34a;font-weight:900;">●</span> Ready</div>
      <div class="h-iconbtn" title="Settings">⚙️</div>
      <div class="h-iconbtn" title="Help">?</div>
    </div>
  </div>
</div>
        """,
        unsafe_allow_html=True,
    )

def push_message(module_name: str, role: str, content: str):
    st.session_state.chat_messages[module_name].append(
        {"role": role, "content": content, "ts": time.strftime("%H:%M")}
    )

def handle_send(module_name: str, text: str):
    text = (text or "").strip()
    if not text:
        return
    push_message(module_name, "user", text)

    with st.spinner("思考中..."):
        ans = call_module(module_name, text)

    push_message(module_name, "assistant", ans)
    st.session_state.composer_text = ""
    st.rerun()

def render_chat(module_name: str):
    meta = MODULE_META[module_name]
    messages = st.session_state.chat_messages.get(module_name, [])

    st.markdown('<div class="panel panel-pad">', unsafe_allow_html=True)
    st.markdown('<div class="chat-wrap">', unsafe_allow_html=True)

    if len(messages) == 0:
        st.markdown(
            f"""
<div class="hero">
  <div class="hero-icon">{meta["icon"]}</div>
  <h2>{esc(meta["title"])}</h2>
  <p>{esc(meta["desc"])}</p>
</div>
            """,
            unsafe_allow_html=True,
        )
    else:
        for m in messages:
            role = m.get("role", "assistant")
            ts = m.get("ts", "")
            content = esc(m.get("content", ""))
            role_label = "你" if role == "user" else "TradeNexus AI"
            st.markdown(
                f"""
<div class="msg-row {role}">
  <div class="bubble {role}">
    <div class="meta">{esc(role_label)} · {esc(ts)}</div>
    <div class="content">{content}</div>
  </div>
</div>
                """,
                unsafe_allow_html=True,
            )

    st.markdown("</div></div>", unsafe_allow_html=True)

def render_quick_start(module_name: str):
    meta = MODULE_META[module_name]
    quick = meta.get("quick", [])[:3]

    st.markdown('<div style="height:14px"></div>', unsafe_allow_html=True)
    st.markdown('<div class="panel panel-pad">', unsafe_allow_html=True)
    st.markdown(f'<div class="quick-title">快速开始</div>', unsafe_allow_html=True)
    st.markdown('<div class="quick-hint">点击即可一键发送到当前模块对话。</div>', unsafe_allow_html=True)

    c1, c2, c3 = st.columns(3)
    cols = [c1, c2, c3]
    for i, (label, payload) in enumerate(quick):
        with cols[i]:
            if st.button(f"一键发送：{label}", use_container_width=True, key=f"qs_{module_name}_{i}"):
                handle_send(module_name, payload)

    st.markdown("</div>", unsafe_allow_html=True)

def render_dashboard_cards():
    # 总控仪表盘的卡片（保持你图1那种入口，但更产品化）
    st.markdown('<div style="height:14px"></div>', unsafe_allow_html=True)
    st.markdown('<div class="panel panel-pad">', unsafe_allow_html=True)
    st.markdown(
        """
<div style="display:flex;align-items:flex-start;justify-content:space-between;gap:14px;flex-wrap:wrap;">
  <div style="flex:1;min-width:220px;padding:14px;border:1px solid rgba(16,24,40,.10);border-radius:16px;background:#fff;">
    <div style="color:#5b6475;font-size:12px;font-weight:700;">目标市场</div>
    <div style="font-size:22px;font-weight:900;color:#0b1220;margin-top:4px;">Global / B2B</div>
    <div style="margin-top:10px;display:inline-flex;align-items:center;gap:8px;font-size:12px;color:#16a34a;font-weight:800;">● Active</div>
  </div>

  <div style="flex:1;min-width:220px;padding:14px;border:1px solid rgba(16,24,40,.10);border-radius:16px;background:#fff;">
    <div style="color:#5b6475;font-size:12px;font-weight:700;">社媒引擎</div>
    <div style="font-size:22px;font-weight:900;color:#0b1220;margin-top:4px;">Ready</div>
    <div style="margin-top:10px;display:inline-flex;align-items:center;gap:8px;font-size:12px;color:#4f46e5;font-weight:800;">● New</div>
  </div>

  <div style="flex:1;min-width:220px;padding:14px;border:1px solid rgba(16,24,40,.10);border-radius:16px;background:#fff;">
    <div style="color:#5b6475;font-size:12px;font-weight:700;">知识资产</div>
    <div style="font-size:22px;font-weight:900;color:#0b1220;margin-top:4px;">0 Char</div>
    <div style="margin-top:10px;display:inline-flex;align-items:center;gap:8px;font-size:12px;color:#16a34a;font-weight:800;">● Loaded</div>
  </div>
</div>

<div style="height:14px"></div>

<div style="display:grid;grid-template-columns:1fr 1fr;gap:12px;">
  <div style="padding:14px;border:1px solid rgba(16,24,40,.10);border-radius:16px;background:linear-gradient(180deg,#ffffff,#fbfbfe);">
    <div style="font-weight:900;color:#0b1220;">全球社媒营销</div>
    <div style="margin-top:6px;color:#5b6475;font-size:12px;">一键生成多平台爆款内容（LinkedIn / TikTok / Cold DM）。</div>
  </div>
  <div style="padding:14px;border:1px solid rgba(16,24,40,.10);border-radius:16px;background:linear-gradient(180deg,#ffffff,#fbfbfe);">
    <div style="font-weight:900;color:#0b1220;">谈判策略军师</div>
    <div style="margin-top:6px;color:#5b6475;font-size:12px;">针对性输出客户压价/拖延/对比竞品的应对打法。</div>
  </div>
  <div style="padding:14px;border:1px solid rgba(16,24,40,.10);border-radius:16px;background:linear-gradient(180deg,#ffffff,#fbfbfe);">
    <div style="font-weight:900;color:#0b1220;">全球情报探挖</div>
    <div style="margin-top:6px;color:#5b6475;font-size:12px;">实时连接搜索，产出公司/竞品/新闻/切入点。</div>
  </div>
  <div style="padding:14px;border:1px solid rgba(16,24,40,.10);border-radius:16px;background:linear-gradient(180deg,#ffffff,#fbfbfe);">
    <div style="font-weight:900;color:#0b1220;">智能技术支持</div>
    <div style="margin-top:6px;color:#5b6475;font-size:12px;">基于你的知识库回答产品与售后技术问题。</div>
  </div>
</div>
        """,
        unsafe_allow_html=True,
    )
    st.markdown("</div>", unsafe_allow_html=True)

def render_sticky_composer(module_name: str):
    meta = MODULE_META[module_name]
    st.markdown('<div class="composer"><div class="composer-inner">', unsafe_allow_html=True)

    # 全球社媒营销额外提供平台选择（跟你原逻辑一致）
    if module_name == "全球社媒营销":
        st.session_state.social_platform = st.selectbox(
            "发布平台",
            ["LinkedIn（专业贴）", "TikTok/IG（短视频脚本）", "Cold DM（私信）"],
            index=["LinkedIn（专业贴）", "TikTok/IG（短视频脚本）", "Cold DM（私信）"].index(
                st.session_state.get("social_platform", "LinkedIn（专业贴）")
            ),
            key="social_platform_select",
        )

    cc1, cc2 = st.columns([6, 1.2], vertical_alignment="bottom")
    with cc1:
        st.session_state.composer_text = st.text_area(
            label="",
            value=st.session_state.composer_text,
            height=80,
            placeholder=meta.get("composer_ph", "描述你的问题…"),
            key=f"composer_{module_name}",
        )

    with cc2:
        send = st.button("发送", type="primary", use_container_width=True, key=f"send_{module_name}")
        clear = st.button("清空", type="secondary", use_container_width=True, key=f"clear_{module_name}")

    if clear:
        st.session_state.chat_messages[module_name] = []
        st.session_state.composer_text = ""
        st.rerun()

    if send:
        handle_send(module_name, st.session_state.composer_text)

    # 技术支持模块提示是否有知识库
    if module_name == "智能技术支持" and mem_len <= 50:
        note = "当前知识库为空：建议先在左侧【知识库管理】粘贴资料或上传 PDF，再提问。"
    else:
        note = "TradeNexus AI 销售专家。发送前请确认已脱敏敏感信息。"

    st.markdown(f'<div class="composer-note">{esc(note)}</div>', unsafe_allow_html=True)
    st.markdown("</div></div>", unsafe_allow_html=True)

# ============================================================
# 10) Sidebar：品牌 + 导航 + 知识库管理（与你原功能等价）
# ============================================================
with st.sidebar:
    st.markdown(
        """
<div class="sidebar-brand">
  <div class="logo">T</div>
  <div>
    <div class="title">TradeNexus AI</div>
    <div class="subtitle">B2B 外贸销售工作台</div>
  </div>
</div>
        """,
        unsafe_allow_html=True,
    )
    st.markdown(
        """
<div class="sidebar-status">
  <div class="badge"><span class="dot"></span> Ready · Online</div>
  <div style="height:8px"></div>
  <div style="font-size:12px;color:rgba(255,255,255,.65);">
    建议：优先在“订单复盘/询盘分析/谈判策略”中沉淀 SOP 与模板。
  </div>
</div>
        """,
        unsafe_allow_html=True,
    )

    selected = option_menu(
        "系统导航",
        ALL_MODULES,
        icons=["speedometer2", "search", "megaphone", "envelope", "globe", "person-check", "chat-dots", "tools"],
        menu_icon="cast",
        default_index=ALL_MODULES.index(st.session_state.get("active_module", "订单复盘")),
        styles={
            "container": {"padding": "0!important", "background-color": "rgba(0,0,0,0)"},
            "icon": {"color": "rgba(255,255,255,.75)", "font-size": "16px"},
            "nav-link": {
                "font-size": "13px",
                "text-align": "left",
                "margin": "6px 10px",
                "color": "rgba(255,255,255,.80)",
                "border-radius": "14px",
                "padding": "10px 12px",
            },
            "nav-link-selected": {
                "background": "linear-gradient(90deg, rgba(79,70,229,.95), rgba(109,40,217,.95))",
                "color": "white",
                "box-shadow": "0 12px 30px rgba(79,70,229,.30)",
            },
        },
    )
    st.session_state.active_module = selected

    st.markdown("---")

    # 知识库管理（保持你原来的功能：粘贴 + 上传PDF + 清空）
    with st.expander("📚 知识库管理", expanded=True):
        if mem_len > 50:
            st.success(f"✅ 知识库已激活（约 {mem_len} 字符）")
        else:
            st.info("🟦 知识库为空：请粘贴资料或上传 PDF。")

        new_txt = st.text_area("粘贴文本资料：", height=110, placeholder="例如：产品参数、FAQ、交期、质检标准、报价规则…")
        col_a, col_b = st.columns(2)
        with col_a:
            if st.button("保存到记忆", use_container_width=True):
                if new_txt.strip():
                    ok = save_memory(new_txt.strip())
                    if ok:
                        st.success("已保存到知识库")
                        time.sleep(0.6)
                        st.rerun()
                    else:
                        st.warning("该内容已存在或为空")
                else:
                    st.warning("请输入内容")

        with col_b:
            if st.button("清空记忆", use_container_width=True):
                clear_memory()
                st.success("已清空知识库")
                time.sleep(0.6)
                st.rerun()

        st.write("---")
        up_file = st.file_uploader("或上传 PDF（提取文字写入知识库）", type=["pdf"])
        if up_file:
            try:
                reader = PdfReader(up_file)
                text = "\n".join([(p.extract_text() or "") for p in reader.pages])
                if len(text.strip()) > 50:
                    save_memory(text.strip())
                    st.success("PDF 已写入知识库")
                    time.sleep(0.6)
                    st.rerun()
                else:
                    st.error("PDF 无可提取文本（可能是扫描版）")
            except Exception:
                st.error("读取 PDF 失败，请更换文件重试。")

# ============================================================
# 11) 主区渲染：多模块切换（你要求的“全部模块都加上”）
# ============================================================
active = st.session_state.active_module
render_top_header(active)

# 总控仪表盘：显示卡片 + 仍保留对话式入口
if active == "总控仪表盘":
    render_dashboard_cards()

# 聊天区 + quick start（所有模块都有）
render_chat(active)
render_quick_start(active)

# sticky 输入框（所有模块都有）
render_sticky_composer(active)
