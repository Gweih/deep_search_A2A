from agent.subagents.knowledge_base_agent import knowledge_base_agent
from agent.subagents.database_query_agent import database_query_agent
from agent.subagents.search_online_agent import search_online_agent
from langgraph.checkpoint.memory import InMemorySaver
from tools.markdown_tools import generate_markdown
from tools.pdf_tools import convert_md_to_pdf
from tools.upload_file_read_tool import read_file_content
from deepagents import create_deep_agent
from agent.llm import model
from agent.prompts import main_agent_config
from api.monitor import monitor
import asyncio
import uuid
import shutil
from pathlib import Path
from api.context import set_session_context, reset_session_context, set_thread_context
from langchain_core.messages import AIMessage

main_agent = create_deep_agent(
   model = model,
   system_prompt=main_agent_config['system_prompt'],
   tools= [generate_markdown,convert_md_to_pdf,read_file_content],
   checkpointer=InMemorySaver(),
   subagents=[
       database_query_agent,
       search_online_agent,
       knowledge_base_agent
   ]
)

project_root_path = Path(__file__).parents[1].resolve() # 使用resolve不用obsolute的原因是resolve会解析找文件真实地址 # TODO:自动识别项目的根目录
async def run_deep_agent(task_query,session_id): # 异步执行智能体,以方便多个客户端使用
    print(f"当前会话的main_agent开始执行了！ 会话id:{session_id}")
    session_dir = project_root_path / "output" / f"session_{session_id}" # 存储文件的专属文件夹
    session_dir.mkdir(parents=True, exist_ok=True) # 第一次请求要创建文件夹,存在也不会报错
    session_dir_str = str(session_dir).replace("\\","/") # 转换绝对路径风格,防止大模型出现幻觉
    relative_session_dir_str = str(session_dir.relative_to(project_root_path)).replace("\\","/") # 防止大模型因为长路径出现幻觉,给大模型输出的是相对路径

    #处理上传文件 （updated / session_session_id）
    updated_dir_path = project_root_path / "updated" / f"session_{session_id}" # 创建一个文件夹用于存放
    updated_info_prompt = "" # 有上传文件，拼接上传文件专属解析位置的提示词
    if updated_dir_path.exists(): # 判断文件中有没有内容
        files = [ f.name  for f in updated_dir_path.iterdir()  if f.is_file()] # 获取文件的名称
        # 将上传文件统一赋值到 output_dir 方便前端统一读取 session_dir
        if files:
            for filename in files:
                shutil.copy2(updated_dir_path / filename, session_dir / filename) # 将原文件复制到目标文件中
            updated_info_prompt = (f"\n    [已上传文件] 已加载到工作目录:\n" + "\n".join([f"    - {f}" for f in files]) + "\n    请优先使用工具（read_file_content）读取并参考这些文件。") # 构建提示词给大模型

    session_dir_token = set_session_context(session_dir_str)  # 存储的当前会话对应的文件夹地址
    session_id_token = set_thread_context(session_id)  # 获取当前会话的session_id对应socket
    monitor.report_session_dir(session_dir_str)  # 当前会话对应的文件夹地址推送给起前端！

    # 执行main_agent
    config = {
        "configurable":{
            "thread_id":session_id
        }
    }

    # 构建提示词
    path_instruction = f"""
    【工作环境指令】
    工作目录: {relative_session_dir_str}
    {updated_info_prompt}

    规则：
    1. 新生成文件必须保存到工作目录：'{relative_session_dir_str}/filename'
    2. 读取已上传的文件时，请直接将文件名（例如：'开篇.txt'）作为 filename 参数传入（read_file_content）读取工具，不要带上任何目录前缀。
    3. 使用相对路径，禁止使用绝对路径
    4. 若存在上传文件，请先分析内容
    """
    # 反馈结果
    try:
        # 执行
        async for chunk in main_agent.astream({
            "messages":[
                {
                    "role":"user","content":task_query+path_instruction
                }
            ]
        },config=config):
            # {"model [大模型决定调用工具 子智能体  最终结果] / tools" : {messages:[xxx...]}}
            for node_name,state in chunk.items():
                if not state or "messages" not in state: continue
                messages = state["messages"]
                if messages and isinstance(messages,list):
                    last_msg = messages[-1]
                    if node_name == 'model':
                        if last_msg.tool_calls:
                            # 工具和子智能体
                            for tool_call in last_msg.tool_calls:
                                if tool_call['name'] == 'task':
                                    # 调用某个子智能体
                                    monitor.report_assistant(tool_call['args']['subagent_type'],{'description':tool_call['args']['description']})
                        elif last_msg.content:
                            # 最终结果
                            print(f"主智能体执行结果，最终结果：{last_msg.content[:100]}")
                            monitor.report_task_result(last_msg.content)

    except Exception as e :
        # 报错推送错误信息给前端
        monitor._emit("error",f"执行主智能发生异常信息：{str(e)}")
    finally:
        # 释放存储的地址和session_id
        reset_session_context(session_dir_token, session_id_token)

