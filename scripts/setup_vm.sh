#!/bin/bash
# VM Setup Script - Run this on the GCP VM
# Installs all dependencies for LeanAgent extraction

set -e

echo "========================================="
echo "Setting up VM for Lean Theorem Extraction"
echo "========================================="

# Update system
echo "Step 1/8: Updating system packages..."
sudo apt-get update -y
sudo apt-get upgrade -y

# Install Python 3.10
echo "Step 2/8: Installing Python 3.10..."
sudo apt-get install -y software-properties-common
sudo add-apt-repository -y ppa:deadsnakes/ppa
sudo apt-get update -y
sudo apt-get install -y python3.10 python3.10-venv python3.10-dev python3-pip

# Install system dependencies
echo "Step 3/8: Installing system dependencies..."
sudo apt-get install -y git unzip wget curl build-essential

# Install gdown for Google Drive downloads
echo "Step 4/8: Installing gdown..."
pip3 install gdown

# Clone LeanAgent repo
echo "Step 5/8: Cloning LeanAgent repository..."
cd ~
git clone https://github.com/lean-dojo/LeanAgent.git
cd LeanAgent

# Create virtual environment
echo "Step 6/8: Creating Python virtual environment..."
python3.10 -m venv venv
source venv/bin/activate

# Install LeanAgent with all dependencies
echo "Step 7/8: Installing LeanAgent and dependencies..."
pip install --upgrade pip
pip install -e .

# Create directories and set environment variables
echo "Step 8/8: Setting up directories and environment..."
mkdir -p ~/LeanAgent/RAID/data
mkdir -p ~/repos_cache

# Set RAID_DIR environment variable
echo 'export RAID_DIR=~/LeanAgent/RAID' >> ~/.bashrc
export RAID_DIR=~/LeanAgent/RAID

echo ""
echo "========================================="
echo "✅ VM Setup Complete!"
echo "========================================="
echo ""
echo "Environment configured:"
echo "  - Python 3.10 installed"
echo "  - LeanAgent installed with all dependencies"
echo "  - RAID_DIR set to ~/LeanAgent/RAID"
echo "  - Virtual environment at ~/LeanAgent/venv"
echo ""
echo "Next steps:"
echo "  1. Download repos from Google Drive"
echo "  2. Run extraction script"
echo ""
