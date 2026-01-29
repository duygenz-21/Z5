from openai import OpenAI

def call_ai_update(current_code, prompt, api_key, model, temp, top_p):
    """
    Hàm gọi OpenRouter để chỉnh sửa code Mermaid.
    """
    client = OpenAI(
        base_url="https://openrouter.ai/api/v1",
        api_key=api_key,
    )

    system_prompt = """
    Bạn là một chuyên gia về Mermaid JS. Nhiệm vụ của bạn là cập nhật biểu đồ dựa trên yêu cầu của người dùng.
    QUY TẮC TUYỆT ĐỐI:
    1. Chỉ trả về mã Mermaid thuần túy.
    2. KHÔNG bao gồm markdown (```mermaid), không giải thích, không lời chào.
    3. Giữ nguyên logic cũ, chỉ thêm hoặc sửa theo yêu cầu.
    """

    user_content = f"Code hiện tại:\n{current_code}\n\nYêu cầu thay đổi: {prompt}"

    try:
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_content}
            ],
            temperature=temp,
            top_p=top_p
        )
        # Clean data lần cuối đề phòng AI vẫn trả về markdown
        raw_content = response.choices[0].message.content.strip()
        clean_content = raw_content.replace("```mermaid", "").replace("```", "").strip()
        return clean_content
        
    except Exception as e:
        return f"Error: {str(e)}"
