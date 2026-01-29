import streamlit as st
# Import các hàm từ file khác
from utils import render_mermaid, extract_mermaid_code
from ai_service import call_ai_update

# --- Cấu hình Trang ---
st.set_page_config(layout="wide", page_title="Mermaid AI Visualizer", page_icon="🧜‍♀️")

# --- Sidebar: Cấu hình ---
with st.sidebar:
    st.header("🤖 Cấu Hình OpenRouter")
    api_key = st.text_input("API Key", type="password")
    model_name = st.text_input("Model", value="openai/gpt-3.5-turbo")
    st.markdown("---")
    temperature = st.slider("Temperature", 0.0, 2.0, 0.7)
    top_p = st.slider("Top P", 0.0, 1.0, 1.0)

# --- Main Interface ---
st.title("🧜‍♀️ Mermaid AI Visualizer")
st.markdown("Upload file `.md` -> AI Vẽ -> Trực quan hoá")

# State Management
if 'mermaid_code' not in st.session_state:
    st.session_state.mermaid_code = "graph TD;\n    A[Start] --> B[End];"

# 1. Upload
uploaded_file = st.file_uploader("📂 Tải lên file Markdown (.md)", type=["md"])
if uploaded_file:
    string_data = uploaded_file.getvalue().decode("utf-8")
    extracted = extract_mermaid_code(string_data)
    
    if extracted:
        # Chỉ update nếu file mới khác file cũ
        if 'last_filename' not in st.session_state or st.session_state.last_filename != uploaded_file.name:
            st.session_state.mermaid_code = extracted
            st.session_state.last_filename = uploaded_file.name
            st.toast("Đã tải code thành công!", icon="✅")
    else:
        st.warning("Không tìm thấy block mermaid trong file.")

# 2. Main Layout
col1, col2 = st.columns([1, 1])

with col1:
    st.subheader("📝 Prompt")
    user_request = st.text_area("Yêu cầu sửa đổi:", height=150)
    
    if st.button("✨ Chạy AI", type="primary"):
        if not api_key:
            st.error("Thiếu API Key!")
        else:
            with st.spinner("Đang xử lý..."):
                new_code = call_ai_update(
                    st.session_state.mermaid_code,
                    user_request,
                    api_key, model_name, temperature, top_p
                )
                if new_code.startswith("Error"):
                    st.error(new_code)
                else:
                    st.session_state.mermaid_code = new_code
                    st.success("Xong!")

    st.markdown("### Code Editor")
    # Cho phép sửa tay nếu muốn
    st.session_state.mermaid_code = st.text_area("Mermaid Code", st.session_state.mermaid_code, height=300)

with col2:
    st.subheader("👀 Preview")
    render_mermaid(st.session_state.mermaid_code)
