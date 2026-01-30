import streamlit as st
from utils import render_mermaid, extract_mermaid_code
from ai_service import call_ai_update
import db  # Import file db mới tạo

# --- 0. Khởi tạo DB & Dọn dẹp ---
db.init_db()
deleted = db.cleanup_old_data() # Tự động xóa dữ liệu cũ hơn 1 tháng

# --- 1. Cấu hình Trang ---
st.set_page_config(layout="centered", page_title="Mermaid Visualizer", page_icon="🧜‍♀️")

# (Giữ nguyên phần CSS styles như cũ)
st.markdown(
    """
    <style>
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        .mermaid-container {
            background-color: #ffffff;
            padding: 20px;
            border-radius: 15px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
            margin-bottom: 20px;
        }
        .stButton button {
            width: 100%;
            border-radius: 10px;
            font-weight: bold;
        }
    </style>
    """,
    unsafe_allow_html=True
)

# --- 2. Sidebar: Settings & DB ---
with st.sidebar:
    st.title("⚙️ Cài đặt")
    
    # Lấy API Key từ DB lên
    saved_key = db.get_api_key()
    
    with st.expander("🔑 Cấu hình AI", expanded=True):
        # Nếu đã có key trong DB thì điền sẵn vào
        api_key = st.text_input("API Key", value=saved_key, type="password", placeholder="sk-...")
        
        # Lưu key vào DB ngay khi người dùng nhập
        if api_key and api_key != saved_key:
            db.save_api_key(api_key)
            st.toast("Đã lưu API Key vào hệ thống!", icon="💾")

        model_name = st.selectbox("Model", ["deepseek/deepseek-v3.2", "openai/gpt-oss-120b", "xiaomi/mimo-v2-flash", "anthropic/claude-3-haiku"])
        temperature = st.slider("Độ sáng tạo", 0.0, 2.0, 0.7)
    
    st.divider()
    
    st.subheader("📂 Tải Dữ liệu")
    # CẬP NHẬT: Hỗ trợ nhiều loại file
    uploaded_file = st.file_uploader("Chọn file (md, txt, mmd, py...)", type=["md", "txt", "mmd", "py", "js"])
    
    if deleted > 0:
        st.info(f"🧹 Đã tự động dọn dẹp {deleted} bản ghi cũ hơn 30 ngày.")

    st.divider()
    if st.button("🔄 Reset App"):
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.rerun()

# --- 3. Quản lý Trạng thái ---
if 'mermaid_code' not in st.session_state:
    st.session_state.mermaid_code = "graph TD;\n    Start((Bắt đầu)) --> Process[Xử lý];\n    Process --> End((Kết thúc));\n    style Start fill:#f9f,stroke:#333,stroke-width:2px"

# Logic xử lý file upload (Cập nhật dùng hàm mới)
if uploaded_file:
    if 'last_filename' not in st.session_state or st.session_state.last_filename != uploaded_file.name:
        string_data = uploaded_file.getvalue().decode("utf-8")
        # Truyền thêm đuôi file để xử lý đúng
        file_ext = uploaded_file.name.split('.')[-1]
        extracted = extract_mermaid_code(string_data, file_ext) #
        
        if extracted:
            st.session_state.mermaid_code = extracted
            st.session_state.last_filename = uploaded_file.name
            db.save_history(extracted) # Lưu log file mới tải lên
            st.toast("Đã nhập dữ liệu thành công!", icon="📥")
        else:
            st.error("Không tìm thấy nội dung hợp lệ trong file!")

# --- 4. Giao diện Chính ---
st.title("🧜‍♀️ Mermaid Flow")
st.caption("Biến ý tưởng thành hình ảnh ngay lập tức.")

# NÚT TẢI XUỐNG (Tính năng mới)
col_res_header, col_download = st.columns([3, 1])
with col_res_header:
    st.markdown("### 👁️ Kết quả")
with col_download:
    st.download_button(
        label="⬇️ Tải Code",
        data=st.session_state.mermaid_code,
        file_name="diagram.mmd",
        mime="text/plain",
    )

with st.container():
    try:
        render_mermaid(st.session_state.mermaid_code)
    except Exception as e:
        st.error(f"Lỗi hiển thị: {e}")

st.divider()

# --- Chat Control ---
st.markdown("### ✏️ Chỉnh sửa với AI")
col_input, col_btn = st.columns([4, 1])

with col_input:
    # THAY ĐỔI 1: Thêm key="user_query" vào đây
    user_request = st.text_input(
        "Bạn muốn sửa gì?", 
        placeholder="Ví dụ: Đổi màu node Bắt đầu thành màu xanh...",
        key="user_query" 
    )

with col_btn:
    st.write("") 
    st.write("")
    run_btn = st.button("🚀 Gửi", type="primary")

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
                db.save_history(new_code)
                st.toast("Cập nhật thành công!", icon="✨")
                
                # THAY ĐỔI 2: Xóa nội dung trong ô input thông qua key
                st.session_state.user_query = "" 
                
                st.rerun()

# --- Developer Mode ---
with st.expander("🛠️ Xem Code Nguồn (Dành cho Developer)"): #
    st.session_state.mermaid_code = st.text_area(
        "Mã nguồn Mermaid", 
        st.session_state.mermaid_code, 
        height=200,
        label_visibility="collapsed"
    )
