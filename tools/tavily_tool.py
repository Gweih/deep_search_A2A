# TODO:网络搜索工具
from typing import  Literal
from langchain_core.tools import tool
from tavily import TavilyClient
import os
from dotenv import load_dotenv
from api.monitor import monitor

# 加载项目根目录的.env
load_dotenv()

# 定义对象
tavily_client = TavilyClient(api_key=os.getenv("TAVTLY_APT_KEY"))

# 定义搜索工具 # https://docs.tavily.com/sdk/python/reference官方文档
@tool
def search_online(
    query:str,
    topic:Literal["general","news","finance"] = "general", # 综合、新闻、财经
    max_results:int = 5,
    include_raw_content = False # 返回原内容 False=精简,True=详细
):
    """
    根据用户问题，进行网络信息收！
    注意：主要搜索公开的网络信息！如果指定查询数据库或者rag不能使用此工具！
    :param query: 用户的查询信息
    :param topic: 查询的类型
    :param max_results: 返回的最大条数
    :param include_raw_content: 是否返回原内容 False 精简 True 详细
    :return:
    """
# 向前端推送调用信息
    monitor.report_tool(tool_name="联网搜索",args={"query":query,"topic":topic,"max_results":max_results,"include_raw_content":include_raw_content})

    return tavily_client.search(query = query,topic = topic,max_results = max_results,include_raw_content = include_raw_content)
