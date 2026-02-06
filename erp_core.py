"""
ERP Core - 店铺管理系统数据库处理器
处理销售、库存、员工和考勤管理
增强版：支持完整网站设置
"""

import sqlite3
from datetime import datetime, date
from typing import Optional, List, Dict, Any
import os
import json
import logging

# 尝试导入 psycopg2 用于 PostgreSQL
try:
    import psycopg2
    from psycopg2.extras import RealDictCursor
    HAS_POSTGRES = True
except ImportError:
    HAS_POSTGRES = False

DB_FILE = "lemon_shop.db"

class ERPDatabase:
    """ERP操作的数据库处理器 (支持 SQLite 和 PostgreSQL)"""
    
    def __init__(self, db_path: str = DB_FILE):
        self.db_path = db_path
        self.db_url = os.environ.get("DATABASE_URL")
        self.is_postgres = bool(self.db_url and HAS_POSTGRES)
        
        if self.db_url and not HAS_POSTGRES:
            logging.warning("检测到 DATABASE_URL 但未安装 psycopg2，将回退到 SQLite")
            
        self._init_database()
    
    def _get_connection(self):
        """获取数据库连接"""
        if self.is_postgres:
            conn = psycopg2.connect(self.db_url)
            return conn
        else:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            return conn

    def _get_cursor(self, conn):
        """获取游标"""
        if self.is_postgres:
            return conn.cursor(cursor_factory=RealDictCursor)
        else:
            return conn.cursor()
    
    def _fix_sql(self, sql: str) -> str:
        """根据数据库类型修正SQL语法"""
        if self.is_postgres:
            # 替换占位符 ? 为 %s
            sql = sql.replace('?', '%s')
            # 替换 AUTOINCREMENT 为 SERIAL (仅在建表时相关，但通常我们用单独的逻辑处理建表)
            return sql
        return sql
    
    def _init_database(self):
        """初始化所有必需的表"""
        conn = self._get_connection()
        cursor = self._get_cursor(conn)
        
        # 定义主键类型
        pk_type = "SERIAL PRIMARY KEY" if self.is_postgres else "INTEGER PRIMARY KEY AUTOINCREMENT"
        
        # 员工表
        cursor.execute(f"""
            CREATE TABLE IF NOT EXISTS staff (
                id {pk_type},
                name TEXT NOT NULL,
                hourly_wage REAL DEFAULT 1200,
                is_active INTEGER DEFAULT 1,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # 考勤表
        cursor.execute(f"""
            CREATE TABLE IF NOT EXISTS attendance (
                id {pk_type},
                staff_id INTEGER NOT NULL,
                clock_in TIMESTAMP,
                clock_out TIMESTAMP,
                work_date DATE NOT NULL,
                hours_worked REAL DEFAULT 0,
                FOREIGN KEY (staff_id) REFERENCES staff(id)
            )
        """)
        
        # 库存表
        cursor.execute(f"""
            CREATE TABLE IF NOT EXISTS inventory (
                id {pk_type},
                item_name TEXT NOT NULL,
                category TEXT DEFAULT 'Ingredient',
                quantity INTEGER DEFAULT 0,
                threshold INTEGER DEFAULT 10,
                unit TEXT DEFAULT '个',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # 销售表
        cursor.execute(f"""
            CREATE TABLE IF NOT EXISTS sales (
                id {pk_type},
                items TEXT NOT NULL,
                total_amount REAL NOT NULL,
                payment_method TEXT DEFAULT '现金',
                staff_id INTEGER,
                sale_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (staff_id) REFERENCES staff(id)
            )
        """)
        
        # 网站设置表
        cursor.execute(f"""
            CREATE TABLE IF NOT EXISTS website_settings (
                id INTEGER PRIMARY KEY,
                settings_json TEXT DEFAULT '{{}}',
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # 产品表
        cursor.execute(f"""
            CREATE TABLE IF NOT EXISTS products (
                id {pk_type},
                name TEXT NOT NULL,
                description TEXT,
                price TEXT,
                category TEXT DEFAULT '蛋糕',
                image_path TEXT,
                status TEXT DEFAULT 'active',
                sort_order INTEGER DEFAULT 0,
                image_fit TEXT DEFAULT 'cover',
                image_position TEXT DEFAULT 'center',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # 公告表
        cursor.execute(f"""
            CREATE TABLE IF NOT EXISTS announcements (
                id {pk_type},
                title TEXT NOT NULL,
                content TEXT,
                is_active INTEGER DEFAULT 1,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        conn.commit()
        conn.close()
        
        # 初始化默认数据
        self._init_default_data()
    
    def _init_default_data(self):
        """如果为空则初始化默认库存和网站设置"""
        conn = self._get_connection()
        cursor = self._get_cursor(conn)
        
        # 检查库存是否为空
        cursor.execute(self._fix_sql("SELECT COUNT(*) FROM inventory"))
        if cursor.fetchone()[0] == 0:
            default_items = [
                ("奶油芝士", "Ingredient", 50, 20, "块"),
                ("鸡蛋", "Ingredient", 100, 30, "个"),
                ("白砂糖", "Ingredient", 20, 5, "公斤"),
                ("面粉", "Ingredient", 15, 5, "公斤"),
                ("黄油", "Ingredient", 30, 10, "块"),
                ("柠檬", "Ingredient", 40, 15, "个"),
                ("蛋糕盒（6寸）", "Packaging", 50, 20, "个"),
                ("单片容器", "Packaging", 100, 30, "个"),
                ("纸袋", "Packaging", 80, 25, "个"),
            ]
            cursor.executemany(
                self._fix_sql("INSERT INTO inventory (item_name, category, quantity, threshold, unit) VALUES (?, ?, ?, ?, ?)"),
                default_items
            )
        
        # 检查网站设置是否存在
        cursor.execute(self._fix_sql("SELECT COUNT(*) FROM website_settings"))
        if cursor.fetchone()[0] == 0:
            default_settings = {
                'shop_name': '柠檬甜品店',
                'shop_icon': '🍋',
                'catchphrase': '甜蜜时光，新鲜滋味',
                'about_text': '我们用心制作每一份甜品，采用最优质的食材，为您带来最美味的享受。',
                'brand_color': '#FCD34D',
                'hero_badge': '✨ 每日新鲜烘焙',
                'address': '大阪市中央区心斋桥1-2-3',
                'phone': '06-1234-5678',
                'hours': '周一至周六 10:00-20:00',
                
                'product1_name': '巴斯克芝士蛋糕',
                'product1_desc': '浓郁奶香，烤制焦糖外皮，入口即化',
                'product1_price': '¥280',
                'product1_unit': '/整个',
                'product1_icon': '🧁',
                
                'product2_name': '精致单片',
                'product2_desc': '完美份量，享受小确幸',
                'product2_price': '¥45',
                'product2_unit': '/片',
                'product2_icon': '🍰',
                
                'product3_name': '柠檬挞',
                'product3_desc': '清新柠檬，酸甜平衡，清爽解腻',
                'product3_price': '¥45',
                'product3_unit': '/个',
                'product3_icon': '🍋',
                
                'stat1_number': '5+',
                'stat1_label': '年专业经验',
                'stat2_number': '10K+',
                'stat2_label': '满意顾客',
                'stat3_number': '15+',
                'stat3_label': '产品种类',
                
                'rating_score': '4.9',
                'rating_label': '超高评分',
                'rating_count': '500+ 好评',
                
                'footer_text': '保留所有权利. 用心烘焙 ❤️',
            }
            cursor.execute(
                self._fix_sql("INSERT INTO website_settings (id, settings_json) VALUES (1, ?)"),
                (json.dumps(default_settings, ensure_ascii=False),)
            )
        
        conn.commit()
        conn.close()
    
    # ========== 员工管理 ==========
    
    def get_all_staff(self, active_only: bool = True) -> List[Dict]:
        """获取所有员工"""
        conn = self._get_connection()
        cursor = self._get_cursor(conn)
        
        if active_only:
            cursor.execute(self._fix_sql("SELECT * FROM staff WHERE is_active = 1 ORDER BY name"))
        else:
            cursor.execute(self._fix_sql("SELECT * FROM staff ORDER BY name"))
        
        rows = cursor.fetchall()
        conn.close()
        return [dict(row) for row in rows]
    
    def add_staff(self, name: str, hourly_wage: float = 1200) -> int:
        """添加新员工"""
        conn = self._get_connection()
        cursor = self._get_cursor(conn)
        sql = "INSERT INTO staff (name, hourly_wage) VALUES (?, ?)"
        if self.is_postgres:
            sql += " RETURNING id"
        
        cursor.execute(self._fix_sql(sql), (name, hourly_wage))
        
        if self.is_postgres:
            staff_id = cursor.fetchone()['id']
        else:
            staff_id = cursor.lastrowid
            
        conn.commit()
        conn.close()
        return staff_id
    
    def deactivate_staff(self, staff_id: int):
        """停用员工"""
        conn = self._get_connection()
        cursor = self._get_cursor(conn)
        cursor.execute(self._fix_sql("UPDATE staff SET is_active = 0 WHERE id = ?"), (staff_id,))
        conn.commit()
        conn.close()
    
    # ========== 考勤管理 ==========
    
    def clock_in(self, staff_id: int) -> bool:
        """员工上班签到"""
        today = date.today().isoformat()
        conn = self._get_connection()
    def clock_in(self, staff_id: int) -> bool:
        """员工上班签到"""
        today = date.today().isoformat()
        conn = self._get_connection()
        cursor = self._get_cursor(conn)
        
        cursor.execute(
            self._fix_sql("SELECT id FROM attendance WHERE staff_id = ? AND work_date = ? AND clock_out IS NULL"),
            (staff_id, today)
        )
        if cursor.fetchone():
            conn.close()
            return False
        
        cursor.execute(
            self._fix_sql("INSERT INTO attendance (staff_id, clock_in, work_date) VALUES (?, ?, ?)"),
            (staff_id, datetime.now().isoformat(), today)
        )
        conn.commit()
        conn.close()
        return True
    
    def clock_out(self, staff_id: int) -> Optional[float]:
        """员工下班签退"""
        today = date.today().isoformat()
        conn = self._get_connection()
        cursor = self._get_cursor(conn)
        
        cursor.execute(
            self._fix_sql("SELECT id, clock_in FROM attendance WHERE staff_id = ? AND work_date = ? AND clock_out IS NULL"),
            (staff_id, today)
        )
        row = cursor.fetchone()
        
        if not row:
            conn.close()
            return None
        
        clock_in_time = datetime.fromisoformat(row['clock_in'])
        clock_out_time = datetime.now()
        hours_worked = (clock_out_time - clock_in_time).total_seconds() / 3600
        
        cursor.execute(
            self._fix_sql("UPDATE attendance SET clock_out = ?, hours_worked = ? WHERE id = ?"),
            (clock_out_time.isoformat(), round(hours_worked, 2), row['id'])
        )
        conn.commit()
        conn.close()
        return round(hours_worked, 2)
    
    def get_today_attendance(self) -> List[Dict]:
        """获取今日考勤记录"""
        today = date.today().isoformat()
        conn = self._get_connection()
        cursor = self._get_cursor(conn)
        
        cursor.execute(self._fix_sql("""
            SELECT a.*, s.name as staff_name, s.hourly_wage
            FROM attendance a
            JOIN staff s ON a.staff_id = s.id
            WHERE a.work_date = ?
            ORDER BY a.clock_in DESC
        """), (today,))
        
        rows = cursor.fetchall()
        conn.close()
        return [dict(row) for row in rows]
    
    def get_staff_status(self, staff_id: int) -> str:
        """获取员工今日签到状态"""
        today = date.today().isoformat()
        conn = self._get_connection()
        cursor = self._get_cursor(conn)
        
        cursor.execute(
            self._fix_sql("SELECT clock_in, clock_out FROM attendance WHERE staff_id = ? AND work_date = ?"),
            (staff_id, today)
        )
        row = cursor.fetchone()
        conn.close()
        
        if not row:
            return "not_clocked_in"
        elif row['clock_out'] is None:
            return "working"
        else:
            return "finished"
    
    # ========== 库存管理 ==========
    
    def get_all_inventory(self) -> List[Dict]:
        """获取所有库存商品"""
        conn = self._get_connection()
        cursor = self._get_cursor(conn)
        cursor.execute(self._fix_sql("SELECT * FROM inventory ORDER BY category, item_name"))
        rows = cursor.fetchall()
        conn.close()
        return [dict(row) for row in rows]
    
    def add_inventory_item(self, item_name: str, category: str, quantity: int, threshold: int, unit: str) -> int:
        """添加新库存商品"""
        conn = self._get_connection()
        cursor = self._get_cursor(conn)
        sql = "INSERT INTO inventory (item_name, category, quantity, threshold, unit) VALUES (?, ?, ?, ?, ?)"
        if self.is_postgres:
            sql += " RETURNING id"
            
        cursor.execute(self._fix_sql(sql), (item_name, category, quantity, threshold, unit))
        
        if self.is_postgres:
            item_id = cursor.fetchone()['id']
        else:
            item_id = cursor.lastrowid
            
        conn.commit()
        conn.close()
        return item_id
    
    def update_inventory_quantity(self, item_id: int, quantity_change: int):
        """更新库存数量"""
        conn = self._get_connection()
        cursor = self._get_cursor(conn)
        cursor.execute(
            self._fix_sql("UPDATE inventory SET quantity = quantity + ? WHERE id = ?"),
            (quantity_change, item_id)
        )
        conn.commit()
        conn.close()
    
    def get_low_stock_items(self) -> List[Dict]:
        """获取低于警戒线的商品"""
        conn = self._get_connection()
        cursor = self._get_cursor(conn)
        cursor.execute(self._fix_sql("SELECT * FROM inventory WHERE quantity < threshold"))
        rows = cursor.fetchall()
        conn.close()
        return [dict(row) for row in rows]
    
    def delete_inventory_item(self, item_id: int):
        """删除库存商品"""
        conn = self._get_connection()
        cursor = self._get_cursor(conn)
        cursor.execute(self._fix_sql("DELETE FROM inventory WHERE id = ?"), (item_id,))
        conn.commit()
        conn.close()
    
    # ========== 销售管理 ==========
    
    def record_sale(self, items: str, total_amount: float, payment_method: str = "现金", staff_id: int = None) -> int:
        """记录新销售"""
        conn = self._get_connection()
        cursor = self._get_cursor(conn)
        sql = "INSERT INTO sales (items, total_amount, payment_method, staff_id) VALUES (?, ?, ?, ?)"
        if self.is_postgres:
            sql += " RETURNING id"
        
        cursor.execute(self._fix_sql(sql), (items, total_amount, payment_method, staff_id))
        
        if self.is_postgres:
            sale_id = cursor.fetchone()['id']
        else:
            sale_id = cursor.lastrowid
            
        conn.commit()
        conn.close()
        return sale_id
    
    def get_today_sales(self) -> List[Dict]:
        """获取今日销售"""
        today = date.today().isoformat()
        conn = self._get_connection()
        cursor = self._get_cursor(conn)
        cursor.execute(
            self._fix_sql("SELECT s.*, st.name as staff_name FROM sales s LEFT JOIN staff st ON s.staff_id = st.id WHERE date(s.sale_date) = ? ORDER BY s.sale_date DESC"),
            (today,)
        )
        rows = cursor.fetchall()
        conn.close()
        return [dict(row) for row in rows]
    
    def get_today_total(self) -> float:
        """获取今日总销售额"""
        today = date.today().isoformat()
        conn = self._get_connection()
        cursor = self._get_cursor(conn)
        cursor.execute(
            self._fix_sql("SELECT COALESCE(SUM(total_amount), 0) as total FROM sales WHERE date(sale_date) = ?"),
            (today,)
        )
        row = cursor.fetchone()
        conn.close()
        return row['total'] if row else 0
    
    # ========== 网站设置 ==========
    
    def get_website_settings(self) -> Dict:
        """获取网站设置"""
        conn = self._get_connection()
        cursor = self._get_cursor(conn)
        cursor.execute(self._fix_sql("SELECT settings_json FROM website_settings WHERE id = 1"))
        row = cursor.fetchone()
        conn.close()
        
        if row and row['settings_json']:
            try:
                return json.loads(row['settings_json'])
            except json.JSONDecodeError:
                return {}
        return {}
    
    def save_website_settings(self, settings: Dict):
        """保存网站设置"""
        conn = self._get_connection()
        cursor = self._get_cursor(conn)
        
        # 先获取现有设置并合并
        existing = self.get_website_settings()
        merged = {**existing, **settings}
        
        cursor.execute(self._fix_sql("""
            UPDATE website_settings SET
                settings_json = ?,
                updated_at = CURRENT_TIMESTAMP
            WHERE id = 1
        """), (json.dumps(merged, ensure_ascii=False),))
        
        # 如果没有更新任何行，插入新记录
        if cursor.rowcount == 0:
            cursor.execute(
                self._fix_sql("INSERT INTO website_settings (id, settings_json) VALUES (1, ?)"),
                (json.dumps(merged, ensure_ascii=False),)
            )
        
        conn.commit()
        conn.close()
    
    # ========== 产品管理 ==========
    
    PRODUCT_CATEGORIES = ['蛋糕', '面包', '甜点', '饮品', '套餐', '其他']
    PRODUCT_STATUS = {
        'active': '在售',
        'new': '🆕新品',
        'hot': '🔥人气',
        'limited': '⏰限定',
        'soldout': '🚫售罄'
    }
    
    def get_all_products(self, category: str = None) -> List[Dict]:
        """获取所有产品，可按分类筛选"""
        conn = self._get_connection()
        cursor = self._get_cursor(conn)
        if category:
            cursor.execute(self._fix_sql("SELECT * FROM products WHERE category = ? ORDER BY sort_order, id"), (category,))
        else:
            cursor.execute(self._fix_sql("SELECT * FROM products ORDER BY sort_order, id"))
        rows = cursor.fetchall()
        conn.close()
        return [dict(row) for row in rows]
    
    def get_product(self, product_id: int) -> Optional[Dict]:
        """获取单个产品"""
        conn = self._get_connection()
        cursor = self._get_cursor(conn)
        cursor.execute(self._fix_sql("SELECT * FROM products WHERE id = ?"), (product_id,))
        row = cursor.fetchone()
        conn.close()
        return dict(row) if row else None
    
    def add_product(self, name: str, description: str = '', price: str = '', 
                    category: str = '蛋糕', image_path: str = None, status: str = 'active') -> int:
        """添加新产品"""
        conn = self._get_connection()
        cursor = self._get_cursor(conn)
        # 获取最大排序值
        cursor.execute(self._fix_sql("SELECT COALESCE(MAX(sort_order), 0) + 1 FROM products"))
        next_order = cursor.fetchone()
        next_order = (next_order['?column?'] if self.is_postgres else next_order[0]) if next_order else 1
        # Postgres fetchone returns dict but column name for expression is uncertain (?column?).
        # Better use alias.
        
        # Retry with alias
        cursor.execute(self._fix_sql("SELECT COALESCE(MAX(sort_order), 0) + 1 as next_order FROM products"))
        row = cursor.fetchone()
        next_order = row['next_order'] if self.is_postgres else row[0]

        sql = """INSERT INTO products (name, description, price, category, image_path, status, sort_order) 
               VALUES (?, ?, ?, ?, ?, ?, ?)"""
        if self.is_postgres:
            sql += " RETURNING id"
            
        cursor.execute(
            self._fix_sql(sql),
            (name, description, price, category, image_path, status, next_order)
        )
        
        if self.is_postgres:
            product_id = cursor.fetchone()['id']
        else:
            product_id = cursor.lastrowid
            
        conn.commit()
        conn.close()
        return product_id
    
    def update_product(self, product_id: int, **kwargs):
        """更新产品信息"""
        if not kwargs:
            return
        conn = self._get_connection()
        cursor = self._get_cursor(conn)
        fields = ', '.join([f"{k} = ?" for k in kwargs.keys()])
        values = list(kwargs.values()) + [product_id]
        cursor.execute(self._fix_sql(f"UPDATE products SET {fields} WHERE id = ?"), values)
        conn.commit()
        conn.close()
    
    def delete_product(self, product_id: int):
        """删除产品"""
        conn = self._get_connection()
        cursor = self._get_cursor(conn)
        cursor.execute(self._fix_sql("DELETE FROM products WHERE id = ?"), (product_id,))
        conn.commit()
        conn.close()
    
    def move_product(self, product_id: int, direction: str):
        """移动产品排序 (up/down)"""
        conn = self._get_connection()
        cursor = self._get_cursor(conn)
        cursor.execute(self._fix_sql("SELECT sort_order FROM products WHERE id = ?"), (product_id,))
        row = cursor.fetchone()
        if not row:
            conn.close()
            return
        current_order = row['sort_order'] if self.is_postgres else row[0]
        
        if direction == 'up':
            cursor.execute(
                self._fix_sql("SELECT id, sort_order FROM products WHERE sort_order < ? ORDER BY sort_order DESC LIMIT 1"),
                (current_order,)
            )
        else:
            cursor.execute(
                self._fix_sql("SELECT id, sort_order FROM products WHERE sort_order > ? ORDER BY sort_order ASC LIMIT 1"),
                (current_order,)
            )
        
        swap_row = cursor.fetchone()
        if swap_row:
            swap_id = swap_row['id'] if self.is_postgres else swap_row[0]
            swap_order = swap_row['sort_order'] if self.is_postgres else swap_row[1]
            cursor.execute(self._fix_sql("UPDATE products SET sort_order = ? WHERE id = ?"), (swap_order, product_id))
            cursor.execute(self._fix_sql("UPDATE products SET sort_order = ? WHERE id = ?"), (current_order, swap_id))
        
        conn.commit()
        conn.close()
    
    # ========== 公告管理 ==========
    
    def get_active_announcements(self) -> List[Dict]:
        """获取激活的公告"""
        conn = self._get_connection()
        cursor = self._get_cursor(conn)
        cursor.execute(self._fix_sql("SELECT * FROM announcements WHERE is_active = 1 ORDER BY created_at DESC"))
        rows = cursor.fetchall()
        conn.close()
        return [dict(row) for row in rows]
    
    def add_announcement(self, title: str, content: str = '') -> int:
        """添加公告"""
        conn = self._get_connection()
        cursor = self._get_cursor(conn)
        sql = "INSERT INTO announcements (title, content) VALUES (?, ?)"
        if self.is_postgres:
            sql += " RETURNING id"
        
        cursor.execute(self._fix_sql(sql), (title, content))
        
        if self.is_postgres:
            ann_id = cursor.fetchone()['id']
        else:
            ann_id = cursor.lastrowid
            
        conn.commit()
        conn.close()
        return ann_id
    
    def delete_announcement(self, ann_id: int):
        """删除公告"""
        conn = self._get_connection()
        cursor = self._get_cursor(conn)
        cursor.execute(self._fix_sql("DELETE FROM announcements WHERE id = ?"), (ann_id,))
        conn.commit()
        conn.close()


# 单例实例
_db_instance = None

def get_db() -> ERPDatabase:
    """获取数据库单例实例"""
    global _db_instance
    if _db_instance is None:
        _db_instance = ERPDatabase()
    return _db_instance
