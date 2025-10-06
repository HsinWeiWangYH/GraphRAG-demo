import asyncio
from pathlib import Path
from neo4j import GraphDatabase

from neo4j_graphrag.embeddings import OllamaEmbeddings
from neo4j_graphrag.llm import OllamaLLM
from neo4j_graphrag.experimental.pipeline.kg_builder import SimpleKGPipeline
from neo4j_graphrag.retrievers import VectorRetriever
from neo4j_graphrag.generation import GraphRAG


NEO4J_URI = "neo4j://localhost:7687"
NEO4J_USER = "neo4j"
NEO4J_PASS = "test1234"

LLM_MODEL = "qwen3:14b"
EMBED_MODEL = "bge-m3"
DATA_FOLDER = "data"
VECTOR_INDEX_NAME = "text-index"


def build_knowledge_graph():
    print("start Neo4j & Pipeline...")
    driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASS))

    llm = OllamaLLM(
        model_name="qwen3:14b",
        model_params={
            "temperature": 0,
            "format": "json",
        },
    )
    llm.system_prompt = (
        "你是一個結構化資訊抽取模型。"
        "請從輸入的文本中提取「實體 (entities)」與「關係 (relationships)」。"
        "請嚴格以 JSON 格式回覆，格式如下：\n"
        "{"
        "\"entities\": [{\"name\": \"實體名稱\", \"type\": \"類別\"}], "
        "\"relationships\": [{\"start\": \"起點實體\", \"end\": \"終點實體\", \"type\": \"關係類型\"}]"
        "}\n"
        "不要加任何說明或文字，只能輸出 JSON。"
    )
    embedder = OllamaEmbeddings(model=EMBED_MODEL)

    kg_pipeline = SimpleKGPipeline(
        llm=llm,
        driver=driver,
        embedder=embedder,
        on_error="IGNORE",
        from_pdf=False,
    )

    async def run_pipeline():
        for file in Path(DATA_FOLDER).glob("*.txt"):
            print(f"done: {file.name}")
            text = file.read_text(encoding="utf-8")
            await kg_pipeline.run_async(text=text)

    asyncio.run(run_pipeline())
    driver.close()
    print("KG done")

def query_graph(question: str):
    print(f"query: {question}")
    driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASS))

    embedder = OllamaEmbeddings(model=EMBED_MODEL)
    llm = OllamaLLM(model_name=LLM_MODEL)

    retriever = VectorRetriever(driver, VECTOR_INDEX_NAME, embedder)
    rag = GraphRAG(retriever=retriever, llm=llm)

    response = rag.search(query_text=question, retriever_config={"top_k": 5})
    driver.close()
    print("result：", response.answer)
    return response.answer

if __name__ == "__main__":
    import sys

    if len(sys.argv) >= 2 and sys.argv[1] == "build":
        build_knowledge_graph()
    else:
        q = "未來城市有甚麼"
        if len(sys.argv) > 1:
            q = " ".join(sys.argv[1:])
        query_graph(q)
