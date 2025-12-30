import streamlit as st
import google.generativeai as genai
import requests
import json
import time

# ==========================================
# 1. 核心配置与初始化
# ==========================================
st.set_page_config(page_title="外贸数字指挥官 (全自动稳定版)", page_icon="🦁", layout="wide")

# 1.1 获取 API Key
try:
    api_key = st.secrets["GOOGLE_API_KEY"]
    genai.configure(api_key=api_key)
except Exception:
    st.error("⚠️ 未检测到 API Key，请在 Streamlit 后台 Secrets 里配置。")
    st.stop()

# ==========================================
# 2. 智能引擎锁定系统 (核心黑科技)
# ==========================================
@st.cache_resource
def auto_select_best_model():
    """
    自动测试并锁定一个最佳模型。
    优先级策略：
    1. 1.5-flash: 速度快，额度高，最适合大量使用。
    2. 1.5-flash-8b: 极速版，更便宜，额度更高。
    3. gemini-pro: 1.0版本，老黄牛，非常稳定。
    4. 2.5-flash: 最新版，但容易限流，作为最后备选。
    """
    candidates = [
        "models/gemini-1.5-flash",
        "models/gemini-1.5-flash-002", # 尝试特定版本号
        "models/gemini-1.5-flash-8b",
        "models/gemini-pro",
        "models/gemini-2.5-flash"
    ]
    
    print("正在进行模型自检...")
    for model_name in candidates:
        try:
            # 实弹测试：尝试生成一个字符
            model = genai.GenerativeModel(model_name)
            model.generate_content("t")
            print(f"✅ 锁定模型: {model_name}")
            return model_name
        except Exception as e:
            print(f"❌ {model_name} 不可用: {e}")
            continue
            
    # 如果全挂了（极小概率），返回一个默认值让它去报错
    return "models/gemini-1.5-flash"

# 启动时自动执行，用户无感知
valid_model_name = auto_select_best_model()

# ==========================================
# 3. 通用 API 请求函数 (用于联网搜索)
# ==========================================
def ask_ai_with_search(payload, model_name, api_key):
    """
    使用 REST API 直连 Google 服务器，绕过 Python 库的版本限制。
    专用于联网搜索功能。
    """
    url = f"https://generativelanguage.googleapis.com/v1beta/{model_name}:generateContent?key={api_key}"
    headers = {'Content-Type': 'application/json'}
    
    try:
        response = requests.post(url, headers=headers, data=json.dumps(payload), timeout=60)
        if response.status_code == 200:
            return response.json()
        else:
            return {"error": f"API请求失败: {response.status_code} - {response.text}"}
    except Exception as e:
        return {"error": f"网络连接错误: {str(e)}"}

# ==========================================
# 4. 界面侧边栏 (极简模式)
# ==========================================
st.sidebar.title("🦁 指挥官控制台")

# 只保留功能选择，不再显示复杂的模型切换
app_mode = st.sidebar.radio("任务选择：", [
    "📧 询盘分析", 
    "🕵️‍♂️ 文本背调", 
    "🌐 全网情报深挖 (联网)",
    "⛔ 谈判军师"
])

st.sidebar.markdown("---")
st.sidebar.success(f"⚡ 引擎状态: 🟢 在线\n🧠 内核: `{valid_model_name.split('/')[-1]}`")
st.sidebar.caption("已启用：智能防限流 & 自动缓存")

# ==========================================
# 5. 功能逻辑实现
# ==========================================

# --- 功能一：询盘深度分析 ---
if app_mode == "📧 询盘分析":
    st.subheader("📧 深度询盘分析")
    st.caption("适用场景：收到客户邮件，分析意图并生成回复。")
    
    user_input = st.text_area("粘贴邮件内容：", height=200)
    
    # 缓存初始化
    if 'email_res' not in st.session_state:
        st.session_state.email_res = None

    if st.button("🚀 开始分析"):
        if not user_input:
            st.warning("内容不能为空")
        else:
            with st.spinner('AI 正在分析...'):
                try:
                    model = genai.GenerativeModel(valid_model_name)
                    PROMPT = """
                    Act as an Expert Sales Manager. Analyze the following email.
                    
                    Output the following structured report:
                    1. **Language & Tone:** (e.g., Professional, Casual, Angry)
                    2. **Core Intent:** What do they really want?
                    3. **Lead Score (0-10):** How valuable is this lead?
                    4. **Key Info Extracted:** (Product, Quantity, Dates, etc.)
                    5. **Strategic Advice:** 2-3 bullet points on how to handle this.
                    6. **Draft Response (Dual Language):** - English Version (Professional)
                       - Native Language Explanation
                    """
                    response = model.generate_content(f"{PROMPT}\nInput Email: {user_input}")
                    st.session_state.email_res = response.text
                except Exception as e:
                    st.error(f"处理失败，请重试: {e}")

    # 显示结果（读取缓存）
    if st.session_state.email_res:
        st.markdown("---")
        st.markdown(st.session_state.email_res)

# --- 功能二：文本背调 ---
elif app_mode == "🕵️‍♂️ 文本背调":
    st.subheader("🕵️‍♂️ 网站文本分析")
    st.caption("适用场景：复制客户网站 'About Us' 页面文字，快速了解客户背景。")
    
    bg_input = st.text_area("粘贴网站文本：", height=300)
    
    if 'bg_res' not in st.session_state:
        st.session_state.bg_res = None
        
    if st.button("🔍 开始侦查"):
        if not bg_input:
            st.warning("请粘贴文本")
        else:
            with st.spinner('侦探正在分析...'):
                try:
                    model = genai.GenerativeModel(valid_model_name)
                    PROMPT = """
                    Analyze this company text and provide a B2B report:
                    1. **Company Identity:** (Manufacturer? Distributor? Retailer?)
                    2. **Scale & Market:** Global or Local? High-end or Budget?
                    3. **Potential Pain Points:** What problems might they have?
                    4. **Pitch Strategy:** How should I sell to them?
                    """
                    response = model.generate_content(f"{PROMPT}\nText: {bg_input}")
                    st.session_state.bg_res = response.text
                except Exception as e:
                    st.error(f"出错: {e}")

    if st.session_state.bg_res:
        st.markdown("---")
        st.markdown(st.session_state.bg_res)

# --- 功能三：全网深挖 (联网直连版) ---
elif app_mode == "🌐 全网情报深挖 (联网)":
    st.subheader("🌐 全网深度商业情报 (Google Search)")
    st.caption("💡 自动调用 Google 搜索，挖掘官网之外的隐秘信息。")
    
    search_query = st.text_input("输入客户公司名 或 网址：", placeholder="例如：Home Depot")
    
    if 'search_res' not in st.session_state:
        st.session_state.search_res = None
    
    if st.button("🌍 启动深度挖掘"):
        if not search_query:
            st.warning("请输入关键词")
        else:
            # 清空旧缓存，强制刷新
            st.session_state.search_res = None
            
            with st.spinner('正在全网检索情报 (约需 10-15 秒)...'):
                # 构造超级 Prompt
                prompt_text = f"""
                Role: Senior B2B Market Intelligence Analyst.
                Task: Use Google Search to investigate: "{search_query}".
                
                Produce a "Deep-Dive Intelligence Report":
                1. **🏢 True Business Identity:** Verify if they are a Factory, Wholesaler, or Retailer.
                2. **🎯 Strategic Radar:** Any recent news? (Expansions, layoffs, new product lines).
                3. **🛒 Procurement Profile:** Based on their products, do they care more about Price or Quality?
                4. **⚔️ Competitors:** Who are they fighting against?
                5. **⚡ Cold Email Hook:** Write 1 powerful opening sentence referencing recent news.
                """
                
                # 构造 API 请求体
                payload = {
                    "contents": [{"parts": [{"text": prompt_text}]}],
                    "tools": [{"google_search": {}}]
                }
                
                # 调用直连函数
                data = ask_ai_with_search(payload, valid_model_name, api_key)
                
                # 解析数据
                if "error" in data:
                    st.error(data["error"])
                else:
                    try:
                        # 提取回答文本
                        ans = data['candidates'][0]['content']['parts'][0]['text']
                        
                        # 尝试提取引用来源 (Grounding)
                        grounding = ""
                        try:
                            grounding = data['candidates'][0]['groundingMetadata']['searchEntryPoint']['renderedContent']
                        except:
                            pass
                        
                        st.session_state.search_res = (grounding, ans)
                        
                    except (KeyError, IndexError):
                        st.error("搜索成功，但AI未能生成有效文本，请重试。")

    # 显示结果
    if st.session_state.search_res:
        grounding_html, answer_text = st.session_state.search_res
        st.success("✅ 情报挖掘完成")
        if grounding_html:
            st.markdown(grounding_html, unsafe_allow_html=True)
        st.markdown(answer_text)

# --- 功能四：谈判军师 ---
elif app_mode == "⛔ 谈判军师":
    st.subheader("⛔ B2B 异议粉碎机")
    st.caption("场景：客户嫌贵、嫌量大。让 AI 给你 3 种回击策略。")
    
    if 'neg_res' not in st.session_state:
        st.session_state.neg_res = None

    c1, c2 = st.columns(2)
    with c1:
        objection = st.text_input("客户拒绝理由:", placeholder="例如：Your price is too high.")
    with c2:
        leverage = st.text_input("我的优势 (可选):", placeholder="例如：Top quality, fast delivery.")
        
    if st.button("💣 生成策略"):
        if not objection:
            st.warning("请输入客户的拒绝理由")
        else:
            with st.spinner('军师正在思考...'):
                try:
                    model = genai.GenerativeModel(valid_model_name)
                    PROMPT = f"""
                    You are a Harvard Negotiation Coach.
                    The Client says: "{objection}"
                    My Leverage: "{leverage}"
                    
                    Provide 3 distinct strategies to overcome this objection:
                    1. **The Value Pivot** (Logic & ROI)
                    2. **The Empathy & Probe** (Psychology)
                    3. **The Alternative Option** (Flexibility)
                    
                    Include exact English email scripts for each.
                    """
                    response = model.generate_content(PROMPT)
                    st.session_state.neg_res = response.text
                except Exception as e:
                    st.error(f"出错: {e}")

    if st.session_state.neg_res:
        st.markdown("---")
        st.markdown(st.session_state.neg_res)
