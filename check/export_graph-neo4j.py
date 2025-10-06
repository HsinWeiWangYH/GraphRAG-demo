from neo4j import GraphDatabase
import json

driver = GraphDatabase.driver("bolt://localhost:7687", auth=("neo4j", "test1234"))

with driver.session() as session:
    result = session.run("MATCH (n)-[r]->(m) RETURN n,r,m LIMIT 100;")
    data = [record.data() for record in result]

with open("graph_sample-neo4j.json", "w", encoding="utf-8") as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

driver.close()
