from app.llm.groq_client import client

models = client.models.list()

for model in models.data:
    print(model.id)