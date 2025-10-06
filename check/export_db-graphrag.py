import lancedb

db = lancedb.connect("../graphragdemo/output/lancedb")

print(db.table_names())          # 查看有哪些表
tbl = db.open_table("default-entity-description")    # 打開一張表
print(tbl.schema)                # 看欄位
print(tbl.head(3))               # 顯示前幾筆資料