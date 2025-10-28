import os
import sys
import time
import shutil
import torch

def setup_environment():
    """Set up the environment and check dependencies."""
    # Create necessary directories
    os.makedirs("./data", exist_ok=True)
    os.makedirs("./vector_db", exist_ok=True)
    
    # Check for GPU
    if torch.cuda.is_available():
        print(f"GPU available: {torch.cuda.get_device_name(0)}")
    else:
        print("WARNING: No GPU detected. Processing will be much slower.")
    
    # Check required packages
    try:
        import sentence_transformers
        import langchain_chroma
        import transformers
        import beautifulsoup4
        print("All required packages are installed.")
    except ImportError as e:
        print(f"Missing package: {e}")
        print("Installing required packages...")
        os.system("pip install sentence-transformers langchain-chroma transformers beautifulsoup4")

def prepare_data():
    """Run the data preparation script."""
    print("Preparing RAG data...")
    start_time = time.time()
    os.system("python prepare_data.py")
    end_time = time.time()
    print(f"Data preparation completed in {(end_time - start_time)/60:.2f} minutes")

def test_system():
    """Test the RAG system."""
    print("Testing the RAG system...")
    start_time = time.time()
    os.system("python test_rag.py")
    end_time = time.time()
    print(f"Testing completed in {(end_time - start_time)/60:.2f} minutes")

def run_server():
    """Start the API server."""
    print("Starting API server...")
    os.system("python app.py")

def clean_start():
    """Remove existing vector database and start fresh."""
    if os.path.exists("./vector_db"):
        print("Removing existing vector database...")
        shutil.rmtree("./vector_db")
    
    print("Starting fresh data preparation...")
    prepare_data()

def process_subset(size=5000):
    """Process only a subset of documents for quick testing."""
    # Backup current prepare_data.py
    if os.path.exists("prepare_data.py.backup"):
        os.remove("prepare_data.py.backup")
    shutil.copy("prepare_data.py", "prepare_data.py.backup")
    
    # Modify the file to use a subset
    with open("prepare_data.py", "r") as f:
        content = f.read()
    
    # Add subset limitation
    modified_content = content.replace(
        "    chunks = split_documents(documents)",
        f"    print(f\"Using subset of {{min(len(documents), {size})}} documents for testing\")\n    documents = documents[:min(len(documents), {size})]\n    chunks = split_documents(documents)"
    )
    
    with open("prepare_data.py", "w") as f:
        f.write(modified_content)
    
    # Run with subset
    prepare_data()
    
    # Restore original
    os.remove("prepare_data.py")
    os.rename("prepare_data.py.backup", "prepare_data.py")

def main():
    setup_environment()
    
    # Check command line arguments
    if len(sys.argv) > 1:
        if sys.argv[1] == "prepare":
            prepare_data()
        elif sys.argv[1] == "test":
            test_system()
        elif sys.argv[1] == "serve":
            run_server()
        elif sys.argv[1] == "clean":
            clean_start()
        elif sys.argv[1] == "subset":
            size = 5000
            if len(sys.argv) > 2:
                try:
                    size = int(sys.argv[2])
                except ValueError:
                    pass
            process_subset(size)
        else:
            print("Unknown command. Use 'prepare', 'test', 'serve', 'clean', or 'subset [size]'")
    else:
        # Default: run all steps
        prepare_data()
        test_system()
        run_server()

if __name__ == "__main__":
    main()