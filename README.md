# NDDF对偶模型计算工具

基于非径向方向距离函数(NDDF)对偶模型的影子价格和边际减排成本计算工具。

## 功能特性

- 支持自定义投入、期望产出、非期望产出列配置
- 支持CRS(规模报酬不变)和VRS(规模报酬可变)两种模式
- 多进程并行计算，显著提升计算效率
- Excel文件上传，支持多工作簿选择
- 计算结果实时预览与导出
- 友好的Web界面

## 技术栈

- **前端**: Vue 3 + Element Plus + Vite
- **后端**: Python + FastAPI
- **优化求解器**: Google OR-Tools (GLOP)

## 项目结构

```
NDDF对偶模型计算工具/
├── backend/                    # 后端服务
│   ├── main.py                 # FastAPI 主应用
│   ├── models.py               # 数据模型定义
│   ├── solver.py               # NDDF对偶模型求解器
│   └── requirements.txt        # Python 依赖
├── frontend/                   # 前端应用
│   ├── src/
│   │   ├── components/
│   │   │   ├── ConfigForm.vue  # 配置表单组件
│   │   │   ├── DataPanel.vue   # 数据上传面板
│   │   │   └── ResultTable.vue # 结果展示表格
│   │   ├── App.vue
│   │   ├── api.js
│   │   └── main.js
│   ├── index.html
│   ├── package.json
│   └── vite.config.js
├── install.bat                 # 安装依赖脚本
├── start.bat                   # 启动应用脚本
└── README.md
```

## 快速开始

### 环境要求

- Python 3.9+
- Node.js 18+
- npm 或 yarn

### 安装步骤

1. **克隆仓库**
```bash
git clone https://github.com/Pei-hsinWang/nddf-calculator.git
cd nddf-calculator
```

2. **安装依赖**

Windows用户可直接双击运行 `install.bat`，或手动执行：

```bash
# 安装后端依赖
cd backend
pip install -r requirements.txt

# 安装前端依赖
cd ../frontend
npm install
```

3. **启动应用**

Windows用户可直接双击运行 `start.bat`，或手动执行：

```bash
# 启动后端服务 (终端1)
cd backend
python main.py

# 启动前端服务 (终端2)
cd frontend
npm run dev
```

4. **访问应用**

- 前端界面: http://localhost:3000
- 后端API: http://localhost:8000
- API文档: http://localhost:8000/docs

## 使用说明

### 1. 配置参数

在左侧配置面板设置：
- **ID列名**: 数据中的标识列（如：id）
- **年份列名**: 数据中的年份列（如：年份）
- **规模报酬类型**: CRS 或 VRS
- **投入要素**: 设置列名、方向向量、权重
- **期望产出**: 设置列名、方向向量、权重
- **非期望产出**: 设置列名、方向向量、权重

### 2. 上传数据

- 支持拖拽或点击上传 Excel 文件 (.xlsx, .xls)
- 上传后可选择不同的工作簿
- 自动预览前10行数据

### 3. 计算与导出

- 点击"开始计算"按钮执行计算
- 计算完成后查看结果表格
- 点击"导出Excel"下载结果文件

## 计算结果说明

| 字段 | 说明 |
|------|------|
| Efficiency_NDDF | NDDF效率值 |
| Zeta | VRS模式下的截距项 |
| Price_X | 投入要素X的影子价格 |
| Price_Y | 期望产出Y的影子价格 |
| Price_B | 非期望产出B的影子价格 |
| MAC_B | 非期望产出B的边际减排成本 |

## API接口

| 接口 | 方法 | 说明 |
|------|------|------|
| `/api/upload` | POST | 上传Excel文件 |
| `/api/sheet-data` | POST | 获取指定工作簿数据 |
| `/api/compute` | POST | 执行计算 |
| `/api/export` | POST | 导出结果 |
| `/api/columns-info` | GET | 获取默认配置信息 |

## 许可证

MIT License

## 作者

Pei-hsinWang
