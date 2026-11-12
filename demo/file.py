import pandas as pd
import os
from difflib import SequenceMatcher
import glob
from collections import defaultdict
import re

def similarity(a, b):
    """计算两个字符串的相似度"""
    return SequenceMatcher(None, a, b).ratio()

def find_similar_scenario(scenario, existing_scenarios, threshold=0.6):
    """查找相似的场景名称"""
    best_match = None
    best_score = 0
    
    for existing in existing_scenarios:
        score = similarity(scenario.strip(), existing.strip())
        if score > best_score and score >= threshold:
            best_score = score
            best_match = existing
    
    return best_match if best_match else scenario

def find_scenario_column(columns):
    """智能识别场景列"""
    scenario_keywords = ['场景', '具体场景', '分场景', '场景类型']
    
    for col in columns:
        col_str = str(col).strip()
        for keyword in scenario_keywords:
            if keyword in col_str:
                return col
    return None

def find_reply_column(columns):
    """智能识别回复参考列"""
    reply_keywords = ['回复参考', '具体回复参考', '回评参考', '好评回复参考', '好评回评参考', '回评话术', '话术参考']
    
    for col in columns:
        col_str = str(col).strip()
        for keyword in reply_keywords:
            if keyword in col_str:
                return col
    return None

def extract_data_from_sheet(df, sheet_name):
    """从工作表中提取数据，使用多种策略"""
    extracted_data = []
    
    print(f"      工作表 '{sheet_name}' 数据形状: {df.shape}")
    
    # 策略1: 智能识别列名
    scenario_col = find_scenario_column(df.columns)
    reply_col = find_reply_column(df.columns)
    
    if scenario_col and reply_col:
        print(f"      识别到场景列: '{scenario_col}'")
        print(f"      识别到回复列: '{reply_col}'")
        
        # 向前填充场景列的空值
        df_copy = df.copy()
        df_copy[scenario_col] = df_copy[scenario_col].fillna(method='ffill')
        
        # 提取数据
        valid_rows = 0
        for index, row in df_copy.iterrows():
            scenario = str(row[scenario_col]).strip() if pd.notna(row[scenario_col]) else ""
            reply = str(row[reply_col]).strip() if pd.notna(row[reply_col]) else ""
            
            # 跳过标题行
            if scenario in ['具体场景', '场景'] or reply in ['具体回复参考', '回复参考', '回评参考', '具体回复']:
                continue
                
            if scenario and reply and scenario != 'nan' and reply != 'nan' and len(scenario) > 0 and len(reply) > 0:
                extracted_data.append((scenario, reply))
                valid_rows += 1
                if valid_rows <= 3:  # 显示前3条有效数据
                    print(f"        有效数据{valid_rows}: 场景='{scenario}' 回复='{reply[:50]}...'")
        
        print(f"      策略1总共提取了 {len(extracted_data)} 条数据")
        return extracted_data
    
    # 策略2: 尝试第一列作为场景，第二列作为回复
    if len(df.columns) >= 2:
        col1, col2 = df.columns[0], df.columns[1]
        
        print(f"      尝试策略2: 列'{col1}' 作为场景, 列'{col2}' 作为回复")
        
        # 向前填充场景列的空值
        df_copy = df.copy()
        df_copy[col1] = df_copy[col1].fillna(method='ffill')
        
        temp_data = []
        valid_rows = 0
        for index, row in df_copy.iterrows():
            scenario = str(row[col1]).strip() if pd.notna(row[col1]) else ""
            reply = str(row[col2]).strip() if pd.notna(row[col2]) else ""
            
            # 跳过标题行
            if scenario in ['具体场景', '场景'] or reply in ['具体回复参考', '回复参考', '回评参考', '具体回复']:
                continue
            
            if scenario and reply and scenario != 'nan' and reply != 'nan' and len(scenario) > 0 and len(reply) > 0:
                temp_data.append((scenario, reply))
                valid_rows += 1
                if valid_rows <= 3:  # 显示前3条有效数据
                    print(f"        有效数据{valid_rows}: 场景='{scenario}' 回复='{reply[:50]}...'")
        
        if len(temp_data) > 0:
            print(f"      策略2总共提取了 {len(temp_data)} 条数据")
            return temp_data
    
    # 策略3: 寻找包含"场景"和"回评参考"的列
    for i, col in enumerate(df.columns):
        if "场景" in str(col) or i == 1:  # 第二列通常是场景列
            scenario_col = col
            for j, col2 in enumerate(df.columns):
                if j > i and ("回评参考" in str(col2) or "回复参考" in str(col2) or j == 2):  # 第三列通常是回复列
                    reply_col = col2
                    
                    print(f"      尝试策略3: 列{i+1}('{scenario_col}') 作为场景, 列{j+1}('{reply_col}') 作为回复")
                    
                    # 向前填充场景列的空值
                    df_copy = df.copy()
                    df_copy[scenario_col] = df_copy[scenario_col].fillna(method='ffill')
                    
                    temp_data = []
                    valid_rows = 0
                    for index, row in df_copy.iterrows():
                        scenario = str(row[scenario_col]).strip() if pd.notna(row[scenario_col]) else ""
                        reply = str(row[reply_col]).strip() if pd.notna(row[reply_col]) else ""
                        
                        # 跳过标题行和空行
                        if (scenario and reply and 
                            scenario != 'nan' and reply != 'nan' and 
                            len(scenario) > 0 and len(reply) > 0 and
                            scenario not in ['具体场景', '场景'] and
                            reply not in ['具体回复参考', '回复参考', '回评参考']):
                            temp_data.append((scenario, reply))
                            valid_rows += 1
                            if valid_rows <= 3:  # 显示前3条有效数据
                                print(f"        有效数据{valid_rows}: 场景='{scenario}' 回复='{reply[:50]}...'")
                    
                    if len(temp_data) > 0:
                        print(f"      策略3总共提取了 {len(temp_data)} 条数据")
                        return temp_data
                    break
            break
    
    # 策略4: 查看所有列，寻找有意义的数据
    print(f"      所有策略均失败，显示调试信息:")
    print(f"      所有列: {list(df.columns)}")
    
    return []

def merge_excel_sheets(input_folder, output_file):
    """
    合并多个Excel文件中所有工作表的数据，按照具体场景进行合并
    
    参数:
    input_folder: 输入文件夹路径（包含所有要合并的Excel文件）
    output_file: 输出文件路径
    """
    
    # 支持的文件格式
    file_patterns = ['*.xlsx', '*.xls']
    all_files = []
    
    # 获取所有Excel文件
    for pattern in file_patterns:
        all_files.extend(glob.glob(os.path.join(input_folder, pattern)))
    
    # 排除之前生成的合并结果文件，避免重复
    original_files = []
    for file in all_files:
        filename = os.path.basename(file)
        if not (filename.startswith('合并结果') or filename.startswith('最终合并结果')):
            original_files.append(file)
    
    if not original_files:
        print(f"在文件夹 {input_folder} 中未找到任何原始Excel文件")
        return
    
    print(f"找到 {len(original_files)} 个原始Excel文件需要合并:")
    for file in original_files:
        print(f"  - {os.path.basename(file)}")
    
    # 存储合并后的数据，使用set来避免重复
    merged_data = defaultdict(set)  # 改为set来自动去重
    existing_scenarios = []
    total_sheets_processed = 0
    successful_sheets = 0
    total_data_extracted = 0
    
    # 用于调试的场景映射记录
    scenario_mappings = {}
    
    # 处理每个Excel文件
    for file_path in original_files:
        try:
            print(f"\n正在处理Excel文件: {os.path.basename(file_path)}")
            
            # 读取Excel文件的所有工作表名称
            excel_file = pd.ExcelFile(file_path)
            sheet_names = excel_file.sheet_names
            print(f"  发现 {len(sheet_names)} 个工作表: {sheet_names}")
            
            # 处理每个工作表
            for sheet_name in sheet_names:
                try:
                    print(f"\n    正在处理工作表: {sheet_name}")
                    
                    # 读取工作表数据
                    df = pd.read_excel(file_path, sheet_name=sheet_name)
                    
                    # 使用新的数据提取函数
                    sheet_data = extract_data_from_sheet(df, sheet_name)
                    
                    # 统计当前工作表的场景分布
                    sheet_scenarios = {}
                    
                    # 处理提取的数据
                    for scenario, reply in sheet_data:
                        # 查找相似的场景名称
                        matched_scenario = find_similar_scenario(scenario, existing_scenarios)
                        
                        # 记录场景映射用于调试
                        if scenario != matched_scenario:
                            if matched_scenario not in scenario_mappings:
                                scenario_mappings[matched_scenario] = set()
                            scenario_mappings[matched_scenario].add(scenario)
                        
                        # 如果是新场景，添加到已有场景列表中
                        if matched_scenario == scenario and scenario not in existing_scenarios:
                            existing_scenarios.append(scenario)
                        
                        # 统计当前工作表场景
                        if matched_scenario not in sheet_scenarios:
                            sheet_scenarios[matched_scenario] = 0
                        sheet_scenarios[matched_scenario] += 1
                        
                        # 添加到合并数据中（set会自动去重）
                        merged_data[matched_scenario].add(reply)
                        total_data_extracted += 1
                    
                    if len(sheet_data) > 0:
                        print(f"      ✓ 成功提取了 {len(sheet_data)} 条数据")
                        print(f"      场景分布:")
                        for scenario, count in sorted(sheet_scenarios.items()):
                            print(f"        - {scenario}: {count}条")
                        successful_sheets += 1
                    else:
                        print(f"      × 未提取到有效数据")
                    
                    total_sheets_processed += 1
                    
                except Exception as e:
                    print(f"      错误: 处理工作表 '{sheet_name}' 时出现错误: {str(e)}")
                    continue
            
            excel_file.close()
            
        except Exception as e:
            print(f"  错误: 处理Excel文件 {file_path} 时出现错误: {str(e)}")
            continue
    
    print(f"\n总共处理了 {total_sheets_processed} 个工作表，成功提取数据的有 {successful_sheets} 个")
    print(f"总共提取了 {total_data_extracted} 条原始数据")
    
    # 显示场景合并信息
    if scenario_mappings:
        print(f"\n场景合并信息:")
        for main_scenario, similar_scenarios in scenario_mappings.items():
            print(f"  '{main_scenario}' 合并了以下相似场景:")
            for similar in similar_scenarios:
                print(f"    - {similar}")
    
    # 创建合并后的DataFrame，并统计去重效果
    merged_rows = []
    total_unique_data = 0
    
    for scenario, replies in merged_data.items():
        for reply in replies:
            merged_rows.append({
                '具体场景': scenario,
                '具体回复参考': reply
            })
            total_unique_data += 1
    
    print(f"\n去重后保留了 {total_unique_data} 条唯一数据")
    
    if not merged_rows:
        print("没有数据可以合并")
        return
    
    # 创建最终的DataFrame
    final_df = pd.DataFrame(merged_rows)
    
    # 按场景排序
    final_df = final_df.sort_values(by='具体场景')
    
    # 输出详细统计信息
    print(f"\n合并完成!")
    print(f"总共合并了 {len(final_df)} 条回复")
    print(f"涉及 {len(merged_data)} 个不同场景:")
    
    # 按数据量排序显示场景
    scenario_counts = [(scenario, len(replies)) for scenario, replies in merged_data.items()]
    scenario_counts.sort(key=lambda x: x[1], reverse=True)
    
    for scenario, count in scenario_counts:
        print(f"  - {scenario}: {count} 条回复")
    
    # 保存结果
    try:
        if output_file.endswith('.csv'):
            final_df.to_csv(output_file, index=False, encoding='utf-8-sig')
        else:
            final_df.to_excel(output_file, index=False)
        print(f"\n结果已保存到: {output_file}")
        
        # 显示最终结果预览
        print(f"\n数据预览（前5行）:")
        print(final_df.head().to_string(index=False))
        
    except Exception as e:
        print(f"保存文件时出错: {str(e)}")

def map_to_standard_scenarios(scenario):
    """将现有场景映射到标准场景"""
    scenario_lower = scenario.lower()
    
    # 定义映射规则
    if any(keyword in scenario_lower for keyword in ['整体夸赞', '夸赞整体', '整体']):
        return "夸赞整体"
    elif any(keyword in scenario_lower for keyword in ['性能', '夸赞性能', '系统', '夸赞系统', '通讯', '通信', '品质', '音质', '夸赞音质']):
        return "系统性能"
    elif any(keyword in scenario_lower for keyword in ['拍照', '夸赞拍照']):
        return "拍照效果"
    elif any(keyword in scenario_lower for keyword in ['游戏', '夸赞游戏', '电竞']):
        return "游戏体验"
    elif any(keyword in scenario_lower for keyword in ['续航', '充电', '夸赞续航']):
        return "续航与充电"
    elif any(keyword in scenario_lower for keyword in ['外观', '夸赞外观']):
        return "外观设计"
    elif any(keyword in scenario_lower for keyword in ['手感', '夸赞手感']):
        return "手感体验"
    elif any(keyword in scenario_lower for keyword in ['性价比', '性价比高']):
        return "性价比"
    elif any(keyword in scenario_lower for keyword in ['屏幕', '夸赞屏幕']):
        return "屏幕效果"
    elif any(keyword in scenario_lower for keyword in ['物流', '夸赞物流', '服务', '夸赞服务', '物流类', '服务类', '物流快', '服务好']):
        return "物流服务"
    elif any(keyword in scenario_lower for keyword in ['第一次购买', '多次购买']):
        return "首次购买"
    elif any(keyword in scenario_lower for keyword in ['忠实粉丝']):
        return "忠实粉丝"
    elif any(keyword in scenario_lower for keyword in ['赠送', '赠送类']):
        return "赠送场景"
    else:
        return "其他"  # 不在标准场景中的数据

def create_standard_output(input_file, output_file):
    """创建标准化场景输出"""
    
    # 读取已合并的数据
    try:
        df = pd.read_excel(input_file)
        print(f"读取了 {len(df)} 条数据")
    except Exception as e:
        print(f"读取文件出错: {e}")
        return
    
    # 定义标准场景顺序
    standard_scenarios = [
        "夸赞整体",
        "系统性能",
        "拍照效果", 
        "游戏体验",
        "续航与充电",
        "外观设计",
        "手感体验",
        "性价比",
        "屏幕效果",
        "物流服务",
        "首次购买",
        "忠实粉丝",
        "赠送场景"
    ]
    
    # 将场景映射到标准场景
    df['标准场景'] = df['具体场景'].apply(map_to_standard_scenarios)
    
    # 统计映射结果
    print(f"\n场景映射统计:")
    mapping_stats = df['标准场景'].value_counts()
    for scenario in standard_scenarios:
        count = mapping_stats.get(scenario, 0)
        print(f"  - {scenario}: {count} 条回复")
    
    # 显示"其他"类别的具体场景
    other_scenarios = df[df['标准场景'] == '其他']['具体场景'].unique()
    if len(other_scenarios) > 0:
        print(f"  - 其他: {mapping_stats.get('其他', 0)} 条回复")
        print(f"    具体包含: {list(other_scenarios)}")
    
    # 创建标准化输出数据
    standard_df = df[df['标准场景'].isin(standard_scenarios)].copy()
    standard_df = standard_df[['标准场景', '具体回复参考']].copy()
    standard_df.columns = ['具体场景', '具体回复参考']
    
    # 按照指定顺序排序
    scenario_order = {scenario: i for i, scenario in enumerate(standard_scenarios)}
    standard_df['排序'] = standard_df['具体场景'].map(scenario_order)
    standard_df = standard_df.sort_values('排序').drop('排序', axis=1)
    
    # 保存结果
    try:
        standard_df.to_excel(output_file, index=False)
        print(f"\n标准化结果已保存到: {output_file}")
        print(f"共包含 {len(standard_df)} 条数据，涵盖 {len(standard_df['具体场景'].unique())} 个标准场景")
        
        # 显示每个标准场景的数据量
        print(f"\n各标准场景数据量:")
        scenario_counts = standard_df['具体场景'].value_counts()
        for scenario in standard_scenarios:
            count = scenario_counts.get(scenario, 0)
            if count > 0:
                print(f"  - {scenario}: {count} 条")
        
        # 显示数据预览
        print(f"\n数据预览（前5行）:")
        print(standard_df.head().to_string(index=False))
        
    except Exception as e:
        print(f"保存文件时出错: {e}")

def main():
    """主函数"""
    print("Excel工作表合并工具")
    print("=" * 50)
    print("此工具会合并Excel文件中所有工作表(tabs)的数据")
    
    # 获取输入文件夹路径
    input_folder = input("请输入包含Excel文件的文件夹路径（回车使用当前目录）: ").strip()
    if not input_folder:
        input_folder = "."
    
    if not os.path.exists(input_folder):
        print(f"文件夹 {input_folder} 不存在")
        return
    
    # 获取输出文件路径
    output_file = input("请输入输出文件路径（默认: 合并结果.xlsx）: ").strip()
    if not output_file:
        output_file = "合并结果.xlsx"
    
    # 执行合并
    merge_excel_sheets(input_folder, output_file)
    
    # 创建标准化输出
    print("\n" + "=" * 50)
    print("创建标准化场景输出...")
    create_standard_output(output_file, "标准场景分类结果.xlsx")

# 示例用法
def example_usage():
    """示例用法"""
    print("示例用法:")
    print("1. 将所有Excel文件放在同一个文件夹中")
    print("2. 运行脚本并输入文件夹路径")
    print("3. 脚本会读取每个Excel文件的所有工作表")
    print("4. 按照相似的场景名称进行智能合并")
    print("5. 输出合并后的Excel文件")
    
    # 直接调用合并函数的示例
    merge_excel_sheets(".", "合并结果.xlsx")

if __name__ == "__main__":
    # 直接执行合并，不需要交互输入
    print("Excel工作表合并工具")
    print("=" * 50)
    print("正在合并当前目录下的所有Excel文件...")
    
    # 直接执行合并操作
    merge_excel_sheets(".", "合并结果_详细.xlsx")
