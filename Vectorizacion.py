from llama_index.embeddings.langchain import LangchainEmbedding
from langchain.embeddings import HuggingFaceEmbeddings
from llama_index.core import SimpleDirectoryReader, GPTVectorStoreIndex, StorageContext, load_index_from_storage

# Configurar embeddings locales
embed_model = LangchainEmbedding(HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2"))

# 1. Cargar documentos y crear índice con modelo local
documents = SimpleDirectoryReader('documentacion').load_data()
index = GPTVectorStoreIndex.from_documents(documents, embed_model=embed_model)

# 2. Guardar el índice
index.storage_context.persist(persist_dir="./mi_indice")

# 3. Cargar el índice desde almacenamiento con modelo local
storage_context = StorageContext.from_defaults(persist_dir="./mi_indice")
index = load_index_from_storage(storage_context, embed_model=embed_model)

# 4. Desactivar explícitamente el LLM para el motor de consulta
query_engine = index.as_query_engine(llm=None)

# 5. Realizar consulta
respuesta = query_engine.query("¿Cuál es el tema principal del documento?")
print(respuesta)