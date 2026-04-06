# 实施检查清单

## 使用说明
本文档提供详细的检查项，用于在任务实施的每个阶段进行质量验证。请在完成每个任务后逐项勾选确认。

---

## 阶段1：环境准备检查

### 1.1 开发环境验证
- [ ] 后端服务运行在 http://localhost:8000
- [ ] 前端服务运行在 http://localhost:3000
- [ ] 浏览器可以访问两个地址
- [ ] 终端窗口可查看后端日志

### 1.2 代码备份（可选但推荐）
- [ ] 已了解当前代码状态
- [ ] 确认Git仓库可用（如使用版本控制）
- [ ] 记录当前问题现象以便对比修复效果

### 1.3 浏览器环境准备
- [ ] 打开浏览器开发者工具（F12）
- [ ] 切换到Console标签页
- [ ] 清除浏览器缓存和Cookie
- [ ] 在Console执行 `localStorage.clear()` 清除本地存储
- [ ] 关闭并重新打开开发者工具（确保干净状态）

---

## 阶段2：任务1 - 页面闪烁修复检查

### 2.1 代码修改检查
- [ ] 在setup函数中找到状态变量声明区域（约第1020行）
- [ ] 添加了 `const isInitializing = ref(true);` 变量
- [ ] 变量位于其他ref变量附近（保持代码组织性）
- [ ] onModified函数开头设置了 `isInitializing.value = true`
- [ ] try块结束前设置了 `isInitializing.value = false`
- [ ] catch块中也设置了 `isInitializing.value = false`

### 2.2 模板修改检查
- [ ] 找到登录容器的v-if条件（约第252行）
- [ ] 条件中添加了 `&& !isInitializing`
- [ ] 找到应用主容器的v-if条件（约第276行）
- [ ] 条件中添加了 `&& !isInitializing && isLoggedIn`
- [ ] （可选）添加了加载指示器元素

### 2.3 功能测试检查
**测试A：未登录用户访问**
- [ ] 清除localStorage：在Console执行 `localStorage.clear()`
- [ ] 刷新页面 http://localhost:3000/
- [ ] **关键观察**：页面直接显示登录表单（无失败提示闪现）
- [ ] 等待2秒，确认无任何内容变化或闪烁
- [ ] Console无红色错误信息
- [ ] 截图记录结果

**测试B：已登录用户访问**
- [ ] 使用 admin / admin123 登录系统
- [ ] 确认成功进入仪表板
- [ ] 刷新页面（F5）
- [ ] **关键观察**：直接显示仪表板（无登录页闪现）
- [ ] 等待2秒，确认内容稳定显示
- [ ] Console无红色错误信息
- [ ] 截图记录结果

**测试C：token失效场景**
- [ ] 在Application/Storage标签中手动删除token
- [ ] 刷新页面
- [ ] **观察**：应直接显示登录页（无失败提示）
- [ ] Console可能显示"验证登录状态失败"日志（这是正常的）

### 2.4 问题排查（如果测试失败）
如果仍然有闪烁：
- [ ] 检查loginError变量的初始值是否为空字符串
- [ ] 检查是否有其他代码在onMounted之前设置了错误信息
- [ ] 检查isInitializing是否正确导出并在return对象中
- [ ] 在Console执行 `document.querySelector('#app').__vue_app__` 查看Vue实例状态

---

## 阶段3：任务2 - 菜单白屏修复检查

### 3.1 数据加载函数检查
**loadDatasets函数**
- [ ] 函数位置在第1240-1247行
- [ ] 包含try-catch错误处理
- [ ] catch块中设置 `datasets.value = []`
- [ ] 无语法错误

**loadModels函数**
- [ ] 包含try-catch错误处理
- [ ] catch块中设置 `models.value = []`

**loadRules函数**
- [ ] 包含try-catch错误处理
- [ ] catch块中设置 `rules.value = []`

**loadTasks函数**
- [ ] 包含try-catch错误处理
- [ ] catch块中设置 `tasks.value = []`

**loadUsers函数**
- [ ] 如有需要也添加了错误处理（此函数当前可能缺少）

### 3.2 响应式变量初始化检查
- [ ] datasets 初始化为 `ref([])` 而非 `ref()` 或 `ref(null)`
- [ ] models 初始化为 `ref([])`
- [ ] rules 初始化为 `ref([])`
- [ ] tasks 初始化为 `ref([])`
- [ ] users 初始化为 `ref([])`

### 3.3 模板空值保护检查
**数据集列表模板（第466行）**
- [ ] v-for使用安全写法：`v-for="dataset in datasets"`
- [ ] 空状态判断使用：`v-if="!datasets || datasets.length === 0"`

**模型列表模板**
- [ ] 类似的空值保护已实现

**规则列表模板**
- [ ] input_fields访问使用可选链：`(rule.input_fields || []).join(', ')`
- [ ] 空状态判断正确

**任务列表模板**
- [ ] 空值保护已实现

**用户列表模板**
- [ ] 空值保护已实现

### 3.4 watch监听器检查
- [ ] watch(currentPage, ...) 位于第1272行
- [ ] 正确保存currentPage到localStorage
- [ ] switch语句覆盖所有页面类型
- [ ] 每个case调用对应的load*函数

### 3.5 功能测试检查
**前提条件**：已成功登录系统

**测试A：数据集管理页面**
- [ ] 点击侧边栏"数据集管理"菜单
- [ ] **关键观察**：主内容区域立即显示数据集表格
- [ ] 如果无数据显示"暂无数据集"提示（非白屏）
- [ ] 地址栏保持 http://localhost:3000/ 不变
- [ ] Console可看到 "加载数据集列表" 或 "loadDatasets called" 日志
- [ ] 截图记录

**测试B：大模型管理页面**
- [ ] 点击"大模型管理"菜单
- [ ] 显示模型列表或"暂无模型配置"提示
- [ ] 截图记录

**测试C：评估规则页面（仅管理员）**
- [ ] 点击"评估规则"菜单
- [ ] 显示规则列表或提示
- [ ] （如果是普通用户，此菜单应不显示）

**测试D：评估任务页面**
- [ ] 点击"评估任务"菜单
- [ ] 显示任务列表或提示
- [ ] 截图记录

**测试E：用户管理页面（仅管理员）**
- [ ] 点击"用户管理"菜单
- [ ] 显示用户列表或提示
- [ ] 截图记录

**测试F：返回仪表板**
- [ ] 点击"仪表板"菜单
- [ ] 显示仪表板内容和统计数字
- [ ] 截图记录

### 3.6 问题排查（如果测试失败）
如果点击菜单后白屏：
- [ ] 检查Console是否有JavaScript错误
- [ ] 检查Network标签页中API请求是否发送成功
- [ ] 检查API响应状态码是否为200
- [ ] 检查Vue DevTools中的组件状态（如安装）
- [ ] 临时在loadDatasets中添加console.log调试输出
- [ ] 确认currentPage.value确实改变为新值

---

## 阶段4：任务3 - 上传功能修复检查

### 4.1 后端代码检查
- [ ] 打开 `backend/main.py`
- [ ] 定位到第202-216行（数据库升级部分）
- [ ] 确认存在三个ALTER TABLE语句：
  - [ ] ADD COLUMN file_type
  - [ ] ADD COLUMN record_count  
  - [ ] ADD COLUMN created_by
- [ ] 每个ALTER TABLE都在try-except块中
- [ ] except捕获的是 sqlite3.OperationalError
- [ ] except块中使用 pass (静默忽略)

### 4.2 后端服务重启检查
- [ ] 停止旧的后端进程（terminal_id: 6f7ed062-c3fb-436c-bd66-a1566f1fe210）
- [ ] 启动新的后端进程：`python backend/main.py`
- [ ] 等待启动日志显示："Uvicorn running on http://0.0.0.0:8000"
- [ ] **关键**：启动日志中无红色错误或异常堆栈
- [ ] 特别注意：无 "OperationalError: table datasets has no column" 错误

### 4.3 数据库结构验证（可选）
- [ ] 可选：使用SQLite查看工具检查datasets表结构
- [ ] 或在后端添加临时API端点返回表结构信息
- [ ] 确认file_type、record_count、created_by列存在

### 4.4 上传功能测试检查
**准备阶段**
- [ ] 创建小的CSV测试文件（建议10-20行，5列以内）
- [ ] 文件内容示例：
  ```csv
  id,text,label
  1,测试文本1,正常
  2,测试文本2,异常
  ```
- [ ] 文件编码：UTF-8（推荐）
- [ ] 文件大小：< 1MB

**上传操作测试**
- [ ] 登录系统（admin账号）
- [ ] 进入"数据集管理"页面
- [ ] 点击"上传数据集"按钮
- [ ] 弹出模态对话框
- [ ] 选择准备好的CSV测试文件
- [ ] 填写数据集名称（如"测试数据集"）
- [ ] 点击"上传"按钮

**结果验证**
- [ ] **关键观察**：显示成功提示消息（非"failed to fetch"）
- [ ] 模态对话框自动关闭
- [ ] 数据集列表刷新
- [ ] 新上传的数据集出现在列表中
- [ ] 显示正确的文件名、格式、行列数等信息
- [ ] Console无红色错误
- [ ] 后端日志显示上传请求且状态码200

**多格式测试（可选但推荐）**
- [ ] 测试Excel文件上传（.xlsx, .xls）
- [ ] 测试JSON文件上传（.json）
- [ ] 验证不同格式的文件都能正确解析

### 4.5 问题排查（如果上传失败）
如果仍然报错"failed to fetch"：
- [ ] 检查后端日志中的具体错误信息
- [ ] 检查Network标签页中请求的详细信息：
  - [ ] 请求URL是否正确（POST /api/datasets/upload）
  - [ ] 请求方法是否为POST
  - [ ] Content-Type是否为multipart/form-data
  - [ ] 是否包含Authorization头
  - [ ] 请求体是否包含file字段
- [ ] 检查CORS相关错误（虽然应该已在之前修复）
- [ ] 检查文件大小是否超过限制
- [ ] 检查磁盘空间是否充足

---

## 阶段5：集成测试与最终验收

### 5.1 完整流程测试
**测试1：冷启动首次访问**
- [ ] 完全关闭浏览器
- [ ] 重新打开浏览器
- [ ] 访问 http://localhost:3000/
- [ ] 直接看到干净的登录页面
- [ ] 无任何闪烁或跳转
- [ ] ✅ 通过

**测试2：完整登录流程**
- [ ] 输入admin / admin123
- [ ] 点击登录
- [ ] 成功进入仪表板
- [ ] 显示统计数据（模型数、数据集数、任务数等）
- [ ] ✅ 通过

**测试3：完整菜单导航**
- [ ] 依次访问所有6个页面
- [ ] 每个页面内容正确显示
- [ ] 无白屏、无加载延迟
- [ ] 侧边栏高亮当前选中项
- [ ] ✅ 通过

**测试4：数据集上传完整流程**
- [ ] 上传CSV文件成功
- [ ] 文件出现在列表
- [ ] 可以预览数据集内容
- [ ] 可以删除数据集
- [ ] ✅ 通过

**测试5：页面刷新稳定性**
- [ ] 在任意页面按F5
- [ ] 保持当前页面状态
- [ ] 无闪烁
- [ ] 数据重新加载成功
- [ ] ✅ 通过

**测试6：退出登录**
- [ ] 点击退出按钮
- [ ] 返回登录页面
- [ ] localStorage已清除
- [ ] 再次访问需重新登录
- [ ] ✅ 通过

### 5.2 控制台清洁度检查
- [ ] 打开Console标签页
- [ ] 过滤只看Errors级别
- [ ] **理想状态**：0个红色错误
- [ ] 允许存在的警告（Warnings）：
  - [ ] favicon.ico 404（已通过CDN解决应消失）
  - [ ] 第三方库的警告（如requests依赖警告）
- [ ] 不允许存在的错误：
  - [ ] ❌ TypeError: Cannot read properties of undefined/null
  - [ ] ❌ Failed to fetch
  - [ ] ❌ Unexpected token '<' (JSON解析错误)

### 5.3 性能基准检查
- [ ] 首次页面加载时间 < 3秒
- [ ] 菜单切换响应时间 < 500ms
- [ ] API请求平均响应时间 < 200ms
- [ ] 页面滚动流畅（60fps）
- [ ] 无明显的UI卡顿或冻结

### 5.4 跨浏览器兼容性（可选）
- [ ] Chrome/Edge：完全正常
- [ ] Firefox：基本功能正常
- [ ] Safari：（如有Mac环境）基本功能正常

### 5.5 用户验收标准最终确认
- [ ] ✅ 问题1解决：访问页面无闪烁
- [ ] ✅ 问题2解决：菜单切换正常显示
- [ ] ✅ 问题3解决：数据集上传成功
- [ ] ✅ 整体体验：流畅自然，无明显缺陷
- [ ] ✅ 错误处理：友好且信息充分
- [ ] ✅ 代码质量：无新增技术债务

---

## 阶段6：文档与交付

### 6.1 修改记录
- [ ] 记录所有修改的文件和行号
- [ ] 记录每个修改的目的和原因
- [ ] 记录回滚方案（如需要）

### 6.2 测试报告
- [ ] 编写简短的测试总结
- [ ] 附上关键截图（可选）
- [ ] 标注仍存在的问题（如有）
- [ ] 提出后续改进建议（可选）

### 6.3 交付确认
- [ ] 用户测试并确认问题已解决
- [ ] 用户签署验收（口头或书面）
- [ ] 项目状态更新为"已完成"

---

## 快速参考卡片

### 常用命令
```bash
# 重启后端
# 在terminal 4中：Ctrl+C 停止，然后 python backend/main.py

# 重启前端
# 在新终端：cd frontend && python -m http.server 3000

# 清除浏览器存储
# 在Console中：localStorage.clear()

# 查看数据库表结构
# python -c "import sqlite3; conn = sqlite3.connect('backend/llm_security_evaluation.db'); cursor = conn.cursor(); cursor.execute('PRAGMA table_info(datasets)'); print(cursor.fetchall())"
```

### 关键文件位置
- 前端：`f:\llmsafe0403\aiev\frontend\index.html`
- 后端：`f:\llmsafe0403\aiev\backend\main.py`
- 数据库：`f:\llmsafe0403\aiev\backend\llm_security_evaluation.db`
- 规格文档：`f:\llmsafe0403\aiev\spec.md`
- 任务文档：`f:\llmsafe0403\aiev\tasks.md`
- 本检查清单：`f:\llmsafe0403\aiev\checklist.md`

### 常见问题速查
| 现象 | 可能原因 | 解决方案 |
|------|----------|----------|
| 页面闪烁 | isInitializing未生效 | 检查变量是否在return对象中 |
| 白屏 | 数据未加载 | 检查load函数是否被调用 |
| 上传失败 | 数据库列缺失 | 检查ALTER TABLE是否执行 |
| CORS错误 | origin配置错误 | 检查allow_origins设置 |
| 401错误 | token无效或过期 | 重新登录获取新token |

---

## 总结

本检查清单涵盖了从环境准备到最终交付的完整流程。请严格按照每个阶段的检查项逐一验证，确保每个修复都达到预期效果。

**重要提醒**：
1. 每完成一个任务立即进行对应阶段的检查
2. 发现问题时不要继续，先解决当前问题
3. 保持终端和浏览器开启以方便随时查看日志
4. 多截图保存关键节点的状态
5. 遇到不确定的情况优先询问而非猜测

祝实施顺利！🚀
