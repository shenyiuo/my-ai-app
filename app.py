import streamlit as st
from openai import OpenAI
import streamlit.components.v1 as components
import PyPDF2

# --- 配置区 ---
st.set_page_config(page_title="学术降维打击器", layout="wide", page_icon="🧠")

# API 安全设置
# 上传到 GitHub 前请确保 Secrets 里有 API_KEY 
try:
    API_KEY = st.secrets["API_KEY"]
except:
    API_KEY = "你的_DEEPSEEK_API_KEY" # 本地测试用

client = OpenAI(api_key=API_KEY, base_url="https://api.deepseek.com")

# --- 核心提示词 ---
SYSTEM_PROMPT = """你是一个“降维打击”专家。任务是将复杂学术文本转化为：
1. 本质总结：用极简、幽默的大学生口语概括 3 个核心本质。
2. Mermaid 思维导图：输出一个清晰的 mindmap 语法代码块。
要求：严禁复读原文，必须把学术黑话转化为直击底层的逻辑。"""

# --- 邀请码设置 ---
VALID_CODE = "SKKU2026"

# --- 主界面 ---
st.title("🧠 学术降维打击器 (Winter Session 内测版)")
st.caption("🚀 专门暴力拆解不说人话的 PDF 讲义 | 目前仅限假期课核心成员使用")

# 侧边栏：注意事项
with st.sidebar:
    st.header("📋 内测协议 (必读)")
    st.warning("""
    **有效反馈要求：**
    1. **拒绝赞美**：不要说“好用”，请说“哪里总结得不够深”。
    2. **纠正逻辑**：如果导图的分支层级错了，请截图告知。
    3. **术语挑刺**：如果 AI 对韩文/英文术语的转换不专业，请直接指出。
    
    *你的反馈质量决定了下个版本的迭代方向。*
    """)

# 1. 身份验证
st.write("### 🔐 权限开启")
invite_code = st.text_input("请输入邀请码以解锁降维打击能力", type="password")

if not invite_code:
    st.info("💡 请向开发者申请内测邀请码，并承诺提供有效反馈。")
    st.stop()

if invite_code != VALID_CODE:
    st.error("🚫 验证失败：邀请码无效或已过期。")
    st.stop()

# 验证通过后显示功能区
st.success("🔓 身份验证成功。请遵守内测协议，提供高质量逻辑反馈。")

st.markdown("---")

# 2. 核心功能区
col_input, col_info = st.columns([2, 1])

with col_input:
    uploaded_file = st.file_uploader("📄 上传你的学术 PDF (支持多语言)", type="pdf")
    user_input = st.text_area("或者直接粘贴天体文本", height=100, placeholder="在此粘贴那些让你头大的文字...")

with col_info:
    st.write("### 🛠️ 正在解决的痛点：")
    st.markdown("""
    - **查词地狱**：不再需要盯着翻译器看半天。
    - **逻辑断层**：一眼看穿教授的思维骨架。
    - **期末焦虑**：把 50 页降维成 1 张图。
    """)

# 提取文本逻辑
extracted_text = ""
if uploaded_file:
    pdf_reader = PyPDF2.PdfReader(uploaded_file)
    for page in pdf_reader.pages:
        extracted_text += page.extract_text() or ""
else:
    extracted_text = user_input

# 3. 执行降维打击
if st.button("🔥 开始降维打击 (消耗 API 额度)", type="primary", use_container_width=True):
    if not extracted_text.strip():
        st.warning("内容为空，你想打击空气吗？")
    else:
        with st.spinner("AI 正在暴力拆解知识骨架..."):
            try:
                # 调用 DeepSeek API
                response = client.chat.completions.create(
                    model="deepseek-chat",
                    messages=[
                        {"role": "system", "content": SYSTEM_PROMPT},
                        {"role": "user", "content": extracted_text[:12000]}
                    ]
                )
                res_content = response.choices[0].message.content
                
                # 渲染结果
                st.markdown("---")
                c1, c2 = st.columns([1, 1])
                
                with c1:
                    st.subheader("📝 本质总结")
                    st.write(res_content.split("```")[0]) # 粗略截取非代码部分
                
                with c2:
                    st.subheader("🗺️ 逻辑地图")
                    if "```mermaid" in res_content:
                        m_code = res_content.split("```mermaid")[1].split("```")[0].strip()
                        components.html(
                            f"""
                            <pre class="mermaid" style="background:#f9f9f9; padding:10px; border-radius:5px;">
                            {m_code}
                            </pre>
                            <script type="module">
                                import mermaid from 'https://cdn.jsdelivr.net/npm/mermaid@10/dist/mermaid.esm.min.mjs';
                                mermaid.initialize({{ startOnLoad: true, theme: 'neutral' }});
                            </script>
                            """,
                            height=500, scrolling=True
                        )
            except Exception as e:
                st.error(f"大脑离线中: {e}")