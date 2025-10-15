mkdir -p ../lightrag-results/

python ../lightrag-example/query_rag.py --mode local "市民的個人化的 AI 助理可以分析甚麼事情?"
python ../lightrag-example/query_rag.py --mode global "市民的個人化的 AI 助理可以分析甚麼事情?"
python ../lightrag-example/query_rag.py --mode hybrid "市民的個人化的 AI 助理可以分析甚麼事情?"
python ../lightrag-example/query_rag.py --mode mix "市民的個人化的 AI 助理可以分析甚麼事情?"
python ../lightrag-example/query_rag.py --mode naive "市民的個人化的 AI 助理可以分析甚麼事情?"
python ../lightrag-example/query_rag.py --mode bypass "市民的個人化的 AI 助理可以分析甚麼事情?"