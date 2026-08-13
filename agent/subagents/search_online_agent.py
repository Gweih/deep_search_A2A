# 创建网络搜索子智能体
from agent.prompts import sub_agents_config
from tools.tavily_tool import search_online

search_online_agent = { # 导入prompts.yml中的提示词
    "name":sub_agents_config["tavily"]["name"],
    "description":sub_agents_config["tavily"]["description"],
    "system_prompt":sub_agents_config["tavily"]["system_prompt"],
    "tools":[search_online]
}


























