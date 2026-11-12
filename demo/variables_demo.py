#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
变量和数据类型演示文件
包含Python中常用的各种数据类型
"""

# ============== 基本数据类型 ==============

# 整数类型 (int)
age = 25
year = 2024
negative_number = -100
large_number = 1000000
binary_number = 0b1010  # 二进制
octal_number = 0o755    # 八进制
hex_number = 0xFF       # 十六进制

# 浮点数类型 (float)
height = 175.5
weight = 68.2
pi = 3.14159
scientific_notation = 1.23e-4
negative_float = -99.99

# 字符串类型 (str)
name = "张三"
city = '北京'
multiline_string = """这是一个
多行字符串
示例"""
raw_string = r"C:\Users\Documents\file.txt"
formatted_string = f"我的名字是{name}，今年{age}岁"

# 布尔类型 (bool)
is_student = True
is_married = False
has_license = True

# 空值类型 (NoneType)
empty_value = None
undefined_variable = None

# ============== 集合数据类型 ==============

# 列表 (list) - 有序、可变
fruits = ["苹果", "香蕉", "橙子", "葡萄"]
numbers = [1, 2, 3, 4, 5]
mixed_list = [1, "hello", 3.14, True, None]
nested_list = [[1, 2], [3, 4], [5, 6]]
empty_list = []

# 元组 (tuple) - 有序、不可变
coordinates = (10, 20)
rgb_color = (255, 128, 0)
single_element_tuple = (42,)
mixed_tuple = (1, "world", 2.71, False)
nested_tuple = ((1, 2), (3, 4))

# 字典 (dict) - 键值对、无序
person = {
    "姓名": "李四",
    "年龄": 30,
    "城市": "上海",
    "已婚": False
}
scores = {"数学": 95, "英语": 88, "物理": 92}
nested_dict = {
    "用户1": {"姓名": "王五", "分数": 85},
    "用户2": {"姓名": "赵六", "分数": 90}
}
empty_dict = {}

# 集合 (set) - 无序、不重复
unique_numbers = {1, 2, 3, 4, 5}
colors = {"红色", "绿色", "蓝色"}
mixed_set = {1, "hello", 3.14, True}
empty_set = set()

# 冻结集合 (frozenset) - 不可变集合
immutable_set = frozenset([1, 2, 3, 4])
frozen_colors = frozenset(["红", "绿", "蓝"])

# ============== 复杂数据类型 ==============

# 复数 (complex)
complex_number1 = 3 + 4j
complex_number2 = complex(2, -3)
pure_imaginary = 5j

# 字节类型 (bytes)
byte_data = b"Hello World"
byte_array = bytes([65, 66, 67, 68])
encoded_string = "你好".encode('utf-8')

# 字节数组 (bytearray) - 可变字节序列
mutable_bytes = bytearray(b"Hello")
byte_array_from_list = bytearray([72, 101, 108, 108, 111])

# 内存视图 (memoryview)
data = bytearray(b"Hello World")
memory_view = memoryview(data)

# ============== 特殊类型 ==============

# 范围对象 (range)
number_range = range(10)
custom_range = range(1, 11, 2)
reverse_range = range(10, 0, -1)

# 枚举对象 (enumerate)
fruits_enum = enumerate(fruits)

# 压缩对象 (zip)
names = ["Alice", "Bob", "Charlie"]
ages_list = [25, 30, 35]
zipped_data = zip(names, ages_list)

# ============== 函数和类 ==============

# 函数定义
def greet(name):
    """问候函数"""
    return f"你好, {name}!"

# Lambda函数
square = lambda x: x ** 2
add = lambda a, b: a + b

# 类定义
class Student:
    """学生类"""
    def __init__(self, name, age):
        self.name = name
        self.age = age
    
    def introduce(self):
        return f"我是{self.name}，今年{self.age}岁"

# 类实例
student1 = Student("小明", 18)
student2 = Student("小红", 19)

# ============== 数据结构示例 ==============

# 嵌套数据结构
company_data = {
    "公司名": "科技有限公司",
    "员工": [
        {"姓名": "张三", "部门": "开发", "薪资": 15000},
        {"姓名": "李四", "部门": "测试", "薪资": 12000},
        {"姓名": "王五", "部门": "产品", "薪资": 18000}
    ],
    "部门": {
        "开发": {"人数": 10, "预算": 500000},
        "测试": {"人数": 5, "预算": 200000},
        "产品": {"人数": 3, "预算": 150000}
    }
}

# 矩阵（二维列表）
matrix = [
    [1, 2, 3],
    [4, 5, 6],
    [7, 8, 9]
]

# 图数据结构（邻接表）
graph = {
    'A': ['B', 'C'],
    'B': ['A', 'D', 'E'],
    'C': ['A', 'F'],
    'D': ['B'],
    'E': ['B', 'F'],
    'F': ['C', 'E']
}

# ============== 变量信息打印 ==============

def print_variable_info():
    """打印所有变量的类型和值"""
    variables = {
        # 基本类型
        'age': age, 'height': height, 'name': name, 'is_student': is_student,
        'empty_value': empty_value, 'complex_number1': complex_number1,
        
        # 集合类型
        'fruits': fruits, 'coordinates': coordinates, 'person': person,
        'unique_numbers': unique_numbers, 'immutable_set': immutable_set,
        
        # 特殊类型
        'byte_data': byte_data, 'number_range': number_range,
        'greet': greet, 'Student': Student, 'student1': student1
    }
    
    print("=" * 50)
    print("变量类型和值信息")
    print("=" * 50)
    
    for var_name, var_value in variables.items():
        print(f"{var_name:20} | {type(var_value).__name__:15} | {str(var_value)[:50]}")

# ============== 类型检查示例 ==============

def demonstrate_type_checking():
    """演示类型检查"""
    print("\n" + "=" * 50)
    print("类型检查演示")
    print("=" * 50)
    
    # isinstance() 检查
    # print(f"age 是整数吗？ {isinstance(age, int)}")
    # print(f"height 是浮点数吗？ {isinstance(height, float)}")
    # print(f"name 是字符串吗？ {isinstance(name, str)}")
    # print(f"fruits 是列表吗？ {isinstance(fruits, list)}")
    # print(f"person 是字典吗？ {isinstance(person, dict)}")
    
    # type() 检查
    # print(f"\nage 的类型: {type(age)}")
    # print(f"fruits 的类型: {type(fruits)}")
    # print(f"greet 的类型: {type(greet)}")

if __name__ == "__main__":
    # print("Python 数据类型演示")
    # print_variable_info()
    demonstrate_type_checking()
    
    # print(f"\n问候示例: {greet('Python学习者')}")
    # print(f"学生介绍: {student1.introduce()}")
    # print(f"平方函数: 5的平方是 {square(5)}")
    # print(f"加法函数: 3 + 7 = {add(3, 7)}") 
    # print(75 - 32 * 5 / 9)
    # print((75 - 32) * 5 / 9)
    # print(f"is{(75 - 32) * 5 / 9:.0f}C")
    # print(f"is{(75 - 32) * 5 / 9:.1f}C")
    
    # print(f'''
    #       eret is{(75 - 32) * 5 / 9:.1f}
    #       etert is{(75 - 32) * 5 / 9:.0f}
    #       ert
    #       ert
    #       ertert
    #       ''')
    list_ages = [42, 34, 56]
    list_ages.remove(34)
    
    print(list_ages)
    
    
    
    