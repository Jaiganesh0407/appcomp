#!/bin/bash

echo "🧠 Brain Tumor MRI Scanner - Demo Version"
echo "=========================================="

# Add local bin to PATH
export PATH="$HOME/.local/bin:$PATH"

# Check if required packages are available
echo "🔍 Checking requirements..."

check_import() {
    python3 -c "import $1" 2>/dev/null
    return $?
}

required_packages=("numpy" "cv2" "streamlit" "plotly")
missing_packages=()

for package in "${required_packages[@]}"; do
    if check_import "$package"; then
        echo "✅ $package is available"
    else
        echo "❌ $package is missing"
        missing_packages+=("$package")
    fi
done

if [ ${#missing_packages[@]} -gt 0 ]; then
    echo ""
    echo "⚠️  Some required packages are missing. Please run:"
    echo "pip3 install --user --break-system-packages numpy opencv-python pillow streamlit plotly"
    echo ""
    read -p "Would you like to install them now? (y/n): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        pip3 install --user --break-system-packages numpy opencv-python pillow streamlit plotly
    else
        echo "❌ Cannot proceed without required packages."
        exit 1
    fi
fi

echo ""
echo "🚀 Launching Brain Tumor Detection Demo..."
echo "📱 Open your browser to the URL shown below"
echo "🔄 Press Ctrl+C to stop the server"
echo ""

# Launch the demo
python3 -m streamlit run brain_tumor_demo.py --server.port 8501 --server.address 0.0.0.0