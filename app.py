import streamlit as st
import openai
import PyPDF2
import docx
import os

# Set page configuration
st.set_page_config(page_title="AI Document Translator", page_icon="🌐", layout="wide")

# List of supported languages
LANGUAGES = [
    "Arabic", "Chinese", "English", "French", "German", 
    "Hindi", "Italian", "Japanese", "Korean", "Portuguese", 
    "Russian", "Spanish", "Turkish"
]

def read_document(uploaded_file):
    """Read contents of uploaded document based on file type"""
    try:
        # PDF file handling
        if uploaded_file.name.endswith('.pdf'):
            pdf_reader = PyPDF2.PdfReader(uploaded_file)
            text = ""
            for page in pdf_reader.pages:
                text += page.extract_text()
            return text
        
        # DOCX file handling
        elif uploaded_file.name.endswith('.docx'):
            doc = docx.Document(uploaded_file)
            return "\n".join([paragraph.text for paragraph in doc.paragraphs])
        
        # Plain text file handling
        elif uploaded_file.name.endswith('.txt'):
            return uploaded_file.getvalue().decode('utf-8')
        
        else:
            st.error("Unsupported file type. Please upload PDF, DOCX, or TXT files.")
            return None
    
    except Exception as e:
        st.error(f"Error reading document: {e}")
        return None

def translate_text(text, target_language, api_key):
    """Translate text using OpenAI's GPT-4o"""
    try:
        openai.api_key = api_key
        
        response = openai.ChatCompletion.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": f"You are a professional translator. Translate the following text to {target_language} while preserving the original formatting and meaning."},
                {"role": "user", "content": text}
            ]
        )
        
        return response.choices[0].message['content']
    
    except Exception as e:
        st.error(f"Translation error: {e}")
        return None

def main():
    st.title("🌐 AI Document Translator")
    
    # Sidebar for API Key and Language Selection
    with st.sidebar:
        st.header("Configuration")
        openai_api_key = st.text_input("OpenAI API Key", type="password")
        target_language = st.selectbox("Select Target Language", LANGUAGES)
    
    # File upload
    uploaded_file = st.file_uploader(
        "Upload Document", 
        type=['pdf', 'docx', 'txt'],
        help="Supported formats: PDF, DOCX, TXT"
    )
    
    # Translation process
    if uploaded_file and openai_api_key:
        # Read document
        document_text = read_document(uploaded_file)
        
        if document_text:
            # Preview original text
            st.subheader("Original Text Preview")
            st.text_area("Preview", document_text, height=200)
            
            # Translate button
            if st.button("Translate Document"):
                with st.spinner(f"Translating to {target_language}..."):
                    translated_text = translate_text(document_text, target_language, openai_api_key)
                
                if translated_text:
                    # Display translated text
                    st.subheader(f"Translated Text ({target_language})")
                    st.text_area("Translation", translated_text, height=300)
                    
                    # Download translated text
                    st.download_button(
                        label="Download Translated Text",
                        data=translated_text,
                        file_name=f"translated_{uploaded_file.name}",
                        mime="text/plain"
                    )
    
    # Error handling for missing inputs
    elif not openai_api_key:
        st.warning("Please enter your OpenAI API Key in the sidebar.")
    
    # Footer
    st.markdown("---")
    st.markdown("*Powered by OpenAI's GPT-4o ✨*")

if __name__ == "__main__":
    main()