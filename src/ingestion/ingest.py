import os
from dotenv import load_dotenv
from langchain_community.document_loaders import TextLoader , DirectoryLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter

load_dotenv()

def load_documents(policy_dir: str):
    """Load all policy text files from the given directory."""
    loader = DirectoryLoader(policy_dir, glob="*.txt", loader_cls=TextLoader)
    documents = loader.load()
    print(f"Loaded {len(documents)} documents")
    return documents

def chunk_documents(documents):
    """Split documents into smaller chunks."""
    splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
    chunks = splitter.split_documents(documents)
    print(f"Created {len(chunks)} chunks")
    return chunks

if __name__ == "__main__":
    docs = load_documents("data/raw/policies")
    chunks = chunk_documents(docs)
    for i, chunk in enumerate(chunks):      #printing each chunk to visually verify the splitting
        print(f"\n----Chunk {i+1}-----")
        print(chunk.page_content)  
