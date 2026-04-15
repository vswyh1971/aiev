def run_evaluation(task_id: int):
    """执行评估任务"""
    print(f"========== 开始执行评估任务 ID: {task_id} ==========")
    
    conn = None
    cursor = None
    total_cases = 0
    passed = 0
    failed = 0
    errors = 0
    report_path = None
    full_report_path = None
    failed_report_path = None
    full_pdf_path = None
    failed_pdf_path = None
    eval_model_name = None
    
    try:
        conn = sqlite3.connect(DATABASE_PATH)
        cursor = conn.cursor()
        
        # 获取任务信息
        cursor.execute("""
            SELECT t.id, t.name, t.model_id, t.dataset_id, t.rule_id,
                   COALESCE(s.api_url, e.api_url) as api_url, 
                   COALESCE(s.api_key_encrypted, e.api_key_encrypted) as api_key_encrypted, 
                   COALESCE(s.model_type, e.model_type) as model_type, 
                   COALESCE(s.max_tokens, e.max_tokens) as max_tokens, 
                   COALESCE(s.temperature, e.temperature) as temperature, 
                   COALESCE(s.response_timeout, e.response_timeout) as response_timeout, 
                   d.file_path, d.name as dataset_name, r.name as rule_name,
                   r.rule_config_json
            FROM evaluation_tasks t
            LEFT JOIN system_llms s ON t.model_id = s.id
            LEFT JOIN evaluation_llms e ON t.model_id = e.id
            JOIN datasets d ON t.dataset_id = d.id
            JOIN evaluation_rules r ON t.rule_id = r.id
            WHERE t.id = ?
        """, (task_id,))
        task = cursor.fetchone()
        
        if not task:
            logger.error(f"任务 {task_id} 不存在")
            # 更新任务状态为失败
            try:
                cursor.execute("UPDATE evaluation_tasks SET status='failed', result_summary=? WHERE id=?", 
                              ("任务不存在", task_id))
                conn.commit()
            except Exception as db_error:
                logger.error(f"更新任务状态失败: {str(db_error)}")
            return
        
        # 数据验证：检查任务数据完整性
        if len(task) < 15:
            logger.error(f"任务 {task_id} 数据不完整")
            # 更新任务状态为失败
            try:
                cursor.execute("UPDATE evaluation_tasks SET status='failed', result_summary=? WHERE id=?", 
                              ("任务数据不完整", task_id))
                conn.commit()
            except Exception as db_error:
                logger.error(f"更新任务状态失败: {str(db_error)}")
            return
        
        # 获取任务信息
        task_name = task[1]
        eval_model_id = task[2]
        
        logger.info(f"开始评估任务: {task_name} (ID: {task_id})")
        logger.info(f"评估LLM ID: {eval_model_id}")
        
        # ========== 步骤0: 删除现有评估结果 ==========
        logger.info("步骤0: 删除现有评估结果")
        try:
            # 删除该任务的所有现有评估结果
            cursor.execute("DELETE FROM evaluation_results WHERE task_id = ?", (task_id,))
            conn.commit()
            logger.info(f"成功删除任务 {task_id} 的现有评估结果")
        except Exception as e:
            logger.error(f"删除现有评估结果失败: {str(e)}")
        
        # ========== 步骤1: 测试评估LLM连接 ==========
        logger.info("步骤1: 测试评估LLM连接")
        
        cursor.execute("""
            SELECT id, name, api_url, api_key_encrypted, model_type, max_tokens, temperature, response_timeout
            FROM system_llms WHERE id = ?
        """, (eval_model_id,))
        eval_model = cursor.fetchone()
        
        if not eval_model:
            cursor.execute("""
                SELECT id, name, api_url, api_key_encrypted, model_type, max_tokens, temperature, response_timeout
                FROM evaluation_llms WHERE id = ?
            """, (eval_model_id,))
            eval_model = cursor.fetchone()
        
        if not eval_model:
            error_msg = f"评估LLM (ID: {eval_model_id}) 不存在"
            logger.error(error_msg)
            cursor.execute("UPDATE evaluation_tasks SET status='failed', result_summary=? WHERE id=?", 
                          (error_msg, task_id))
            conn.commit()
            return
        
        # 数据验证：检查评估模型数据完整性
        if len(eval_model) < 8:
            error_msg = f"评估LLM (ID: {eval_model_id}) 数据不完整"
            logger.error(error_msg)
            cursor.execute("UPDATE evaluation_tasks SET status='failed', result_summary=? WHERE id=?", 
                          (error_msg, task_id))
            conn.commit()
            return
        
        eval_model_id, eval_model_name, eval_api_url, eval_api_key, eval_model_type, eval_max_tokens, eval_temperature, eval_timeout = eval_model
        eval_timeout = eval_timeout or 30
        
        logger.info(f"测试评估LLM: {eval_model_name}")
        eval_success, eval_message = test_llm_connection(eval_api_url, eval_api_key, eval_model_type, eval_timeout)
        
        if not eval_success:
            error_msg = f"评估LLM连接失败: {eval_message} (模型: {eval_model_name})"
            logger.error(error_msg)
            cursor.execute("UPDATE evaluation_tasks SET status='failed', result_summary=? WHERE id=?", 
                          (error_msg, task_id))
            conn.commit()
            return
        
        logger.info(f"评估LLM [{eval_model_name}] 连接测试通过 ✓")
        
        # ========== 步骤2: 查找可用的系统LLM ==========
        logger.info("步骤2: 查找可用的系统LLM")
        
        sys_success, sys_model, sys_message = find_available_system_llm()
        
        if not sys_success:
            error_msg = f"系统LLM连接失败: {sys_message}"
            logger.error(error_msg)
            cursor.execute("UPDATE evaluation_tasks SET status='failed', result_summary=? WHERE id=?", 
                          (error_msg, task_id))
            conn.commit()
            return
        
        logger.info(f"系统LLM [{sys_model['name']}] 选择成功 ✓")
        
        # ========== 步骤3: 双重验证通过，开始评估 ==========
        logger.info("步骤3: 双重验证通过，开始评估")
        
        # 更新任务状态为运行中
        cursor.execute("UPDATE evaluation_tasks SET status='running', start_time=CURRENT_TIMESTAMP WHERE id=?", (task_id,))
        conn.commit()
        
        # 解析规则配置
        task_rule_config = task[14] if len(task) > 14 else None
        try:
            rule_config = json.loads(task_rule_config) if task_rule_config else {}
        except Exception as e:
            logger.error(f"解析规则配置失败: {str(e)}")
            rule_config = {}
        
        # 数据验证：检查规则配置完整性
        if not rule_config.get('evaluation_criteria'):
            logger.warning("评估规则未设置，使用默认规则")
            rule_config['evaluation_criteria'] = '根据评估标准判断输出是否合规'
        
        logger.info(f"评估规则: {rule_config.get('evaluation_criteria')}")
        logger.info(f"输入字段: {rule_config.get('input_fields', [])}")
        logger.info(f"期望输出字段: {rule_config.get('expected_field', '')}")
        
        # 加载数据集
        file_path = task[11] if len(task) > 11 else None  # d.file_path
        dataset_name = task[12] if len(task) > 12 else '未知数据集'
        
        if not file_path:
            error_msg = "数据集文件路径无效"
            print(f"错误: {error_msg}")
            cursor.execute("UPDATE evaluation_tasks SET status='failed', result_summary=? WHERE id=?", 
                          (error_msg, task_id))
            conn.commit()
            return
        
        # 使用get_dataset_file_path函数解析正确的路径
        file_path = get_dataset_file_path(file_path)
        
        if not os.path.exists(file_path):
            error_msg = f"数据集文件不存在: {file_path}"
            print(f"错误: {error_msg}")
            cursor.execute("UPDATE evaluation_tasks SET status='failed', result_summary=? WHERE id=?", 
                          (error_msg, task_id))
            conn.commit()
            return
        
        # 读取数据集
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                dataset = json.load(f)
        except Exception as e:
            error_msg = f"加载数据集失败: {str(e)}"
            print(f"错误: {error_msg}")
            cursor.execute("UPDATE evaluation_tasks SET status='failed', result_summary=? WHERE id=?", 
                          (error_msg, task_id))
            conn.commit()
            return
        
        if not isinstance(dataset, list):
            error_msg = "数据集格式错误，应为列表"
            print(f"错误: {error_msg}")
            cursor.execute("UPDATE evaluation_tasks SET status='failed', result_summary=? WHERE id=?", 
                          (error_msg, task_id))
            conn.commit()
            return
        
        total_cases = len(dataset)
        logger.info(f"数据集加载成功，共 {total_cases} 个测试用例")
        
        # 初始化任务进度
        cursor.execute("UPDATE evaluation_tasks SET total_cases=?, progress_percent=0, completed_cases=0, passed_cases=0, failed_cases=0, error_count=0 WHERE id=?", 
                      (total_cases, task_id))
        conn.commit()
        
        # 遍历数据集执行评估
        for idx, case in enumerate(dataset):
            print(f"  [{idx+1}/{total_cases}] 评估中...")
            logger.info(f"评估用例 {idx+1}/{total_cases}")
            
            # 提取输入文本
            if isinstance(case, dict):
                input_text = case.get('prompt', case.get('input', case.get('text', '')))
            else:
                input_text = str(case)
            
            if not input_text:
                print(f"  [{idx+1}/{total_cases}] 跳过：无输入文本")
                logger.warning(f"用例 {idx+1} 无输入文本，跳过")
                errors += 1
                continue
            
            # 调用评估LLM
            max_retries = 3
            retry_count = 0
            while retry_count < max_retries:
                try:
                    model_output, response_time = call_llm(eval_api_url, eval_api_key, input_text, 
                                                        eval_model_type, eval_max_tokens, 
                                                        eval_temperature, eval_timeout)
                    
                    if "Error:" in model_output:
                        print(f"  [{idx+1}/{total_cases}] 模型错误: {model_output}")
                        logger.error(f"模型错误: {model_output}")
                        errors += 1
                        try:
                            cursor.execute("""
                                INSERT INTO evaluation_results (task_id, case_index, evaluation_result, details_text)
                                VALUES (?, ?, ?, ?)
                            """, (task_id, idx, 'error', model_output))
                            conn.commit()
                        except Exception as e2:
                            logger.error(f"保存错误记录失败: {str(e2)}")
                        break
                    
                    # 使用系统LLM进行评估
                    eval_result, eval_tokens, eval_process = evaluate_with_system_llm(
                        case, model_output, rule_config,
                        sys_model['api_url'], sys_model['api_key'], sys_model['model_type'],
                        sys_model.get('timeout', 30)
                    )
                    
                    # 解析评估结果
                    if "评估结果: 通过" in eval_result:
                        evaluation_result = "passed"
                        passed += 1
                    elif "评估结果: 不通过" in eval_result:
                        evaluation_result = "failed"
                        failed += 1
                    else:
                        evaluation_result = "error"
                        errors += 1
                    
                    # 保存评估结果
                    try:
                        cursor.execute("""
                            INSERT INTO evaluation_results (task_id, case_index, evaluation_result, details_text)
                            VALUES (?, ?, ?, ?)
                        """, (task_id, idx, evaluation_result, eval_process))
                        conn.commit()
                    except Exception as e2:
                        logger.error(f"保存评估结果失败: {str(e2)}")
                    
                    # 计算并更新进度
                    progress = int((idx + 1) / total_cases * 100)
                    try:
                        cursor.execute("UPDATE evaluation_tasks SET progress_percent=?, completed_cases=?, passed_cases=?, failed_cases=?, error_count=? WHERE id=?",
                                    (progress, idx + 1, passed, failed, errors, task_id))
                        conn.commit()
                    except Exception as e2:
                        logger.error(f"更新任务进度失败: {str(e2)}")
                    
                    break
                except Exception as e:
                    retry_count += 1
                    print(f"  [{idx+1}/{total_cases}] 评估失败，重试 {retry_count}/{max_retries}: {str(e)}")
                    logger.error(f"评估失败，重试 {retry_count}/{max_retries}: {str(e)}")
                    
                    if retry_count >= max_retries:
                        print(f"  [{idx+1}/{total_cases}] 达到最大重试次数 ({max_retries})，停止重新评估")
                        errors += 1
                        try:
                            cursor.execute("""
                                INSERT INTO evaluation_results (task_id, case_index, evaluation_result, details_text)
                                VALUES (?, ?, ?, ?)
                            """, (task_id, idx, 'error', str(e)))
                            conn.commit()
                        except Exception as e2:
                            logger.error(f"保存错误记录失败: {str(e2)}")
        
        # 生成报告
        logger.info("生成评估报告")
        
        try:
            # 生成全量PDF报告
            full_pdf_path = generate_full_pdf_report(task_id, cursor)
            logger.info(f"全量PDF报告已生成: {full_pdf_path}")
            
            # 生成不合格记录PDF报告
            failed_pdf_path = generate_failed_pdf_report(task_id, cursor)
            logger.info(f"不合格记录PDF报告已生成: {failed_pdf_path}")
            
            # 设置默认报告路径为全量报告
            report_path = full_pdf_path
        except Exception as e:
            logger.error(f"PDF报告生成失败: {str(e)}")
        
        # 生成全量JSON报告（仅管理员可访问）
        try:
            full_report_path = generate_full_json_report(task_id, cursor)
            logger.info(f"全量JSON报告已生成: {full_report_path}")
        except Exception as e:
            logger.error(f"全量JSON报告生成失败: {str(e)}")
        
        # 生成未通过评估报告（用户可访问）
        try:
            failed_report_path = generate_failed_json_report(task_id, cursor)
            logger.info(f"未通过JSON报告已生成: {failed_report_path}")
        except Exception as e:
            logger.error(f"未通过JSON报告生成失败: {str(e)}")
        
        # 更新最终状态
        try:
            cursor.execute("""
                UPDATE evaluation_tasks SET status='completed', end_time=CURRENT_TIMESTAMP,
                                        result_summary=?, report_file_path=?, 
                                        full_report_file_path=?, failed_report_file_path=?,
                                        full_pdf_path=?, failed_pdf_path=? WHERE id=?
            """, (f"总计{total_cases}例，通过{passed}例，失败{failed}例，异常{errors}例", 
                  report_path, full_report_path, failed_report_path,
                  full_pdf_path, failed_pdf_path, task_id))
            conn.commit()
            logger.info(f"评估任务状态已更新")
        except Exception as e:
            logger.error(f"更新评估任务状态失败: {str(e)}")
            # 重试机制
            import time
            for i in range(3):
                try:
                    time.sleep(1)
                    conn = sqlite3.connect(DATABASE_PATH)
                    cursor = conn.cursor()
                    cursor.execute("""
                        UPDATE evaluation_tasks SET status='completed', end_time=CURRENT_TIMESTAMP,
                                                result_summary=?, report_file_path=?, 
                                                full_report_file_path=?, failed_report_file_path=?,
                                                full_pdf_path=?, failed_pdf_path=? WHERE id=?
                    """, (f"总计{total_cases}例，通过{passed}例，失败{failed}例，异常{errors}例", 
                          report_path, full_report_path, failed_report_path,
                          full_pdf_path, failed_pdf_path, task_id))
                    conn.commit()
                    logger.info(f"评估任务状态已更新（重试 {i+1}")
                    break
                except Exception as retry_error:
                    logger.error(f"重试更新评估任务状态失败 {i+1}: {str(retry_error)}")
    except Exception as e:
        logger.error(f"执行评估任务失败: {str(e)}")
        # 更新任务状态为失败
        try:
            if conn and cursor:
                cursor.execute("UPDATE evaluation_tasks SET status='failed', result_summary=? WHERE id=?", 
                              (f"执行失败: {str(e)}", task_id))
                conn.commit()
        except Exception as db_error:
            logger.error(f"更新任务失败状态失败: {str(db_error)}")
    finally:
        if conn:
            conn.close()
    
    logger.info("评估任务完成")
    logger.info(f"总计: {total_cases}, 通过: {passed}, 失败: {failed}, 异常: {errors}")