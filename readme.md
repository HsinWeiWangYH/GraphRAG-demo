# GraphRAG x Neo4j Demo

本專案為 使用 Microsoft & Neo4j 建立知識圖譜，並結合 LLM 進行全域與在地語意查詢。
* Microsoft (https://github.com/microsoft/graphrag) 
* Neo4j (https://github.com/neo4j/neo4j-graphrag-python)

---
### 環境設定 與 資料集準備

#### 建立 Conda 環境

```
conda create -n graphrag-denv python=3.11 -y
conda activate graphrag-denv
pip install -r requirements.txt
```

#### 安裝 LLM 模型（使用本地 Ollama）

Ollama (https://ollama.ai/)
```
curl -fsSL https://ollama.com/install.sh | sh
ollama pull qwen3:4b
ollama pull bge-m3
```

#### 準備資料集

範例
```

├── data
│   ├── 公民AI助理的角色.txt
│   ├── 政策與永續決策委員會.txt
│   ├── 能源中心與智慧電網.txt
│   ├── 自駕交通與能源整合.txt
│   └── 雲端資料與城市模型.txt
```

---

### 📦 Microsoft GraphRAG 建立流程 (graphragdemo/ 底下運行)

#### 初始化
```
mkdir -p graphragdemo
graphrag init --root ./graphragdemo

mkdir -p graphragdemo/input/
cp data/*.txt graphragdemo/input/
```

#### 修改 ollama 參數
參考 ms-graphrag-example/
修改 `graphragdemo/settings.yaml` 與 `.env` 參數。

#### 建立索引
```
graphrag index --root ./graphragdemo
```

#### 執行 global / local 查詢
```
graphrag query --root graphragdemo/ --method global --query "請用要點總結這些文件的主題"
graphrag query --root graphragdemo/ --method local --query "請解釋 AI 管理的能源中心"
```

#### 匯出與檢視 GraphRAG 資料庫 (check/ 運行)

```
python export_db-graphrag.py
```

#### Visualizing and Debugging
> 可參考: [Visualization Guide](https://microsoft.github.io/graphrag/visualization_guide/)

---

### 📦 使用 Neo4j 建立圖形資料庫 (neo4jdemo/ 底下運行)

#### 初始化
啟動 Neo4j Docker 容器
```
docker run -d \
  --name neo4j-graphrag \
  -p7474:7474 -p7687:7687 \
  -e NEO4J_AUTH=neo4j/test123 \
  -e NEO4J_PLUGINS='["apoc"]' \
  neo4j:5.20
```

準備資料
```
mkdir -p neo4jdemo
cp -r data/ neo4jdemo/data/
```

#### 建立知識圖譜

```
python neo4jdemo/demo_build_graph.py build
```

#### 建立向量索引（Neo4j 內部）

進入容器：

```
docker exec -it neo4j-graphrag cypher-shell -u neo4j -p test123
```

在 Cypher Shell 執行：

```
CREATE VECTOR INDEX `text-index` IF NOT EXISTS
FOR (c:Chunk)
ON (c.embedding)
OPTIONS {
  indexConfig: {
    `vector.dimensions`: 1024,
    `vector.similarity_function`: 'cosine'
  }
};
```
完成後離開：
```
: exit
```

#### 執行查詢

使用以下指令向 LLM 提問：

```
python neo4jdemo/demo_build_graph.py "請解釋 AI 管理的能源中心"
```

#### 匯出現有的圖形資料庫 (check/ 運行)

```
python export_graph-neo4j.py
```

-----

### 架構

```
.
├── data/                           # 原始輸入文件
├── ms-graphrag-example             # 適用 ollama 的settings.yaml & .env 範例 
├── graphragdemo/                   # GraphRAG 工作資料夾
├── neo4jdemo/                      # Neo4j 工作資料夾
├── check/ 
│   └── export_db-graphrag.py           # 匯出 GraphRAG 資料
│   └── export_graph-neo4j.py           # 匯出 Neo4j 圖資料
├── requirements.txt
└── readme.md                       # 本文件
```

### Reference

* [Microsoft GraphRAG](https://microsoft.github.io/graphrag/)
* [Neo4j](https://neo4j.com/docs/neo4j-graphrag-python/current/)
* [Ollama](https://docs.ollama.com/)

---

更新日期：2025-10-06
