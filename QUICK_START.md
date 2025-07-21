# 🚀 Quick Start Guide - Brain Tumor MRI Scanner

## Instant Demo (Recommended)

**Get started in 30 seconds:**

```bash
# Make script executable and run
chmod +x run_demo.sh
./run_demo.sh
```

That's it! The demo will:
- ✅ Check dependencies
- ✅ Install missing packages automatically  
- ✅ Launch the web interface
- ✅ Open on `http://localhost:8501`

## What You Get

🧠 **4 Tumor Types Detection:**
- Glioma (High severity)
- Meningioma (Low-Moderate severity)  
- Pituitary Tumor (Low-Moderate severity)
- No Tumor (Healthy)

📊 **Features:**
- Upload any image format (PNG, JPG, etc.)
- Generate sample MRI images for testing
- Interactive pie charts and bar graphs
- Confidence percentages for each tumor type
- Detailed medical information
- Export results as text files

## Demo vs Full Version

| Feature | Demo Version | Full Version |
|---------|-------------|--------------|
| **Dependencies** | Light (no TensorFlow) | Full (with TensorFlow) |
| **Predictions** | Simulated realistic | Real CNN model |
| **Interface** | Identical | Identical |
| **Setup Time** | 30 seconds | 2-3 minutes |
| **File Size** | Small | Large |
| **Accuracy** | Demo purposes | 95%+ (simulated) |

## Manual Setup (If Script Fails)

```bash
# Install dependencies
pip3 install --user --break-system-packages numpy opencv-python pillow streamlit plotly

# Add to PATH
export PATH="$HOME/.local/bin:$PATH"

# Run demo
streamlit run brain_tumor_demo.py
```

## Command Line Version

```bash
# For simple output
python3 brain_tumor_cli.py image.jpg

# For detailed analysis  
python3 brain_tumor_cli.py image.jpg --detailed

# Save results to file
python3 brain_tumor_cli.py image.jpg --output results.txt
```

## Testing

1. **Run the demo**
2. **Generate sample images** using the built-in buttons
3. **Upload your own MRI scans**
4. **Analyze results** with interactive charts

## Troubleshooting

**Common Issues:**
- **Permission denied**: Run `chmod +x run_demo.sh`
- **Module not found**: Run the manual setup commands above
- **Port in use**: Change port with `--server.port 8502`

## Important Notes

⚠️ **Medical Disclaimer**: This is for educational purposes only. Never use for actual medical diagnosis. Always consult healthcare professionals.

🔬 **Demo Mode**: The demo uses simulated predictions to showcase the interface. The full version would use a trained CNN model.

📱 **Browser**: Works best in Chrome, Firefox, or Safari. Open `http://localhost:8501` after launching.

---

**Need help?** Check the full README.md for detailed documentation.