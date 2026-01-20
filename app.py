import streamlit as st
from streamlit_option_menu import option_menu
import time

# =========================
# 0) 基础配置
# =========================
st.set_page_config(
    page_title="TradeNexus AI - B2B 外贸销售专家",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded",
)

# =========================
# 1) 全局 CSS（AI Studio 风格）
# =========================
def inject_ai_studio_css():
    st.markdown(
        """
<style>
/* ---------- Root tokens ---------- */
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

  --primary: #4f46e5;  /* indigo */
  --primary-2: #6d28d9;
  --success: #16a34a;
  --warn: #f59e0b;

  --bubble-user: #eef2ff;
  --bubble-assistant: #ffffff;

  --radius-lg: 18px;
  --radius-md: 14px;
}

/* ---------- Streamlit base ---------- */
html, body, [class*="css"]{
  font-family: ui-sans-serif, system-ui, -apple-system, Segoe UI, Roboto, Helvetica, Arial, "Apple Color Emoji","Segoe UI Emoji";
}
.stApp {
  background: var(--bg);
}

/* Hide default header */
header {visibility: hidden;}
/* reduce default paddings */
.block-container{
  padding-top: 0.75rem;
  padding-bottom: 6.5rem; /* leave space for sticky composer */
  max-width: 1200px;
}

/* ---------- Sidebar ---------- */
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
section[data-testid="stSidebar"] hr{
  border-color: var(--nav-border);
}
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
.sidebar-brand .title{
  font-weight: 800;
  letter-spacing: .2px;
}
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

/* ---------- Top header ---------- */
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
.h-left{
  display:flex; align-items:center; gap: 12px;
}
.h-appmark{
  width: 34px; height: 34px; border-radius: 12px;
  background: #ffffff;
  border: 1px solid var(--border);
  display:flex; align-items:center; justify-content:center;
  box-shadow: 0 8px 22px rgba(16,24,40,.06);
}
.h-title{
  font-size: 15px; font-weight: 800; color: var(--text);
  line-height: 1.1;
}
.h-sub{
  font-size: 12px; color: var(--muted);
  margin-top: 1px;
}
.h-right{
  display:flex; align-items:center; gap: 8px;
}
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

/* ---------- Main cards ---------- */
.panel{
  background: var(--panel);
  border: 1px solid var(--border);
  border-radius: var(--radius-lg);
  box-shadow: var(--shadow);
}
.panel-pad{
  padding: 18px 18px;
}
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
.hero h2{
  margin: 0;
  font-size: 22px;
  color: var(--text);
  font-weight: 900;
}
.hero p{
  margin: 8px 0 0 0;
  color: var(--muted);
  font-size: 13px;
}

/* Quick start buttons look */
.quick-title{
  margin: 14px 0 10px 0;
  font-weight: 800;
  color: var(--text);
  font-size: 13px;
  text-align: left;
}
.quick-grid{
  display:grid;
  grid-template-columns: 1fr;
  gap: 10px;
  max-width: 720px;
  margin: 0 auto;
}
.quick-card{
  display:flex; align-items:center; gap: 10px;
  padding: 12px 14px;
  border-radius: 16px;
  background: var(--panel-2);
  border: 1px solid var(--border);
  transition: transform .12s ease, box-shadow .12s ease;
}
.quick-card:hover{
  transform: translateY(-1px);
  box-shadow: 0 10px 25px rgba(16,24,40,.08);
}
.quick-ic{
  width: 34px; height: 34px; border-radius: 14px;
  background: rgba(79,70,229,.10);
  border: 1px solid rgba(79,70,229,.16);
  display:flex; align-items:center; justify-content:center;
  color: var(--primary);
  font-weight: 900;
}
.quick-text{
  flex: 1;
  color: var(--text);
  font-size: 13px;
  font-weight: 700;
}
.quick-sub{
  color: var(--muted);
  font-size: 12px;
  font-weight: 500;
  margin-top: 2px;
}

/* ---------- Chat bubbles ---------- */
.chat-wrap{
  display:flex;
  flex-direction:column;
  gap: 10px;
}
.msg-row{
  display:flex;
}
.msg-row.user { justify-content: flex-end; }
.msg-row.assistant { justify-content: flex-start; }

.bubble{
  max-width: 78%;
  border-radius: 18px;
  border: 1px solid var(--border);
  padding: 12px 14px;
  box-shadow: 0 8px 22px rgba(16,24,40,.04);
}
.bubble.user{
  background: var(--bubble-user);
}
.bubble.assistant{
  background: var(--bubble-assistant);
}
.bubble .meta{
  font-size: 11px;
  color: var(--muted);
  margin-bottom: 6px;
}
.bubble .content{
  color: var(--text);
  font-size: 13.5px;
  line-height: 1.55;
  white-space: pre-wrap;
}

/* ---------- Sticky composer ---------- */
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
.composer-box{
  display:flex;
  align-items:flex-end;
  gap: 10px;
}
.composer-note{
  font-size: 12px;
  color: var(--muted);
  margin-top: 8px;
  text-align: center;
}

/* Style Streamlit inputs inside composer */
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

/* Remove extra whitespace from Streamlit elements inside fixed composer */
.composer-inner [data-testid="stVerticalBlock"]{ gap: 0.35rem; }
</style>
        """,
        unsafe_allow_html=True,
    )

inject_ai_studio_css()

# =========================
# 2) Session state
# =========================
if "active_module" not in st.session_state:
    st.session_state.active_module = "订单复盘"
if "chat_messages" not in st.session_state:
    # 每个模块一套对话，避免相互污染
    st.session_state.chat_messages = {
        "订单复盘": [],
        "全球社媒营销": [],
        "深度询盘分析": [],
        "全球情报探挖": [],
        "客户背景调查": [],
        "谈判策略军师": [],
        "智能技术支持": [],
        "总控仪表盘": [],
    }
if "composer_text" not in st.session_state:
    st.session_state.composer_text = ""

# =========================
# 3) 你的模型调用入口（替换为你现有 robust_generate）
# =========================
def call_model(prompt: str) -> str:
    """
    TODO: 用你的 Gemini 调用逻辑替换这里：
      - 你已有 robust_generate(prompt, valid_model_name)
      - 或者你已有 robust_api_search(...) / google_search tool 等
    """
    # 示例：假装调用耗时
    time.sleep(0.3)
    return f"（示例输出）已收到你的请求：\n\n{prompt}\n\n请把 call_model() 替换为你的 Gemini 调用函数。"

# =========================
# 4) UI 组件：顶部栏 / 聊天区 / 空状态 / Quick Start / 发送逻辑
# =========================
def render_top_header(module_name: str):
    st.markdown(
        f"""
<div class="ai-header">
  <div class="ai-header-inner">
    <div class="h-left">
      <div class="h-appmark">🧠</div>
      <div>
        <div class="h-title">{module_name}</div>
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

def render_chat(messages):
    st.markdown('<div class="panel panel-pad">', unsafe_allow_html=True)
    st.markdown('<div class="chat-wrap">', unsafe_allow_html=True)

    if len(messages) == 0:
        # 空状态更像 AI Studio
        st.markdown(
            """
<div class="hero">
  <div class="hero-icon">🔎</div>
  <h2>订单复盘</h2>
  <p>专为出单任务设计的 AI 模块。粘贴交易结果或对话历史，获得更精准的复盘建议。</p>
</div>
            """,
            unsafe_allow_html=True,
        )
    else:
        for m in messages:
            role = m.get("role", "assistant")
            ts = m.get("ts", "")
            content = m.get("content", "")
            role_label = "你" if role == "user" else "TradeNexus AI"
            st.markdown(
                f"""
<div class="msg-row {role}">
  <div class="bubble {role}">
    <div class="meta">{role_label} · {ts}</div>
    <div class="content">{content.replace("<","&lt;").replace(">","&gt;")}</div>
  </div>
</div>
                """,
                unsafe_allow_html=True,
            )

    st.markdown("</div></div>", unsafe_allow_html=True)

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
        # 你可以在这里拼接 KB_INJECTION、模块提示词、系统规则等
        # e.g. prompt = f"{KB_INJECTION}\n你是订单复盘专家...\n用户输入：{text}"
        prompt = f"[模块：{module_name}]\n用户输入：{text}"
        answer = call_model(prompt)

    push_message(module_name, "assistant", answer)
    st.session_state.composer_text = ""
    st.rerun()

def render_quick_start(module_name: str):
    # 只在“订单复盘”示例展示 quick start（你也可扩展到其他模块）
    if module_name != "订单复盘":
        return

    st.markdown(
        """
<div style="height:14px"></div>
<div class="panel panel-pad">
  <div class="quick-title">快速开始</div>
  <div class="quick-grid">
    <div class="quick-card">
      <div class="quick-ic">①</div>
      <div style="flex:1">
        <div class="quick-text">复盘这个失败的订单</div>
        <div class="quick-sub">我将从报价、跟进节奏、异议处理给出改进建议</div>
      </div>
    </div>
    <div class="quick-card">
      <div class="quick-ic">②</div>
      <div style="flex:1">
        <div class="quick-text">总结最近 5 个客户流失的原因</div>
        <div class="quick-sub">输出归因结构 + 可执行的纠偏动作</div>
      </div>
    </div>
    <div class="quick-card">
      <div class="quick-ic">③</div>
      <div style="flex:1">
        <div class="quick-text">如何提高我的询盘转化率？</div>
        <div class="quick-sub">给出漏斗诊断 + 话术与流程优化建议</div>
      </div>
    </div>
  </div>
</div>
        """,
        unsafe_allow_html=True,
    )

    # 用真正的按钮实现“一键发送”（视觉仍然由上面的卡片承担）
    # 这样能避免复杂 JS，同时可靠触发 rerun
    c1, c2, c3 = st.columns(3)
    with c1:
        if st.button("一键发送：复盘失败订单", use_container_width=True):
            handle_send(module_name, "复盘这个失败的订单：我将把交易记录/对话粘贴给你，请按时间线拆解问题并给出改进策略。")
    with c2:
        if st.button("一键发送：总结 5 个流失原因", use_container_width=True):
            handle_send(module_name, "请总结我最近 5 个客户流失的原因：给出归因分类（产品/价格/交付/信任/时机/跟进）+ 我应该立刻做的动作清单。")
    with c3:
        if st.button("一键发送：提升转化率", use_container_width=True):
            handle_send(module_name, "如何提高我的询盘转化率？请基于漏斗（曝光-询盘-跟进-报价-成交）给我诊断框架和可执行改进方案。")

def render_sticky_composer(module_name: str):
    # 固定底部输入框（用空容器 + CSS fixed 来实现）
    st.markdown('<div class="composer"><div class="composer-inner">', unsafe_allow_html=True)

    # 用 columns 模拟“输入框 + 发送按钮”
    cc1, cc2 = st.columns([6, 1.2], vertical_alignment="bottom")

    with cc1:
        st.session_state.composer_text = st.text_area(
            label="",
            value=st.session_state.composer_text,
            height=80,
            placeholder="粘贴交易结果或对话历史，或直接描述你的问题…",
            key=f"composer_{module_name}",
        )

    with cc2:
        send = st.button("发送", type="primary", use_container_width=True)
        clear = st.button("清空", type="secondary", use_container_width=True)

    if clear:
        st.session_state.chat_messages[module_name] = []
        st.session_state.composer_text = ""
        st.rerun()

    if send:
        handle_send(module_name, st.session_state.composer_text)

    st.markdown(
        """
<div class="composer-note">TradeNexus AI 销售专家。发送前请确认已脱敏敏感信息。</div>
        """,
        unsafe_allow_html=True,
    )
    st.markdown("</div></div>", unsafe_allow_html=True)

# =========================
# 5) Sidebar 导航（多模块 1A）
# =========================
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
    建议：优先在“订单复盘/深度询盘分析/谈判策略”中沉淀你的 SOP。
  </div>
</div>
        """,
        unsafe_allow_html=True,
    )

    module = option_menu(
        "系统导航",
        [
            "总控仪表盘",
            "订单复盘",
            "全球社媒营销",
            "深度询盘分析",
            "全球情报探挖",
            "客户背景调查",
            "谈判策略军师",
            "智能技术支持",
        ],
        icons=["speedometer2", "search", "megaphone", "envelope", "globe", "person-check", "chat-dots", "tools"],
        menu_icon="cast",
        default_index=1,
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

st.session_state.active_module = module

# =========================
# 6) 主区渲染
# =========================
active = st.session_state.active_module
render_top_header(active)

# 模块页面：你可以按模块区分不同 prompt / UI
messages = st.session_state.chat_messages.get(active, [])

# 你也可以在“总控仪表盘”做 KPI 卡片；这里先给一个简洁占位
if active == "总控仪表盘":
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

else:
    # 聊天页面
    render_chat(messages)
    render_quick_start(active)

# 底部固定输入框（所有模块都有）
render_sticky_composer(active)
