import sqlite3
from datetime import datetime, timedelta

DB_NAME = "local_data.db"

def init_db():
    """Khởi tạo database: bảng settings (lưu key) và bảng history (lưu log)."""
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    # Bảng lưu API Key
    c.execute('''CREATE TABLE IF NOT EXISTS settings
                 (key_name TEXT PRIMARY KEY, key_value TEXT)''')
    # Bảng lưu lịch sử (để sau này có thể xem lại hoặc để xóa định kỳ)
    c.execute('''CREATE TABLE IF NOT EXISTS history
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, 
                  content TEXT, 
                  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)''')
    conn.commit()
    conn.close()

def save_api_key(api_key):
    """Lưu API Key vào DB."""
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("INSERT OR REPLACE INTO settings (key_name, key_value) VALUES (?, ?)", 
              ("openai_api_key", api_key))
    conn.commit()
    conn.close()

def get_api_key():
    """Lấy API Key từ DB."""
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("SELECT key_value FROM settings WHERE key_name = 'openai_api_key'")
    result = c.fetchone()
    conn.close()
    return result[0] if result else ""

def save_history(content):
    """Lưu nội dung biểu đồ vào lịch sử."""
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("INSERT INTO history (content) VALUES (?)", (content,))
    conn.commit()
    conn.close()

def cleanup_old_data():
    """Xóa sạch lịch sử cũ hơn 30 ngày."""
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    # Tính thời gian 30 ngày trước
    one_month_ago = datetime.now() - timedelta(days=30)
    c.execute("DELETE FROM history WHERE created_at < ?", (one_month_ago,))
    deleted_count = c.rowcount
    conn.commit()
    conn.close()
    return deleted_count
