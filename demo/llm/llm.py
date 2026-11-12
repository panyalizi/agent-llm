"""
极简 OpenAI LLM 封装示例。

使用前请在环境变量中配置 `OPENAI_API_KEY`，或者在实例化 `MinimalLLM`
时显式传入 `api_key`。默认模型演示为 `deepseek-v3.2-exp`，你可以根据需要
替换为任意可用模型。

API Key 配置方式（推荐顺序）：

1. 【最推荐】使用 .env 文件（项目根目录下创建 .env 文件）：
   步骤：
   a) 复制 .env.example 为 .env：cp .env.example .env
   b) 编辑 .env 文件，填入你的真实 API Key
   c) 在代码中直接使用 MinimalLLM()，无需传参，会自动读取 .env 配置
   
   .env 文件格式示例：
   OPENAI_API_KEY=sk-your-api-key-here
   OPENAI_BASE_URL=https://api.moonshot.cn/v1  # 可选，如果使用代理服务
   
2. 系统环境变量：
   在终端中执行：export OPENAI_API_KEY="sk-your-api-key-here"
   
3. 代码中直接传入（不推荐，安全性较低）：
   client = MinimalLLM(api_key="sk-your-api-key-here")
   
4. 使用代理/自建服务（需要同时配置 base_url）：
   client = MinimalLLM(
       api_key="sk-your-api-key-here",
       base_url="https://api.deepseek.com/v1"  # 你的服务地址
   )
"""

from __future__ import annotations

import os
from pathlib import Path
from typing import List, Mapping, Sequence
import json

try:
    from dotenv import load_dotenv
    # 自动加载项目根目录下的 .env 文件
    project_root = Path(__file__).parent.parent.parent
    env_path = project_root / ".env"
    env_example_path = project_root / ".env.example"
    
    # 优先加载 .env，如果不存在则尝试加载 .env.example（用于开发测试）
    if env_path.exists():
        load_dotenv(env_path)
    elif env_example_path.exists():
        load_dotenv(env_example_path)
        import warnings
        warnings.warn(
            "⚠️  检测到使用的是 .env.example 文件，建议复制为 .env 文件：\n"
            f"   cp {env_example_path} {env_path}\n"
            "   然后编辑 .env 文件填入真实的 API Key",
            UserWarning
        )
except ImportError:
    # 如果没有安装 python-dotenv，跳过自动加载
    pass

from openai import OpenAI


Message = Mapping[str, str]


class MinimalLLM:
    """一个极简的 ChatCompletion 封装（兼容 OpenAI API v1.0+）。"""

    def __init__(
        self,
        model: str | None = None,
        api_key: str | None = None,
        base_url: str | None = None,
    ) -> None:
        # 优先使用传入的参数，其次从环境变量读取（支持 .env 文件）
        key = api_key or os.getenv("OPENAI_API_KEY")
        if not key:
            project_root = Path(__file__).parent.parent.parent
            env_path = project_root / ".env"
            env_example_path = project_root / ".env.example"
            
            error_msg = "缺少 OpenAI API key。\n"
            error_msg += "解决方法（三选一）：\n"
            error_msg += "1. 创建 .env 文件：复制 .env.example 为 .env，然后填入真实的 API Key\n"
            error_msg += f"   cp {env_example_path} {env_path}\n"
            error_msg += "2. 在代码中传入：MinimalLLM(api_key='your-api-key')\n"
            error_msg += "3. 设置系统环境变量：export OPENAI_API_KEY='your-api-key'"
            raise RuntimeError(error_msg)

        # base_url / model 也支持从环境变量读取（百炼兼容模式示例见 .env）
        url = base_url or os.getenv("OPENAI_BASE_URL")
        resolved_model = model or os.getenv("OPENAI_MODEL") or "qwen-plus"

        # 使用新版 OpenAI API (v1.0+)
        self.client = OpenAI(
            api_key=key,
            base_url=url,  # 如果为 None，则使用默认的 OpenAI API 地址
        )
        self.model = resolved_model

    def chat(self, messages: Sequence[Message], **kwargs) -> str:
        """
        调用大模型并返回回复文本。

        重要说明：
        - 每次调用只返回1个答案
        - 如果传入多轮对话历史，模型会基于整个对话历史理解上下文
        - 你需要手动维护对话历史列表（每次调用后将回答加入历史）

        Parameters
        ----------
        messages:
            消息列表，支持单轮或多轮对话：
            
            单轮对话：
            [{"role": "user", "content": "你好"}]
            
            多轮对话（模型会理解上下文）：
            [
                {"role": "user", "content": "你好，我是Python初学者"},
                {"role": "assistant", "content": "你好！很高兴认识你。"},
                {"role": "user", "content": "请推荐3本Python入门书籍"}
            ]
            
            注意：每次调用只返回最后1个问题的答案，但会基于整个历史理解上下文。
            
        kwargs:
            可选参数，例如：
            - temperature: 控制随机性 (0.0-2.0)，默认 1.0
            - max_tokens: 最大生成token数
            - top_p: 核采样参数

        Returns
        -------
        str:
            模型返回的文本内容（每次调用只返回1个答案）

        使用示例:
        --------
        >>> # 单轮对话
        >>> client = MinimalLLM()
        >>> response = client.chat([{"role": "user", "content": "你好"}])
        >>> print(response)
        
        >>> # 多轮对话（需要手动维护历史）
        >>> history = [{"role": "user", "content": "什么是机器学习？"}]
        >>> response1 = client.chat(history)
        >>> history.append({"role": "assistant", "content": response1})
        >>> history.append({"role": "user", "content": "它和深度学习有什么区别？"})
        >>> response2 = client.chat(history)  # 模型会理解"它"指的是机器学习
        """
        if not messages:
            raise ValueError("messages 不能为空。")

        response = self.client.chat.completions.create(
            model=self.model,
            messages=list(messages),
            **kwargs,
        )
        return response.choices[0].message.content.strip()


def quick_chat(prompt: str, model: str | None = None, api_key: str | None = None, base_url: str | None = None) -> str:
    """
    针对单轮对话的便捷调用。

    示例:
        quick_chat("用一句话解释量子隧穿")
    """
    client = MinimalLLM(model=model, api_key=api_key, base_url=base_url)
    return client.chat([{"role": "user", "content": prompt}])


if __name__ == "__main__":
  # 用脚本所在目录定位 JSON，避免依赖当前工作目录（cwd）
  dome_json = Path(__file__).resolve().parent / "dome.json"
  with open(dome_json, 'r', encoding='utf-8') as f:
    data = json.load(f)
    name = data.get('name', [])
    print(f"name: {name}") 
    
    for name in name:
      text = f"介绍一下 {name}歌手，并说出他代表作的3首歌，并说出他代表的3句搞笑名言"
      response = quick_chat(text)
      print(f"response: {response}")
    
    # ========== 使用大模型的基本步骤 ==========
    # 步骤1: 创建 MinimalLLM 实例（配置 API Key 和模型）
    # 步骤2: 调用 chat() 方法，传入消息列表
    
    # ========== 使用示例 ==========
    
    # 示例1: 【推荐】使用 .env 文件配置（最简单的方式）
    # 前提：在项目根目录创建 .env 文件，内容如下：
    #   OPENAI_API_KEY=sk-your-api-key-here
    #   OPENAI_BASE_URL=https://api.moonshot.cn/v1  # 可选
    # 然后直接使用，无需传参：
    # print("=" * 60)
    # print("📋 使用 .env 文件配置示例")
    # print("=" * 60)
    # print("如果已在 .env 文件中配置了 OPENAI_API_KEY 和 OPENAI_BASE_URL")
    # print("可以直接使用 MinimalLLM()，无需传参：\n")
    
    # try:
    #     # 从 .env 文件自动读取配置
    #     client_from_env = MinimalLLM(model="moonshot-v1-8k")
    #     print("✅ 成功从 .env 文件加载配置！")
    #     print(f"   模型: {client_from_env.model}")
    #     print(f"   Base URL: {client_from_env.client.base_url or '默认 (OpenAI)'}\n")
        
    #     # 测试调用
    #     test_response = client_from_env.chat([{"role": "user", "content": "你好"}])
    #     print(f"测试响应: {test_response[:50]}...\n")
    # except RuntimeError as e:
    #     print(f"❌ {e}")
    #     print("请确保已在 .env 文件中配置 OPENAI_API_KEY\n")
    # except Exception as e:
    #     print(f"⚠️  从 .env 加载配置时出错: {e}\n")
    
    # # 示例2: 显式传入配置（用于测试或临时使用）
    # print("=" * 60)
    # print("📝 显式传入配置示例（用于测试）")
    # print("=" * 60)
    # client = MinimalLLM(
    #     model="moonshot-v1-8k",
    #     api_key="sk-your-api-key-here",
    #     base_url="https://api.moonshot.cn/v1"
    # )
    # client = MinimalLLM(model="moonshot-v1-8k")
    
    # 示例3: 单轮对话
    # demo_prompt = "用三点概述深度学习和机器学习的区别。"
    # print("=" * 60)
    # print("📝 单轮对话示例")
    # print("=" * 60)
    # print(f"问题: {demo_prompt}\n")
    
    # try:
    #     response = client.chat([{"role": "user", "content": demo_prompt}])
    #     print(f"回答: {response}\n")
    # except Exception as e:
    #     print(f"❌ 调用失败: {e}\n")
    
    # # 示例4: 多轮对话（说明：每次调用只返回1个答案，但会基于整个对话历史）
    # print("=" * 60)
    # print("💬 多轮对话示例 - 理解上下文")
    # print("=" * 60)
    # print("说明：传入多轮对话历史，模型会理解整个上下文，但只返回1个答案\n")
    # try:
    #     # 方式A: 一次性传入完整对话历史（推荐用于已有历史记录的场景）
    #     messages = [
    #         {"role": "user", "content": "你好，我是Python初学者"},
    #         {"role": "assistant", "content": "你好！很高兴认识你，有什么Python相关的问题我可以帮你解答。"},
    #         {"role": "user", "content": "请推荐3本Python入门书籍"}
    #     ]
    #     print("传入的对话历史：")
    #     for msg in messages:
    #         print(f"  {msg['role']}: {msg['content']}")
    #     print()
        
    #     response = client.chat(messages)
    #     print(f"模型回答（基于整个对话历史）: {response}\n")
    # except Exception as e:
    #     print(f"❌ 调用失败: {e}\n")
    
    # # 示例4.1: 逐步累积的多轮对话（实际使用场景）
    # print("=" * 60)
    # print("💬 逐步累积的多轮对话示例")
    # print("=" * 60)
    # print("说明：在实际使用中，你需要手动维护对话历史列表\n")
    # try:
    #     # 初始化对话历史
    #     conversation_history = []
        
    #     # 第1轮：用户提问
    #     user_msg_1 = {"role": "user", "content": "什么是机器学习？"}
    #     conversation_history.append(user_msg_1)
    #     print(f"第1轮 - 用户: {user_msg_1['content']}")
    #     response_1 = client.chat(conversation_history)
    #     print(f"第1轮 - 助手: {response_1[:50]}...\n")
        
    #     # 将助手的回答加入历史
    #     conversation_history.append({"role": "assistant", "content": response_1})
        
    #     # 第2轮：基于第1轮的上下文继续提问
    #     user_msg_2 = {"role": "user", "content": "它和深度学习有什么区别？"}
    #     conversation_history.append(user_msg_2)
    #     print(f"第2轮 - 用户: {user_msg_2['content']}")
    #     print("（注意：模型会理解'它'指的是机器学习）")
    #     response_2 = client.chat(conversation_history)
    #     print(f"第2轮 - 助手: {response_2[:50]}...\n")
        
    #     # 第3轮：继续对话
    #     conversation_history.append({"role": "assistant", "content": response_2})
    #     user_msg_3 = {"role": "user", "content": "请给我一个简单的例子"}
    #     conversation_history.append(user_msg_3)
    #     print(f"第3轮 - 用户: {user_msg_3['content']}")
    #     print("（注意：模型会理解'例子'指的是机器学习或深度学习的例子）")
    #     response_3 = client.chat(conversation_history)
    #     print(f"第3轮 - 助手: {response_3[:50]}...\n")
        
    #     print("✅ 多轮对话完成！每次调用只返回1个答案，但会基于整个对话历史理解上下文。\n")
    # except Exception as e:
    #     print(f"❌ 调用失败: {e}\n")
    
    # # 示例5: 带参数调用（控制生成参数）
    # print("=" * 60)
    # print("⚙️  带参数调用示例（temperature=0.7, max_tokens=100）")
    # print("=" * 60)
    # try:
    #     response = client.chat(
    #         [{"role": "user", "content": "用一句话解释什么是机器学习"}],
    #         temperature=0.7,  # 控制随机性
    #         max_tokens=100    # 限制最大长度
    #     )
    #     print(f"回答: {response}\n")
    # except Exception as e:
    #     print(f"❌ 调用失败: {e}\n")
        
        

