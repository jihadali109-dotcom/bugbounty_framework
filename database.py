import sqlite3
from datetime import datetime
import os

DB_PATH = "hunter_state.db"

def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    # دروستکردنی خشتەی کەلێنەکان
    c.execute('''CREATE TABLE IF NOT EXISTS findings
                 (domain TEXT, template_id TEXT, timestamp DATETIME)''')
    # دروستکردنی خشتەی ئامانجە پشکنراوەکان
    c.execute('''CREATE TABLE IF NOT EXISTS scanned_targets
                 (domain TEXT PRIMARY KEY, timestamp DATETIME)''')
    conn.commit()
    conn.close()

def is_duplicate(domain, template_id):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT 1 FROM findings WHERE domain=? AND template_id=?", (domain, template_id))
    res = c.fetchone()
    conn.close()
    return res is not None

def save_finding(domain, template_id):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("INSERT INTO findings VALUES (?, ?, ?)", (domain, template_id, datetime.now()))
    conn.commit()
    conn.close()

def is_domain_scanned(domain):
    """پشکنین کە ئایا ئەم دۆمەینە پێشتر پشکنراوە یان نا"""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT 1 FROM scanned_targets WHERE domain=?", (domain,))
    res = c.fetchone()
    conn.close()
    return res is not None

def mark_domain_scanned(domain):
    """نیشانکردنی دۆمەینێک وەک پشکنراو"""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("INSERT OR IGNORE INTO scanned_targets VALUES (?, ?)", (domain, datetime.now()))
    conn.commit()
    conn.close()
