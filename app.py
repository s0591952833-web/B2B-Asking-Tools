import streamlit as st
import google.generativeai as genai

# ==========================================
# 1. 核心配置与 API 连接
# ==========================================
st.set_page_config(page_title="外贸数字指挥官 (终极诊断版)", page_icon="🦁", layout="wide")

try:
    api_key = st.secrets["GOOGLE_API_KEY"]
    genai.configure(api_key=api_key)
except Exception:
    st.error("⚠️ 未检测到 API Key，请在 Streamlit 后台 Secrets 里配置。")
    st.stop()

# ==========================================
# 2. 自动寻找可用模型 (自愈系统)
# ==========================================
@st.cache_resource
def find_working_model():
    # 优先尝试你之前验证成功的 2.5-flash
    candidates = [
        "models/gemini-2.5-flash",
        "models/gemini-1.5-pro",
        "models/gemini-1.5-flash",
        "models/gemini-pro",
    ]
    
    for model_name in candidates:
        try:
            # 实弹测试：真的生成一句话试试
            model = genai.GenerativeModel(model_name)
            response = model.generate_content("Hi")
            if response.text:
                return model_name
        except:
            continue
    return None

# 获取经过验证的模型
with st.spinner("系统自检中，正在寻找最佳模型..."):
    valid_model_name = find_working_model()

if not valid_model_name:
    st.error("❌ 无法找到任何可用的模型。请检查 API Key 额度。")
    st.stop()

# ==========================================
# 3. 联网搜索工具配置 (带详细报错)
# ==========================================
def get_search_model():
    try:
        # 尝试加载 Google 搜索工具
        # 使用最新的工具定义语法
        tools = [{"google_search": {}}] 
        return genai.GenerativeModel(valid_model_name, tools=tools)
    except Exception as e:
        # ⚠️ 这里是关键！如果加载失败，直接把错误原因打印在屏幕上
        st.error(f"❌ 联网工具加载失败，报错详情：\n{str(e)}")
        return None

# ==========================================
# 4. 侧边栏界面
# ==========================================
st.sidebar.title("🦁 指挥官控制台")
app_mode = st.sidebar.radio("任务选择：", [
    "📧 询盘深度分析", 
    "🕵️‍♂️ 粘贴文本背调 (稳)", 
    "🌐 全网背景深挖 (联网版)" 
])
st.sidebar.markdown("---")

# 显示当前使用的模型
if "pro" in valid_model_name.lower():
    st.sidebar.success(f"🧠 深度模式 (Pro)\n引擎: `{valid_model_name}`")
elif "2.5" in valid_model_name:
    st.sidebar.success(f"🚀 最新极速版 (2.5)\n引擎: `{valid_model_name}`")
else:
    st.sidebar.info(f"⚡ 稳定极速版\n引擎: `{valid_model_name}`")

# ==========================================
# 5. 功能逻辑实现
# ==========================================

# --- 功能一：询盘分析 ---
if app_mode == "📧 询盘深度分析":
    st.title("📧 深度询盘分析")
    user_input = st.text_area("请粘贴客户邮件：", height=200)
    
    if st.button("🚀 开始分析"):
        if not user_input:
            st.warning("请输入内容")
        else:
            with st.spinner(f'AI ({valid_model_name}) 正在分析...'):
                try:
                    model = genai.GenerativeModel(valid_model_name)
                    PROMPT = """
                    Act as an Expert Sales Manager. Analyze this email.
                    Output structured report: 1.Language 2.Intent 3.Lead Score(0-10) 4.Key Info 5.Draft Response(Dual Language).
                    """
                    response = model.generate_content(f"{PROMPT}\nInput: {user_input}")
                    st.success("分析完成！")
                    st.markdown(response.text)
                except Exception as e:
                    st.error(f"发生错误: {e}")

# --- 功能二：文本背调 (稳) ---
elif app_mode == "🕵️‍♂️ 粘贴文本背调 (稳)":
    st.title("🕵️‍♂️ 静态背景侦探")
    st.caption("适用场景：手动复制客户网站的 About Us 文本。")
    bg_input = st.text_area("请粘贴网站文本：", height=300)
    
    if st.button("🔍 开始侦查"):
        if not bg_input:
            st.warning("请粘贴文本")
        else:
            with st.spinner('侦探正在分析...'):
                try:
                    model = genai.GenerativeModel(valid_model_name)
                    PROMPT = """
                    Analyze this company text. Report:
                    1. Identity (Wholesaler/Builder/End User?) 2. Scale 3. Pain Points 4. Pitch Strategy.
                    """
                    response = model.generate_content(f"{PROMPT}\nText: {bg_input}")
                    st.success("报告已生成！")
                    st.markdown(response.text)
                except Exception as e:
                    st.error(f"发生错误: {e}")

# --- 功能三：全网深挖 (调试重点) ---
elif app_mode == "🌐 全网背景深挖 (联网版)":
    st.title("🌐 全网背景深挖 (Google Search)")
    st.info("💡 提示：此功能尝试调用 Google 搜索权限。")
    
    search_query = st.text_input("输入客户公司名 或 网址：", placeholder="例如：Costco Wholesale")
    
    if st.button("🌍 联网搜索分析"):
        if not search_query:
            st.warning("请输入公司名！")
        else:
            with st.spinner('正在连接 Google 搜索互联网...'):
                search_model = get_search_model() # 尝试加载带工具的模型
                
                if search_model:
                    try:
                        SEARCH_PROMPT = f"""
                        Use Google Search to find info about: "{search_query}".
                        Write a B2B investigation report:
                        1. Business Type 2. Key Products 3. Size & Location 4. Latest News 5. Website URL.
                        """
                        response = search_model.generate_content(SEARCH_PROMPT)
                        
                        # 显示搜索来源（如果有）
                        try:
                            grounding = response.candidates[0].grounding_metadata
                            if grounding.search_entry_point:
                                st.success("✅ 数据来源：Google Search")
                                st.markdown(grounding.search_entry_point.rendered_content)
                        except:
                            pass
                        
                        st.markdown(response.text)
                    except Exception as e:
                        st.error(f"❌ 搜索过程中报错: {str(e)}")
                else:
                    st.warning("由于工具加载失败，无法执行搜索。请查看上方的红色报错信息。")
