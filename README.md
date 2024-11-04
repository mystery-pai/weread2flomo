# 微信读书笔记处理器

这是一个使用 Python 和 Streamlit 开发的应用程序，用于处理微信读书笔记。它可以解析笔记文本、使用 LLM 进行润色，并将处理后的笔记导出到 Flomo。

## 功能

1. **笔记解析**
   - 自动提取书籍信息（书名、作者、笔记数量）
   - 识别章节结构
   - 解析单条笔记内容

2. **LLM 处理**
   - 使用 LLM API 润色笔记内容
   - 自动生成笔记小标题
   - 智能生成相关标签

3. **Flomo 导出**
   - 自动格式化笔记内容
   - 包含章节信息和标签
   - 批量导出到 Flomo

4. **交互式处理**
   - 卡片式笔记展示
   - 支持单条笔记处理和导出
   - 支持批量处理和导出
   - 可编辑处理后的内容
## 界面
![界面](https://s2.loli.net/2024/11/03/CIAbSxgXdNDztVh.png)
## 安装

1. 克隆此仓库：
   ```bash
   git clone https://github.com/mystery-pai/weread2flomo.git
   cd weread2flomo
   ```

2. 创建虚拟环境：
   ```bash
   python -m venv venv
   ```

3. 激活虚拟环境：
   ```bash
   # Windows:
   .\venv\Scripts\activate

   # MacOS/Linux:
   source venv/bin/activate
   ```

4. 安装依赖：
   ```bash
   pip install -r requirements.txt
   ```

## 配置

在 `config/settings.py` 文件中配置以下参数：

```python
# LLM API配置
LLM_API_ENDPOINT = "your_llm_api_endpoint"
LLM_MODEL = "your_model_name"
LLM_API_KEY = "your_api_key"

# Flomo API配置
FLOMO_API_ENDPOINT = "your_flomo_api_endpoint"
```

## 使用方法

1. 配置 API 参数：
   - 在 `config/settings.py` 中设置 LLM 和 Flomo 的 API 配置

2. 运行 Streamlit 应用：
   ```bash
   streamlit run app.py
   ```

3. 在浏览器中打开显示的 URL（通常是 http://localhost:8501）

4. 使用步骤：
   - 将微信读书笔记文本复制并粘贴到输入框
   - 点击"解析笔记"按钮，查看解析结果
   - 在笔记卡片中：
     * 查看原始笔记内容（左侧）
     * 点击"润色"按钮处理单条笔记
     * 编辑处理后的标题、内容和标签（右侧）
     * 点击"导出到 Flomo"按钮导出单条笔记
   - 批量操作：
     * 使用"批量润色"按钮一次处理所有笔记
     * 使用"批量导出到 Flomo"按钮一次导出所有处理后的笔记

## 笔记格式要求

支持的微信读书笔记格式示例：
```
《书名》

作者名
N个笔记

章节名称

◆ 笔记内容

-- 来自微信读书
```

## 模块说明

- `note_parser.py`: 负责解析微信读书笔记文本，提取书籍信息和笔记内容
- `llm_processor.py`: 使用 LLM API 处理笔记，包括润色内容、生成标题和标签
- `flomo_exporter.py`: 负责将处理后的笔记格式化并导出到 Flomo
- `api_helpers.py`: 提供 API 调用相关的辅助函数

## 注意事项

1. 确保在 `config/settings.py` 中正确配置 API 密钥
2. 保持网络连接稳定，以确保 API 调用正常
3. 建议一次处理的笔记数量不要过多，以避免 API 调用限制

## 贡献

欢迎提交问题和拉取请求。对于重大更改，请先开 issue 讨论您想要更改的内容。

## 许可证

[MIT](https://choosealicense.com/licenses/mit/)
