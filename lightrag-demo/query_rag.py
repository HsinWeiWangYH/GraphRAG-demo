import asyncio
from lightrag import LightRAG, QueryParam
from lightrag.utils import setup_logger
from lightrag.llm.ollama import ollama_model_complete, ollama_embed
from lightrag.utils import EmbeddingFunc
from lightrag.kg.shared_storage import initialize_pipeline_status

from dotenv import load_dotenv
load_dotenv()

async def init_rag(working_dir: str, llm_model: str, embed_model: str, num_ctx: int = 32768):
    """
    初始化 LightRAG，使用 Ollama (qwen3:14b + bge-m3)
    """
    setup_logger("lightrag", level="INFO")

    # 建立 embedding 函數
    embedding_func = EmbeddingFunc(
        embedding_dim=1024,  # bge-m3 的向量維度是 1024
        max_token_size=8192,  # 可自行調整
        func=lambda texts: ollama_embed(texts, embed_model=embed_model),
    )

    # 設定 LLM context 長度
    llm_kwargs = {"options": {"num_ctx": num_ctx}}

    rag = LightRAG(
        working_dir=working_dir,
        llm_model_func=ollama_model_complete,
        llm_model_name=llm_model,
        llm_model_kwargs=llm_kwargs,
        embedding_func=embedding_func,
    )

    await rag.initialize_storages()
    await initialize_pipeline_status()

    return rag


def run_query(working_dir: str, question: str, mode: str = "global"):
    rag = asyncio.run(init_rag(working_dir, llm_model="qwen3:14b", embed_model="bge-m3"))
    param = QueryParam(mode=mode)
    result = rag.query(question, param=param)
    return result


import argparse
import sys

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run RAG query")
    parser.add_argument("--mode", required=True, help="查詢模式，例如: global, local")
    parser.add_argument("question", help="要查詢的問題")

    args = parser.parse_args()

    WORKING_DIR = "./rag_storage"
    QUESTION = args.question
    MODE = args.mode

    answer = run_query(WORKING_DIR, QUESTION, mode=MODE)
