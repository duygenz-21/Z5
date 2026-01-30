import streamlit.components.v1 as components
import re
import streamlit as st

def render_mermaid(code):
    """Render code Mermaid (Giữ nguyên như cũ)."""
    html_code = f"""
    <script type="module">
        import mermaid from 'https://cdn.jsdelivr.net/npm/mermaid@10/dist/mermaid.esm.min.mjs';
        mermaid.initialize({{ startOnLoad: true }});
    </script>
    <div class="mermaid">
        {code}
    </div>
    """
    components.html(html_code, height=600, scrolling=True)

def extract_mermaid_code(text, file_extension):
    """
    Lấy nội dung code tùy theo loại file.
    """
    # Nếu là file markdown, dùng regex tìm block mermaid
    if "md" in file_extension:
        match = re.search(r'```mermaid(.*?)```', text, re.DOTALL)
        if match:
            return match.group(1).strip()
    
    # Nếu là file code thuần (txt, mmd, py...), trả về toàn bộ text hoặc lọc sơ
    else:
        # Loại bỏ các ký tự thừa nếu người dùng copy cả ```mermaid vào file txt
        clean_text = text.replace("```mermaid", "").replace("```", "").strip()
        return clean_text
        
    return None