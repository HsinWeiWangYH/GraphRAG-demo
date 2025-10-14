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
git clone https://github.com/microsoft/graphrag.git ms-graphrag
cd ms-graphrag
pip install -e .
```

#### 安裝 LLM 模型（使用本地 Ollama）

Ollama (https://ollama.ai/)
```
curl -fsSL https://ollama.com/install.sh | sh
ollama pull qwen3:14b
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

將 ms-graphrag/graphrag/query/structured_search/local_search/search.py 內容用 ms-graphrag-example/search_local.py 替換

將 ms-graphrag/graphrag/query/structured_search/global_search/search.py 內容用 ms-graphrag-example/search_global.py 替換

以下程式碼 會在search完後自動終止，若希望產生 回答 請註解：
```
sys.exit("All results have been successfully retrieved and saved to ms-graphrag-results. Execution stopped.") 
```

#### 建立索引
```
graphrag index --root ./graphragdemo
```

#### global / local 查詢 範例
```
graphrag query --root graphragdemo/ --method global --query "請用要點總結這些文件的主題"
graphrag query --root graphragdemo/ --method local --query "請解釋 AI 管理的能源中心"
```

#### 批次執行每一次查詢
寫一個 shell 批次執行 並 將所有結果存在 ms-graphrag-results/
之後轉換成 graphrag_eval_ntnu/eval_graphrag.py 適用格式

```
sh run-ms-graphrag.sh
python ms-graphrag-example/convert_graphrag_results.py
```
#### 運行 graphrag_eval_ntnu 計算範例
使用 graphrag_eval_ntnu/get_ans.py 得到以下類似的 json 檔案 (ans.json)
```
[
    {
        "query": "請用要點總結這些文件的主題",
        "video_name": "video001",
        "ans": "標準答案段落文字"
    },
    ...
]
```
ms-graphrag-results/graphrag_results.json 儲存 查詢結果 json 檔案
```
[
    {
        "query": "請用要點總結這些文件的主題",
        "source": "城市的 AI 模型不斷學習這些資訊，模擬能源消耗、交通趨勢與人口活動"
    },
    ...
]
```
將 graphrag_eval_ntnu/eval_graphrag.py 跟 ms-graphrag-example/run-eval.py 放在一起
運行 ms-graphrag-example/run-eval.py 

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
├── ms-graphrag-example             # 適用 ollama 的 graphrag 修改範例 含 settings.yaml & .env
├── ms-graphrag-results             # 儲存 graphrag 查詢結果
├── graphragdemo/                   # GraphRAG 工作資料夾
├── neo4jdemo/                      # Neo4j 工作資料夾
├── check/ 
│   └── export_db-graphrag.py           # 匯出 GraphRAG 資料
│   └── export_graph-neo4j.py           # 匯出 Neo4j 圖資料
├── requirements.txt
├── run-ms-graphrag.sh                  # 運行 graphrag 查詢結果
└── readme.md                       # 本文件
```

### Reference

* [Microsoft GraphRAG](https://microsoft.github.io/graphrag/)
* [Neo4j](https://neo4j.com/docs/neo4j-graphrag-python/current/)
* [Ollama](https://docs.ollama.com/)

---

更新日期：2025-10-06
