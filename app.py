import streamlit as st
from utils import render_mermaid, extract_mermaid_code
from ai_service import call_ai_update

# --- 1. Cấu hình Trang & Giao diện Mobile ---
st.set_page_config(layout="centered", page_title="Mermaid Visualizer", page_icon="🧜‍♀️")

st.markdown(
    """
    <style>
        /* Ẩn menu mặc định để giống App */
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        header {visibility: hidden;}//
        
        /* Tùy chỉnh khung hiển thị biểu đồ cho đẹp hơn */
        .mermaid-container {
            background-color: #ffffff;
            padding: 20px;
            border-radius: 15px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
            margin-bottom: 20px;
        }
        /* Tăng kích thước nút bấm */
        .stButton button {
            width: 100%;
            border-radius: 10px;
            font-weight: bold;
        }
    </style>
    """,
    unsafe_allow_html=True
)

# --- 2. Sidebar: Trung tâm Điều khiển (Settings) ---
with st.sidebar:
    st.title("⚙️ Cài đặt")
    
    with st.expander("🔑 Cấu hình AI", expanded=True):
        api_key = st.text_input("API Key", type="password", placeholder="sk-...")
        model_name = st.selectbox("Model", ["openai/gpt-3.5-turbo", "openai/gpt-4-turbo", "anthropic/claude-3-haiku"])
        temperature = st.slider("Độ sáng tạo", 0.0, 2.0, 0.7)
    
    st.divider()
    
    st.subheader("📂 Tải Dữ liệu")
    uploaded_file = st.file_uploader("Chọn file .md", type=["md"])
    
    st.divider()
    # Nút Reset
    if st.button("🔄 Reset App"):
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.rerun()

# --- 3. Quản lý Trạng thái (State) ---
if 'mermaid_code' not in st.session_state:
    st.session_state.mermaid_code = "graph TD;\n    Start((Bắt đầu)) --> Process[Xử lý];\n    Process --> End((Kết thúc));\n    style Start fill:#f9f,stroke:#333,stroke-width:2px"

# Logic xử lý file upload
if uploaded_file:
    # Chỉ xử lý khi file thay đổi
    if 'last_filename' not in st.session_state or st.session_state.last_filename != uploaded_file.name:
        string_data = uploaded_file.getvalue().decode("utf-8")
        extracted = extract_mermaid_code(string_data)
        if extracted:
            st.session_state.mermaid_code = extracted
            st.session_state.last_filename = uploaded_file.name
            st.toast("Đã nhập dữ liệu thành công!", icon="📥")
        else:
            st.error("Không tìm thấy biểu đồ trong file này!")

# --- 4. Giao diện Chính (Main UI) ---

# Header
st.title("🧜‍♀️ Mermaid Flow")
st.caption("Biến ý tưởng thành hình ảnh ngay lập tức.")

# 🖼️ KHU VỰC HIỂN THỊ (Visualizer)
# Đặt trong container để tạo điểm nhấn
with st.container():
    st.markdown("### 👁️ Kết quả")
    # Render biểu đồ
    try:
        render_mermaid(st.session_state.mermaid_code)
    except Exception as e:
        st.error(f"Lỗi hiển thị: {e}")

st.divider()

# 💬 KHU VỰC TƯƠNG TÁC (Chat Control)
st.markdown("### ✏️ Chỉnh sửa với AI")

col_input, col_btn = st.columns([4, 1])

with col_input:
    user_request = st.text_input("Bạn muốn sửa gì?", placeholder="Ví dụ: Đổi màu node Bắt đầu thành màu xanh...")

with col_btn:
    # Căn chỉnh nút bấm xuống dưới cùng hàng
    st.write("") 
    st.write("")
    run_btn = st.button("🚀 Gửi", type="primary")

# Logic chạy AI
if run_btn and user_request:
    if not api_key:
        st.toast("Vui lòng nhập API Key trong cài đặt!", icon="⚠️")
    else:
        with st.spinner("🤖 AI đang vẽ lại..."):
            new_code = call_ai_update(
                st.session_state.mermaid_code,
                user_request,
                api_key, model_name, temperature, 1.0
            )
            if new_code.startswith("Error"):
                st.error(new_code)
            else:
                st.session_state.mermaid_code = new_code
                st.toast("Cập nhật thành công!", icon="✨")
                st.rerun()

# --- 5. Khu vực Ẩn (Developer Mode) ---
# Chỉ dành cho ai muốn xem code gốc, mặc định đóng lại
with st.expander("🛠️ Xem Code Nguồn (Dành cho Developer)"):
    st.info("Bạn có thể sửa tay trực tiếp tại đây nếu AI làm sai.")
    st.session_state.mermaid_code = st.text_area(
        "Mã nguồn Mermaid", 
        st.session_state.mermaid_code, 
        height=200,
        label_visibility="collapsed"
    )