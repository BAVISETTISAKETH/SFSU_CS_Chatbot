from bs4 import BeautifulSoup
import re
import torch
from langchain_core.documents import Document

class CSDataProcessor:
    """Specialized processor for CS department data."""
    
    @staticmethod
    def process_course_data(text):
        """Extract and format course information from text."""
        if not text:
            return text
            
        # Extract course codes and descriptions
        course_pattern = re.compile(r'(CS[C]?\s*\d{3}[A-Z]?)\s*[:-]?\s*([^\.]+)')
        matches = course_pattern.findall(text)
        
        if matches:
            formatted_courses = []
            for course_code, description in matches:
                formatted_courses.append(f"Course: {course_code.strip()} - {description.strip()}")
            
            return "\n".join(formatted_courses)
        
        return text
    
    @staticmethod
    def process_faculty_data(text):
        """Extract and format faculty information from text."""
        if not text:
            return text
            
        if "faculty" in text.lower() or "professor" in text.lower():
            # Look for patterns like "Dr. Name" or "Professor Name"
            faculty_pattern = re.compile(r'(Dr\.|Professor|Prof\.|Faculty)\s+([A-Z][a-z]+\s+[A-Z][a-z]+)')
            matches = faculty_pattern.findall(text)
            
            if matches:
                formatted_faculty = []
                for title, name in matches:
                    formatted_faculty.append(f"Faculty: {title} {name}")
                
                return "\n".join(formatted_faculty)
        
        return text
    
    @staticmethod
    def enhance_document(document):
        """Apply specialized processing to a document based on content."""
        content = document.page_content
        metadata = document.metadata
        
        # Detect document type based on content keywords
        if any(keyword in content.lower() for keyword in ["course", "prerequisite", "requirement", "major"]):
            enhanced_content = CSDataProcessor.process_course_data(content)
            if enhanced_content != content:
                document.page_content = enhanced_content
                document.metadata["document_type"] = "course_info"
        
        elif any(keyword in content.lower() for keyword in ["faculty", "professor", "staff", "chair", "dean"]):
            enhanced_content = CSDataProcessor.process_faculty_data(content)
            if enhanced_content != content:
                document.page_content = enhanced_content
                document.metadata["document_type"] = "faculty_info"
        
        return document
    
    @staticmethod
    def batch_enhance_documents(documents, batch_size=1000):
        """Process documents in batches to improve performance."""
        enhanced_documents = []
        total_docs = len(documents)
        
        print(f"Enhancing {total_docs} documents with specialized processing...")
        for i in range(0, total_docs, batch_size):
            end_idx = min(i + batch_size, total_docs)
            batch = documents[i:end_idx]
            
            print(f"Processing batch {i//batch_size + 1}: documents {i} to {end_idx-1}")
            for doc in batch:
                enhanced_doc = CSDataProcessor.enhance_document(doc)
                enhanced_documents.append(enhanced_doc)
        
        return enhanced_documents

class TextCleaningUtils:
    """Utilities for cleaning and processing text."""
    
    @staticmethod
    def clean_html(html_content, advanced=True):
        """Clean HTML content with advanced options."""
        if not html_content or not isinstance(html_content, str):
            return ""
        
        try:
            soup = BeautifulSoup(html_content, 'html.parser')
            
            # Remove script, style, and navigation elements
            for element in soup(['script', 'style', 'nav', 'footer', 'header']):
                element.extract()
            
            if advanced:
                # Handle lists to maintain structure
                for ul in soup.find_all('ul'):
                    for li in ul.find_all('li'):
                        li.insert_before('• ')
                    ul.insert_after('\n')
                
                # Make headings stand out
                for heading in soup.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6']):
                    heading_text = heading.get_text()
                    heading.replace_with(f"\n{heading_text}\n")
                
                # Handle tables
                for table in soup.find_all('table'):
                    # Create a simplified text representation of the table
                    rows_text = []
                    for tr in table.find_all('tr'):
                        cells = [cell.get_text(strip=True) for cell in tr.find_all(['td', 'th'])]
                        rows_text.append(' | '.join(cells))
                    table_text = '\n'.join(rows_text)
                    table.replace_with(f"\n{table_text}\n")
            
            # Get text with proper spacing
            text = soup.get_text(separator=' ', strip=True)
            
            # Normalize whitespace
            text = re.sub(r'\s+', ' ', text).strip()
            
            # Clean up any remaining HTML entities
            text = text.replace('&nbsp;', ' ').replace('&amp;', '&').replace('&lt;', '<').replace('&gt;', '>')
            
            return text
        except Exception as e:
            print(f"Error cleaning HTML: {e}")
            return html_content  # Return original if parsing fails
    
    @staticmethod
    def extract_course_info(text):
        """Extract structured course information."""
        course_info = {}
        
        # Try to find course code
        code_match = re.search(r'(CS[C]?\s*\d{3}[A-Z]?)', text)
        if code_match:
            course_info['code'] = code_match.group(1).strip()
        
        # Try to find title
        title_match = re.search(r'(?:titled|called|named)[:\s]+([^\.]+)', text, re.IGNORECASE)
        if title_match:
            course_info['title'] = title_match.group(1).strip()
        
        # Try to find units/credits
        units_match = re.search(r'(\d+)\s+(?:unit|credit)', text, re.IGNORECASE)
        if units_match:
            course_info['units'] = units_match.group(1)
        
        # Try to find prerequisites
        prereq_match = re.search(r'(?:prerequisite|prereq)[s]?[:\s]+([^\.]+)', text, re.IGNORECASE)
        if prereq_match:
            course_info['prerequisites'] = prereq_match.group(1).strip()
        
        return course_info

# Utility function to convert any document processing to utilize GPU if available
def apply_gpu_acceleration():
    """Configure torch to use GPU if available."""
    if torch.cuda.is_available():
        # Set default tensor type to CUDA
        torch.set_default_tensor_type('torch.cuda.FloatTensor')
        return True
    return False