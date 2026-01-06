import streamlit as st
from openai import OpenAI
import streamlit.components.v1 as components
import PyPDF2

# --- 配置区 ---
st.set_page_config(page_title="学术降维打击器", layout="wide", page_icon="🧠")

# ⚠️ 安全警告：在本地测试时，把你的真实Key填在这里。
# 上传到GitHub前，请务必改成 st.secrets["API_KEY"]，并在Streamlit Cloud设置Secrets。
# API_KEY = st.secrets["API_KEY"]
API_KEY = st.secrets["API_KEY"]  
client = OpenAI(api_key=API_KEY, base_url="https://api.deepseek.com")

# --- 核心提示词 ---
SYSTEM_PROMPT = """你是一个“降维打击”专家。任务是将复杂学术文本转化为：
1. 本质总结：用极简、幽默的大学生口语概括 3 个核心本质。
2. Mermaid 思维导图：输出一个清晰的 mindmap 语法代码块，确保节点简洁。
严禁复读原文术语，必须直击底层逻辑。"""

# --- 🔥 邀请码设置 (这里设置你的密码) 🔥 ---
# 你可以随时在这里修改密码，比如每天换一个
VALID_CODE = "SKKU2026"

# --- 主界面 ---
st.title("🧠 学术降维打击器 (内测版)")
st.caption("🚫 拒绝无效熬夜 | 把天书变成人话和导图")

# 侧边栏
with st.sidebar:
    st.write("## 💡 关于")
    st.info("这是一个专为被学术文献折磨的留学生开发的 AI 工具。")
    st.write("目前处于内测阶段，需要邀请码才能使用。")

# 文件上传
uploaded_file = st.file_uploader("📄 拖入你的 PDF 文件 (支持韩/英/中)", type="pdf")
user_input = st.text_area("或者直接粘贴文本内容", height=150)

# 提取文本
extracted_text = ""
if uploaded_file is not None:
    try:
        pdf_reader = PyPDF2.PdfReader(uploaded_file)
        for page in pdf_reader.pages:
            extracted_text += page.extract_text() or ""
        st.success(f"✅ 成功提取 {len(pdf_reader.pages)} 页内容！")
    except Exception as e:
        st.error(f"PDF 解析失败: {e}")
else:
    extracted_text = user_input

st.markdown("---")
st.write("### 🔐 身份验证")

# --- 🔥 核心修改：增加邀请码输入框 🔥 ---
invite_code = st.text_input("请输入内测邀请码 (必填)", type="password", placeholder="找开发者获取...")

# 执行按钮
if st.button("🚀 开始降维打击", type="primary", use_container_width=True):
    # --- 🔥 核心修改：检查邀请码 🔥 ---
    if invite_code != VALID_CODE:
        st.error("🚫 邀请码错误或已失效！请联系开发者获取最新内测码。")
        st.stop()  # 停止往下执行，保护 API

    if not extracted_text.strip():
        st.warning("请先上传 PDF 或输入文字内容！")
    else:
        with st.spinner("🧠 AI 大脑正在疯狂运转，正在暴力拆解知识点... (约需 10-20 秒)"):
            try:
                response = client.chat.completions.create(
                    model="deepseek-chat",
                    messages=[
                        {"role": "system", "content": SYSTEM_PROMPT},
                        # 截取前 1.2 万字，防止超长 PDF 爆 Token
                        {"role": "user", "content": extracted_text[:12000]}
                    ],
                    temperature=0.4  #稍微降低温度，让总结更准确
                )
                content = response.choices[0].message.content
                
                # 分隔总结和导图
                parts = content.split("## Part 2: 逻辑地图")
                
                col1, col2 = st.columns([2, 3]) # 左侧总结占2份，右侧导图占3份

                with col1:
                    st.subheader("📝 本质总结 (人话版)")
                    st.markdown(parts[0].replace("## Part 1: 本质总结（人话版）", "").strip())

                with col2:
                    st.subheader("🗺️ 逻辑思维导图")
                    if len(parts) > 1:
                        mermaid_code = parts[1].replace("```mermaid", "").replace("```", "").strip()
                        # 优化导图显示样式，增加边框和背景
                        components.html(
                            f"""
                            <div class="mermaid" style="background-color: #f8f9fa; padding: 20px; border-radius: 10px; border: 1px solid #e9ecef;">
                            {mermaid_code}
                            </div>
                            <script type="module">
                                import mermaid from 'https://cdn.jsdelivr.net/npm/mermaid@10/dist/mermaid.esm.min.mjs';
                                mermaid.initialize({{ startOnLoad: true, theme: 'base', securityLevel: 'loose' }});
                            </script>
                            """,
                            height=600,
                            scrolling=True
                        )
                    else:
                        st.info("AI 居然没生成导图，可能是内容太少，再试一次？")

            except Exception as e:
                st.error(f"发生错误，请检查网络或联系开发者：{e}")