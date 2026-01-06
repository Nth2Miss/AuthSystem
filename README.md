# 用户注册登录系统

这是一个使用 Flask 作为后端和 Vue 作为前端的用户认证系统，支持邮箱注册和登录功能，包含验证码验证。

## 功能特性

- 用户注册：输入邮箱和密码，通过邮箱验证码验证完成注册
- 用户登录：输入邮箱和密码，通过图形验证码验证完成登录
- 邮箱验证：使用 Flask-Mail 发送验证码（仅用于注册）
- 图形验证码：4位数字图形验证码，用于登录验证
- 验证码：4位数字验证码，10分钟有效期
- 频率限制：防止频繁发送验证码

## 技术栈

- 后端：Flask、Flask-SQLAlchemy、Flask-Mail
- 前端：Vue 3、Axios、Vite
- 数据库：SQLite（默认）

## 安装和运行

### 后端设置

1. 安装 Python 依赖：
   
   ```bash
   cd backend
   pip install -r requirements.txt
   ```

2. 配置环境变量：
   在 `.env` 文件中设置邮箱服务信息：
   
   ```
   SECRET_KEY=your-secret-key-here
   MAIL_SERVER=smtp.gmail.com
   MAIL_PORT=587
   MAIL_USE_TLS=True
   MAIL_USERNAME=your-email@gmail.com
   MAIL_PASSWORD=your-app-password
   ```

3. 运行 Flask 应用：
   
   ```bash
   python app.py
   ```
   
   应用将在 `http://localhost:5000` 启动

### 前端设置

1. 安装 Node.js 依赖：
   
   ```bash
   cd frontend
   npm install
   ```

2. 运行开发服务器：
   
   ```bash
   npm run dev
   ```
   
   应用将在 `http://localhost:3000` 启动，并自动代理 API 请求到后端

## API 接口

- `POST /api/register` - 用户注册
- `POST /api/login` - 用户登录
- `POST /api/send-verification-code` - 发送邮箱验证码
- `GET /api/generate-captcha` - 生成图形验证码
- `POST /api/refresh-captcha` - 刷新图形验证码

## 邮箱配置说明

要使用 Mail 发送验证码，请按以下步骤配置：

1. 开启 Mail 的两步验证
2. 生成应用专用密码
3. 在 `.env` 文件中配置以下信息：
   - `MAIL_USERNAME`: 你的 Mail 地址
   - `MAIL_PASSWORD`: 你的应用专用密码

其他邮件服务提供商的配置方式类似，请参考相应文档。

## 安全说明

- 验证码有效期为10分钟
- 限制验证码发送频率（1分钟内不能重复发送）
- 密码使用哈希存储
- 前后端分离，使用 CORS 进行跨域配置

## 生产环境建议

在生产环境中，建议：

- 使用 Redis 存储验证码（当前使用内存存储）
- 使用更安全的邮件服务
- 添加更多安全措施，如速率限制、IP 封禁等
- 使用 HTTPS 协议
- 使用生产级数据库（如 PostgreSQL 或 MySQL）
