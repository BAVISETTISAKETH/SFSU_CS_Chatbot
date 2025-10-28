#!/bin/bash
# SFSU Q&A Generation - AWS Setup Script
# Run this on your AWS EC2 instance

echo "=========================================="
echo "SFSU Q&A Generation - AWS Setup"
echo "=========================================="

# Install Ollama
echo "Installing Ollama..."
curl -fsSL https://ollama.com/install.sh | sh

# Start Ollama server
echo "Starting Ollama server..."
nohup ollama serve > ollama.log 2>&1 &
sleep 10

# Pull model
echo "Downloading llama3.2 model (this may take a few minutes)..."
ollama pull llama3.2

# Test
echo "Testing Ollama..."
ollama run llama3.2 "Say OK" --verbose false

# Install Python dependencies
echo "Installing Python dependencies..."
pip install requests python-dotenv --quiet

# Create data directory
mkdir -p data

echo ""
echo "=========================================="
echo "Setup Complete!"
echo "=========================================="
echo ""
echo "Next steps:"
echo "1. Upload your files:"
echo "   From your PC: scp D:\\sfsu-cs-chatbot\\data\\comprehensive_sfsu_crawl.json ubuntu@YOUR_IP:~/data/"
echo "   From your PC: scp D:\\sfsu-cs-chatbot\\generate_qa_with_ollama.py ubuntu@YOUR_IP:~/"
echo ""
echo "2. Run generation:"
echo "   python3 generate_qa_with_ollama.py"
echo ""
echo "=========================================="
