import pandas as pd
from llm import quick_chat
# import matplotlib.pyplot as plt 
text = quick_chat('为什么这么有趣的编程语言叫Python')
print('为什么这么有趣的编程语言叫Python', text)

# from bs4 import BeautifulSoup
# import requests
# from IPython.display import display, HTML  # 仅在 Jupyter Notebook 中需要，普通 Python 脚本不需要


# url = "https://www.deeplearning.ai/the-batch/the-world-needs-more-intelligence/"
# response = requests.get(url) 
# print(response)
# soup = BeautifulSoup(response.text, 'html.parser')
# print(soup.prettify())