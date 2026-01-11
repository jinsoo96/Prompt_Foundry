import chromadb
from chromadb.utils import embedding_functions
from typing import List, Dict
import uuid
from app.services.llm_provider import get_default_llm


class RAGService:
    """RAG (Retrieval-Augmented Generation) 서비스"""

    def __init__(self, collection_name: str = "documents"):
        # ChromaDB 클라이언트 초기화
        self.client = chromadb.PersistentClient(path="./data/chroma")

        # 임베딩 함수 설정 (sentence-transformers 사용)
        self.embedding_function = embedding_functions.SentenceTransformerEmbeddingFunction(
            model_name="all-MiniLM-L6-v2"
        )

        # 컬렉션 생성 또는 가져오기
        try:
            self.collection = self.client.get_collection(
                name=collection_name,
                embedding_function=self.embedding_function
            )
        except:
            self.collection = self.client.create_collection(
                name=collection_name,
                embedding_function=self.embedding_function
            )

        # 기본 LLM 프로바이더
        self.default_llm = get_default_llm()

    def add_documents(self, documents: List[str], metadatas: List[Dict] = None):
        """문서를 벡터 DB에 추가"""
        ids = [str(uuid.uuid4()) for _ in documents]

        if metadatas is None:
            metadatas = [{"source": f"doc_{i}"} for i in range(len(documents))]

        self.collection.add(
            documents=documents,
            metadatas=metadatas,
            ids=ids
        )

        return ids

    def retrieve_context(self, query: str, n_results: int = 3) -> List[str]:
        """쿼리와 관련된 컨텍스트 검색"""
        results = self.collection.query(
            query_texts=[query],
            n_results=n_results
        )

        # 검색된 문서 반환
        if results['documents']:
            return results['documents'][0]
        return []

    def generate_response(
        self,
        query: str,
        system_prompt: str,
        context: List[str] = None,
        conversation_history: List[Dict] = None,
        llm_provider_type: str = None,
        model_name: str = None
    ) -> str:
        """LLM을 사용하여 응답 생성"""

        # LLM 프로바이더 선택
        from app.services.llm_provider import get_llm_provider
        if llm_provider_type:
            llm = get_llm_provider(llm_provider_type, model_name)
        else:
            llm = self.default_llm

        # 컨텍스트가 없으면 검색
        if context is None:
            context = self.retrieve_context(query)

        # 프롬프트 구성
        context_str = "\n\n".join(context) if context else "No relevant context found."

        # 메시지 구성
        messages = []

        # 시스템 프롬프트 추가
        messages.append({
            "role": "system",
            "content": f"{system_prompt}\n\nContext from knowledge base:\n{context_str}"
        })

        # 대화 히스토리 추가
        if conversation_history:
            messages.extend(conversation_history)

        # 현재 질문 추가
        messages.append({
            "role": "user",
            "content": query
        })

        # LLM으로 응답 생성
        try:
            return llm.chat(messages)
        except Exception as e:
            return f"Error generating response: {str(e)}"

    def chat(
        self,
        message: str,
        system_prompt: str,
        conversation_history: List[Dict] = None,
        llm_provider: str = None,
        model_name: str = None
    ) -> Dict:
        """채팅 인터페이스"""

        # 관련 컨텍스트 검색
        context = self.retrieve_context(message)

        # 응답 생성
        response = self.generate_response(
            query=message,
            system_prompt=system_prompt,
            context=context,
            conversation_history=conversation_history,
            llm_provider_type=llm_provider,
            model_name=model_name
        )

        return {
            "response": response,
            "context_used": context
        }
