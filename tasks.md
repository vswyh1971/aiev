# 任务分解清单

## 总览
本文档将规格说明中定义的解决方案分解为可执行的具体任务，每个任务包含明确的输入、输出和验收标准。

---

## 任务1：修复页面闪烁问题

**优先级**：P0 (关键)  
**预计时间**：10分钟  
**依赖关系**：无  
**负责模块**：前端初始化逻辑

### 输入
- 当前文件：`frontend/index.html`
- 问题现象：访问页面时短暂显示登录失败信息

### 具体步骤
1. **添加初始化状态变量**
   - 位置：Vue setup函数中的状态声明部分（约第1020行附近）
   - 操作：添加 `const isInitializing = ref(true);`
   
2. **修改onMounted函数**
   - 位置：第1577-1604行
   - 操作：
     a. 在函数开始时设置 `isInitializing.value = true`
     b. 在try块成功后设置 `isInitializing.value = false`
     c. 在catch块中也设置 `isInitializing.value = false`
   
3. **更新模板条件渲染**
   - 位置：登录容器和应用主容器的v-if/v-show条件
   - 操作：添加 `&& !isInitializing` 条件
   
4. **可选：添加加载指示器**
   - 位置：在根元素内添加loading spinner
   - 操作：当 `isInitializing.value === true` 时显示

### 输出
- 修改后的 `frontend/index.html`
- 无闪烁的页面加载体验

### 验收标准
- [ ] 清除localStorage后刷新页面，直接看到干净的登录页（无失败提示闪现）
- [ ] 已登录用户刷新页面后直接进入仪表板（无登录页闪现）
- [ ] 控制台无相关错误日志

### 回滚方案
如果修改导致问题：
```javascript
// 删除 isInitializing 相关代码
// 恢复原始 onMounted 逻辑
```

---

## 任务2：修复菜单白屏问题

**优先级**：P0 (关键)  
**预计时间**：15分钟  
**依赖关系**：任务1完成后更佳（但非必须）  
**负责模块**：前端数据加载与状态管理

### 输入
- 当前文件：`frontend/index.html`
- 问题现象：点击菜单项后白屏，内容不更新

### 具体步骤
1. **增强loadDatasets函数**
   - 位置：第1240-1247行
   - 当前实现：
     ```javascript
     async function loadDatasets() {
         try {
             datasets.value = await apiRequest('GET', '/api/datasets');
         } catch (error) {
             console.error('加载数据集列表失败:', error);
             datasets.value = [];
         }
     }
   ```
   - 验证：确认此实现已存在且正确
   
2. **检查datasets响应式变量初始化**
   - 位置：setup函数中（约第1030行附近）
   - 确认：`const datasets = ref([]);` （必须是空数组而非undefined）
   
3. **检查模板空值保护**
   - 位置：第466行和第487行
   - 确认：
     ```html
     <tr v-for="dataset in datasets" :key="dataset.id">
     ...
     <tr v-if="!datasets || datasets.length === 0">
     ```
   
4. **检查watch监听器**
   - 位置：第1272-1282行
   - 确认currentPage变化时正确触发数据加载
   
5. **添加调试日志（临时）**
   - 在loadDatasets开头添加：
     ```javascript
     console.log('loadDatasets called, currentPage:', currentPage.value);
     ```
   - 在loadDatasets成功后添加：
     ```javascript
     console.log('datasets loaded:', datasets.value.length, 'items');
     ```

### 输出
- 修改后的 `frontend/index.html`
- 可正常切换的数据集管理页面

### 验收标准
- [ ] 登录后点击"数据集菜单"，页面立即显示数据集列表或"暂无数据集"提示
- [ ] 点击其他菜单项（模型、规则、任务、用户）均正常显示
- [ ] 控制台可以看到数据加载日志

### 回滚方案
如果修改导致问题：
- 移除所有新增的console.log
- 恢复原有的loadDatasets实现

---

## 任务3：修复上传数据集失败问题

**优先级**：P0 (关键)  
**预计时间**：5分钟  
**依赖关系**：无  
**负责模块**：后端数据库结构

### 输入
- 当前文件：`backend/main.py`
- 数据库文件：`backend/llm_security_evaluation.db`
- 问题现象：上传时报错 "table datasets has no column named file_type"

### 具体步骤
1. **验证数据库升级代码**
   - 位置：第202-216行
   - 确认以下代码已存在且格式正确：
     ```python
     # 升级数据集表结构（确保所有必要的列都存在）
     try:
         cursor.execute("ALTER TABLE datasets ADD COLUMN file_type VARCHAR(20) DEFAULT 'csv'")
     except sqlite3.OperationalError:
         pass
     
     try:
         cursor.execute("ALTER TABLE datasets ADD COLUMN record_count INTEGER DEFAULT 0")
     except sqlite3.OperationalError:
         pass
     
     try:
         cursor.execute("ALTER TABLE datasets ADD COLUMN created_by INTEGER")
     except sqlite3.OperationalError:
         pass
     ```
   
2. **重启后端服务**
   - 停止当前运行的后端进程（terminal_id: 6f7ed062-c3fb-436c-bd66-a1566f1fe210）
   - 重新启动：`python backend/main.py`
   
3. **验证表结构升级**
   - 检查启动日志是否正常（无报错）
   - 可选：使用SQLite工具查看datasets表结构
   
4. **测试上传功能**
   - 通过浏览器UI上传一个小的CSV文件
   - 验证返回成功消息
   - 验证文件出现在数据集列表中

### 输出
- 升级后的数据库（自动完成）
- 重启后的后端服务
- 可正常工作的上传功能

### 验收标准
- [ ] 后端启动无错误日志
- [ ] 上传CSV文件成功，显示成功提示
- [ ] 上传的文件出现在数据集列表中
- [ ] 文件名、大小等信息正确显示

### 回滚方案
如果升级失败：
1. 删除现有数据库文件：`backend/llm_security_evaluation.db`
2. 重启后端服务（会自动创建新的完整表结构）
3. 注意：此操作会丢失所有现有数据

---

## 任务4：集成测试与验证

**优先级**：P0 (关键)  
**预计时间**：10分钟  
**依赖关系**：任务1、2、3全部完成  
**负责模块**：端到端测试

### 输入
- 完成前三个任务的系统
- 浏览器（Chrome/Firefox/Edge）

### 具体步骤
1. **环境准备**
   - 打开浏览器开发者工具（F12）
   - 切换到Console标签页
   - 清除浏览器缓存（Ctrl+Shift+Delete）
   - 清除localStorage：在Console执行 `localStorage.clear()`
   
2. **测试场景A：首次访问（未登录）**
   - 访问 http://localhost:3000/
   - 观察是否直接显示干净登录页（无闪烁）
   - 检查Console无红色错误
   - 截图记录
   
3. **测试场景B：登录流程**
   - 输入用户名：admin
   - 输入密码：admin123
   - 点击登录按钮
   - 观察是否跳转到仪表板
   - 检查Console无红色错误
   - 截图记录
   
4. **测试场景C：菜单切换**
   - 依次点击：仪表板 → 大模型管理 → 数据集管理 → 评估规则 → 评估任务 → 用户管理
   - 每个页面应正常显示内容或空状态提示
   - 地址栏应保持 http://localhost:3000/ 不变（SPA正常行为）
   - 截图记录每个页面
   
5. **测试场景D：数据集上传**
   - 进入数据集管理页面
   - 点击"上传数据集"按钮
   - 选择一个小的CSV测试文件（<100行）
   - 点击上传
   - 验证成功提示出现
   - 验证文件出现在列表中
   
6. **测试场景E：页面刷新（已登录）**
   - 在任意页面按F5刷新
   - 应保持登录状态并显示当前页面
   - 无闪烁或白屏
   
7. **收集测试结果**
   - 记录每个测试用例的结果（通过/失败）
   - 记录任何异常行为
   - 记录Console中的错误或警告

### 输出
- 测试报告文档（文本形式）
- 每个测试场景的截图（可选）
- 发现的问题清单（如有）

### 验收标准
- [ ] 所有测试场景通过
- [ ] Console无JavaScript运行时错误
- [ ] 无UI闪烁或白屏
- [ ] 数据集上传功能正常工作

### 回滚方案
如果测试发现新问题：
- 根据具体问题定位到对应任务的修改
- 使用Git回滚该任务的修改
- 重新测试确保回归到稳定状态

---

## 任务依赖关系图

```
任务1 (修复闪烁)
    ↓
任务2 (修复白屏) ← 可并行，但建议在任务1后
    ↓
任务3 (修复上传) ← 完全独立，可并行
    ↓
任务4 (集成测试) ← 必须在1、2、3之后
```

## 时间线估算

| 时间 | 任务 | 状态 |
|------|------|------|
| 0-10min | 任务1：修复页面闪烁 | ⬜ 待开始 |
| 10-25min | 任务2：修复菜单白屏 | ⬜ 待开始 |
| 5-10min | 任务3：修复上传失败（可与任务2并行）| ⬜ 待开始 |
| 25-35min | 任务4：集成测试验证 | ⬜ 待开始 |

**总预计时间**：35分钟（串行）或 25分钟（部分并行）

## 资源需求
- 开发终端：用于查看日志和编辑代码
- 浏览器：用于测试前端功能
- 后端服务：需要在8000端口运行
- 前端服务：需要在3000端口运行

## 成功指标
所有任务完成后，系统应达到以下标准：
1. ✅ 页面加载流畅，无视觉闪烁
2. ✅ 所有菜单可正常切换，内容正确显示
3. ✅ 数据集上传功能完全可用
4. ✅ 无控制台JavaScript错误
5. ✅ 用户体验流畅自然
