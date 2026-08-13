from agent.prompts import sub_agents_config
from tools.sql_tools import list_sql_tables,get_table_data,execute_sql_query

database_query_agent = {
    "name":sub_agents_config["sql"].get("name",""),
    "description":sub_agents_config["sql"].get("description",""),
    "system_prompt":sub_agents_config["sql"].get("system_prompt",""),
    "tools": [list_sql_tables,get_table_data,execute_sql_query]
}