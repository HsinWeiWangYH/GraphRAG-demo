# GraphRAG x Neo4j Demo

本專案為 使用 Microsoft & LightRAG & Neo4j 建立知識圖譜，並結合 LLM 進行全域與本地語意查詢。
* Microsoft GraphRAG (https://github.com/microsoft/graphrag) 
* Neo4j (https://github.com/neo4j/neo4j-graphrag-python)
* LightRAG (https://github.com/HKUDS/LightRAG)

---
### 環境設定 與 資料集準備

#### > 建立 Conda 環境

```
conda create -n graphrag-denv python=3.11 -y
conda activate graphrag-denv
pip install -r requirements.txt

<!-- 安裝 GraphRAG  -->
git clone https://github.com/microsoft/graphrag.git ms-graphrag
cd ms-graphrag
pip install -e .
cd ..

<!-- 安裝 LightRAG  -->
git clone https://github.com/HKUDS/LightRAG.git
cd LightRAG/
pip install -e .
cd ..
```

#### > 安裝 LLM 模型（使用本地 Ollama）

Ollama (https://ollama.ai/)
```
curl -fsSL https://ollama.com/install.sh | sh
ollama pull qwen3:14b
ollama pull bge-m3
```

#### > 準備資料集

儲存範例
```

├── data
│   ├── 公民AI助理的角色.txt
│   ├── 政策與永續決策委員會.txt
│   ├── 能源中心與智慧電網.txt
│   ├── 自駕交通與能源整合.txt
│   └── 雲端資料與城市模型.txt
```

---

### 📦 Microsoft GraphRAG 建立流程

#### > 初始化 (專案目錄)
```
mkdir -p graphragdemo
graphrag init --root ./graphragdemo

mkdir -p graphragdemo/input/
cp data/*.txt graphragdemo/input/
```

#### > 修改 ollama 參數
參考 ms-graphrag-example/ 修改 `graphragdemo/settings.yaml` 與 `.env` 參數。
#### > 更新程式碼
參考 ms-graphrag-example/ 替換 search.py

* 將 ms-graphrag/graphrag/query/structured_search/local_search/search.py 內容用 ms-graphrag-example/search_local.py 替換
* 將 ms-graphrag/graphrag/query/structured_search/global_search/search.py 內容用 ms-graphrag-example/search_global.py 替換

以上程式碼會導出檢索結果，其中以下片段會使 GraphRAG search 完後自動終止流程，若希望產生 "回答結果" 請註解相關段落：
```
sys.exit("All results have been successfully retrieved and saved to ms-graphrag-results. Execution stopped.") 
```

#### > 建立索引  (專案目錄)
```
graphrag index --root ./graphragdemo
```

#### > global / local 查詢範例 (專案目錄)
```
graphrag query --root ./graphragdemo/ --method global --query "請用要點總結這些文件的主題"
graphrag query --root ./graphragdemo/ --method local --query "請解釋 AI 管理的能源中心"
```

#### > 批次執行每一次查詢 (ms-graphrag-example/)
寫一個 shell 批次執行查詢 結果將存於 ms-graphrag-results/

以 convert_graphrag_results.py 將 查詢結果 轉換成 json

* 產生適用於 graphrag_eval_ntnu/eval_graphrag.py 的檔案
* 將 local-search-sources.csv 視為查詢結果

```
sh run-ms-graphrag.sh
python convert_graphrag_results.py
```
#### > 運行 graphrag_eval_ntnu 計算查詢分數 (graphrag_eval_ntnu/)
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
將 graphrag_eval_ntnu/eval_graphrag.py 跟 ms-graphrag-example/run-eval.py 放在一起執行
```
cp ms-graphrag-example/run-eval.py graphrag_eval_ntnu/
cd graphrag_eval_ntnu/
python run-eval.py -ans ans.json --result ../ms-graphrag-results/graphrag_results.json
```

#### > [其他] 匯出與檢視 GraphRAG 資料庫 (check/)

```
python export_db-graphrag.py
```

#### > [其他] Visualizing and Debugging
> 可參考: [Visualization Guide](https://microsoft.github.io/graphrag/visualization_guide/)

---

### 📦 LightRAG 建立流程

#### > 初始化 (專案目錄)
```
mkdir -p lightrag-demo/
cp -r data/ lightrag-demo/inputs
```

#### > 修改 ollama 參數 (專案目錄)
參考 lightrag-example/ 修改 `.env` 參數。

`.env` 請放在運行程式時的資料夾中
```
cp lightrag-example/env.example lightrag-demo/.env
```
#### > 更新程式碼 (專案目錄)
參考 lightrag-example/ 替換 lightrag.py
* 將 LightRAG/lightrag/lightrag.py 內容用 lightrag-example/lightrag-example.py  替換

以上程式碼會導出檢索結果，其中以下片段會使 GraphRAG search 完後自動終止流程，若希望產生 "回答結果" 請註解相關段落：
```
sys.exit("All results have been successfully retrieved and saved to lightrag-results. Execution stopped.") 
```
#### > 建立索引  (lightrag-demo/)
```
python ../lightrag-example/build_index.py
```
#### > 查詢範例 (lightrag-demo/)
Query Mode: "local", "global", "hybrid", "mix", "naive", "bypass"

```bash
python ../lightrag-example/query_rag.py --mode local "請解釋 AI 管理的能源中心"
```
#### > 批次執行每一次查詢 (lightrag-demo/)
寫一個 shell 批次執行查詢 結果將存於 lightrag-results/

以 convert_graphrag_results.py 將 查詢結果 轉換成 json
* 產生適用於 graphrag_eval_ntnu/eval_graphrag.py 的檔案
* 將 lightrag-local-search-chunks.csv 視為查詢結果

```bash
sh ../lightrag-example/run-lightrag.sh
python ../lightrag-example/convert_graphrag_results.py
```
#### > 運行 graphrag_eval_ntnu 計算查詢分數 (graphrag_eval_ntnu/)
將 graphrag_eval_ntnu/eval_graphrag.py 跟 ms-graphrag-example/run-eval.py 放在一起執行
```
cp ms-graphrag-example/run-eval.py graphrag_eval_ntnu/
cd graphrag_eval_ntnu/
python run-eval.py -ans ans.json --result ../lightrag-results/graphrag_results.json
```

-----

### 📦 使用 Neo4j 建立圖形資料庫

#### > 初始化
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

#### > 建立知識圖譜

```
python neo4jdemo/demo_build_graph.py build
```

#### > 建立向量索引（Neo4j 內部）

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

#### > 執行查詢

使用以下指令向 LLM 提問：

```
python neo4jdemo/demo_build_graph.py "請解釋 AI 管理的能源中心"
```

#### > [其他] 匯出現有的圖形資料庫 (check/ 運行)

```
python export_graph-neo4j.py
```

---

### 架構

```
.
├── data/                           # 原始輸入資料
│
├── ms-graphrag/                    # [git clone] GraphRAG 專案主程式
├── ms-graphrag-example/            # GraphRAG + Ollama 修改範例與相關程式碼
├── graphragdemo/                   # GraphRAG 索引資料夾
├── ms-graphrag-results/            # GraphRAG 查詢結果輸出
│
├── LightRAG/                       # [git clone] LightRAG 專案主程式
├── lightrag-example/               # LightRAG + Ollama 修改範例與相關程式碼
├── lightrag-demo/                  # LightRAG 索引資料夾
├── lightrag-results/               # LightRAG 查詢結果輸出
│
├── neo4jdemo/                      # Neo4j 實驗資料夾
│
├── check/
│   ├── export_db-graphrag.py       # 匯出 GraphRAG 圖資料
│   └── export_graph-neo4j.py       # 匯出 Neo4j 圖資料
│
├── graphrag_eval_ntnu/             # [額外下載] RAG 評測程式
│
├── requirements.txt                # 依賴套件清單
└── readme.md                       # 專案說明文件

```

### Reference

* [Microsoft GraphRAG](https://microsoft.github.io/graphrag/)
* [LightRAG](https://arxiv.org/pdf/2410.05779)
* [Neo4j](https://neo4j.com/docs/neo4j-graphrag-python/current/)
* [Ollama](https://docs.ollama.com/)

---

更新日期：2025-10-15