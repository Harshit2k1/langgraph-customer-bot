from pypdf import PdfReader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from src.config import Config
import os

class DocumentProcessor:
    """Handles PDF loading, text extraction, and chunking"""
    
    def __init__(self):
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=Config.CHUNK_SIZE,
            chunk_overlap=Config.CHUNK_OVERLAP,
            length_function=len,
            separators=["\n\n", "\n", ". ", " ", ""]
        )
    
    def load_pdf(self, pdf_path):
        """Extract text from PDF file page by page"""
        if not os.path.exists(pdf_path):
            print(f"PDF file not found: {pdf_path}")
            return None
        
        try:
            reader = PdfReader(pdf_path)
            
            if len(reader.pages) == 0:
                print(f"PDF has no pages: {pdf_path}")
                return None
            
            text_by_page = []
            filename = os.path.basename(pdf_path)
            
            for page_num, page in enumerate(reader.pages, start=1):
                text = page.extract_text()
                
                if text and text.strip():
                    text_by_page.append({
                        'text': text.strip(),
                        'page': page_num,
                        'source': filename
                    })
            
            print(f"Extracted text from {len(text_by_page)} pages in {filename}")
            return text_by_page
            
        except Exception as e:
            print(f"Error loading PDF {pdf_path}: {e}")
            return None
    
    def chunk_document(self, pages_data):
        """Split document pages into smaller chunks with metadata"""
        if not pages_data:
            return []
        
        chunks = []
        
        for page_data in pages_data:
            page_text = page_data['text']
            
            if not page_text or not page_text.strip():
                continue
            
            page_chunks = self.text_splitter.split_text(page_text)
            
            for chunk_idx, chunk in enumerate(page_chunks):
                if chunk and chunk.strip():
                    chunks.append({
                        'text': chunk.strip(),
                        'metadata': {
                            'source': page_data['source'],
                            'page': page_data['page'],
                            'chunk_index': chunk_idx
                        }
                    })
        
        return chunks
    
    def process_pdf(self, pdf_path):
        """Complete pipeline: load PDF and chunk into searchable segments"""
        pages = self.load_pdf(pdf_path)
        
        if not pages:
            return None
        
        chunks = self.chunk_document(pages)
        
        if not chunks:
            print(f"No chunks generated from {pdf_path}")
            return None
        
        print(f"Generated {len(chunks)} chunks from {pdf_path}")
        return chunks
    
    def process_directory(self, directory_path):
        """Process all PDF files in a directory"""
        if not os.path.isdir(directory_path):
            print(f"Directory not found: {directory_path}")
            return []
        
        all_chunks = []
        pdf_files = [f for f in os.listdir(directory_path) if f.lower().endswith('.pdf')]
        
        if not pdf_files:
            print(f"No PDF files found in {directory_path}")
            return []
        
        print(f"Found {len(pdf_files)} PDF files to process")
        
        for pdf_file in pdf_files:
            pdf_path = os.path.join(directory_path, pdf_file)
            chunks = self.process_pdf(pdf_path)
            
            if chunks:
                all_chunks.extend(chunks)
        
        return all_chunks
    
    def get_chunk_preview(self, chunk, max_length=100):
        """Get a preview of chunk text for debugging"""
        text = chunk.get('text', '')
        if len(text) <= max_length:
            return text
        return text[:max_length] + "..."
