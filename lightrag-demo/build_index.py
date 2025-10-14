import os
import asyncio
from lightrag import LightRAG
from lightrag.llm.ollama import ollama_model_complete, ollama_embed
from lightrag.kg.shared_storage import initialize_pipeline_status

WORKING_DIR = "./rag_storage"
DOCS_DIR = "./inputs"

from dotenv import load_dotenv
load_dotenv()

class OllamaEmbeddingWrapper:
    def __init__(self, embed_model: str, embedding_dim: int):
        self.embed_model = embed_model
        self.embedding_dim = embedding_dim

    async def __call__(self, texts):
        return await ollama_embed(texts, embed_model=self.embed_model)

embedding_func = OllamaEmbeddingWrapper(embed_model="bge-m3", embedding_dim=1024)

async def init_rag():
    rag = LightRAG(
        working_dir=WORKING_DIR,
        llm_model_func=ollama_model_complete,
        llm_model_name="qwen3:14b",
        llm_model_kwargs={
            "options": {
                "num_ctx": 32768,
                "temperature": 0.2,
                "repeat_penalty": 1.1
            }
        },
        embedding_func=embedding_func
    )
    await rag.initialize_storages()
    await initialize_pipeline_status()
    return rag

async def insert_txt_files(rag):
    for file in os.listdir(DOCS_DIR):
        if file.endswith(".txt"):
            path = os.path.join(DOCS_DIR, file)
            with open(path, "r", encoding="utf-8") as f:
                text = f.read()
                print(f"Inserting {file}...")
                await rag.ainsert(
                    input=text,
                    ids=file,
                    file_paths=path
                )

async def main():
    rag = await init_rag()
    await insert_txt_files(rag)
    await rag.finalize_storages()

if __name__ == "__main__":
    asyncio.run(main())
