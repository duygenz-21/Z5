import streamlit.components.v1 as components
import re
import streamlit as st

def render_mermaid(code):
    """
    Render code Mermaid bằng HTML/JS nhúng.
    """
    html_code = f"""
    <script type="module">
        import mermaid from 'https://cdn.jsdelivr.net/npm/mermaid@10/dist/mermaid.esm.min.mjs';
        mermaid.initialize({{ startOnLoad: true }});
    </script>
    <div class="mermaid">
        {code}
    </div>
    """
    # Chiều cao linh động, scroll nếu quá dài
    components.html(html_code, height=600, scrolling=True)

def extract_mermaid_code(text):
    """
    Tìm và lấy nội dung trong block ```mermaid ... ```
    """
    match = re.search(r'```mermaid(.*?)```', text, re.DOTALL)
    if match:
        return match.group(1).strip()
    return None
