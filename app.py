import streamlit as st
import google.generativeai as genai
import requests
import json
import time
import pypdf
import os

# ==========================================
# 1. 核心配置与 SaaS 深色 UI (视觉重构)
# ==========================================
st.set_page_config(
    page_title="外贸数字指挥官 | Global Command Center", 
    page_icon="🦁", 
    layout="wide",
    initial_sidebar_state="expanded"
)

# 注入高级 SaaS 深色主题 CSS
st.markdown("""
<style>
    /* 全局深色背景 */
    .stApp {
        background-color: #0E1117;
        color: #FAFAFA;
    }
    
    /* 侧边栏深色优化 */
    section[data-testid="stSidebar"] {
        background-color: #161B22;
        border-right: 1px solid #30363D;
    }
    
    /* 输入框优化：深灰底白字，高对比度 */
    .stTextArea textarea, .stTextInput input, .stSelectbox div[data-baseweb="select"] {
        background-color: #21262D !important;
        color: #FFFFFF !important;
        border: 1px solid #30363D;
        border-radius: 8px;
    }
    
    /* 按钮优化：蓝紫渐变，悬停发光 */
    .stButton>button {
        background: linear-gradient(90deg, #4F46E5 0%, #7C3AED 100%);
        color: white;
        border: none;
        border-radius: 8px;
        height: 3.5em;
        font-weight: 600;
        font-size: 16px;
        transition: all 0.3s ease;
    }
    .stButton>button:hover {
        box-shadow: 0 4px 15px rgba(124, 58, 237, 0.4);
        transform: translateY(-2px);
    }
    
    /* 卡片容器风格 */
    div[data-testid="metric-container"] {
        background-color: #161B22;
        border: 1px solid #30363D;
        padding: 20px;
        border-radius: 10px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.3);
    }
    
    /* 标题与字体优化 */
    h1, h2, h3 {
        color: #FFFFFF !important;
        font-family: 'PingFang SC', 'Microsoft YaHei', sans-serif;
        font-weight: 700;
    }
    p, label {
        color: #E6EDF3 !important; /* 亮灰白色，防止顺色 */
    }
    
    /* 侧边栏文字高亮 */
    .css-17lntkn {
        color: #E6EDF3 !important;
    }
</style>
""", unsafe_allow_html=True)

MEMORY_FILE = "b2b_kb_memory.json"

try:
    api_key = st.secrets["GOOGLE_API_KEY"]
    genai.configure(api_key=api_key)
except Exception:
    st.error("⚠️ 系统错误: 未检测到 API Key，请检查 Secrets 配置。")
    st.stop()

# ==========================================
# 2. 逻辑内核 (保持稳健)
# ==========================================
def load_memory():
    if os.path.exists(MEMORY_FILE):
        try:
            with open(MEMORY_FILE, "r", encoding="utf-8") as f:
                return json.load(f).get("text", "")
        except: return ""
    return ""

def save_memory(new_text):
    current = load_memory()
    if new_text.strip() in current: return False
    updated = current + "\n" + new_text
    with open(MEMORY_FILE, "w", encoding="utf-8") as f:
        json.dump({"text": updated}, f, ensure_ascii=False)
    return True

def clear_memory():
    if os.path.exists(MEMORY_FILE): os.remove(MEMORY_FILE)

@st.cache_resource
def get_best_model(): return "models/gemini-2.5-flash"
valid_model_name = get_best_model()

def robust_generate(prompt, model_name):
    model = genai.GenerativeModel(model_name)
    max_retries = 5
    for i in range(max_retries):
        try:
            response = model.generate_content(prompt)
            return response.text
        except Exception as e:
            if "429" in str(e): time.sleep((i+1)*5); continue
            else: time.sleep(2); continue
    return "⚠️ 网络繁忙，请稍后重试。"

def robust_api_search(payload, model_name, api_key):
    url = f"https://generativelanguage.googleapis.com/v1beta/{model_name}:generateContent?key={api_key}"
    headers = {'Content-Type': 'application/json'}
    for i in range(3):
        try:
            res = requests.post(url, headers=headers, data=json.dumps(payload), timeout=60)
            if res.status_code == 200: return res.json()
            elif res.status_code == 429: time.sleep(5); continue
            else: return {"error": f"错误代码 {res.status_code}"}
        except Exception as e: return {"error": str(e)}
    return {"error": "请求超时"}

# ==========================================
# 3. 侧边栏 (SaaS 风格导航)
# ==========================================
st.sidebar.markdown("### 🦁 **外贸数字指挥官**")
st.sidebar.caption(f"内核引擎: {valid_model_name.split('/')[-1]} | 状态: 🟢 在线")
st.sidebar.markdown("---")

# 中文导航
MENU = {
    "home": "🏠 总控仪表盘 (Dashboard)",
    "social": "📱 全域社媒营销 (Social)",
    "email": "📧 深度询盘分析 (Email)",
    "search": "🌐 全球情报深挖 (Search)",
    "bg": "🕵️‍♂️ 客户背景背调 (Check)",
    "neg": "⛔ 谈判策略军师 (Coach)",
    "support": "🛠️ 智能技术支持 (Support)"
}

selected_page = st.sidebar.radio("系统导航", list(MENU.values()))

# 知识库状态
st.sidebar.markdown("---")
current_mem = load_memory()
mem_len = len(current_mem)
kb_status = "🟢 已激活" if mem_len > 50 else "⚪ 空闲中"
st.sidebar.metric("🧠 企业知识库", kb_status, f"{mem_len} 字符")

# 投喂入口
with st.sidebar.expander("📂 知识库管理 (上传资料)"):
    new_txt = st.text_area("粘贴产品参数/话术:", height=100)
    if st.button("💾 保存文本"): 
        if new_txt: save_memory(new_txt); st.rerun()
    
    up_file = st.file_uploader("上传 PDF 手册:", type=['pdf'])
    if up_file:
        try:
            reader = pypdf.PdfReader(up_file)
            txt = "".join([p.extract_text() or "" for p in reader.pages])
            if len(txt)>50: save_memory(txt); st.success("已保存!"); time.sleep(1); st.rerun()
            else: st.error("PDF 内容为空或为纯图片")
        except: st.error("文件读取失败")

    if st.button("🗑️ 清空所有记忆"): clear_memory(); st.rerun()

KB_INJECTION = f"[内部知识库数据]: {current_mem}" if mem_len > 50 else ""

# ==========================================
# 4. 主界面逻辑 (全中文 + 卡片式布局)
# ==========================================

# --- 🏠 仪表盘 ---
if selected_page == MENU["home"]:
    st.title("🚀 指挥官总控台")
    st.markdown("欢迎回来，这里是您的全球业务增长引擎。")
    
    # 核心指标卡
    c1, c2, c3 = st.columns(3)
    c1.metric("目标市场", "全球 / B2B", "Active")
    c2.metric("社媒引擎", "已就绪", "New")
    c3.metric("知识资产", f"{mem_len} 字符", "Loaded")
    
    st.markdown("---")
    st.subheader("💡 核心能力概览")
    
    col1, col2 = st.columns(2)
    with col1:
        st.info("📱 **全域社媒营销**\n\n一键生成 LinkedIn 深度文、TikTok 脚本及开发信，支持多语言裂变。")
        st.success("🌐 **全球情报深挖**\n\n实时连接 Google 搜索，挖掘客户官网看不到的隐秘信息。")
    with col2:
        st.warning("⛔ **谈判策略军师**\n\n哈佛谈判专家视角，针对客户压价、甚至拒单提供回击话术。")
        st.error("🛠️ **智能技术支持**\n\n基于您上传的 PDF 手册，自动回答任何刁钻的技术或售后问题。")

# --- 📱 社媒营销 ---
elif selected_page == MENU["social"]:
    st.title("📱 全域社媒营销引擎")
    st.markdown("一次输入，全网分发。基于您的产品知识库自动生成多平台爆款内容。")
    
    col_input, col_opt = st.columns([3, 1])
    with col_input:
        campaign_topic = st.text_input("📢 请输入营销主题 / 产品焦点:", placeholder="例如：新款 X500 环保包装材料发布")
    
    with col_opt:
        platform = st.selectbox(
            "选择发布平台:",
            ["👔 LinkedIn (专业领袖IP)", "🎥 TikTok/IG (短视频脚本)", "🤝 Cold DM (陌生开发私信)"]
        )
    
    if st.button("🚀 立即生成营销素材"):
        if not campaign_topic:
            st.warning("请先输入主题")
        else:
            with st.spinner('AI 正在查阅知识库并撰写文案...'):
                social_prompt = f"""
                {KB_INJECTION}
                
                **角色:** B2B 外贸社媒营销专家
                **任务:** 为主题 "{campaign_topic}" 撰写内容
                **平台:** {platform}
                
                **规则:**
                1. 若是 LinkedIn: 使用 Hook-Insight-Solution-CTA 结构，专业且有深度。
                2. 若是 TikTok: 输出两列表格 [画面描述] | [口播台词]，时长45秒内。
                3. 若是 Cold DM: 简短、不骚扰、提供价值，第一条信息不带链接。
                
                **约束:** 必须严格基于[内部知识库数据]中的产品参数，禁止胡编乱造。输出中文（或根据语境输出英文）。
                """
                
                res = robust_generate(social_prompt, valid_model_name)
                st.session_state.social_res = res

    if 'social_res' in st.session_state:
        st.markdown("---")
        st.subheader("✨ 生成结果")
        st.markdown(st.session_state.social_res)

# --- 📧 询盘分析 ---
elif selected_page == MENU["email"]:
    st.title("📧 深度询盘分析")
    c1, c2 = st.columns([2, 1])
    with c1:
        user_input = st.text_area("请粘贴客户邮件内容:", height=300)
    with c2:
        st.markdown("#### 💡 功能说明")
        st.info("AI 将分析客户语气、潜在意图，并结合库存/产品表生成中英文双语回复。")
        if st.button("🚀 开始分析"):
            if user_input:
                with st.spinner('分析中...'):
                    prompt = f"{KB_INJECTION}\n扮演销售总监。分析邮件。输出: 客户意图, 评分(0-10), 建议策略, 草拟回复(英文+中文解释)。\n邮件内容: {user_input}"
                    st.session_state.res_email = robust_generate(prompt, valid_model_name)
    
    if 'res_email' in st.session_state:
        st.markdown("---")
        st.markdown(st.session_state.res_email)

# --- 🌐 搜情报 ---
elif selected_page == MENU["search"]:
    st.title("🌐 全球市场情报")
    query = st.text_input("请输入客户公司名或关键词:", placeholder="例如：Home Depot Procurement")
    if st.button("🌍 深度挖掘"):
        if query:
            with st.spinner('正在全网检索...'):
                prompt = f"Role: B2B Analyst. Search: '{query}'. Report: Identity, Latest News, Competitors, Cold Email Hook."
                data = robust_api_search({"contents":[{"parts":[{"text":prompt}]}],"tools":[{"google_search":{}}]}, valid_model_name, api_key)
                if "error" in data: st.error(data['error'])
                else:
                    try:
                        ans = data['candidates'][0]['content']['parts'][0]['text']
                        st.success("✅ 情报获取成功")
                        st.markdown(ans)
                    except: st.error("数据解析失败")

# --- 🕵️‍♂️ 背调 ---
elif selected_page == MENU["bg"]:
    st.title("🕵️‍♂️ 客户背景静态分析")
    st.caption("适用于分析客户官网 'About Us' 页面文本")
    txt_input = st.text_area("粘贴文本:", height=200)
    if st.button("🔍 生成画像"):
        if txt_input:
            with st.spinner('分析中...'):
                prompt = "分析这家公司。输出: 商业模式, 规模, 痛点, 推销切入点。"
                st.markdown(robust_generate(f"{prompt}\nText: {txt_input}", valid_model_name))

# --- ⛔ 谈判 ---
elif selected_page == MENU["neg"]:
    st.title("⛔ 谈判与异议粉碎机")
    c1, c2 = st.columns(2)
    obj = c1.text_input("客户拒绝理由:", placeholder="例如：价格太贵了 (Price is too high)")
    lev = c2.text_input("我的筹码 (可选):", placeholder="例如：交期快，质量好")
    
    if st.button("💣 生成回击策略"):
        if obj:
            with st.spinner('军师正在思考...'):
                prompt = f"{KB_INJECTION}\n谈判专家。客户拒绝: '{obj}'。我方优势: '{lev}'。提供3个策略(价值/共情/替代方案)。"
                st.markdown(robust_generate(prompt, valid_model_name))

# --- 🛠️ 售后 ---
elif selected_page == MENU["support"]:
    st.title("🛠️ 智能技术支持")
    if mem_len < 50: 
        st.warning("⚠️ 知识库为空。请先在左侧侧边栏上传产品手册 PDF。")
    else: 
        st.success("✅ 知识库已激活。您可以询问关于产品的任何技术细节。")
    
    q = st.chat_input("请输入关于产品的问题...")
    if q:
        with st.chat_message("user"): st.write(q)
        with st.chat_message("assistant"):
            with st.spinner('查询内部文档...'):
                prompt = f"{KB_INJECTION}\n角色: 技术支持专家。问题: '{q}'。严格基于提供的知识库数据回答。"
                res = robust_generate(prompt, valid_model_name)
                st.write(res)
