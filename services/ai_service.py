import os
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import Chroma
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import TextLoader
from langchain.chains import RetrievalQA
from langchain_openai import OpenAI
from core.config import settings

# Initialize OpenAI
import openai
openai.api_key = settings.openai_api_key

# Spa knowledge base
SPA_KNOWLEDGE = """
Spa Services and Information:

Massage Services:
- Swedish Massage: 60 min - $80, 90 min - $120
- Deep Tissue Massage: 60 min - $90, 90 min - $130
- Hot Stone Massage: 75 min - $110
- Aromatherapy Massage: 60 min - $85

Facial Services:
- Classic Facial: 60 min - $75
- Anti-Aging Facial: 75 min - $95
- Acne Treatment Facial: 60 min - $80
- Hydrating Facial: 60 min - $70

Body Treatments:
- Body Scrub: 60 min - $85
- Mud Wrap: 90 min - $120
- Seaweed Wrap: 90 min - $130
- Detox Wrap: 90 min - $140

Spa Policies:
- Cancellation: 24 hours notice required
- Late arrivals: Service time may be reduced
- Gratuity: 18-20% recommended
- Payment: Cash, credit cards, gift certificates accepted
- Age requirement: 18+ for most services, 16+ with parent consent

Spa Amenities:
- Locker rooms with showers
- Robes and slippers provided
- Tea and water available
- Relaxation room
- Free WiFi

Booking Information:
- Online booking available 24/7
- Phone booking: 9 AM - 6 PM daily
- Same-day appointments subject to availability
- Group bookings available with advance notice

Location and Hours:
- Address: 123 Spa Street, Wellness City, WC 12345
- Hours: Monday-Saturday 9 AM - 8 PM, Sunday 10 AM - 6 PM
- Phone: (555) 123-4567
- Email: info@wellnessspa.com

Special Offers:
- First-time client: 20% off any service
- Package deals available
- Monthly membership options
- Gift certificates available
"""

# Global variables for lazy initialization
_embeddings = None
_vectorstore = None
_text_splitter = None

def _get_embeddings():
    """Get embeddings instance (lazy initialization)"""
    global _embeddings
    if _embeddings is None:
        _embeddings = OpenAIEmbeddings(api_key=settings.openai_api_key)
    return _embeddings

def _get_vectorstore():
    """Get vector store instance (lazy initialization)"""
    global _vectorstore
    if _vectorstore is None:
        embeddings = _get_embeddings()
        _vectorstore = Chroma(
            embedding_function=embeddings,
            persist_directory="./chroma_db"
        )
    return _vectorstore

def _get_text_splitter():
    """Get text splitter instance (lazy initialization)"""
    global _text_splitter
    if _text_splitter is None:
        _text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200
        )
    return _text_splitter

def initialize_knowledge_base():
    """Initialize the knowledge base with spa information"""
    try:
        vectorstore = _get_vectorstore()
        
        # Check if knowledge base already exists
        if vectorstore._collection.count() > 0:
            return
        
        # Split the knowledge text into chunks
        text_splitter = _get_text_splitter()
        texts = text_splitter.split_text(SPA_KNOWLEDGE)
        
        # Add texts to vector store
        vectorstore.add_texts(texts)
        vectorstore.persist()
        
    except Exception as e:
        print(f"Error initializing knowledge base: {e}")

def generate_inquiry_response(inquiry_text: str) -> str:
    """Generate AI response for customer inquiries"""
    try:
        # Initialize knowledge base if needed
        initialize_knowledge_base()
        
        # Create retrieval QA chain
        vectorstore = _get_vectorstore()
        qa_chain = RetrievalQA.from_chain_type(
            llm=OpenAI(temperature=0.7, api_key=settings.openai_api_key),
            chain_type="stuff",
            retriever=vectorstore.as_retriever(search_kwargs={"k": 3})
        )
        
        # Generate response
        response = qa_chain.run(
            f"Customer inquiry: {inquiry_text}\n\nPlease provide a helpful, professional response based on our spa services and policies. Be friendly and informative."
        )
        
        return response.strip()
        
    except Exception as e:
        print(f"Error generating inquiry response: {e}")
        return "Thank you for your inquiry. Please contact us directly at (555) 123-4567 for immediate assistance."

def generate_chat_response(message: str, chat_history: list = None) -> str:
    """Generate AI response for chat messages"""
    try:
        # Initialize knowledge base if needed
        initialize_knowledge_base()
        
        # Create context from chat history
        context = ""
        if chat_history:
            context = "Previous conversation:\n" + "\n".join([
                f"User: {msg['user']}\nAssistant: {msg['assistant']}" 
                for msg in chat_history[-3:]  # Last 3 exchanges
            ]) + "\n\n"
        
        # Create retrieval QA chain
        vectorstore = _get_vectorstore()
        qa_chain = RetrievalQA.from_chain_type(
            llm=OpenAI(temperature=0.7, api_key=settings.openai_api_key),
            chain_type="stuff",
            retriever=vectorstore.as_retriever(search_kwargs={"k": 3})
        )
        
        # Generate response
        prompt = f"{context}Current message: {message}\n\nPlease provide a helpful, friendly response about our spa services, booking, or general questions. Be conversational and informative."
        response = qa_chain.run(prompt)
        
        return response.strip()
        
    except Exception as e:
        print(f"Error generating chat response: {e}")
        return "I'm here to help with your spa questions! Please let me know how I can assist you with booking, services, or any other inquiries."
