import streamlit as st
from openai import OpenAI
import streamlit.components.v1 as components
import PyPDF2  # 新增：用于解析 PDF

# --- 配置区 ---
st.set_page_config(page_title="降维打击：本质萃取器", layout="wide")
API_KEY = st.secrets["API_KEY"]
client = OpenAI(api_key=API_KEY, base_url="https://api.deepseek.com")

SYSTEM_PROMPT = """你是一个“降维打击”专家。任务是将复杂文本转化为：
1. 本质总结：用极简、幽默的“人话”概括 3 个核心本质。
2. Mermaid 思维导图：输出一个清晰的 mindmap 语法代码块。
严禁复读原文术语，必须直击底层逻辑。"""

# --- 侧边栏：管理后台 ---
with st.sidebar:
    st.title("⚙️ 管理后台")
    admin_key = st.text_input("管理员口令", type="password")
    if admin_key == "123456":
        st.write("🔧 运行正常")
    else:
        st.info("输入口令解锁更多功能")

# --- 主界面 ---
st.title("🧠 知识降维打击器")
st.caption("上传 PDF 或直接粘贴，把晦涩内容变成三句话和一张图")

# 新增：文件上传组件
uploaded_file = st.file_uploader("点击上传 PDF 文件", type="pdf")

# 文本输入框（如果没有上传文件，可以手动粘贴）
user_input = st.text_area("或者在这里粘贴文字内容", height=200)

# --- 提取文本的逻辑 ---
extracted_text = ""
if uploaded_file is not None:
    # 解析 PDF
    pdf_reader = PyPDF2.PdfReader(uploaded_file)
    for page in pdf_reader.pages:
        extracted_text += page.extract_text()
    st.success("✅ PDF 文本提取成功！")
else:
    extracted_text = user_input

# --- 执行按钮 ---
if st.button("开始降维打击", type="primary"):
    if not extracted_text:
        st.warning("请先上传文件或输入文字！")
    else:
        with st.spinner("正在暴力拆解知识点..."):
            try:
                response = client.chat.completions.create(
                    model="deepseek-chat",
                    messages=[
                        {"role": "system", "content": SYSTEM_PROMPT},
                        {"role": "user", "content": extracted_text[:10000]} # 截取前1万字防止爆Token
                    ]
                )
                content = response.choices[0].message.content
                
                # 分隔总结和导图
                parts = content.split("## Part 2: 逻辑地图")
                st.markdown(parts[0])
                
                if len(parts) > 1:
                    mermaid_code = parts[1].replace("```mermaid", "").replace("```", "").strip()
                    components.html(
                        f"""
                        <div class="mermaid" style="background-color: white;">
                        {mermaid_code}
                        </div>
                        <script type="module">
                            import mermaid from 'https://cdn.jsdelivr.net/npm/mermaid@10/dist/mermaid.esm.min.mjs';
                            mermaid.initialize({{ startOnLoad: true, theme: 'default' }});
                        </script>
                        """,
                        height=600,
                        scrolling=True
                    )
            except Exception as e:
                st.error(f"出错了：{e}")