import streamlit as st
import google.generativeai as genai
import requests
import json
import time
import pypdf
import os

# ==========================================
# 1. 核心配置
# ==========================================
st.set_page_config(page_title="外贸数字指挥官 (最终修复版)", page_icon="🦁", layout="wide")

MEMORY_FILE = "b2b_kb_memory.json"

try:
    api_key = st.secrets["GOOGLE_API_KEY"]
    genai.configure(api_key=api_key)
except Exception:
    st.error("⚠️ 未检测到 API Key，请配置 Secrets。")
    st.stop()

# ==========================================
# 2. 记忆系统
# ==========================================
def load_memory():
    if os.path.exists(MEMORY_FILE):
        try:
            with open(MEMORY_FILE, "r", encoding="utf-8") as f:
                return json.load(f).get("text", "")
        except:
            return ""
    return ""

def save_memory(new_text):
    current_text = load_memory()
    if new_text.strip() in current_text: return False
    updated_text = current_text + "\n" + new_text
    with open(MEMORY_FILE, "w", encoding="utf-8") as f:
        json.dump({"text": updated_text}, f, ensure_ascii=False)
    return True

def clear_memory():
    if os.path.exists(MEMORY_FILE): os.remove(MEMORY_FILE)

# ==========================================
# 3. 智能引擎 (抗压版)
# ==========================================
@st.cache_resource
def get_best_model():
    return "models/gemini-2.5-flash"

valid_model_name = get_best_model()

def robust_generate(prompt, model_name):
    model = genai.GenerativeModel(model_name)
    max_retries = 5
    last_err = ""
    for i in range(max_retries):
        try:
            response = model.generate_content(prompt)
            return response.text
        except Exception as e:
            last_err = str(e)
            if "429" in str(e):
                time.sleep((i + 1) * 5)
                continue
            elif "400" in str(e):
                 return f"❌ 内容可能过长或违规: {str(e)}"
            else:
                time.sleep(2)
                continue
    return f"⚠️ 系统繁忙 (重试{max_retries}次失败)。原因: {last_err}"

def robust_api_search(payload, model_name, api_key):
    url = f"https://generativelanguage.googleapis.com/v1beta/{model_name}:generateContent?key={api_key}"
    headers = {'Content-Type': 'application/json'}
    for i in range(3):
        try:
            response = requests.post(url, headers=headers, data=json.dumps(payload), timeout=60)
            if response.status_code == 200:
                return response.json()
            elif response.status_code == 429:
                time.sleep(5)
                continue
            else:
                return {"error": f"Error {response.status_code}"}
        except Exception as e:
            return {"error": str(e)}
    return {"error": "网络超时"}

# ==========================================
# 4. 侧边栏：记忆管理
# ==========================================
st.sidebar.title("🦁 控制台")
st.sidebar.markdown("### 🧠 记忆体状态")

current_memory = load_memory()
mem_length = len(current_memory.strip())

if mem_length > 50:
    st.sidebar.success(f"🟢 记忆库: {mem_length} 字符")
    with st.sidebar.expander("👀 检查记忆内容"):
        st.text(current_memory[:500] + "...")
else:
    st.sidebar.warning("⚪ 记忆库为空")

st.sidebar.markdown("---")
st.sidebar.write("📤 **追加新资料:**")

new_kb_text = st.sidebar.text_area("粘贴文本:", height=70)
if st.sidebar.button("💾 保存文本"):
    if new_kb_text:
        save_memory(new_kb_text)
        st.sidebar.success("已保存！")
        time.sleep(1)
        st.rerun()

uploaded_file = st.sidebar.file_uploader("上传 PDF:", type=['pdf'], key="pdf_up")
if uploaded_file is not None:
    try:
        reader = pypdf.PdfReader(uploaded_file)
        pdf_text = ""
        for page in reader.pages:
            t = page.extract_text()
            if t: pdf_text += t + "\n"
        
        if len(pdf_text.strip()) < 50:
            st.sidebar.error("❌ 读取失败！可能是纯图片/扫描件 PDF。")
        else:
            if save_memory(pdf_text):
                st.sidebar.success(f"✅ 成功提取 {len(pdf_text)} 字！")
                time.sleep(1)
                st.rerun()
    except Exception as e:
        st.sidebar.error(f"文件错误: {e}")

st.sidebar.markdown("---")
if st.sidebar.button("🗑️ 清空记忆"):
    clear_memory()
    st.sidebar.warning("记忆已清空")
    time.sleep(1)
    st.rerun()

# ==========================================
# 5. 功能菜单
# ==========================================
st.sidebar.markdown("---")
MENU_OPTIONS = [
    "📧 询盘深度分析", 
    "🕵️‍♂️ 文本背调 (稳)", 
    "🌐 全网情报深挖 (联网)", 
    "⛔ 谈判与异议粉碎",
    "🛠️ 智能售后/专家问答"
]
app_mode = st.sidebar.radio("功能选择：", MENU_OPTIONS)

KB_INJECTION = ""
if mem_length > 50:
    KB_INJECTION = f"""
    [IMPORTANT: INTERNAL KNOWLEDGE BASE]
    You have access to the following product data. Use it to answer.
    {current_memory}
    [END OF DATA]
    """

# ==========================================
# 6. 功能逻辑 (已修复截断问题)
# ==========================================

# --- 询盘分析 ---
if app_mode == MENU_OPTIONS[0]: 
    st.subheader("📧 深度询盘分析")
    user_input = st.text_area("粘贴邮件：", height=200)
    if 'res_1' not in st.session_state: st.session_state.res_1 = None
    if st.button("🚀 分析邮件"):
        if user_input:
            with st.spinner('正在分析...'):
                PROMPT = f"""
                {KB_INJECTION}
                Act as Sales Manager. Analyze email. 
                Output: Language, Intent, Score, Advice, Draft Response.
                Input: {user_input}
                """
                st.session_state.res_1 = robust_generate(PROMPT, valid_model_name)
    if st.session_state.res_1: st.markdown(st.session_state.res_1)

# --- 文本背调 ---
elif app_mode == MENU_OPTIONS[1]: 
    st.subheader("🕵️‍♂️ 网站文本分析")
    bg_input = st.text_area("粘贴网站文本：", height=200)
    if 'res_2' not in st.session_state: st.session_state.res_2 = None
    if st.button("🔍 分析"):
        if bg_input:
            with st.spinner('分析中...'):
                PROMPT = f"""
                Analyze company text. Output: Identity, Scale, Pain Points, Pitch Strategy.
                Text: {bg_input}
                """
                st.session_state.res_2 = robust_generate(PROMPT, valid_model_name)
    if st.session_state.res_2: st.markdown(st.session_state.res_2)

# --- 全网深挖 ---
elif app_mode == MENU_OPTIONS[2]: 
    st.subheader("🌐 全网商业情报")
    query = st.text_input("关键词：")
    if 'res_3' not in st.session_state: st.session_state.res_3 = None
    if st.button("🌍 挖掘"):
        if query:
            st.session_state.res_3 = None
            with st.spinner('检索中...'):
                prompt = f"""
                Role: Analyst. Search: '{query}'. 
                Report: Identity, News, Procurement, Competitors, Hook.
                """
                payload = {"contents": [{"parts": [{"text": prompt}]}], "tools": [{"google_search": {}}]}
                data = robust_api_search(payload, valid_model_name, api_key)
                if "error" in data: st.error(data["error"])
                else:
                    try:
                        ans = data['candidates'][0]['content']['parts'][0]['text']
                        g = data['candidates'][0].get('groundingMetadata', {}).get('searchEntryPoint', {}).get('renderedContent', "")
                        st.session_state.res_3 = (g, ans)
                    except: st.error("解析失败")
    if st.session_state.res_3:
        g, a = st.session_state.res_3
        if g: st.markdown(g, unsafe_allow_html=True)
        st.markdown(a)

# --- 谈判 ---
elif app_mode == MENU_OPTIONS[3]: 
    st.subheader("⛔ 谈判与异议粉碎机")
    col1, col2 = st.columns(2)
    with col1: obj = st.text_input("拒绝理由:")
    with col2: lev = st.text_input("我的优势 (留空则查记忆库):")
    if 'res_4' not in st.session_state: st.session_state.res_4 = None
    if st.button("💣 生成策略"):
        if obj:
            with st.spinner('思考中...'):
                # ⭐ 这里的写法改了，更安全，不容易被截断
                PROMPT = f"""
                {KB_INJECTION}
                Negotiation Coach. 
                Objection: '{obj}'
                Leverage: '{lev}'
                Provide 3 strategies.
                """
                st.session_state.res_4 = robust_generate(PROMPT, valid_model_name)
    if st.session_state.res_4: st.markdown(st.session_state.res_4)

# --- 售后 ---
elif app_mode == MENU_OPTIONS[4]:
    st.subheader("🛠️ 智能售后 & 问答")
    q = st.text_input("请输入问题:")
    if 'res_5' not in st.session_state: st.session_state.res_5 = None
    if st.button("🤖 提问"):
        if q:
            with st.spinner('查询中...'):
                PROMPT = f"""
                {KB_INJECTION}
                Role: Tech Support. Question: '{q}'
                Answer strictly based on data.
                """
                st.session_state.res_5 = robust_generate(PROMPT, valid_model_name)
    if st.session_state.res_5: st.markdown(st.session_state.res_5)
