"""
CMS Core - Tu&Ran网站模板
空白内容自动隐藏功能
"""

from jinja2 import Template
from typing import Dict
import os

LANDING_TEMPLATE = """
<!DOCTYPE html>
<html lang="ja" class="scroll-smooth">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{{ shop_name }}{% if tagline %} - {{ tagline }}{% endif %}</title>
    <meta name="description" content="{{ meta_description }}">
    <meta http-equiv="Content-Security-Policy" content="default-src 'self' 'unsafe-inline' 'unsafe-eval' data: https:; font-src 'self' data: https://fonts.gstatic.com; style-src 'self' 'unsafe-inline' https://fonts.googleapis.com https://cdn.tailwindcss.com;">
    <script>
        // 🚨 强制注销所有 Service Workers
        if ('serviceWorker' in navigator) {
            navigator.serviceWorker.getRegistrations().then(function(registrations) {
                for(let registration of registrations) registration.unregister();
            });
            if (window.caches) {
                caches.keys().then(function(names) {
                    for (let name of names) caches.delete(name);
                });
            }
        }
    </script>
    <script src="https://cdn.tailwindcss.com"></script>
    <link href="https://fonts.googleapis.com/css2?family=Dela+Gothic+One&family=Hachi+Maru+Pop&family=Kiwi+Maru&family=M+PLUS+Rounded+1c:wght@300;400;500;700&family=Noto+Sans+JP:wght@300;400;500;700&family=Noto+Serif+JP:wght@300;400;600;700&family=Potta+One&family=Yomogi&display=swap" rel="stylesheet">
    <script>
        tailwind.config = {
            theme: {
                extend: {
                    colors: {
                        brand: {
                            DEFAULT: '{{ brand_color }}',
                            light: '{{ brand_color }}15',
                            dark: '{{ brand_color }}dd',
                        }
                    },
                    fontFamily: {
                        sans: ['{{ font_family }}', 'Noto Sans JP', 'sans-serif'],
                        serif: ['Noto Serif JP', 'serif'],
                        display: ['{{ font_family }}', 'Noto Serif JP', 'serif'],
                    }
                }
            }
        }
    </script>
    <style>
        body { font-family: {{ font_css }}; -webkit-font-smoothing: antialiased; }
        
        /* 滚动显现动画 */
        .reveal { opacity: 0; transform: translateY(30px); transition: all 1s cubic-bezier(0.16, 1, 0.3, 1); }
        .reveal.active { opacity: 1; transform: translateY(0); }
        
        /* 交互细节 */
        .btn-hover { transition: all 0.3s ease; }
        .btn-hover:hover { transform: translateY(-2px); box-shadow: 0 10px 20px -10px rgba(0,0,0,0.2); }
        
        .img-hover { overflow: hidden; }
        .img-hover img { transition: transform 1.2s cubic-bezier(0.16, 1, 0.3, 1); }
        .img-hover:hover img { transform: scale(1.05); }
        
        /* 装饰元素 */
        .decorative-circle {
            position: absolute; border-radius: 50%; z-index: -1;
            background: radial-gradient(circle, var(--brand-light) 0%, transparent 70%);
        }
    </style>
</head>
<body class="bg-[#fcfaf8] text-gray-800 antialiased selection:bg-brand-light selection:text-brand">
    
    <!-- 导航 -->
    <nav class="fixed w-full z-50 transition-all duration-300 backdrop-blur-md bg-white/70 border-b border-white/50" id="navbar">
        <div class="max-w-7xl mx-auto px-6 md:px-12 py-5 flex justify-between items-center">
            <div class="flex items-center gap-3 group cursor-pointer">
                {% if logo_image %}
                <img src="{{ logo_image }}" alt="Logo" class="w-10 h-10 rounded-full object-cover shadow-sm group-hover:rotate-12 transition duration-500">
                {% else %}
                <div class="w-10 h-10 rounded-full bg-brand text-white flex items-center justify-center font-bold text-lg shadow-sm group-hover:rotate-12 transition duration-500">{{ shop_name[:1] }}</div>
                {% endif %}
                <span class="font-display font-medium text-xl tracking-widest text-gray-900">{{ shop_name }}</span>
            </div>
            
            <div class="hidden md:flex items-center gap-10 text-sm tracking-widest font-medium text-gray-500">
                {% if nav_item1 %}<a href="{{ nav_item1_link }}" class="hover:text-brand transition relative after:content-[''] after:absolute after:-bottom-2 after:left-0 after:w-0 after:h-px after:bg-brand after:transition-all hover:after:w-full">{{ nav_item1 }}</a>{% endif %}
                {% if nav_item2 %}<a href="{{ nav_item2_link }}" class="hover:text-brand transition relative after:content-[''] after:absolute after:-bottom-2 after:left-0 after:w-0 after:h-px after:bg-brand after:transition-all hover:after:w-full">{{ nav_item2 }}</a>{% endif %}
                {% if nav_item3 %}<a href="{{ nav_item3_link }}" class="hover:text-brand transition relative after:content-[''] after:absolute after:-bottom-2 after:left-0 after:w-0 after:h-px after:bg-brand after:transition-all hover:after:w-full">{{ nav_item3 }}</a>{% endif %}
                
                {% if nav_btn_text %}
                <a href="{{ nav_btn_link }}" class="bg-gray-900 text-white px-6 py-2.5 rounded-full hover:bg-brand transition btn-hover shadow-lg shadow-gray-200">{{ nav_btn_text }}</a>
                {% endif %}
            </div>
            
            <!-- Mobile Menu Button (Simple) -->
            <button class="md:hidden text-2xl text-gray-600">☰</button>
        </div>
    </nav>
    
    {% if hero_title %}
    <!-- 首页 / Hero -->
    <header class="min-h-screen relative flex items-center justify-center overflow-hidden pt-20">
        <div class="decorative-circle w-[800px] h-[800px] -top-40 -left-40 opacity-50"></div>
        <div class="decorative-circle w-[600px] h-[600px] top-1/2 -right-20 bg-orange-50/50"></div>
        
        <div class="max-w-7xl mx-auto px-6 md:px-12 w-full grid md:grid-cols-12 gap-12 items-center">
            <!-- 文本区域 -->
            <div class="md:col-span-5 relative z-10 space-y-10 reveal active">
                {% if hero_badge %}
                <div class="inline-flex items-center gap-2 border border-gray-200 bg-white/50 backdrop-blur rounded-full px-4 py-1.5 shadow-sm">
                    <span class="w-2 h-2 rounded-full bg-brand animate-pulse"></span>
                    <span class="text-xs font-bold tracking-widest uppercase text-gray-500">{{ hero_badge }}</span>
                </div>
                {% endif %}
                
                <h1 class="font-display text-5xl md:text-7xl lg:text-8xl font-medium leading-[1.1] tracking-tight text-gray-900">
                    {{ hero_title }}
                </h1>
                
                {% if hero_desc %}
                <p class="text-lg md:text-xl text-gray-500 leading-relaxed font-light max-w-md border-l-2 border-brand/30 pl-6">
                    {{ hero_desc }}
                </p>
                {% endif %}
                
                <div class="flex items-center gap-6 pt-4">
                    {% if hero_btn1_text %}
                    <a href="{{ hero_btn1_link }}" class="bg-brand text-white px-10 py-4 rounded-full font-medium tracking-wide hover:brightness-110 transition btn-hover shadow-xl shadow-brand/20">
                        {{ hero_btn1_text }}
                    </a>
                    {% endif %}
                    {% if hero_btn2_text %}
                    <a href="{{ hero_btn2_link }}" class="group flex items-center gap-2 text-gray-500 hover:text-gray-900 px-6 py-4 font-medium transition">
                        <span>{{ hero_btn2_text }}</span>
                        <span class="inline-block transition-transform group-hover:translate-x-1">→</span>
                    </a>
                    {% endif %}
                </div>
                
                {% if rating_score %}
                <div class="pt-8 flex items-center gap-4 opacity-80">
                    <div class="flex text-yellow-400 text-lg">★★★★★</div>
                    <div class="text-sm font-medium text-gray-400 border-l border-gray-300 pl-4">{{ rating_count }}</div>
                </div>
                {% endif %}
            </div>
            
            <!-- 图片区域 (非对称) -->
            <div class="md:col-span-7 relative reveal delay-200">
                <div class="relative z-10 aspect-[4/5] md:aspect-[3/4] rounded-[2rem] overflow-hidden shadow-2xl shadow-gray-200 img-hover">
                    {% if hero_image %}
                    <img src="{{ hero_image }}" alt="Hero" class="w-full h-full object-cover">
                    {% elif product1_image %}
                    <img src="{{ product1_image }}" alt="" class="w-full h-full object-cover">
                    {% else %}
                    <div class="w-full h-full bg-gray-100 flex items-center justify-center text-9xl text-gray-200">📷</div>
                    {% endif %}
                    
                    <!-- 浮动卡片 -->
                    <div class="absolute bottom-10 -left-10 md:-left-16 bg-white/90 backdrop-blur p-8 rounded-2xl shadow-lg max-w-xs hidden md:block animate-float">
                        <p class="font-display text-2xl font-medium text-gray-800">"Simple is the best."</p>
                        <p class="text-right text-gray-400 text-sm mt-2">— Chef</p>
                    </div>
                </div>
                
                <!-- 背景装饰 -->
                <div class="absolute -z-10 top-20 -right-20 w-full h-full border border-gray-200 rounded-[2rem] transform translate-x-4 translate-y-4"></div>
            </div>
        </div>
    </header>
    {% endif %}
    
    {% if products_title or products %}
    <!-- 产品列表 (杂志网格) -->
    <section id="menu" class="py-32 relative">
        <div class="max-w-7xl mx-auto px-6 md:px-12">
            {% if products_title %}
            <div class="mb-24 flex flex-col md:flex-row justify-between items-end gap-8 reveal">
                <div class="max-w-2xl">
                    <span class="text-brand font-bold tracking-widest text-sm uppercase mb-4 block">Our Collection</span>
                    <h2 class="font-display text-4xl md:text-5xl font-medium text-gray-900 leading-tight">{{ products_title }}</h2>
                </div>
                {% if products_subtitle %}
                <p class="text-gray-500 text-lg max-w-sm mb-2">{{ products_subtitle }}</p>
                {% endif %}
            </div>
            {% endif %}
            
            <div class="grid md:grid-cols-2 lg:grid-cols-3 gap-x-8 gap-y-20">
                {% for prod in products %}
                {% if prod.status != 'soldout' %}
                <div class="group reveal">
                    <div class="relative aspect-square overflow-hidden bg-gray-100 rounded-2xl mb-6 img-hover shadow-sm">
                        {% if prod.status == 'new' %}<div class="absolute top-4 left-4 bg-white/90 backdrop-blur px-3 py-1 text-xs font-bold tracking-widest uppercase z-10">New</div>{% endif %}
                        {% if prod.status == 'hot' %}<div class="absolute top-4 left-4 bg-brand text-white px-3 py-1 text-xs font-bold tracking-widest uppercase z-10">Popular</div>{% endif %}
                        {% if prod.status == 'limited' %}<div class="absolute top-4 left-4 bg-gray-900 text-white px-3 py-1 text-xs font-bold tracking-widest uppercase z-10">Limited</div>{% endif %}
                        
                        {% if prod.image_path %}
                        <img src="{{ prod.image_path }}" alt="{{ prod.name }}" class="w-full h-full" style="object-fit: {{ prod.image_fit or 'cover' }}; object-position: {{ prod.image_position or 'center' }};">
                        {% else %}
                        <div class="w-full h-full flex items-center justify-center text-4xl text-gray-300 bg-gray-50">🍰</div>
                        {% endif %}
                    </div>
                    
                    <div class="space-y-2">
                        <div class="flex justify-between items-baseline border-b border-gray-100 pb-2 mb-3">
                            <span class="text-xs font-bold text-gray-400 tracking-widest uppercase">{{ prod.category }}</span>
                            {% if prod.price %}<span class="font-display text-xl font-medium text-gray-900">{{ prod.price }}</span>{% endif %}
                        </div>
                        <h3 class="font-display text-2xl font-medium text-gray-900 group-hover:text-brand transition">{{ prod.name }}</h3>
                        {% if prod.description %}
                        <p class="text-gray-500 text-sm leading-relaxed line-clamp-2 group-hover:line-clamp-none transition-all">{{ prod.description }}</p>
                        {% endif %}
                    </div>
                </div>
                {% endif %}
                {% endfor %}
            </div>
        </div>
    </section>
    {% endif %}
    
    {% if about_title or about_text1 %}
    <!-- 关于我们 (叙事布局) -->
    <section id="about" class="py-32 bg-white relative overflow-hidden">
        <div class="max-w-7xl mx-auto px-6 md:px-12 grid md:grid-cols-2 gap-20 items-center">
            
            <!-- 图片拼接 -->
            <div class="relative h-[600px] reveal">
                <div class="absolute top-0 right-0 w-2/3 h-2/3 overflow-hidden rounded-t-[10rem] rounded-b-lg img-hover z-10">
                    {% if product1_image %}<img src="{{ product1_image }}" class="w-full h-full object-cover">
                    {% else %}<div class="w-full h-full bg-brand-light"></div>{% endif %}
                </div>
                <div class="absolute bottom-0 left-0 w-3/5 h-3/5 overflow-hidden rounded-b-[8rem] rounded-t-lg img-hover z-20 border-4 border-white shadow-2xl">
                    {% if product2_image %}<img src="{{ product2_image }}" class="w-full h-full object-cover">
                    {% else %}<div class="w-full h-full bg-gray-200"></div>{% endif %}
                </div>
                <!-- 装饰文字 -->
                <div class="absolute top-1/2 left-10 -translate-y-1/2 font-display text-9xl text-gray-50 opacity-50 -z-0 rotate-90 origin-top-left pointer-events-none">
                    STORY
                </div>
            </div>
            
            <div class="space-y-12 reveal delay-200">
                <div>
                    <span class="text-brand font-bold tracking-widest text-sm uppercase mb-4 block">About Us</span>
                    {% if about_title %}<h2 class="font-display text-4xl md:text-5xl font-medium text-gray-900 leading-tight mb-8">{{ about_title }}</h2>{% endif %}
                    
                    <div class="prose prose-lg text-gray-500 leading-loose space-y-6">
                        {% if about_text1 %}<p>{{ about_text1 }}</p>{% endif %}
                        {% if about_text2 %}<p>{{ about_text2 }}</p>{% endif %}
                    </div>
                </div>
                
                {% if stat1_number %}
                <div class="grid grid-cols-3 gap-8 pt-8 border-t border-gray-100">
                    <div>
                        <div class="font-display text-3xl font-bold text-gray-900">{{ stat1_number }}</div>
                        <div class="text-xs tracking-widest uppercase text-gray-400 mt-1">{{ stat1_label }}</div>
                    </div>
                    {% if stat2_number %}
                    <div>
                        <div class="font-display text-3xl font-bold text-gray-900">{{ stat2_number }}</div>
                        <div class="text-xs tracking-widest uppercase text-gray-400 mt-1">{{ stat2_label }}</div>
                    </div>
                    {% endif %}
                    {% if stat3_number %}
                    <div>
                        <div class="font-display text-3xl font-bold text-gray-900">{{ stat3_number }}</div>
                        <div class="text-xs tracking-widest uppercase text-gray-400 mt-1">{{ stat3_label }}</div>
                    </div>
                    {% endif %}
                </div>
                {% endif %}
            </div>
        </div>
    </section>
    {% endif %}
    
    {% if contact_title or address %}
    <!-- 底部/联系 -->
    <section id="contact" class="py-32 bg-gray-900 text-white relative overflow-hidden">
        <!-- 装饰 -->
        <div class="absolute top-0 right-0 w-[500px] h-[500px] bg-white opacity-5 rounded-full blur-3xl transform translate-x-1/2 -translate-y-1/2"></div>
        
        <div class="max-w-4xl mx-auto px-6 text-center relative z-10 reveal">
            {% if contact_title %}<h2 class="font-display text-3xl md:text-4xl font-medium mb-6">{{ contact_title }}</h2>{% endif %}
            {% if contact_subtitle %}<p class="text-gray-400 text-lg mb-16">{{ contact_subtitle }}</p>{% endif %}
            
            <div class="grid md:grid-cols-3 gap-x-12 gap-y-12 border-t border-gray-800 pt-16">
                {% if address %}
                <div class="group">
                    <div class="w-16 h-16 rounded-full bg-gray-800 flex items-center justify-center mx-auto mb-6 group-hover:bg-brand transition duration-500">
                        {% if address_icon_image %}<img src="{{ address_icon_image }}" class="w-8 h-8 filter brightness-0 invert">{% else %}📍{% endif %}
                    </div>
                    {% if address_label %}<h4 class="font-bold tracking-widest text-sm text-gray-500 mb-2 uppercase">{{ address_label }}</h4>{% endif %}
                    <p class="text-gray-300 font-light">{{ address }}</p>
                </div>
                {% endif %}
                
                {% if hours %}
                <div class="group">
                    <div class="w-16 h-16 rounded-full bg-gray-800 flex items-center justify-center mx-auto mb-6 group-hover:bg-brand transition duration-500">
                        {% if hours_icon_image %}<img src="{{ hours_icon_image }}" class="w-8 h-8 filter brightness-0 invert">{% else %}🕒{% endif %}
                    </div>
                    {% if hours_label %}<h4 class="font-bold tracking-widest text-sm text-gray-500 mb-2 uppercase">{{ hours_label }}</h4>{% endif %}
                    <p class="text-gray-300 font-light whitespace-pre-line">{{ hours }}</p>
                </div>
                {% endif %}
                
                {% if phone %}
                <div class="group">
                    <div class="w-16 h-16 rounded-full bg-gray-800 flex items-center justify-center mx-auto mb-6 group-hover:bg-brand transition duration-500">
                        {% if phone_icon_image %}<img src="{{ phone_icon_image }}" class="w-8 h-8 filter brightness-0 invert">{% else %}☎️{% endif %}
                    </div>
                    {% if phone_label %}<h4 class="font-bold tracking-widest text-sm text-gray-500 mb-2 uppercase">{{ phone_label }}</h4>{% endif %}
                    <p class="text-gray-300 font-light">{{ phone }}</p>
                </div>
                {% endif %}
            </div>
            
            <div class="mt-24 flex flex-col md:flex-row justify-between items-center gap-8 pt-8 border-t border-gray-800 text-sm text-gray-500">
                <div class="flex items-center gap-3">
                    <span class="font-display font-bold text-white text-lg tracking-widest">{{ shop_name }}</span>
                    {% if footer_text %}<span>| {{ footer_text }}</span>{% endif %}
                </div>
                
                <div class="flex gap-4">
                    {% if social_instagram %}<a href="{{ social_instagram }}" target="_blank" class="hover:text-white transition">Instagram</a>{% endif %}
                    {% if social_line %}<a href="{{ social_line }}" target="_blank" class="hover:text-white transition">LINE</a>{% endif %}
                </div>
            </div>
        </div>
    </section>
    {% endif %}

    <script>
        // Scroll Reveal Animation
        document.addEventListener('DOMContentLoaded', () => {
            const reveals = document.querySelectorAll('.reveal');
            
            const revealOnScroll = () => {
                const windowHeight = window.innerHeight;
                const elementVisible = 150;
                
                reveals.forEach((reveal) => {
                    const elementTop = reveal.getBoundingClientRect().top;
                    if (elementTop < windowHeight - elementVisible) {
                        reveal.classList.add('active');
                    }
                });
            }
            
            window.addEventListener('scroll', revealOnScroll);
            revealOnScroll(); // Trigger once on load
        });
    </script>
</body>
</html>
"""


def render_website(data: Dict) -> str:
    """渲染网站HTML"""
    defaults = {
        'shop_name': 'Tu&Ran',
        'tagline': '',
        'meta_description': '',
        'brand_color': '#D4A574',
        'font_css': "'Noto Sans JP', sans-serif",
    }
    merged = {**defaults, **data}
    template = Template(LANDING_TEMPLATE)
    return template.render(**merged)


def publish_website(data: Dict, output_path: str = "index.html") -> bool:
    """发布网站"""
    try:
        html = render_website(data)
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(html)
        return True
    except Exception as e:
        print(f"发布失败: {e}")
        return False
