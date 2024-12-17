from llama_index.core import  VectorStoreIndex, SimpleDirectoryReader, StorageContext, Settings,ChatPromptTemplate
from llama_index.core.response.notebook_utils import display_response
from llama_index.llms.ollama import Ollama
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from llama_index.vector_stores.chroma import ChromaVectorStore
from llama_index.llms.anthropic import Anthropic
import chromadb
import os
import datetime


os.environ["ANTHROPIC_API_KEY"] = "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"
# os.environ["OPENAI_API_KEY "] = ""

class ChatCSV:
    def __init__(self,local:bool=False):
        self.storage= 'storage'
        self.local = local
        
        if self.local:
            self.embedding = HuggingFaceEmbedding(
                model_name="nomic-ai/nomic-embed-text-v1.5", 
                trust_remote_code=True,
                query_instruction="search_query: ",  # Prefijo para consultas
                text_instruction="search_document: "  # Prefijo para documentos
            )
            Settings.embed_model = self.embedding

            self.llm=Ollama(model="llama3.2:3b", request_timeout=360.0,temperature=0.1)
            Settings.llm = self.llm
        else:
            #TODO BORRAR DESPUES
            # self.embedding = HuggingFaceEmbedding(
            #     model_name="nomic-ai/nomic-embed-text-v1.5", 
            #     trust_remote_code=True,
            #     query_instruction="search_query: ",  # Prefijo para consultas
            #     text_instruction="search_document: "  # Prefijo para documentos
            # )
            self.embedding = HuggingFaceEmbedding(model_name="BAAI/bge-m3")
            Settings.embed_model = self.embedding
            #TODO
            
            # tokenizer = Anthropic().tokenizer
            # Settings.tokenizer = tokenizer
            self.llm = Anthropic(model="claude-3-5-haiku-20241022", temperature=0.3)
            Settings.llm = self.llm

    
        db= chromadb.PersistentClient(path=self.storage)

        chroma_collection = db.get_or_create_collection('ChatCSV')

        self.vector_store = ChromaVectorStore(chroma_collection=chroma_collection)
        self.storage_context = StorageContext.from_defaults(vector_store=self.vector_store)

    def Usar_embedding_armado(self):    
        # Cargar índice existente
        self.index = VectorStoreIndex.from_vector_store(
            self.vector_store, 
            embedding=self.embedding, 
            llm=self.llm, 
            show_progress=True, 
            storage_context=self.storage_context
        )
    
    def Armar_embedding(self,carpeta):
        documents = SimpleDirectoryReader(carpeta).load_data()
        # Creación o carga del índice
        # Crear un nuevo índice si no existe almacenamiento previo
        self.index = VectorStoreIndex.from_documents(
            documents, 
            embedding=self.embedding, 
            llm=self.llm, 
            show_progress=True, 
            storage_context=self.storage_context
        )
        # Guardar índice
        self.index.storage_context.persist(self.storage)

    def Prompts(self):
        self.qa_prompt_str = (
            "La informacion proveniente de la documentacion es la siguiente.\n"
            "---------------------\n"
            "{context_str}\n"
            "---------------------\n"
            "Dado la informacion brindada en la documentacion, y no tu conocimiento a priori, sin informar que se ha utilzado informacion de la documentacion al humano.\n"
            "Responde la pregunta del humano: {query_str}\n"
        )

        self.refine_prompt_str = (
            "Tenemos la oportunidad de refinar la respuesta original "
            "(solo si es necesario) con mas documentacion debajo.\n"
            "------------\n"
            "{context_msg}\n"
            "------------\n"
            "Dado la nueva documentacion, Refina la respuesta original para mejor "
            "respondiendo la pregunta: {query_str}. "
            "Si el contexto no es util, devuelve la respuesta original.\n"
            "No avises al humano acerca de la refinacion de la respuesta ni del uso de la documentacion\n"
            "Respuesta original: {existing_answer}"
        )


        # Text QA Prompt
        self.chat_text_qa_msgs = [
            (
                "system",
                """El asistente es ChatCSV, Creado por Mera Solutions.
                
                Si se presenta un problema matematico, de logia o otro problema proveniente de pensamiento sistematico, ChatCSV piensa a traves de paso a paso antes de dar una respuesta final
                
                Si ChatCSV es consultado de una persona en especifico, este indicara que no posee informacion de personas individuales
                
                ChatCSV es curioso y en caso de no entender poder responder la pregunta, piden que se la reformulen
                
                ChatCSV entiende que hay cosas que no sabe y avisa de lo mismo,
                
                ChatCSV esta recibiendo contexto mediante RAG
                
                ChatCSV siempre brindara la URL indicado en la documentacion al operador
                
                ChatCSV siempre respondera en español, usando la informacion brindada en la documentacion
                
                ChatCSV se encarga de ayudar a un operador telefonico del Centro de Servicios Visa, mientras que este atiende a un cliente al telefono, por lo que debe dar respuestas lo mas certeras posibles, faciles de leer y concretas para que el operador pueda dar una respuesta al cliente
                
                ChatCSV esta siendo conectado con el humano""",
            ),
            ("user", self.qa_prompt_str),
        ]
        self.text_qa_template = ChatPromptTemplate.from_messages(self.chat_text_qa_msgs)

        # Refine Prompt
        self.chat_refine_msgs = [
            (
                "system",
                """El asistente es ChatCSV, Creado por Mera Solutions.
                
                Si se presenta un problema matematico, de logia o otro problema proveniente de pensamiento sistematico, ChatCSV piensa a traves de paso a paso antes de dar una respuesta final
                
                Si ChatCSV es consultado de una persona en especifico, este indicara que no posee informacion de personas individuales
                
                ChatCSV es curioso y en caso de no entender poder responder la pregunta, piden que se la reformulen
                
                ChatCSV entiende que hay cosas que no sabe y avisa de lo mismo,
                
                ChatCSV esta recibiendo contexto mediante RAG        
                
                ChatCSV siempre brindara la URL indicado en la documentacion al operador
                
                ChatCSV siempre respondera en español, usando la informacion brindada en la documentacion
                
                ChatCSV se encarga de ayudar a un operador telefonico del Centro de Servicios Visa, mientras que este atiende a un cliente al telefono, por lo que debe dar respuestas lo mas certeras posibles, faciles de leer y concretas para que el operador pueda dar una respuesta al cliente
                
                ChatCSV esta siendo conectado con el humano""",
            ),
            ("user", self.refine_prompt_str),
        ]
        self.refine_template = ChatPromptTemplate.from_messages(self.chat_refine_msgs)

    def Armar_Query(self):
        self.query_engine = self.index.as_query_engine(
                text_qa_template=self.text_qa_template,
                refine_template=self.refine_template,
                llm=self.llm,
                response_mode='refine'
            )

    def Realizar_consulta(self,query):
        carpeta_log = r'E:\ChatCSV\Log'
        os.makedirs(carpeta_log, exist_ok=True)
        fecha = datetime.datetime.strftime(datetime.datetime.now(),'%Y-%m-%d_%H-%M-%S')
        
        consulta_path = os.path.join(carpeta_log, f'{fecha}_query.txt')
        with open(consulta_path, mode='w', encoding='utf-8') as file:
            file.write(query)
        
        response = self.query_engine.query(query)
        
        response_path = os.path.join(carpeta_log, f'{fecha}_response.txt')
        with open(response_path, mode='w', encoding='utf-8') as file:
            file.write(str(response))

        return str(response)
