import os.path

# 导入依赖
from ragflow_sdk import RAGFlow #链接rag服务的客户端
from ragflow.rag_config import _load_ragflow_env

# 创建一个ragflow的客户端
api_key,base_url =_load_ragflow_env()
ragflow_client = RAGFlow(api_key=api_key,base_url=base_url)

# 代码创建知识库
def create_knowledge_base(knowledge_base_name, description):
    # knowledge_base_name: 名字   description: 描述   text-embedding-v2@Tongyi-Qianwen:向量模型
    ds = ragflow_client.create_dataset(name=knowledge_base_name, description=description,embedding_model="text-embedding-v2@Tongyi-Qianwen")
    print(f"创建知识库成功：{ds},{ds.id}")

# TODO:测试代码
if __name__ == '__main__':
    # 创建知识库
    create_knowledge_base("代码创建的知识库", "这一个学搭建智能体学疯的人用代码创建的知识库",)

# 上传文件到知识库
def upload_file_to_knowledge_base(kb_id, file_paths):
    # 链接ragflow的客户端
    # 获取当前账号下知识库的列表信息
    datasets = ragflow_client.list_datasets(id=kb_id,page=1,page_size=10)
    dataset = datasets[0] # 获取列表的第一个
    # 文件包装成对应的上传dict格式
    document_list = [] # 存储上传文件的列表
    for file_path in file_paths: # file_path->文件的地址
        file_name = os.path.basename(file_path) # 获取文件名
        with open(file_path, 'rb') as f:
            blob = f.read()
            document_list.append({
                "display_name": file_name, # 显示名称
                "name": file_name, # 名称
                "blob": blob
            })

    # 进行文件上传了
    dataset.upload_documents(document_list)

"""
多了一个知识库:
    名字:代码创建的知识库
    描述:这一个学搭建智能体学疯的人用代码创建的知识库
"""