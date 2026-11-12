import pandas as pd

def check_duplicates(file_path):
    """检查Excel文件中的重复内容"""
    print(f"正在检查文件: {file_path}")
    
    # 读取Excel文件
    df = pd.read_excel(file_path)
    print(f"总数据量: {len(df)}")
    
    # 检查具体回复参考列的重复情况
    replies = df['具体回复参考']
    unique_replies = replies.drop_duplicates()
    
    print(f"唯一回复数量: {len(unique_replies)}")
    print(f"重复回复数量: {len(replies) - len(unique_replies)}")
    
    if len(replies) != len(unique_replies):
        print("\n❌ 发现重复内容！")
        
        # 找出重复的回复
        duplicated_replies = replies[replies.duplicated(keep=False)]
        duplicate_counts = duplicated_replies.value_counts()
        
        print(f"重复回复的种类数: {len(duplicate_counts)}")
        print(f"\n重复次数最多的前10个回复:")
        
        for i, (reply, count) in enumerate(duplicate_counts.head(10).items(), 1):
            print(f"{i}. 重复{count}次: {reply[:80]}...")
            
        # 显示这些重复内容分布在哪些场景中
        print(f"\n重复内容的场景分布:")
        for reply, count in duplicate_counts.head(5).items():
            scenarios = df[df['具体回复参考'] == reply]['具体场景'].unique()
            print(f"  '{reply[:50]}...' 出现在场景: {list(scenarios)}")
            
    else:
        print("\n✅ 没有发现重复内容！所有回复都是唯一的。")
    
    # 检查场景分布
    print(f"\n📊 场景分布:")
    scenario_counts = df['具体场景'].value_counts()
    for scenario, count in scenario_counts.items():
        print(f"  - {scenario}: {count}条")

if __name__ == "__main__":
    # 检查最终版文件
    check_duplicates("标准场景分类结果_含夸赞整体.xlsx") 