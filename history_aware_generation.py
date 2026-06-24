from dotenv import load_dotenv
from langchain_chroma import Chroma
from langchain_core.messages import HumanMessage, SystemMessage, AIMessage
from langchain_ollama import ChatOllama
from langchain_huggingface import HuggingFaceEmbeddings
# Load environment variables
load_dotenv()

# Connect to your document database
def initialize_db():
    persistent_directory = "db/chroma_db"

    embeddings = HuggingFaceEmbeddings(
        model_name="sentence-transformers/all-mpnet-base-v2"
    )

    db = Chroma(
        persist_directory=persistent_directory,
        embedding_function=embeddings
    )

    return db
db=initialize_db()
# Set up AI model
model = ChatOllama(
    model="llama3.2:3b",
    temperature=0
)

# Store our conversation as messages
chat_history = []

def ask_question(user_question):
    print(f"\n--- You asked: {user_question} ---")
    
    # Step 1: Make the question clear using conversation history
    if chat_history:
        # Ask AI to make the question standalone
        messages = [
            SystemMessage(content="""
Given the chat history, rewrite the user's latest question as a standalone search query.

Rules:
1. Return ONLY the rewritten question.
2. Do NOT answer the question.
3. Do NOT add explanations.
4. Keep it short and searchable.
""")        ] + chat_history + [
            HumanMessage(content=f"New question: {user_question}")
        ]
        
        result = model.invoke(messages)
        search_question = result.content.strip()
        print(f"Searching for: {search_question}")
    else:
        search_question = user_question
    
    # Step 2: Find relevant documents
    retriever = db.as_retriever(
    search_type="similarity",
    search_kwargs={"k": 8}
)
    docs = retriever.invoke(search_question)
    
    docs = sorted(
    docs,
    key=lambda d: len(d.page_content),
    reverse=True
)
    
    print(f"Found {len(docs)} relevant documents:")
    for i, doc in enumerate(docs, 1):
        # Show first 2 lines of each document
        lines = doc.page_content.split('\n')[:2]
        preview = '\n'.join(lines)
        print(f"  Doc {i}: {preview}...")
    
    # Step 3: Create final prompt
    document_context = ""

    for i, doc in enumerate(docs, 1):
        document_context += f"""
    DOCUMENT {i}:
    {doc.page_content}

    ----------------------------------------
    """

    combined_input = f"""
    Question:
    {user_question}

    Retrieved Documents:

    {document_context}

    Instructions:
    1. Answer ONLY using the retrieved documents.
    2. Use the document that directly answers the question.
    3. If multiple documents are relevant, combine their information.
    4. Do NOT use outside knowledge.
    5. If the answer is not present in the documents, say:
    "I don't have enough information in the provided documents."
    6. For comparison questions, compare the relevant sections explicitly.
    7. For follow-up questions, use the context implied by the question.

    Answer:
    """
    
    # Step 4: Get the answer
    messages = [
        SystemMessage(content="You are a helpful assistant that answers questions based on provided documents and conversation history."),
    ] + chat_history + [
        HumanMessage(content=combined_input)
    ]
    
    result = model.invoke(messages)
    answer = result.content
    
    # Step 5: Remember this conversation
    chat_history.append(HumanMessage(content=user_question))
    chat_history.append(AIMessage(content=answer))
    
    print(f"Answer: {answer}")
    return answer

# Simple chat loop
def start_chat():
    print("Ask me questions! Type 'quit' to exit.")
    
    while True:
        question = input("\nYour question: ")
        
        if question.lower() == 'quit':
            print("Goodbye!")
            break
            
        ask_question(question)
# Function for Flask frontend
def get_answer(question):
    return ask_question(question)

if __name__ == "__main__":
    start_chat()