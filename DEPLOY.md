# 🚀 烘焙店网站云端部署指南

本指南将帮助你将网站部署到 **Vercel** (前端) 和 **Supabase** (数据库)，并将后台部署到 **Streamlit Cloud**。

## 1. 为什么推荐云端部署？
相比于 "使用自己的公网 IP 部署" (自托管)，云端部署有以下绝对优势，特别是对于面向日本客户的商用网站：
- **稳定性**: 云服务器 24/7 在线，不会因为你家电脑关机、睡眠或断网而无法访问。
- **速度**: Vercel 在全球（包括日本）都有节点，访问速度远快于家庭宽带。
- **安全性**: 不需要暴露你家里的真实 IP，避免被黑客攻击家庭网络。
- **固定域名**: 云平台提供固定的 URL (如 `.vercel.app`)，而家庭宽带 IP 通常每天都会变。

如果你坚持要使用**本机公网 IP**，你需要：
1. 拥有公网 IP (需要联系运营商)。
2. 配置路由器端口映射 (Port Forwarding)。
3. 确保电脑 24 小时开机且不休眠。
4. 处理动态 IP 问题 (DDNS)。
*(这通常非常麻烦且不稳定，不建议商用)*

## 2. 准备工作


### 注册账号
- [GitHub](https://github.com/) (用于存放代码)
- [Vercel](https://vercel.com/) (使用 GitHub 登录)
- [Supabase](https://supabase.com/) (使用 GitHub 登录)
- [Streamlit Cloud](https://streamlit.io/cloud) (使用 GitHub 登录)

### 推送代码到 GitHub
1. 在 GitHub 上创建一个新仓库（例如 `lemon-shop`）。
2. 在本地终端执行：
   ```bash
   git init
   git add .
   git commit -m "Initial commit"
   git branch -M main
   # 将 URL 替换为你创建的仓库地址
   git remote add origin https://github.com/YOUR_USERNAME/lemon-shop.git
   git push -u origin main
   ```

---

## 2. 数据库部署 (Supabase)

1. 登录 Supabase，点击 **"New Project"**。
2. 设置数据库密码（**务必记住**）。
3. 选择区域（建议选择离你近的，如 Tokyo 或 Singapore）。
4. 等待项目创建完成（约1-2分钟）。
5. 进入 **Project Settings -> Database**。
6. 找到 **Connection String (URI)**，复制它。格式如：
   `postgresql://postgres:[PASSWORD]@db.xxxx.supabase.co:5432/postgres`
   *将 `[PASSWORD]` 替换为你设置的密码。*

> 💡 **提示**: 我们的代码会自动在第一次运行时创建表，所以不需要手动建表。

---

## 3. 后台部署 (Streamlit Cloud)

1. 登录 Streamlit Cloud，点击 **"New app"**。
2. 选择刚才创建的 GitHub 仓库 (`lemon-shop`)。
3. **Main file path** 输入 `shop_admin.py`。
4. 点击 **"Advanced settings"**。
5. 在 **Secrets** 区域，输入你的数据库连接串：
   ```toml
   [env]
   DATABASE_URL = "postgresql://postgres:你的密码@db.xxxx.supabase.co:5432/postgres"
   ```
6. 点击 **"Deploy!"**。
7. 等待部署完成，你将获得一个后台管理网址（例如 `https://lemon-shop-admin.streamlit.app`）。

---

## 4. 前台部署 (Vercel)

由于我们的网站是动态生成的（图片、产品数据都在数据库中），推荐将前台也作为动态应用部署。

**简单方案：使用 Streamlit 托管前台**
我们可以在 `shop_admin.py` 中添加一个只读的“顾客模式”，直接通过 Streamlit 访问。

**进阶方案：使用 Flask/FastAPI + Vercel**
1. 创建一个新的 `app.py` 使用 Flask 读取数据库并渲染 `index.html`。
2. 在 Vercel 部署该 Flask 应用。

---
