#!/usr/bin/env python3
"""
数据库迁移脚本
用于将SQLite数据库迁移到PostgreSQL
"""
import os
import sqlite3
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

# SQLite数据库路径
SQLITE_DB = os.path.join('database', 'llm_eval_system.db')
# PostgreSQL连接信息
PG_HOST = 'localhost'
PG_PORT = '5432'
PG_USER = 'admin'
PG_PASSWORD = 'password'
PG_DB = 'llm_eval_system'

# 连接到PostgreSQL
print("连接到PostgreSQL...")
try:
    # 先连接到默认数据库
    conn = psycopg2.connect(
        host=PG_HOST,
        port=PG_PORT,
        user=PG_USER,
        password=PG_PASSWORD,
        dbname='postgres'
    )
    conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
    cursor = conn.cursor()
    
    # 检查数据库是否存在
    cursor.execute("SELECT 1 FROM pg_database WHERE datname = %s", (PG_DB,))
    if not cursor.fetchone():
        # 创建数据库
        print(f"创建数据库 {PG_DB}...")
        cursor.execute(f"CREATE DATABASE {PG_DB}")
    
    cursor.close()
    conn.close()
    
    # 连接到目标数据库
    conn = psycopg2.connect(
        host=PG_HOST,
        port=PG_PORT,
        user=PG_USER,
        password=PG_PASSWORD,
        dbname=PG_DB
    )
    cursor = conn.cursor()
    print("连接成功!")
except Exception as e:
    print(f"连接PostgreSQL失败: {e}")
    exit(1)

# 连接到SQLite
print("连接到SQLite...")
try:
    sqlite_conn = sqlite3.connect(SQLITE_DB)
    sqlite_cursor = sqlite_conn.cursor()
    print("连接成功!")
except Exception as e:
    print(f"连接SQLite失败: {e}")
    exit(1)

# 获取SQLite中的表
print("获取SQLite中的表...")
sqlite_cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
tables = sqlite_cursor.fetchall()
table_names = [table[0] for table in tables]
print(f"找到表: {table_names}")

# 为每个表创建对应的PostgreSQL表并迁移数据
for table_name in table_names:
    print(f"\n处理表: {table_name}")
    
    # 获取表结构
    sqlite_cursor.execute(f"PRAGMA table_info({table_name});")
    columns = sqlite_cursor.fetchall()
    
    # 构建CREATE TABLE语句
    create_table_sql = f"CREATE TABLE IF NOT EXISTS {table_name} ("
    column_defs = []
    for col in columns:
        col_name = col[1]
        col_type = col[2]
        
        # 转换SQLite类型到PostgreSQL类型
        if col_type == 'INTEGER':
            pg_type = 'INTEGER'
        elif col_type == 'TEXT':
            pg_type = 'TEXT'
        elif col_type == 'REAL':
            pg_type = 'REAL'
        elif col_type == 'BLOB':
            pg_type = 'BYTEA'
        elif col_type == 'BOOLEAN':
            pg_type = 'BOOLEAN'
        else:
            pg_type = 'TEXT'
        
        # 添加列定义
        column_defs.append(f"{col_name} {pg_type}")
    
    create_table_sql += ", ".join(column_defs) + ")"
    
    # 执行CREATE TABLE语句
    try:
        cursor.execute(create_table_sql)
        conn.commit()
        print(f"  创建表 {table_name} 成功")
    except Exception as e:
        print(f"  创建表 {table_name} 失败: {e}")
        continue
    
    # 获取表数据
    sqlite_cursor.execute(f"SELECT * FROM {table_name};")
    rows = sqlite_cursor.fetchall()
    
    if rows:
        # 构建INSERT语句
        placeholders = ", ".join(["%s" for _ in columns])
        insert_sql = f"INSERT INTO {table_name} VALUES ({placeholders})"
        
        # 执行批量插入
        try:
            cursor.executemany(insert_sql, rows)
            conn.commit()
            print(f"  迁移 {len(rows)} 条数据成功")
        except Exception as e:
            print(f"  迁移数据失败: {e}")
            conn.rollback()
    else:
        print("  表为空，跳过迁移")

# 关闭连接
sqlite_cursor.close()
sqlite_conn.close()
cursor.close()
conn.close()

print("\n数据库迁移完成!")
