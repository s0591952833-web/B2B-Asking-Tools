import streamlit as st
import google.generativeai as genai
import requests
import json
import time
import pypdf
import os

# ==========================================
# 1. 核心配置与记忆文件设置
# ==========================================
st.set_page_config(page_title="外贸数字指挥官 (长期记忆版)", page_icon="🦁", layout="wide")

# 定义记忆文件存储路径 (在同级目录下生成一个 json 文件)
MEMORY_FILE = "b2b_kb_memory.json"

try:
    api_key = st.secrets["GOOGLE_API_KEY"]
    genai.configure(api_key=api_key)
except Exception:
    st.error("⚠️ 未检测到 API Key，请配置 Secrets。")
    st.stop()

# ==========================================
# 2. 记忆系统核心函数 (读写硬盘)
# ==========================================
def load_memory():
    """从硬盘读取记忆"""
    if os.path.exists(MEMORY_FILE):
        try:
            with open(MEMORY_FILE, "r", encoding="utf-8") as f:
                return json.load(f).get("text", "")
        except:
            return ""
    return ""

def save_memory(new_text):
    """保存记忆到硬盘 (增量更新)"""
    current_text = load_memory()
    # 避免重复保存相同内容 (简单去重)
    if new_text not in current_text:
        updated_text = current_text + "\n" + new_text
        with open(MEMORY_FILE, "w", encoding="utf-8") as f:
            json.dump({"text": updated_text}, f, ensure_ascii=False)
        return True
    return False

def clear_memory():
    """彻底清空记忆"""
    if os.path.exists(MEMORY_FILE):
        os.remove(MEMORY_FILE)

# ==========================================
# 3. 智能引擎与抗压系统
# ==========================================
@st.cache_resource
def get_best_model():
    return "models/gemini-2.5-flash"

valid_model_name = get_best_model()

def robust_generate(prompt, model_name):
    model = genai.GenerativeModel(model_name)
    for i in range(3):
        try:
            response = model.generate_content(prompt)
            return response.text
        except Exception as e:
            if "429" in str(e):
                time.sleep(5)
                continue
            else:
                return f"❌ 错误: {str(e)}"
    return "⚠️ 系统繁忙，请稍后重试。"

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
# 4. 侧边栏：记忆管理控制台
# ==========================================
st.sidebar.title("🦁 控制台")

st.sidebar.markdown("### 🧠 长期记忆库")

# A. 初始化：读取现有记忆
current_memory = load_memory()
memory_status = "🟢 记忆已激活" if current_memory else "⚪ 记忆为空"
st.sidebar.caption(f"状态: {memory_status}")

if current_memory:
    st.sidebar.info(f"✅ 已加载过往资料 ({len(current_memory)} 字)")
    with st.sidebar.expander("查看当前记忆内容"):
        st.text(current_memory[:500] + "...") # 只显示前500字预览

# B. 投喂新资料
st.sidebar.markdown("---")
st.sidebar.write("📤 **追加新资料:**")

# 1. 文本投喂
new_kb_text = st.sidebar.text_area("粘贴新文本:", height=70, placeholder="粘贴补充的产品参数...")
if st.sidebar.button("💾 保存文本到记忆"):
    if new_kb_text:
        save_memory(new_kb_text)
        st.sidebar.success("已存入大脑！请刷新页面生效。")
        time.sleep(1)
        st.rerun()

# 2. 文件投喂 (PDF)
uploaded_file = st.sidebar.file_uploader("上传新 PDF:", type=['pdf'], key="pdf_uploader")
if uploaded_file is not None:
    try:
        reader = pypdf.PdfReader(uploaded_file)
        pdf_text = ""
        for page in reader.pages:
            pdf_text += page.extract_text() + "\n"
        
        # 自动保存
        if save_memory(pdf_text):
            st.sidebar.success(f"✅ PDF '{uploaded_file.name}' 已存入长期记忆！")
            time.sleep(1)
            st.rerun() # 自动刷新页面以更新状态
    except Exception as e:
        st.sidebar.error("PDF 读取失败")

# C. 清空记忆
st.sidebar.markdown("---")
if st.sidebar.button("🗑️ 格式化/清空所有记忆"):
    clear_memory()
    st.sidebar.warning("记忆已擦除。")
    time.sleep(1)
    st.rerun()

# ==========================================
# 5. 功能菜单 (注入长期记忆)
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

# 构造注入 Prompt (使用长期记忆)
KB_INJECTION = ""
if current_memory:
    KB_INJECTION = f"""
    [IMPORTANT: LONG-TERM COMPANY KNOWLEDGE BASE]
    You have access to the following internal product data/files stored in your memory.
    ALWAYS strictly verify your answers against this data. Do not hallucinate product specs.
    
    {current_memory}
    [END OF KNOWLEDGE BASE]
    """

# ==========================================
# 6. 功能逻辑实现
# ==========================================

# --- 功能一: 询盘分析 ---
if app_mode == MENU_OPTIONS[0]: 
    st.subheader("📧 深度询盘分析")
    st.caption("AI 将基于【长期记忆】中的产品库生成回复。")
    user_input = st.text_area("粘贴客户邮件：", height=200)
    
    if 'res_1' not in st.session_state: st.session_state.res_1 = None
    if st.button("🚀 分析邮件"):
        if not user_input: st.warning("请粘贴内容")
        else:
            with st.spinner('正在调取记忆库分析...'):
                PROMPT = f"""
                {KB_INJECTION}
                Act as Sales Manager. Analyze email. 
                If the user asks about products mentioned in the Knowledge Base, use the specific specs/price to answer.
                Output: Language, Intent, Score, Advice, Draft Response.
                """
                res = robust_generate(f"{PROMPT}\nInput: {user_input}", valid_model_name)
                st.session_state.res_1 = res
    if st.session_state.res_1: st.markdown(st.session_state.res_1)

# --- 功能二: 文本背调 ---
elif app_mode == MENU_OPTIONS[1]: 
    st.subheader("🕵️‍♂️ 网站文本分析")
    bg_input = st.text_area("粘贴网站文本：", height=200)
    
    if 'res_2' not in st.session_state: st.session_state.res_2 = None
    if st.button("🔍 分析背景"):
        if not bg_input: st.warning("请粘贴内容")
        else:
            with st.spinner('分析中...'):
                PROMPT = "Analyze company text. Output: Identity, Scale, Pain Points, Pitch Strategy."
                res = robust_generate(f"{PROMPT}\nText: {bg_input}", valid_model_name)
                st.session_state.res_2 = res
    if st.session_state.res_2: st.markdown(st.session_state.res_2)

# --- 功能三: 全网深挖 ---
elif app_mode == MENU_OPTIONS[2]: 
    st.subheader("🌐 全网商业情报")
    query = st.text_input("公司名/关键词：")
    
    if 'res_3' not in st.session_state: st.session_state.res_3 = None
    if st.button("🌍 深度挖掘"):
        if not query: st.warning("请输入关键词")
        else:
            st.session_state.res_3 = None
            with st.spinner('全网检索中...'):
                prompt = f"""
                Role: Senior B2B Analyst. Search: "{query}".
                Report: 1. Identity 2. Latest News 3. Procurement Prediction 4. Competitors 5. Cold Email Hook.
                """
                payload = {"contents": [{"parts": [{"text": prompt}]}], "tools": [{"google_search": {}}]}
                data = robust_api_search(payload, valid_model_name, api_key)
                
                if "error" in data: st.error(data["error"])
                else:
                    try:
                        ans = data['candidates'][0]['content']['parts'][0]['text']
                        grounding = ""
                        try: grounding = data['candidates'][0]['groundingMetadata']['searchEntryPoint']['renderedContent']
                        except: pass
                        st.session_state.res_3 = (grounding, ans)
                    except: st.error("解析失败")
    if st.session_state.res_3:
        g, a = st.session_state.res_3
        if g: st.markdown(g, unsafe_allow_html=True)
        st.markdown(a)

# --- 功能四: 谈判 ---
elif app_mode == MENU_OPTIONS[3]: 
    st.subheader("⛔ 谈判与异议粉碎机")
    st.caption("AI 将利用记忆中的产品优势来反击客户。")
    
    col1, col2 = st.columns(2)
    with col1: obj = st.text_input("拒绝理由:", placeholder="Price too high")
    with col2: lev = st.text_input("我的优势 (留空则自动读取记忆库):")
    
    if 'res_4' not in st.session_state: st.session_state.res_4 = None
    if st.button("💣 生成策略"):
        if not obj: st.warning("请输入拒绝理由")
        else:
            with st.spinner('军师正在查阅记忆...'):
                PROMPT = f"""
                {KB_INJECTION}
                Negotiation Coach. Objection: "{obj}". 
                Context/Leverage: "{lev}" (If empty, use Knowledge Base info).
                Provide 3 strategies (Value, Empathy, Alternative).
                """
                res = robust_generate(PROMPT, valid_model_name)
                st.session_state.res_4 = res
    if st.session_state.res_4: st.markdown(st.session_state.res_4)

# --- 功能五: 售后 (新) ---
elif app_mode == MENU_OPTIONS[4]:
    st.subheader("🛠️ 智能售后 & 产品专家问答")
    
    if not current_memory:
        st.warning("⚠️ 记忆库为空！请先在左侧上传 PDF 或粘贴资料。")
    else:
        st.success("✅ 记忆库在线。AI 已熟读你投喂的所有资料。")
        
    question = st.text_input("请输入问题 (关于产品/售后/参数):")
    
    if 'res_5' not in st.session_state: st.session_state.res_5 = None
    
    if st.button("🤖 提问"):
        if not question: st.warning("请输入问题")
        else:
            with st.spinner('正在回忆内部资料...'):
                PROMPT = f"""
                {KB_INJECTION}
                Role: Senior Technical Support & Product Expert.
                User Question: "{question}"
                
                Task: Answer the question strictly based on the provided [LONG-TERM KNOWLEDGE BASE]. 
                If the answer is found, explain it clearly.
                """
                res = robust_generate(PROMPT, valid_model_name)
                st.session_state.res_5 = res
                
    if st.session_state.res_5:
        st.markdown("---")
        st.markdown(st.session_state.res_5)
