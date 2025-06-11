# AI金融助手

这是一个基于大语言模型的金融助手应用，可以回答金融相关问题并提供实时数据分析。

## 功能特点

- 回答金融相关问题
- 查询股票价格和市场数据
- 实时显示AI思考过程
- 响应式用户界面

## 系统要求

### 后端
- Python 3.8+
- FastAPI
- LangChain
- 其他依赖项（见`backend/requirements.txt`）

### 前端
- Node.js 14+
- React
- TypeScript
- Vite

## 快速启动

本项目提供了多种启动脚本，适用于不同的操作系统：

### Windows

#### 使用批处理文件（推荐）

双击`start.bat`文件或在命令提示符中运行：

```
start.bat
```

#### 使用PowerShell

在PowerShell中运行：

```powershell
.\start.ps1
```

### Linux/macOS

在终端中运行：

```bash
chmod +x start.sh  # 只需第一次运行时执行此命令，赋予执行权限
./start.sh
```

## 手动启动

如果自动启动脚本不起作用，您可以手动启动前后端服务：

### 启动后端

```bash
cd backend
python main.py
```

### 启动前端

```bash
cd frontend
npm run dev
```

## 访问应用

启动成功后，您可以通过以下地址访问应用：

- 前端界面：http://localhost:5173
- 后端API：http://localhost:3000

## 配置

### 后端配置

在`backend/.env`文件中设置您的API密钥和其他配置项。

### 前端配置

如果后端运行在不同的地址，请修改`frontend/src/services/config.ts`文件中的`API_BASE_URL`。

## 显示AI思考过程

应用默认启用了AI思考过程的实时显示功能。您可以在界面上通过切换开关来启用或禁用此功能。

## 故障排除

### WebSocket连接失败

如果您看到WebSocket连接错误，请检查：

1. 确保后端服务正在运行
2. 检查`frontend/src/services/config.ts`中的URL配置是否正确
3. 确保您的浏览器支持WebSocket

### 其他问题

如果遇到其他问题，请查看控制台日志以获取更多信息。