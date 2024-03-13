from langchain_openai import ChatOpenAI

llm = ChatOpenAI(openai_api_key="ls__087b5cc75f2b402f9eb01d314a18d044")

llm.invoke("how can langsmith help with testing?")