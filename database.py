import sqlite3
import hashlib
from config import DB_PATH
import logging

def init_db():
    """بەگەڕخستنی بنکەدراوە بۆ پاراستنی که‌لێنه‌ دۆزراوه‌کان"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS findings (
            hash_id TEXT PRIMARY KEY,
            target TEXT,
            template_id TEXT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    conn.close()
    logging.info("Database initialized successfully.")

def is_duplicate(target, template_id):
    """پشکنین دەکات بزانێت ئایا ئەم کەلێنە پێشتر دۆزراوەتەوە تا دووبارە نەینێرێت"""
    hash_str = f"{target}_{template_id}".encode('utf-8')
    hash_id = hashlib.md5(hash_str).hexdigest()
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT 1 FROM findings WHERE hash_id = ?", (hash_id,))
    result = cursor.fetchone()
    conn.close()
    return result is not None

def save_finding(target, template_id):
    """هەڵگرتنی کەلێنە نوێیەکە بۆ ئەوەی لە داهاتوودا نەبێتە دووبارە"""
    hash_str = f"{target}_{template_id}".encode('utf-8')
    hash_id = hashlib.md5(hash_str).hexdigest()
    
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("INSERT INTO findings (hash_id, target, template_id) VALUES (?, ?, ?)", 
                       (hash_id, target, template_id))
        conn.commit()
    except sqlite3.IntegrityError:
        # ئەگەر پێشتر هەبوو (بە هەڵە هاتبێتە ئێرە) هیچ مەکە
        pass 
    finally:
        conn.close()
