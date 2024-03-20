import httpx
from langchain_openai import AzureChatOpenAI
from langchain.document_loaders import UnstructuredFileLoader
from langchain.text_splitter import CharacterTextSplitter
from langchain.embeddings import AzureOpenAIEmbeddings
from langchain.chains import RetrievalQA
from langchain.vectorstores import Chroma

import CodeToUml

azure_embedded_configs = {
    "azure_endpoint": "https://dev-mgmt-infra.amaiz.corp.amdocs.azr/v1/hackathon/regions/northcentralus/",
    "openai_api_version": "2023-05-15",
    "azure_deployment": "text-embedding-ada",
    "openai_api_key": "5d57e861530c4f30b60dd25fae432f52",
    "openai_api_type": "azure",
    "http_client": httpx.Client(verify=False)  # SSL Disabled
}

azure_configs = {
    "azure_endpoint": "https://dev-mgmt-infra.amaiz.corp.amdocs.azr/v1/hackathon/regions/canadaeast/",
    "openai_api_version": "2023-05-15",
    "azure_deployment": "gpt-35",
    "openai_api_key": "5d57e861530c4f30b60dd25fae432f52",
    "openai_api_type": "azure",
    "http_client": httpx.Client(verify=False)  # SSL Disabled
}

llm = AzureChatOpenAI(**azure_configs)
filepath = ''
documents = ''
try:
    filepath = input("Enter File Path: ")
    if filepath.lower().endswith('py'):
        CodeToUml.main(filepath)
        exit()
    else:
        loader = UnstructuredFileLoader(filepath)
        documents = loader.load()
        #print(documents)
except (KeyboardInterrupt, EOFError):
    print('Exception Occurred!!!')

text_splitter = CharacterTextSplitter(chunk_size=2000, chunk_overlap=0)
texts = text_splitter.split_documents(documents)
#print(texts)

embeddings = AzureOpenAIEmbeddings(**azure_embedded_configs)
doc_search = Chroma.from_documents(texts, embeddings)
chain = RetrievalQA.from_chain_type(llm, retriever=doc_search.as_retriever())

while True:
    try:
        user_input = input("You: ")
        if user_input.__eq__('Thats all'):
            print("Bot: Bye Bye!! Better Luck Next Time")
            exit()
        response = chain.run(user_input)
        print("Bot: ", response)

    except (KeyboardInterrupt, EOFError, SystemExit):
        break
