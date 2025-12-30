import streamlit as st
import google.generativeai as genai

# ==========================================
# 1. 核心配置
# ==========================================
st.set_page_config(page_title="外贸数字指挥官 (联网修复版)", page_icon="🌍", layout="wide")

try:
    api_key = st.secrets["GOOGLE_API_KEY"]
    genai.configure(api_key=api_key)
except Exception:
    st.error("⚠️ 未检测到 API Key，请在 Streamlit 后台配置。")
    st.stop()

# ==========================================
# 2. 模型自检 (Self-Healing)
# ==========================================
@st.cache_resource
def find_working_model():
    # 既然你之前的截图证明 2.5-flash 能用，我们把它放第一位
    candidates = [
        "models/gemini-2.5-flash",    
        "models/gemini-1.5-pro",
        "models/gemini-1.5-flash",
    ]
    for model_name in candidates:
        try:
            model = genai.GenerativeModel(model_name)
            response = model.generate_content("Hi")
            if response.text:
                return model_name
        except:
            continue
    return None

with st.spinner("正在连接 Google AI 大脑..."):
    valid_model_name = find_working_model()

if not valid_model_name:
    st.error("❌ 无法连接任何模型。")
    st.stop()

# ==========================================
# 3. 联网搜索工具配置 (修复重点!)
# ==========================================
def get_search_model():
    try:
        # ⚠️ 修复：根据报错提示，改用最简单的 'google_search' 声明
        # 不再使用复杂的 google_search_retrieval 字典
        tools = [{"google_search": {}}] 
        return genai.GenerativeModel(valid_model_name, tools=tools)
    except Exception:
        return None

# ==========================================
# 4. 侧边栏
# ==========================================
st.sidebar.title("🌍 指挥官控制台")
app_mode = st.sidebar.radio("任务选择：", [
    "📧 询盘深度分析", 
    "🕵️‍♂️ 粘贴文本背调 (稳)", 
    "🌐 全网背景深挖 (联网版)" 
])
st.sidebar.markdown("---")
st.sidebar.success(f"🚀 引擎在线: `{valid_model_name}`")

# ==========================================
# 5. 功能逻辑
# ==========================================

# --- 功能一：询盘分析 ---
if app_mode == "📧 询盘深度分析":
    st.title("📧 深度询盘分析")
    user_input = st.text_area("请粘贴客户邮件：", height=200)
    if st.button("🚀 分析"):
        if not user_input:
            st.warning("请输入内容")
        else:
            with st.spinner('AI 正在思考...'):
                try:
                    model = genai.GenerativeModel(valid_model_name)
                    PROMPT = """
                    Act as an Expert Sales Manager. Analyze this email.
                    Output: 1.Language 2.Intent 3.Lead Score(0-10) 4.Key Info 5.Draft Response(Dual Language).
                    """
                    response = model.generate_content(f"{PROMPT}\nInput: {user_input}")
                    st.markdown(response.text)
                except Exception as e:
                    st.error(f"出错: {e}")

# --- 功能二：文本背调 (稳) ---
elif app_mode == "🕵️‍♂️ 粘贴文本背调 (稳)":
    st.title("🕵️‍♂️ 静态背景侦探")
    st.caption("适用场景：你已经打开了客户网站，复制了 'About Us' 的文字。")
    bg_input = st.text_area("粘贴网站文本：", height=300)
    if st.button("🔍 侦查"):
        if not bg_input:
            st.warning("请粘贴文本")
        else:
            with st.spinner('分析中...'):
                try:
                    model = genai.GenerativeModel(valid_model_name)
                    PROMPT = """
                    Analyze this company text. Report:
                    1. Identity (Wholesaler/Builder/End User?) 2. Scale 3. Pain Points 4. Pitch Strategy.
                    """
                    response = model.generate_content(f"{PROMPT}\nText: {bg_input}")
                    st.markdown(response.text)
                except Exception as e:
                    st.error(f"出错: {e}")

# --- 功能三：全网深挖 (联网!) ---
elif app_mode == "🌐 全网背景深挖 (联网版)":
    st.title("🌐 全网背景深挖 (Google Search)")
    st.info("💡 提示：此功能通过 Google Search 获取最新信息。")
    
    search_query = st.text_input("输入客户公司名：", placeholder="例如：Costco Wholesale")
    
    if st.button("🌍 联网搜索分析"):
        if not search_query:
            st.warning("请输入公司名！")
        else:
            with st.spinner('正在连接 Google 搜索互联网...'):
                try:
                    search_model = get_search_model()
                    if not search_model:
                        st.error("无法加载搜索工具。")
                    else:
                        SEARCH_PROMPT = f"""
                        Search Google for "{search_query}" to generate a B2B investigation report.
                        
                        Include:
                        1. **Company Overview:** What do they do? (Distributor/Retailer?)
                        2. **Key Products/Services:**
                        3. **Size & Location:**
                        4. **Latest News:** Any recent projects?
                        5. **Website:** Their official URL if found.
                        """
                        
                        # 这里的 key 改得非常简单，直接发 prompt，让工具自己跑
                        response = search_model.generate_content(SEARCH_PROMPT)
                        
                        # 尝试显示引用来源
                        try:
                            grounding = response.candidates[0].grounding_metadata
                            if grounding.search_entry_point:
                                st.success("✅ 数据来源：Google Search")
                                st.markdown(grounding.search_entry_point.rendered_content)
                        except:
                            pass
                            
                        st.markdown(response.text)
                        
                except Exception as e:
                    st.error(f"出错: {e}")
                    st.caption("如果还是报错 400，说明 2.5-flash 模型暂时还不支持免费 API 进行搜索。请使用功能二。")
