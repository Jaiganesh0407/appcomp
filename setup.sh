#!/bin/bash

echo "🧠 Brain Tumor Detection System Setup"
echo "======================================"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}📦 Setting up Brain Tumor Detection System...${NC}"

# Check Python version
python_version=$(python3 -c 'import sys; print(".".join(map(str, sys.version_info[:2])))')
echo -e "${BLUE}🐍 Python version: ${python_version}${NC}"

# Install packages with user flag
echo -e "${YELLOW}📥 Installing dependencies...${NC}"

# Try different installation methods
if command -v pipx &> /dev/null; then
    echo -e "${GREEN}Using pipx for installation...${NC}"
    pipx install streamlit
    pip3 install --user tensorflow numpy opencv-python pillow matplotlib scikit-learn plotly seaborn
elif pip3 install --user --break-system-packages tensorflow numpy opencv-python pillow matplotlib scikit-learn streamlit plotly seaborn 2>/dev/null; then
    echo -e "${GREEN}✅ Packages installed successfully with --break-system-packages${NC}"
elif pip3 install --user tensorflow numpy opencv-python pillow matplotlib scikit-learn streamlit plotly seaborn 2>/dev/null; then
    echo -e "${GREEN}✅ Packages installed successfully with --user${NC}"
else
    echo -e "${RED}❌ Failed to install packages. Trying alternative approach...${NC}"
    echo -e "${YELLOW}Installing minimal versions...${NC}"
    pip3 install --user numpy pillow matplotlib streamlit plotly
    echo -e "${YELLOW}⚠️  TensorFlow may need manual installation${NC}"
    echo -e "${YELLOW}Try: pip3 install --user tensorflow-cpu${NC}"
fi

# Check installations
echo -e "\n${BLUE}🔍 Verifying installations...${NC}"

check_package() {
    if python3 -c "import $1" 2>/dev/null; then
        echo -e "${GREEN}✅ $1${NC}"
        return 0
    else
        echo -e "${RED}❌ $1${NC}"
        return 1
    fi
}

packages=("numpy" "cv2" "PIL" "matplotlib" "streamlit" "plotly")
failed_packages=()

for package in "${packages[@]}"; do
    if ! check_package "$package"; then
        failed_packages+=("$package")
    fi
done

# Special check for TensorFlow
if python3 -c "import tensorflow as tf; print('TensorFlow version:', tf.__version__)" 2>/dev/null; then
    echo -e "${GREEN}✅ tensorflow${NC}"
else
    echo -e "${RED}❌ tensorflow${NC}"
    failed_packages+=("tensorflow")
fi

# Summary
echo -e "\n${BLUE}📋 Setup Summary${NC}"
echo "=================="

if [ ${#failed_packages[@]} -eq 0 ]; then
    echo -e "${GREEN}🎉 All packages installed successfully!${NC}"
    echo -e "\n${GREEN}🚀 You can now run:${NC}"
    echo -e "${YELLOW}   streamlit run brain_tumor_detector.py${NC}"
    echo -e "${YELLOW}   python3 brain_tumor_cli.py --help${NC}"
else
    echo -e "${RED}⚠️  Some packages failed to install:${NC}"
    for package in "${failed_packages[@]}"; do
        echo -e "${RED}   - $package${NC}"
    done
    echo -e "\n${YELLOW}💡 Manual installation options:${NC}"
    echo -e "${YELLOW}   pip3 install --user tensorflow-cpu  # For CPU-only TensorFlow${NC}"
    echo -e "${YELLOW}   pip3 install --user opencv-python-headless  # Alternative OpenCV${NC}"
fi

echo -e "\n${BLUE}📖 Next Steps:${NC}"
echo "1. Run the web interface: streamlit run brain_tumor_detector.py"
echo "2. Or use CLI: python3 brain_tumor_cli.py image.jpg"
echo "3. Check README.md for detailed usage instructions"

echo -e "\n${RED}⚠️  Medical Disclaimer:${NC}"
echo -e "${RED}This tool is for educational purposes only.${NC}"
echo -e "${RED}Always consult healthcare professionals for medical advice.${NC}"