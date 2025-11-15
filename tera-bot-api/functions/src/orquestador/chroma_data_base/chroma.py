from __future__ import annotations
import logging
import os
from dataclasses import dataclass
from typing import Any, List, Optional
import chromadb
from chromadb.utils import embedding_functions
from chromadb.api.types import (
    OneOrMany,
    URI,
)

from dotenv import load_dotenv
load_dotenv()

@dataclass
class ChromaConfig:
    """Configuración para ChromaDB y embeddings."""
    # Configuración de ChromaDB
    database: str = os.getenv("CHROMA_DATABASE_NAME", "Development")
    path: str = os.getenv("CHROMA_PATH", "Development")

    # Configuración de embeddings
    openai_api_key = os.getenv("OPENAI_API_KEY")
    openai_model: str = os.getenv("OPENAI_EMBEDDING_MODEL", "text-embedding-3-small")


class ChromaService:
    """
    Servicio para manejar ChromaDB con diferentes proveedores de embeddings.
    Usa OpenAI o SentenceTransformers para generar embeddings.
    Soporta operaciones CRUD y consultas.
    """
    def __init__(self, cfg: Optional[ChromaConfig] = None) -> None:
        logging.info("Iniciando ChromaService...")
        self.cfg = cfg or ChromaConfig()
        self._validate_cfg()
        self._client = None

    def _validate_cfg(self) -> None:
        """ 
        Valida la configuración necesaria.
        """
        if not self.cfg.database:
            raise ValueError("CHROMA_DATABASE no configurada.")

    @property
    def client(self):
        if self._client is None:
            self._client = self._create_client()
        return self._client

    def _create_client(self):
        """
        Crea un cliente ChromaDB persistente.
        """

        # Parámetros de conexión
        try:
            api_key = os.getenv("CHROMA_API_KEY")
            tenant_id = os.getenv("CHROMA_TENANT_ID")
            database_name = os.getenv("CHROMA_DATABASE_NAME")
            if not api_key or not tenant_id or not database_name:
                raise ValueError("CHROMA_API_KEY, CHROMA_TENANT_ID o CHROMA_DATABASE_NAME no configuradas.")
            # Creamos un cliente persistente para bases de datos locales
            return chromadb.CloudClient(
                api_key=api_key,
                tenant=tenant_id,
                database=database_name
            )
        except Exception as e:
            logging.error(f"Error creando ChromaDB client: {e}")
            raise

    def _create_embedder(self) -> embedding_functions.EmbeddingFunction:
        """
        Esta función traduce los textos a vectores y poder ser almacenados en ChromaDB.
        Crea el proveedor de embeddings con OpenAI.
        """
        try:
            api_key = self.cfg.openai_api_key
            logging.info(f"Using OpenAI model: {self.cfg.openai_model}")
            if not api_key:
                raise ValueError("OPENAI_API_KEY no configurada y EMBEDDINGS_PROVIDER=openai.")
            return embedding_functions.OpenAIEmbeddingFunction(api_key=api_key, model_name="text-embedding-3-small")
        except Exception as e:
            logging.error(f"Error creando OpenAIEmbedder: {e}")
            raise

    def _get_or_create_collection(self, name: str) -> chromadb.Collection:
        """
        Obtiene o crea una colección en ChromaDB.
        Args:
            name: Nombre de la colección.
        Returns:
            La colección de ChromaDB.
        """
        client = self._create_client()
        embedding_function = self._create_embedder()
        collection = client.get_or_create_collection(
            name=name,
            embedding_function=embedding_function,
            configuration={
                "hnsw": {
                    "space": "cosine",
                    "ef_construction": 200,
                }
            }
        )
        logging.info(f"ChromaService: Usando colección '{name}' en base '{self.cfg.database}'")
        return collection

    def add_texts(
        self,
        texts: List[str],
        name_collection: str,
        metadatas: chromadb.CollectionMetadata,
        ids: OneOrMany[URI],
    ) -> None:
        """
        Agrega textos a una colección en ChromaDB.
        Args:
            texts: Lista de textos a agregar.
            name_collection: Nombre de la colección.
            metadatas: Metadatos asociados a cada texto.
            ids: Identificadores únicos para cada texto.
        """
        if not texts:
            return
        collection = self._get_or_create_collection(name_collection)
        collection.add(ids=ids, documents=texts, metadatas=metadatas)
        logging.info(f"ChromaService: Agregados {len(texts)} textos a la colección '{name_collection}'")
    
    def upsert_texts(
        self,
        texts: List[str],
        name_collection: str,
        metadatas: chromadb.CollectionMetadata,
        ids: OneOrMany[URI],
    ) -> None:
        """
        Inserta o actualiza textos en una colección en ChromaDB.
        Args:
            texts: Lista de textos a insertar o actualizar.
            name_collection: Nombre de la colección.
            metadatas: Metadatos asociados a cada texto.
            ids: Identificadores únicos para cada texto.
        """
        if not texts:
            return
        
        collection = self._get_or_create_collection(name_collection)
        collection.upsert(documents=texts, metadatas=metadatas, ids=ids)
        logging.info(f"ChromaService: Upserted {len(texts)} textos en la colección '{name_collection}'")

    def query(
        self,
        name_collection: str,
        query_texts: List[str],
        n_results: int = 5,
    ) -> Any:
        """
        Consulta la base de conocimientos en una colección específica.
        Args:
            name_collection: Nombre de la colección.
            query_texts: Lista de textos de consulta.
            n_results: Número de resultados a retornar por consulta.
        Returns:
            Resultados de la consulta incluyendo documentos, metadatos y distancias.
        """
        collection = self._get_or_create_collection(name_collection)
        results = collection.query(
            query_texts=query_texts,
            n_results=n_results,
            include=["documents", "metadatas", "distances"]
        )
        documents = results.get('documents', []) if results else []
        if not documents:
            logging.warning(f"ChromaService: Sin resultados en '{name_collection}' para {len(query_texts)} textos")

        logging.info(f"ChromaService: Resultados de consulta: {results}")

        logging.info(f"ChromaService: Consulta en '{name_collection}' con {len(query_texts)} textos, resultados obtenidos {results}")
        return results

    def reset_collection(self, name_collection: str) -> None:
        """
        Resetea una colección en ChromaDB.
        Nota: Esto elimina todos los datos en la colección.
        Args:
            name_collection: Nombre de la colección a resetear.
        """
        # elimina la colección y la crea de nuevo con la misma config
        self.client.delete_collection(name_collection)
        self.collection = self._get_or_create_collection(name_collection)


# Fábrica rápida si solo quieres el cliente/colección listos
def get_chroma_service() -> ChromaService:
    cfg = ChromaConfig()
    return ChromaService(cfg)
