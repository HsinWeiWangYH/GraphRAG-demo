mkdir -p ../ms-graphrag-results/
graphrag query --root ../graphragdemo/ --method local --query "每位市民都有個人化的 AI 助理，能做甚麼?"
graphrag query --root ../graphragdemo/ --method global --query "每位市民都有個人化的 AI 助理，能做甚麼?"