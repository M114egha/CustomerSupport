
import os
from langchain_community.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from langchain.chains import RetrievalQA
from langchain_groq import ChatGroq
from dotenv import load_dotenv

#  Load environment
load_dotenv()

# 🧾 Load PDF Document (place your actual file path)
pdf_path = "data/faq_document.pdf"  # <-- change as needed
loader = PyPDFLoader(pdf_path)
pages = loader.load()

# 🔪 Split into chunks
splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=150)
docs = splitter.split_documents(pages)

# 🔍 Create Embedding + Vector Store
embedding = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
vector_db = FAISS.from_documents(docs, embedding)
vector_db.save_local("faiss_index")
print("Pdf indexed and vectorstore saved")
retriever = vector_db.as_retriever(search_kwargs={"k": 3})

# LLM from Groq
llm = ChatGroq(model_name="llama3-70b-8192", temperature=0)

#  Retrieval-Augmented QA Chain
faq_rag_chain = RetrievalQA.from_chain_type(llm=llm, retriever=retriever)

# Test it!
if __name__ == "__main__":
    question = "For how long is my login/transaction password valid?"
    response = faq_rag_chain.invoke({"query": question})
    print("Q:", question)
    print("A:", response["result"] if isinstance(response, dict) else response)
