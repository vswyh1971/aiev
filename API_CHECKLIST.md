# API 端点检查清单

## 认证 API
- [x] POST /api/auth/login - 用户登录

## 用户管理 API
- [x] GET /api/users - 获取用户列表
- [x] POST /api/users - 创建用户
- [x] PUT /api/users/{user_id} - 更新用户
- [x] DELETE /api/users/{user_id} - 删除用户

## 系统 LLM API
- [x] GET /api/models?category=system - 获取系统 LLM 列表
- [x] POST /api/models/system - 创建系统 LLM
- [x] PUT /api/models/{model_id} - 更新系统 LLM
- [x] DELETE /api/models/{model_id}?category=system - 删除系统 LLM
- [x] POST /api/models/system/{model_id}/test - 测试系统 LLM 连接

## 评估 LLM API
- [x] GET /api/models?category=evaluation - 获取评估 LLM 列表
- [x] POST /api/models/evaluation - 创建评估 LLM
- [x] PUT /api/models/{model_id} - 更新评估 LLM
- [x] DELETE /api/models/{model_id}?category=evaluation - 删除评估 LLM
- [x] POST /api/models/evaluation/{model_id}/test - 测试评估 LLM 连接

## 数据集管理 API
- [x] GET /api/datasets - 获取数据集列表
- [x] POST /api/datasets - 创建数据集
- [x] GET /api/datasets/{dataset_id}/data - 获取数据集数据（分页）

## 评估规则 API
- [x] GET /api/rules - 获取规则列表
- [x] POST /api/rules - 创建规则
- [x] GET /api/rules/{rule_id} - 获取规则详情
- [x] PUT /api/rules/{rule_id} - 更新规则
- [x] DELETE /api/rules/{rule_id} - 删除规则

## 评估任务 API
- [x] GET /api/tasks - 获取任务列表
- [x] POST /api/tasks - 创建任务
- [x] POST /api/tasks/{task_id}/start - 启动任务
- [x] POST /api/tasks/{task_id}/pause - 暂停任务
- [x] GET /api/tasks/{task_id}/results - 获取任务结果
- [x] GET /api/tasks/{task_id}/download/full_pdf - 下载全量 PDF 报告
- [x] GET /api/tasks/{task_id}/download/full_json - 下载全量 JSON 报告
- [x] GET /api/tasks/{task_id}/download/failed_pdf - 下载失败 PDF 报告
- [x] GET /api/tasks/{task_id}/download/failed_json - 下载失败 JSON 报告
- [x] DELETE /api/tasks/{task_id} - 删除任务

## 数据库表结构
- [x] users - 用户表
  - id, username, password_hash, role, is_active, created_at, created_by
- [x] system_llms - 系统 LLM 表
  - id, name, provider, model_type, api_url, api_key_encrypted, auth_type, access_token, max_tokens, temperature, status, response_timeout, owner_id, created_at, updated_at
- [x] evaluation_llms - 评估 LLM 表
  - id, name, provider, model_type, api_url, api_key_encrypted, auth_type, access_token, max_tokens, temperature, status, response_timeout, owner_id, created_at, updated_at
- [x] datasets - 数据集表
  - id, name, file_name, file_path, file_format, encoding, size_bytes, row_count, column_count, has_header, schema_json, metadata_json, owner_id, created_by, created_at, updated_at, description, case_count
- [x] evaluation_rules - 评估规则表
  - id, name, rule_config_json, created_at
- [x] evaluation_tasks - 评估任务表
  - id, name, model_id, dataset_id, rule_id, status, progress_percent, total_cases, completed_cases, passed_cases, failed_cases, error_count, start_time, end_time, result_summary, report_file_path, owner_id, created_at, updated_at, full_report_file_path, failed_report_file_path, full_pdf_path, failed_pdf_path, error_cases, model_category, created_by
- [x] evaluation_results - 评估结果表
  - id, task_id, case_index, input_data, model_output, evaluation_result, details_text, model_response_time, created_at

## 前端字段映射
- [x] 模型对象使用 `category` 字段（不是 `model_category`）
- [x] 数据集对象包含 `description` 和 `case_count` 字段
- [x] 登录响应包含 `access_token`, `username`, `role` 字段
