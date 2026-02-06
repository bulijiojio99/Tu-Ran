"""
店铺管理系统 - Tu&Ran专用版
日语网站 + 中文管理界面
支持自定义图片、字段清空自动隐藏
"""

import streamlit as st
import streamlit.components.v1 as components
from datetime import datetime
import json
import os
from PIL import Image
import io

from erp_core import get_db
from cms_core import render_website, publish_website

# 配置
UPLOADS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "uploads")
os.makedirs(UPLOADS_DIR, exist_ok=True)

FONT_OPTIONS = {
    "标准黑体 (Noto Sans)": "'Noto Sans JP', sans-serif",
    "标准宋体 (Noto Serif)": "'Noto Serif JP', serif",
    "圆体 (M PLUS Rounded)": "'M PLUS Rounded 1c', sans-serif",
    "可受体 (Kiwi Maru)": "'Kiwi Maru', serif",
    "蓬松体 (Yomogi)": "'Yomogi', cursive",
    "波普体 (Hachi Maru Pop)": "'Hachi Maru Pop', cursive",
    "粗圆体 (Dela Gothic One)": "'Dela Gothic One', cursive",
    "胖胖体 (Potta One)": "'Potta One', cursive",
}

def get_font_index(font_name):
    font_list = list(FONT_OPTIONS.keys())
    if font_name in font_list:
        return font_list.index(font_name)
    return 0

# 页面配置
st.set_page_config(
    page_title="🍋 Tu&Ran 店铺管理",
    page_icon="🍰",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
    .stButton > button { border-radius: 8px; font-weight: 500; }
    .section-header { 
        background: linear-gradient(90deg, #f8fafc, #e2e8f0); 
        padding: 0.4rem 0.8rem; 
        border-radius: 8px; 
        margin: 0.8rem 0 0.4rem 0; 
        font-weight: 600;
        display: flex;
        justify-content: space-between;
        align-items: center;
    }
    .del-btn { color: #ef4444; font-size: 0.8rem; cursor: pointer; }
</style>
""", unsafe_allow_html=True)

db = get_db()

# ==================== 工具函数 ====================

def save_uploaded_image(uploaded_file, filename):
    if uploaded_file is not None:
        try:
            image = Image.open(uploaded_file)
            if image.mode in ('RGBA', 'P'):
                image = image.convert('RGB')
            max_size = (800, 800)
            image.thumbnail(max_size, Image.Resampling.LANCZOS)
            save_path = os.path.join(UPLOADS_DIR, filename)
            image.save(save_path, 'JPEG', quality=85)
            return f"uploads/{filename}"
        except Exception as e:
            st.error(f"图片处理失败: {str(e)}")
            return None
    return None

def get_image_path(image_key):
    filename = f"{image_key}.jpg"
    full_path = os.path.join(UPLOADS_DIR, filename)
    if os.path.exists(full_path):
        return f"uploads/{filename}"
    return None

def get_image_base64(image_key):
    """获取图片的base64编码（用于iframe预览）"""
    import base64
    filename = f"{image_key}.jpg"
    full_path = os.path.join(UPLOADS_DIR, filename)
    if os.path.exists(full_path):
        try:
            with open(full_path, "rb") as f:
                data = base64.b64encode(f.read()).decode()
                return f"data:image/jpeg;base64,{data}"
        except Exception:
            return None
    return None

def image_uploader(key, label):
    """图片上传组件"""
    existing = get_image_path(key)
    if existing:
        c1, c2 = st.columns([3, 1])
        with c1:
            full_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), existing)
            st.image(full_path, width=60)
        with c2:
            if st.button("🗑️", key=f"del_{key}", help="删除"):
                os.remove(full_path)
                st.rerun()
    uploaded = st.file_uploader(label, type=['jpg', 'jpeg', 'png'], key=f"up_{key}", label_visibility="collapsed")
    if uploaded:
        save_uploaded_image(uploaded, f"{key}.jpg")
        st.rerun()

def clear_field(field_key):
    """清空字段"""
    st.session_state.website_data[field_key] = ''

def clear_fields(field_keys):
    """清空多个字段"""
    for key in field_keys:
        st.session_state.website_data[key] = ''

def section_header_with_clear(title, field_keys, btn_key):
    """带清空按钮的区块标题"""
    c1, c2 = st.columns([6, 1])
    with c1:
        st.markdown(f'<div class="section-header">{title}</div>', unsafe_allow_html=True)
    with c2:
        if st.button("🗑️", key=btn_key, help="清空此区块"):
            clear_fields(field_keys)
            st.rerun()

def get_default_website_data():
    settings = db.get_website_settings()
    defaults = {
        'shop_name': 'Tu&Ran',
        'tagline': '日常の幸せベイキング',
        'meta_description': '大阪のバスクチーズケーキ専門店',
        'brand_color': '#D4A574',
        'font_family': 'Noto Sans JP',
        
        'nav_item1': '私たちについて', 'nav_item1_link': '#about',
        'nav_item2': 'メニュー', 'nav_item2_link': '#menu',
        'nav_item3': 'お問い合わせ', 'nav_item3_link': '#contact',
        'nav_btn_text': 'ご予約', 'nav_btn_link': '#contact',
        
        'show_hero': True,
        'hero_badge': '毎日焼きたて',
        'hero_title': '日常の幸せベイキング',
        'hero_desc': '私たちは一つ一つのスイーツに心を込めて作っています。',
        'hero_btn1_text': 'メニューを見る', 'hero_btn1_link': '#menu',
        'hero_btn2_text': '詳しく見る', 'hero_btn2_link': '#about',
        'rating_score': '4.9', 'rating_label': '高評価', 'rating_count': '500+ レビュー',
        
        'show_products': True,
        'products_title': 'おすすめメニュー',
        'products_subtitle': '厳選素材と職人技で作り上げた自慢の一品',
        
        'product1_name': 'バスクチーズケーキ', 
        'product1_desc': '濃厚なクリームチーズと焦がしキャラメルの外皮',
        'product1_price': '¥2,800', 'product1_unit': '/ホール',
        
        'product2_name': '軽乳茶セット', 
        'product2_desc': 'ケーキ1/6カット＋自家製ミルクティー',
        'product2_price': '¥900', 'product2_unit': '/セット',
        
        'product3_name': 'カットケーキ', 
        'product3_desc': '1/6カットサイズ、テイクアウトOK',
        'product3_price': '¥500', 'product3_unit': '/カット',
        
        'show_about': True,
        'about_title': '私たちの想い',
        'about_text1': '当店の店長は日本で暮らす中国人です。',
        'about_text2': '100%高品質の輸入クリームチーズのみを使用。',
        'stat1_number': '100%', 'stat1_label': '良心食材',
        'stat2_number': '毎日', 'stat2_label': '焼きたて',
        'stat3_number': '心込', 'stat3_label': '手作り',
        
        'show_contact': True,
        'contact_title': 'ご来店お待ちしております',
        'contact_subtitle': '皆様との出会いを',
        'address_label': '店舗住所', 'address': '大阪市中央区',
        'hours_label': '営業時間', 'hours': '11:00-19:00',
        'phone_label': 'お問い合わせ', 'phone': '@turan.osaka',
        
        'show_footer': True,
        'footer_text': 'All Rights Reserved.',
        'social_instagram': 'https://www.instagram.com/turan.osaka/',
        'social_line': '',
    }
    
    for key, default in defaults.items():
        defaults[key] = settings.get(key, default)
    
    image_keys = ['logo', 'hero', 'product1', 'product2', 'product3', 
                  'badge_icon', 'rating_icon', 'address_icon', 'hours_icon', 
                  'phone_icon', 'instagram_icon', 'line_icon']
    for k in image_keys:
        defaults[f'{k}_image'] = get_image_path(k)
    
    return defaults

# 初始化
if 'cart' not in st.session_state:
    st.session_state.cart = []
if 'website_data' not in st.session_state:
    st.session_state.website_data = get_default_website_data()

WEBSITE_DIR = os.path.dirname(os.path.abspath(__file__))
INDEX_PATH = os.path.join(WEBSITE_DIR, "index.html")

# ==================== 侧边栏 ====================
st.sidebar.title("🍰 Tu&Ran 管理")
st.sidebar.markdown("---")
page = st.sidebar.radio("导航", ["🎨 网站编辑器", "🏪 店铺运营"], label_visibility="collapsed")
st.sidebar.markdown("---")
st.sidebar.caption(f"📅 {datetime.now().strftime('%Y-%m-%d %H:%M')}")
if os.path.exists(INDEX_PATH):
    st.sidebar.success("🌐 网站已发布")
else:
    st.sidebar.warning("⚠️ 网站尚未发布")

# ==================== 网站编辑器 ====================
if page == "🎨 网站编辑器":
    st.title("🎨 网站编辑器")
    
    # 自动保存提示（侧边栏显示）
    if 'last_saved' not in st.session_state:
        st.session_state.last_saved = None
    
    def auto_save():
        """自动保存到数据库"""
        db.save_website_settings(st.session_state.website_data)
        st.session_state.last_saved = datetime.now().strftime('%H:%M:%S')
    
    col_editor, col_preview = st.columns([1, 1], gap="large")
    
    with col_editor:
        tabs = st.tabs(["🏠 基础", "🔗 导航", "✨ 首页", "🍰 产品", "📖 关于", "📍 联系", "🖼️ 图片"])
        
        # ===== 基础 =====
        with tabs[0]:
            st.markdown('<div class="section-header">🏪 店铺信息</div>', unsafe_allow_html=True)
            st.session_state.website_data['shop_name'] = st.text_input("店铺名称", st.session_state.website_data['shop_name'])
            st.session_state.website_data['tagline'] = st.text_input("标语", st.session_state.website_data['tagline'])
            st.session_state.website_data['meta_description'] = st.text_input("SEO描述", st.session_state.website_data['meta_description'])
            
            st.markdown('<div class="section-header">🎨 样式</div>', unsafe_allow_html=True)
            c1, c2 = st.columns(2)
            with c1:
                st.session_state.website_data['brand_color'] = st.color_picker("品牌色", st.session_state.website_data['brand_color'])
            with c2:
                st.session_state.website_data['font_family'] = st.selectbox("字体", list(FONT_OPTIONS.keys()),
                    index=get_font_index(st.session_state.website_data.get('font_family', 'Noto Sans JP')))
        
        # ===== 导航 =====
        with tabs[1]:
            for i in range(1, 4):
                section_header_with_clear(f"菜单项 {i}", [f'nav_item{i}', f'nav_item{i}_link'], f"clr_nav{i}")
                c1, c2 = st.columns([2, 1])
                with c1:
                    st.session_state.website_data[f'nav_item{i}'] = st.text_input("名称", st.session_state.website_data.get(f'nav_item{i}', ''), key=f"nav{i}")
                with c2:
                    st.session_state.website_data[f'nav_item{i}_link'] = st.text_input("链接", st.session_state.website_data.get(f'nav_item{i}_link', ''), key=f"navl{i}")
            
            section_header_with_clear("预订按钮", ['nav_btn_text', 'nav_btn_link'], "clr_navbtn")
            c1, c2 = st.columns([2, 1])
            with c1:
                st.session_state.website_data['nav_btn_text'] = st.text_input("按钮文字", st.session_state.website_data.get('nav_btn_text', ''))
            with c2:
                st.session_state.website_data['nav_btn_link'] = st.text_input("链接", st.session_state.website_data.get('nav_btn_link', ''), key="navbtn")
        
        # ===== 首页 =====
        with tabs[2]:
            section_header_with_clear("🏷️ 徽章", ['hero_badge'], "clr_badge")
            st.session_state.website_data['hero_badge'] = st.text_input("徽章文字", st.session_state.website_data.get('hero_badge', ''), label_visibility="collapsed")
            
            section_header_with_clear("📝 标题描述", ['hero_title', 'hero_desc'], "clr_hero_text")
            st.session_state.website_data['hero_title'] = st.text_input("主标题", st.session_state.website_data.get('hero_title', ''))
            st.session_state.website_data['hero_desc'] = st.text_area("描述", st.session_state.website_data.get('hero_desc', ''), height=60)
            
            section_header_with_clear("🔘 按钮1", ['hero_btn1_text', 'hero_btn1_link'], "clr_btn1")
            c1, c2 = st.columns([2, 1])
            with c1:
                st.session_state.website_data['hero_btn1_text'] = st.text_input("文字", st.session_state.website_data.get('hero_btn1_text', ''), key="hb1t")
            with c2:
                st.session_state.website_data['hero_btn1_link'] = st.text_input("链接", st.session_state.website_data.get('hero_btn1_link', ''), key="hb1l")
            
            section_header_with_clear("🔘 按钮2", ['hero_btn2_text', 'hero_btn2_link'], "clr_btn2")
            c1, c2 = st.columns([2, 1])
            with c1:
                st.session_state.website_data['hero_btn2_text'] = st.text_input("文字", st.session_state.website_data.get('hero_btn2_text', ''), key="hb2t")
            with c2:
                st.session_state.website_data['hero_btn2_link'] = st.text_input("链接", st.session_state.website_data.get('hero_btn2_link', ''), key="hb2l")
            
            section_header_with_clear("⭐ 评分卡片", ['rating_score', 'rating_label', 'rating_count'], "clr_rating")
            c1, c2, c3 = st.columns(3)
            with c1:
                st.session_state.website_data['rating_score'] = st.text_input("评分", st.session_state.website_data.get('rating_score', ''))
            with c2:
                st.session_state.website_data['rating_label'] = st.text_input("标签", st.session_state.website_data.get('rating_label', ''), key="rl")
            with c3:
                st.session_state.website_data['rating_count'] = st.text_input("数量", st.session_state.website_data.get('rating_count', ''))
        
        # ===== 产品 =====
        with tabs[3]:
            section_header_with_clear("📋 区块标题", ['products_title', 'products_subtitle'], "clr_prod_title")
            st.session_state.website_data['products_title'] = st.text_input("标题", st.session_state.website_data.get('products_title', ''))
            st.session_state.website_data['products_subtitle'] = st.text_input("副标题", st.session_state.website_data.get('products_subtitle', ''))
            
            st.markdown("---")
            st.markdown("### 🍰 产品管理")
            
            # 初始化编辑状态
            if 'editing_product' not in st.session_state:
                st.session_state.editing_product = None
            
            # ===== 编辑产品面板 =====
            if st.session_state.editing_product:
                prod = db.get_product(st.session_state.editing_product)
                if prod:
                    st.markdown("### ✏️ 编辑产品")
                    with st.container():
                        c1, c2 = st.columns([1, 2])
                        with c1:
                            # 显示当前图片
                            if prod['image_path'] and os.path.exists(os.path.join(WEBSITE_DIR, prod['image_path'])):
                                st.image(os.path.join(WEBSITE_DIR, prod['image_path']), width=150)
                            else:
                                st.markdown("🍰 *暂无图片*")
                            # 图片上传
                            uploaded = st.file_uploader("更换图片", type=['jpg', 'jpeg', 'png'], key="edit_img")
                            if uploaded:
                                img_filename = f"product_{prod['id']}.jpg"
                                save_uploaded_image(uploaded, img_filename)
                                db.update_product(prod['id'], image_path=f"uploads/{img_filename}")
                                st.rerun()
                            
                            # 图片显示设置
                            st.markdown("**图片显示设置**")
                            fit_options = {'cover': '填充裁剪', 'contain': '完整显示', 'fill': '拉伸填充'}
                            pos_options = {'center': '居中', 'top': '顶部', 'bottom': '底部', 'left': '左侧', 'right': '右侧'}
                            c_fit, c_pos = st.columns(2)
                            with c_fit:
                                current_fit = prod.get('image_fit', 'cover') or 'cover'
                                edit_fit = st.selectbox("缩放模式", list(fit_options.keys()),
                                    index=list(fit_options.keys()).index(current_fit) if current_fit in fit_options else 0,
                                    key="edit_fit", format_func=lambda x: fit_options[x])
                            with c_pos:
                                current_pos = prod.get('image_position', 'center') or 'center'
                                edit_pos = st.selectbox("位置", list(pos_options.keys()),
                                    index=list(pos_options.keys()).index(current_pos) if current_pos in pos_options else 0,
                                    key="edit_pos", format_func=lambda x: pos_options[x])
                        
                        with c2:
                            edit_name = st.text_input("名称", prod['name'], key="edit_name")
                            edit_desc = st.text_input("描述", prod['description'] or '', key="edit_desc")
                            c_a, c_b = st.columns(2)
                            with c_a:
                                edit_price = st.text_input("价格", prod['price'] or '', key="edit_price")
                                edit_cat = st.selectbox("分类", db.PRODUCT_CATEGORIES, 
                                    index=db.PRODUCT_CATEGORIES.index(prod['category']) if prod['category'] in db.PRODUCT_CATEGORIES else 0,
                                    key="edit_cat")
                            with c_b:
                                edit_status = st.selectbox("状态", list(db.PRODUCT_STATUS.keys()),
                                    index=list(db.PRODUCT_STATUS.keys()).index(prod['status']),
                                    key="edit_status", format_func=lambda x: db.PRODUCT_STATUS[x])
                            
                            c_save, c_cancel = st.columns(2)
                            with c_save:
                                if st.button("💾 保存修改", type="primary", use_container_width=True):
                                    db.update_product(prod['id'], name=edit_name, description=edit_desc,
                                        price=edit_price, category=edit_cat, status=edit_status,
                                        image_fit=edit_fit, image_position=edit_pos)
                                    st.session_state.editing_product = None
                                    st.rerun()
                            with c_cancel:
                                if st.button("取消", use_container_width=True):
                                    st.session_state.editing_product = None
                                    st.rerun()
                    st.markdown("---")
            
            # ===== 产品列表 =====
            st.markdown("### 🍰 产品列表")
            products = db.get_all_products()
            if products:
                for prod in products:
                    status_label = db.PRODUCT_STATUS.get(prod['status'], '在售')
                    has_img = "📷" if prod['image_path'] else ""
                    c1, c2, c3, c4, c5, c6 = st.columns([3, 1, 1, 1, 1, 1])
                    with c1:
                        st.markdown(f"{has_img} **{prod['name']}** {status_label}")
                    with c2:
                        st.caption(prod['category'])
                    with c3:
                        st.caption(prod['price'] or '-')
                    with c4:
                        if st.button("✏️", key=f"edit_{prod['id']}", help="编辑"):
                            st.session_state.editing_product = prod['id']
                            st.rerun()
                    with c5:
                        if st.button("⬆️", key=f"up_{prod['id']}", help="上移"):
                            db.move_product(prod['id'], 'up')
                            st.rerun()
                    with c6:
                        if st.button("🗑️", key=f"del_{prod['id']}", help="删除"):
                            if prod['image_path']:
                                try: os.remove(os.path.join(WEBSITE_DIR, prod['image_path']))
                                except: pass
                            db.delete_product(prod['id'])
                            st.rerun()
            else:
                st.info("暂无产品，点击下方添加")
            
            # ===== 添加新产品 =====
            st.markdown("---")
            st.markdown("### ➕ 添加产品")
            
            # 图片上传（表单外）
            new_img = st.file_uploader("产品图片", type=['jpg', 'jpeg', 'png'], key="new_prod_img")
            
            with st.form("add_product"):
                c1, c2 = st.columns(2)
                with c1:
                    new_name = st.text_input("产品名称 *")
                    new_price = st.text_input("价格 (如 ¥280)")
                with c2:
                    new_cat = st.selectbox("分类", db.PRODUCT_CATEGORIES)
                    new_status = st.selectbox("状态", list(db.PRODUCT_STATUS.keys()), 
                        format_func=lambda x: db.PRODUCT_STATUS[x])
                new_desc = st.text_input("描述")
                
                if st.form_submit_button("添加产品", type="primary") and new_name:
                    # 添加产品
                    new_id = db.add_product(new_name, new_desc, new_price, new_cat, status=new_status)
                    # 保存图片
                    if new_img:
                        img_filename = f"product_{new_id}.jpg"
                        save_uploaded_image(new_img, img_filename)
                        db.update_product(new_id, image_path=f"uploads/{img_filename}")
                    st.rerun()
        
        
        # ===== 关于 =====
        with tabs[4]:
            section_header_with_clear("📋 标题", ['about_title'], "clr_about_t")
            st.session_state.website_data['about_title'] = st.text_input("标题", st.session_state.website_data.get('about_title', ''), key="abt", label_visibility="collapsed")
            
            section_header_with_clear("📝 段落1", ['about_text1'], "clr_ab1")
            st.session_state.website_data['about_text1'] = st.text_area("内容", st.session_state.website_data.get('about_text1', ''), height=80, label_visibility="collapsed")
            
            section_header_with_clear("📝 段落2", ['about_text2'], "clr_ab2")
            st.session_state.website_data['about_text2'] = st.text_area("内容", st.session_state.website_data.get('about_text2', ''), height=60, key="ab2", label_visibility="collapsed")
            
            for i in range(1, 4):
                section_header_with_clear(f"统计 {i}", [f'stat{i}_number', f'stat{i}_label'], f"clr_st{i}")
                c1, c2 = st.columns([1, 2])
                with c1:
                    st.session_state.website_data[f'stat{i}_number'] = st.text_input("数据", st.session_state.website_data.get(f'stat{i}_number', ''), key=f"sn{i}")
                with c2:
                    st.session_state.website_data[f'stat{i}_label'] = st.text_input("标签", st.session_state.website_data.get(f'stat{i}_label', ''), key=f"sl{i}")
        
        # ===== 联系 =====
        with tabs[5]:
            section_header_with_clear("📋 标题", ['contact_title', 'contact_subtitle'], "clr_ct")
            st.session_state.website_data['contact_title'] = st.text_input("标题", st.session_state.website_data.get('contact_title', ''), key="ct")
            st.session_state.website_data['contact_subtitle'] = st.text_input("副标题", st.session_state.website_data.get('contact_subtitle', ''), key="cs")
            
            section_header_with_clear("📍 地址", ['address_label', 'address'], "clr_addr")
            c1, c2 = st.columns([1, 3])
            with c1:
                st.session_state.website_data['address_label'] = st.text_input("标签", st.session_state.website_data.get('address_label', ''), key="al")
            with c2:
                st.session_state.website_data['address'] = st.text_input("内容", st.session_state.website_data.get('address', ''), key="ad")
            
            section_header_with_clear("🕐 营业时间", ['hours_label', 'hours'], "clr_hrs")
            c1, c2 = st.columns([1, 3])
            with c1:
                st.session_state.website_data['hours_label'] = st.text_input("标签", st.session_state.website_data.get('hours_label', ''), key="hl")
            with c2:
                st.session_state.website_data['hours'] = st.text_input("内容", st.session_state.website_data.get('hours', ''), key="hr")
            
            section_header_with_clear("📞 联系方式", ['phone_label', 'phone'], "clr_ph")
            c1, c2 = st.columns([1, 3])
            with c1:
                st.session_state.website_data['phone_label'] = st.text_input("标签", st.session_state.website_data.get('phone_label', ''), key="pl")
            with c2:
                st.session_state.website_data['phone'] = st.text_input("内容", st.session_state.website_data.get('phone', ''), key="ph")
            
            section_header_with_clear("🔗 社交媒体", ['social_instagram', 'social_line'], "clr_social")
            st.session_state.website_data['social_instagram'] = st.text_input("Instagram", st.session_state.website_data.get('social_instagram', ''))
            st.session_state.website_data['social_line'] = st.text_input("LINE", st.session_state.website_data.get('social_line', ''))
            
            section_header_with_clear("📝 页脚", ['footer_text'], "clr_footer")
            st.session_state.website_data['footer_text'] = st.text_input("版权文字", st.session_state.website_data.get('footer_text', ''), label_visibility="collapsed")
        
        # ===== 图片 =====
        with tabs[6]:
            st.markdown('<div class="section-header">🏪 基础图片</div>', unsafe_allow_html=True)
            c1, c2 = st.columns(2)
            with c1:
                st.caption("Logo")
                image_uploader('logo', '上传')
            with c2:
                st.caption("首页大图")
                image_uploader('hero', '上传')
            
            st.markdown('<div class="section-header">🍰 产品图片</div>', unsafe_allow_html=True)
            c1, c2, c3 = st.columns(3)
            with c1:
                st.caption("产品1")
                image_uploader('product1', '上传')
            with c2:
                st.caption("产品2")
                image_uploader('product2', '上传')
            with c3:
                st.caption("产品3")
                image_uploader('product3', '上传')
            
            st.markdown('<div class="section-header">🎯 自定义图标</div>', unsafe_allow_html=True)
            st.caption("上传图片替代表情符号")
            c1, c2, c3 = st.columns(3)
            with c1:
                st.caption("徽章")
                image_uploader('badge_icon', '上传')
            with c2:
                st.caption("评分⭐")
                image_uploader('rating_icon', '上传')
            with c3:
                st.caption("地址📍")
                image_uploader('address_icon', '上传')
            
            c1, c2, c3 = st.columns(3)
            with c1:
                st.caption("时间🕐")
                image_uploader('hours_icon', '上传')
            with c2:
                st.caption("电话📞")
                image_uploader('phone_icon', '上传')
            with c3:
                st.caption("Instagram")
                image_uploader('instagram_icon', '上传')
        
        # 保存按钮
        st.markdown("---")
        if st.button("💾 保存并发布", type="primary", use_container_width=True):
            image_keys = ['logo', 'hero', 'product1', 'product2', 'product3', 
                          'badge_icon', 'rating_icon', 'address_icon', 'hours_icon', 
                          'phone_icon', 'instagram_icon', 'line_icon']
            for k in image_keys:
                st.session_state.website_data[f'{k}_image'] = get_image_path(k)
            st.session_state.website_data['font_css'] = FONT_OPTIONS.get(
                st.session_state.website_data.get('font_family', 'Noto Sans JP'), "'Noto Sans JP', sans-serif")
            db.save_website_settings(st.session_state.website_data)
            # 添加产品列表用于发布
            publish_data = st.session_state.website_data.copy()
            publish_data['products'] = db.get_all_products()
            if publish_website(publish_data, INDEX_PATH):
                # 自动推送代码到 GitHub
                try:
                    import subprocess
                    subprocess.run(["git", "add", "."], check=True)
                    subprocess.run(["git", "commit", "-m", "Auto-update from Shop Admin"], check=False) # 允许空提交
                    subprocess.run(["git", "push"], check=True)
                    st.success("✅ 保存并发布成功！(云端同步中...)")
                except Exception as e:
                    st.warning(f"✅ 保存成功，但云端同步失败: {e}")
                
                st.balloons()
    
    with col_preview:
        st.subheader("👁️ 实时预览")
        preview_data = st.session_state.website_data.copy()
        image_keys = ['logo', 'hero', 
                      'badge_icon', 'rating_icon', 'address_icon', 'hours_icon', 
                      'phone_icon', 'instagram_icon', 'line_icon']
        # 使用base64编码图片（让iframe能显示）
        for k in image_keys:
            preview_data[f'{k}_image'] = get_image_base64(k)
        preview_data['font_css'] = FONT_OPTIONS.get(preview_data.get('font_family', 'Noto Sans JP'), "'Noto Sans JP', sans-serif")
        # 添加产品列表，并将产品图片转为base64
        products = db.get_all_products()
        import base64
        for prod in products:
            if prod['image_path']:
                img_full_path = os.path.join(WEBSITE_DIR, prod['image_path'])
                if os.path.exists(img_full_path):
                    try:
                        with open(img_full_path, "rb") as f:
                            prod['image_path'] = f"data:image/jpeg;base64,{base64.b64encode(f.read()).decode()}"
                    except:
                        prod['image_path'] = None
        preview_data['products'] = products
        components.html(render_website(preview_data), height=800, scrolling=True)
    
    # ===== 自动保存（每次页面刷新时执行）=====
    auto_save()
    st.sidebar.markdown("---")
    st.sidebar.success(f"💾 自动保存: {st.session_state.last_saved}")

# ==================== 店铺运营 ====================
elif page == "🏪 店铺运营":
    st.title("🏪 店铺运营")
    
    tab_staff, tab_inventory, tab_pos = st.tabs(["👥 员工", "📦 库存", "💰 收银"])
    
    with tab_staff:
        c1, c2 = st.columns([2, 1])
        with c1:
            st.markdown("### ⏰ 打卡")
            staff_list = db.get_all_staff()
            if staff_list:
                for staff in staff_list:
                    status = db.get_staff_status(staff['id'])
                    c_a, c_b, c_c, c_d = st.columns([3, 1, 1, 1])
                    with c_a:
                        icons = {"working": "🟢", "finished": "✅", "not_clocked_in": "⚪"}
                        st.markdown(f"{icons[status]} **{staff['name']}** (¥{staff['hourly_wage']:,.0f}/h)")
                    with c_b:
                        if status == "not_clocked_in" and st.button("上班", key=f"in_{staff['id']}"):
                            db.clock_in(staff['id'])
                            st.rerun()
                    with c_c:
                        if status == "working" and st.button("下班", key=f"out_{staff['id']}"):
                            db.clock_out(staff['id'])
                            st.rerun()
                    with c_d:
                        if st.button("🗑️", key=f"del_staff_{staff['id']}", help="停用员工"):
                            db.deactivate_staff(staff['id'])
                            st.rerun()
            else:
                st.info("暂无员工，请先添加")
            
            # 今日考勤记录
            st.markdown("---")
            st.markdown("### 📊 今日考勤")
            today_attendance = db.get_today_attendance()
            if today_attendance:
                for att in today_attendance:
                    clock_in = att['clock_in'].split('T')[-1][:5] if att['clock_in'] and 'T' in att['clock_in'] else (att['clock_in'][-8:-3] if att['clock_in'] else '-')
                    clock_out = att['clock_out'].split('T')[-1][:5] if att['clock_out'] and 'T' in att['clock_out'] else (att['clock_out'][-8:-3] if att['clock_out'] else '工作中')
                    hours = f"{att['hours_worked']:.1f}h" if att['hours_worked'] else '-'
                    wage = att['hourly_wage'] * att['hours_worked'] if att['hours_worked'] else 0
                    st.markdown(f"• {att['staff_name']}: {clock_in} → {clock_out} | {hours} | ¥{wage:,.0f}")
            else:
                st.caption("今日暂无考勤记录")
        
        with c2:
            st.markdown("### ➕ 添加员工")
            with st.form("add_staff"):
                name = st.text_input("姓名")
                wage = st.number_input("时薪(日元)", value=1200, step=100)
                if st.form_submit_button("添加", type="primary") and name:
                    db.add_staff(name, wage)
                    st.rerun()
    
    
    with tab_inventory:
        # 低库存警报
        low_stock = db.get_low_stock_items()
        if low_stock:
            st.error(f"⚠️ {len(low_stock)} 项库存不足！")
            with st.expander("查看低库存商品", expanded=False):
                for item in low_stock:
                    st.markdown(f"🔴 **{item['item_name']}**: {item['quantity']}/{item['threshold']} {item['unit']}")
        
        st.markdown("### 📦 库存列表")
        inventory = db.get_all_inventory()
        for item in inventory:
            is_low = item['quantity'] < item['threshold']
            c1, c2, c3, c4, c5 = st.columns([3, 2, 1, 1, 1])
            with c1:
                prefix = "🔴 " if is_low else ""
                st.markdown(f"{prefix}**{item['item_name']}**")
            with c2:
                color = "red" if is_low else "inherit"
                st.markdown(f"<span style='color:{color}'>{item['quantity']} {item['unit']}</span>", unsafe_allow_html=True)
            with c3:
                if st.button("➖", key=f"m_{item['id']}", help="减少1"):
                    if item['quantity'] > 0:
                        db.update_inventory_quantity(item['id'], -1)
                        st.rerun()
            with c4:
                if st.button("➕", key=f"a_{item['id']}", help="增加1"):
                    db.update_inventory_quantity(item['id'], 1)
                    st.rerun()
            with c5:
                if st.button("🗑️", key=f"d_{item['id']}", help="删除"):
                    db.delete_inventory_item(item['id'])
                    st.rerun()
        
        # 添加新库存
        st.markdown("---")
        st.markdown("### ➕ 添加库存")
        with st.form("add_inventory"):
            c1, c2 = st.columns(2)
            with c1:
                new_name = st.text_input("商品名称")
                new_qty = st.number_input("初始数量", min_value=0, value=10)
            with c2:
                new_category = st.selectbox("分类", ["Ingredient", "Packaging", "Other"])
                new_threshold = st.number_input("警戒线", min_value=1, value=10)
            new_unit = st.text_input("单位", value="个")
            if st.form_submit_button("添加", type="primary") and new_name:
                db.add_inventory_item(new_name, new_category, new_qty, new_threshold, new_unit)
                st.rerun()
    
    with tab_pos:
        c_menu, c_cart = st.columns([2, 1])
        
        # 从动态产品表获取菜单（排除售罄产品）
        products = db.get_all_products()
        menu_items = {}
        for prod in products:
            if prod['status'] != 'soldout' and prod['price']:
                # 解析价格字符串，提取数字
                price = int(''.join(filter(str.isdigit, prod['price'])) or '0')
                if price > 0:
                    menu_items[prod['name']] = price
        
        # 如果没有产品，显示提示
        if not menu_items:
            st.info("请先在网站编辑器的产品Tab添加产品")
        
        with c_menu:
            st.markdown("### 🍰 菜单")
            cols = st.columns(3)
            for idx, (item, price) in enumerate(menu_items.items()):
                with cols[idx % 3]:
                    if st.button(f"{item}\n¥{price:,}", key=f"m_{item}", use_container_width=True):
                        st.session_state.cart.append({'name': item, 'price': price})
                        st.rerun()
            
            # 今日销售记录
            st.markdown("---")
            st.markdown("### 📊 今日销售")
            today_sales = db.get_today_sales()
            if today_sales:
                for sale in today_sales[:5]:  # 只显示最近5笔
                    sale_time = sale['sale_date'].split('T')[-1][:5] if 'T' in sale['sale_date'] else sale['sale_date'][-8:-3]
                    st.markdown(f"• {sale_time} | {sale['items'][:15]}... | ¥{sale['total_amount']:,.0f} | {sale['payment_method']}")
                if len(today_sales) > 5:
                    st.caption(f"共 {len(today_sales)} 笔销售")
            else:
                st.caption("暂无销售记录")
        
        with c_cart:
            st.markdown("### 🛒 购物车")
            if st.session_state.cart:
                total = sum(i['price'] for i in st.session_state.cart)
                for idx, ci in enumerate(st.session_state.cart):
                    c1, c2 = st.columns([4, 1])
                    with c1:
                        st.markdown(f"{ci['name']} ¥{ci['price']:,}")
                    with c2:
                        if st.button("✕", key=f"del_cart_{idx}", help="删除"):
                            st.session_state.cart.pop(idx)
                            st.rerun()
                
                st.markdown(f"**合计: ¥{total:,}**")
                
                # 支付方式
                payment = st.radio("支付方式", ["现金", "PayPay", "信用卡", "交通卡"], horizontal=True, label_visibility="collapsed")
                
                c1, c2 = st.columns(2)
                with c1:
                    if st.button("🗑️ 清空", use_container_width=True):
                        st.session_state.cart = []
                        st.rerun()
                with c2:
                    if st.button("✅ 结账", type="primary", use_container_width=True):
                        db.record_sale(", ".join([i['name'] for i in st.session_state.cart]), total, payment)
                        st.session_state.cart = []
                        st.balloons()
                        st.rerun()
            else:
                st.info("购物车为空")
            
            st.markdown("---")
            st.metric("今日营业额", f"¥{db.get_today_total():,.0f}")

