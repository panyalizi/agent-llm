#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
整理Excel文件中的'配置'列
输出格式：配置:["配置1","配置2","配置3"]
注意：跳过包含"平板"的sheet
"""

import pandas as pd
import json
import sys
import os

def extract_config_from_sheet(df, sheet_name):
    """从单个DataFrame中提取配置列"""
    config_set = set()
    
    # 查找配置列
    config_col = None
    for col in df.columns:
        col_str = str(col).strip()
        if '配置' in col_str:
            config_col = col
            break
    
    if config_col is None:
        # 如果没找到配置列，默认使用第三列
        if len(df.columns) >= 3:
            config_col = df.columns[2]
            print(f"  [Sheet: {sheet_name}] 未找到配置列，默认使用第三列: '{config_col}'")
        else:
            print(f"  [Sheet: {sheet_name}] 列数少于3，跳过")
            return config_set
    else:
        print(f"  [Sheet: {sheet_name}] 找到配置列: '{config_col}'")
    
    # 提取所有非空的配置
    for idx, row in df.iterrows():
        config_value = row[config_col]
        if pd.notna(config_value):
            config_str = str(config_value).strip()
            if config_str and config_str != 'nan':
                # 如果配置是用逗号、分号等分隔的，需要拆分
                if ',' in config_str:
                    for cfg in config_str.split(','):
                        cfg_clean = cfg.strip()
                        if cfg_clean:
                            config_set.add(cfg_clean)
                elif ';' in config_str:
                    for cfg in config_str.split(';'):
                        cfg_clean = cfg.strip()
                        if cfg_clean:
                            config_set.add(cfg_clean)
                elif '、' in config_str:
                    for cfg in config_str.split('、'):
                        cfg_clean = cfg.strip()
                        if cfg_clean:
                            config_set.add(cfg_clean)
                else:
                    config_set.add(config_str)
    
    return config_set

def extract_config_from_excel(excel_file):
    """从Excel文件的所有sheet中提取配置并去重（跳过包含'平板'的sheet）"""
    try:
        # 读取Excel文件的所有sheet
        xlsx = pd.ExcelFile(excel_file)
        sheet_names = xlsx.sheet_names
        
        print(f"发现 {len(sheet_names)} 个工作表: {sheet_names}")
        print(f"\n{'='*50}")
        
        # 用于存储所有配置的集合（自动去重）
        all_configs = set()
        
        # 遍历每个sheet
        for sheet_name in sheet_names:
            # 跳过包含"平板"的sheet
            if '平板' in sheet_name:
                print(f"\n跳过工作表: '{sheet_name}' (包含'平板')")
                continue
            
            df = pd.read_excel(excel_file, sheet_name=sheet_name)
            print(f"\n处理工作表: '{sheet_name}' (共 {len(df)} 行)")
            
            # 从当前sheet提取配置
            sheet_configs = extract_config_from_sheet(df, sheet_name)
            print(f"  提取到 {len(sheet_configs)} 个配置")
            
            # 合并到总集合
            all_configs.update(sheet_configs)
        
        # 转换为排序后的列表
        config_list = sorted(list(all_configs))
        
        print(f"\n{'='*50}")
        print(f"所有工作表合并去重后，共 {len(config_list)} 个配置")
        
        return config_list
        
    except Exception as e:
        print(f"读取文件时出错: {e}")
        import traceback
        traceback.print_exc()
        return None

def main():
    # 获取脚本所在目录的绝对路径
    script_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Excel文件路径（使用绝对路径）
    excel_file = os.path.join(script_dir, "Oppo好评回复规则 V2.0.xlsx")
    
    if not os.path.exists(excel_file):
        print(f"文件不存在: {excel_file}")
        print(f"脚本目录: {script_dir}")
        return
    
    # 提取配置
    configs = extract_config_from_excel(excel_file)
    
    if configs:
        # 输出格式：配置:["配置1","配置2","配置3"]
        output = f"配置:{json.dumps(configs, ensure_ascii=False)}"
        print(f"\n{'='*50}")
        print("输出结果:")
        print(output)
        print(f"{'='*50}")
        
        # 保存到文件（也放在脚本所在目录）
        output_file = os.path.join(script_dir, "config_output.txt")
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(output)
        print(f"\n结果已保存到: {output_file}")
    else:
        print("未能提取到配置")

if __name__ == "__main__":
    main()

