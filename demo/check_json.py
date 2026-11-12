import pandas as pd
import json
from collections import defaultdict

def xlsx_to_json(xlsx_file, json_file):
    """
    将Excel文件转换为JSON格式
    以具体场景为key，具体回复参考为value的数组
    """
    print(f"正在读取Excel文件: {xlsx_file}")
    
    # 读取Excel文件
    df = pd.read_excel(xlsx_file)
    print(f"总数据量: {len(df)}")
    
    # 创建字典来存储数据
    scenario_dict = defaultdict(list)
    
    # 按场景分组数据
    for index, row in df.iterrows():
        scenario = row['具体场景']
        reply = row['具体回复参考']
        
        # 添加到对应场景的列表中
        scenario_dict[scenario].append(reply)
    
    # 转换为普通字典（保持顺序）
    result_dict = dict(scenario_dict)
    
    # 显示统计信息
    print(f"\n📊 场景统计:")
    for scenario, replies in result_dict.items():
        print(f"  - {scenario}: {len(replies)}条回复")
    
    # 保存为JSON文件
    with open(json_file, 'w', encoding='utf-8') as f:
        json.dump(result_dict, f, ensure_ascii=False, indent=2)
    
    print(f"\n✅ JSON文件已保存到: {json_file}")
    
    # 显示JSON预览
    print(f"\n📄 JSON数据预览:")
    preview_dict = {}
    for scenario, replies in list(result_dict.items())[:2]:  # 只显示前2个场景
        preview_dict[scenario] = replies[:2]  # 每个场景只显示前2条回复
    
    print(json.dumps(preview_dict, ensure_ascii=False, indent=2))
    
    return result_dict

def main():
    """主函数"""
    # 输入和输出文件路径
    xlsx_file = "标准场景分类结果_含夸赞整体.xlsx"
    json_file = "场景回复数据.json"
    
    # 转换文件
    result = xlsx_to_json(xlsx_file, json_file)
    
    print(f"\n🎉 转换完成！")
    print(f"生成的JSON文件包含 {len(result)} 个场景")
    print(f"总回复数量: {sum(len(replies) for replies in result.values())}")

if __name__ == "__main__":
    main()
