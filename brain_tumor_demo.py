import numpy as np
import cv2
from PIL import Image
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import matplotlib.pyplot as plt
import random
from io import BytesIO

# Set page config
st.set_page_config(
    page_title="Brain Tumor MRI Scanner (Demo)",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded"
)

class BrainTumorDemo:
    def __init__(self):
        self.class_names = ['Glioma', 'Meningioma', 'No Tumor', 'Pituitary']
        self.input_shape = (224, 224, 3)
    
    def preprocess_image(self, image):
        """Preprocess the input image"""
        # Convert PIL Image to numpy array
        if isinstance(image, Image.Image):
            image = np.array(image)
        
        # Convert to RGB if needed
        if len(image.shape) == 3 and image.shape[2] == 4:
            image = cv2.cvtColor(image, cv2.COLOR_RGBA2RGB)
        elif len(image.shape) == 3 and image.shape[2] == 1:
            image = cv2.cvtColor(image, cv2.COLOR_GRAY2RGB)
        elif len(image.shape) == 2:
            image = cv2.cvtColor(image, cv2.COLOR_GRAY2RGB)
        
        # Resize to model input size
        image = cv2.resize(image, (224, 224))
        
        # Normalize pixel values
        image = image.astype(np.float32) / 255.0
        
        return image
    
    def predict(self, image):
        """Make simulated prediction on preprocessed image"""
        processed_image = self.preprocess_image(image)
        
        # Simulate realistic predictions based on image characteristics
        # This creates more realistic-looking probabilities
        
        # Calculate image features for more realistic simulation
        gray = cv2.cvtColor((processed_image * 255).astype(np.uint8), cv2.COLOR_RGB2GRAY)
        brightness = np.mean(gray)
        contrast = np.std(gray)
        
        # Create base probabilities with some randomness
        base_probs = np.random.dirichlet([1, 1, 1, 1])  # Creates probabilities that sum to 1
        
        # Adjust probabilities based on image characteristics for realism
        if brightness < 0.3:  # Dark images might suggest tumors
            base_probs[0] *= 1.5  # Increase Glioma probability
            base_probs[2] *= 0.7  # Decrease No Tumor probability
        elif brightness > 0.7:  # Bright images might be normal
            base_probs[2] *= 1.8  # Increase No Tumor probability
            base_probs[0] *= 0.6  # Decrease Glioma probability
        
        # Normalize to ensure they sum to 1
        probabilities = base_probs / np.sum(base_probs)
        
        # Get predicted class
        predicted_class_idx = np.argmax(probabilities)
        predicted_class = self.class_names[predicted_class_idx]
        confidence = probabilities[predicted_class_idx] * 100
        
        # Create results dictionary
        results = {
            'predicted_class': predicted_class,
            'confidence': confidence,
            'all_probabilities': {self.class_names[i]: prob * 100 for i, prob in enumerate(probabilities)}
        }
        
        return results

def create_visualization(results):
    """Create visualization for the results"""
    # Pie chart for probability distribution
    fig_pie = px.pie(
        values=list(results['all_probabilities'].values()),
        names=list(results['all_probabilities'].keys()),
        title="Tumor Classification Probabilities",
        color_discrete_sequence=px.colors.qualitative.Set3
    )
    
    # Bar chart for probabilities
    fig_bar = px.bar(
        x=list(results['all_probabilities'].keys()),
        y=list(results['all_probabilities'].values()),
        title="Classification Confidence Scores",
        labels={'x': 'Tumor Type', 'y': 'Confidence (%)'},
        color=list(results['all_probabilities'].values()),
        color_continuous_scale='Viridis'
    )
    
    return fig_pie, fig_bar

def get_tumor_info(tumor_type):
    """Get detailed information about each tumor type"""
    tumor_info = {
        'Glioma': {
            'description': 'Gliomas are tumors that arise from glial cells in the brain. They are the most common type of primary brain tumor.',
            'severity': 'High',
            'treatment': 'Surgery, radiation therapy, chemotherapy',
            'prognosis': 'Varies by grade and subtype'
        },
        'Meningioma': {
            'description': 'Meningiomas are tumors that develop from the meninges, the membranes surrounding the brain and spinal cord.',
            'severity': 'Low to Moderate',
            'treatment': 'Surgery, radiation therapy for aggressive types',
            'prognosis': 'Generally good, most are benign'
        },
        'Pituitary': {
            'description': 'Pituitary tumors develop in the pituitary gland, which controls hormone production.',
            'severity': 'Low to Moderate',
            'treatment': 'Medication, surgery, radiation therapy',
            'prognosis': 'Generally good with appropriate treatment'
        },
        'No Tumor': {
            'description': 'No tumor detected in the MRI scan.',
            'severity': 'None',
            'treatment': 'No treatment required',
            'prognosis': 'Excellent'
        }
    }
    
    return tumor_info.get(tumor_type, {})

def main():
    # Initialize the model
    if 'model' not in st.session_state:
        st.session_state.model = BrainTumorDemo()
    
    # Header
    st.title("🧠 AI Brain Tumor MRI Scanner (Demo)")
    st.markdown("### Advanced CNN-based Brain Tumor Detection System")
    st.markdown("Upload an MRI scan to get instant tumor classification with confidence scores.")
    
    # Demo notice
    st.info("🚀 **DEMO VERSION**: This version uses simulated predictions for demonstration. The interface and features are identical to the full version.")
    
    # Sidebar
    st.sidebar.header("📋 Model Information")
    st.sidebar.info("""
    **Model Architecture:** Deep CNN
    **Input Size:** 224x224x3
    **Classes:** 4 types
    - Glioma
    - Meningioma  
    - Pituitary Tumor
    - No Tumor
    
    **Demo Mode:** Simulated predictions
    """)
    
    st.sidebar.markdown("### 🎯 Demo Features")
    st.sidebar.success("""
    ✅ Image upload & preprocessing
    ✅ Realistic simulated predictions
    ✅ Interactive visualizations
    ✅ Detailed tumor information
    ✅ Medical disclaimers
    ✅ Export functionality
    """)
    
    # Main content
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.header("📤 Upload MRI Image")
        uploaded_file = st.file_uploader(
            "Choose an MRI scan image...",
            type=['png', 'jpg', 'jpeg', 'bmp', 'tiff'],
            help="Upload a brain MRI scan image for tumor detection"
        )
        
        # Sample images section
        st.markdown("### 📸 Try Sample Images")
        sample_col1, sample_col2 = st.columns(2)
        
        with sample_col1:
            if st.button("🧠 Generate Sample Brain MRI"):
                # Create a sample brain MRI-like image
                sample_img = np.random.randint(20, 200, (224, 224, 3), dtype=np.uint8)
                # Add some structure to make it look more brain-like
                center = (112, 112)
                cv2.circle(sample_img, center, 80, (150, 150, 150), -1)
                cv2.circle(sample_img, center, 60, (100, 100, 100), -1)
                
                st.session_state.sample_image = Image.fromarray(sample_img)
                st.session_state.use_sample = True
        
        with sample_col2:
            if st.button("🔬 Generate Tumor Sample"):
                # Create a sample with tumor-like features
                sample_img = np.random.randint(30, 180, (224, 224, 3), dtype=np.uint8)
                center = (112, 112)
                cv2.circle(sample_img, center, 70, (120, 120, 120), -1)
                # Add bright spot (tumor-like)
                cv2.circle(sample_img, (90, 90), 20, (200, 200, 200), -1)
                
                st.session_state.sample_image = Image.fromarray(sample_img)
                st.session_state.use_sample = True
        
        # Display image
        if uploaded_file is not None:
            image = Image.open(uploaded_file)
            st.image(image, caption="Uploaded MRI Scan", use_column_width=True)
            st.session_state.use_sample = False
        elif hasattr(st.session_state, 'use_sample') and st.session_state.use_sample:
            image = st.session_state.sample_image
            st.image(image, caption="Sample MRI Scan", use_column_width=True)
        else:
            image = None
        
        # Analysis button
        if image is not None:
            if st.button("🔍 Analyze MRI Scan", type="primary"):
                with st.spinner('Analyzing MRI scan...'):
                    # Make prediction
                    results = st.session_state.model.predict(image)
                    
                    # Store results in session state
                    st.session_state.results = results
                    st.session_state.analyzed = True
    
    with col2:
        st.header("📊 Analysis Results")
        
        if hasattr(st.session_state, 'analyzed') and st.session_state.analyzed:
            results = st.session_state.results
            
            # Display main result
            st.success(f"Analysis Complete!")
            
            # Result metrics
            col2_1, col2_2 = st.columns(2)
            with col2_1:
                st.metric(
                    label="Detected Tumor Type",
                    value=results['predicted_class'],
                    delta=f"{results['confidence']:.1f}% confidence"
                )
            
            with col2_2:
                # Color code based on tumor type
                if results['predicted_class'] == 'No Tumor':
                    st.success("✅ No Tumor Detected")
                else:
                    st.warning(f"⚠️ {results['predicted_class']} Detected")
            
            # Detailed tumor information
            tumor_info = get_tumor_info(results['predicted_class'])
            if tumor_info:
                st.subheader("📋 Tumor Information")
                st.write(f"**Description:** {tumor_info['description']}")
                st.write(f"**Severity Level:** {tumor_info['severity']}")
                st.write(f"**Treatment Options:** {tumor_info['treatment']}")
                st.write(f"**Prognosis:** {tumor_info['prognosis']}")
        else:
            st.info("Upload an MRI image and click 'Analyze' to see results here.")
    
    # Visualization section
    if hasattr(st.session_state, 'analyzed') and st.session_state.analyzed:
        st.header("📈 Detailed Analysis")
        
        # Create visualizations
        fig_pie, fig_bar = create_visualization(st.session_state.results)
        
        col3, col4 = st.columns(2)
        with col3:
            st.plotly_chart(fig_pie, use_container_width=True)
        
        with col4:
            st.plotly_chart(fig_bar, use_container_width=True)
        
        # Confidence table
        st.subheader("🎯 Classification Scores")
        confidence_data = []
        for tumor_type, confidence in st.session_state.results['all_probabilities'].items():
            confidence_data.append({
                'Tumor Type': tumor_type,
                'Confidence (%)': f"{confidence:.2f}%",
                'Status': '✅ Detected' if tumor_type == st.session_state.results['predicted_class'] else '❌'
            })
        
        st.table(confidence_data)
        
        # Export results
        st.subheader("💾 Export Results")
        results_text = f"""
Brain Tumor Detection Results
=============================

Predicted Class: {st.session_state.results['predicted_class']}
Confidence: {st.session_state.results['confidence']:.2f}%

All Probabilities:
{chr(10).join([f"  {tumor}: {prob:.2f}%" for tumor, prob in st.session_state.results['all_probabilities'].items()])}

Tumor Information:
{tumor_info['description']}
Treatment: {tumor_info['treatment']}
Prognosis: {tumor_info['prognosis']}
        """
        
        st.download_button(
            label="📄 Download Results as Text",
            data=results_text,
            file_name="brain_tumor_analysis_results.txt",
            mime="text/plain"
        )
    
    # Footer
    st.markdown("---")
    st.markdown("### ⚠️ Medical Disclaimer")
    st.warning("""
    This AI tool is for educational and research purposes only. 
    **DO NOT** use this as a substitute for professional medical diagnosis. 
    Always consult with qualified healthcare professionals for medical advice.
    """)
    
    # Technical details in expander
    with st.expander("🔧 Technical Details"):
        st.markdown("""
        **Demo Model Features:**
        - Image preprocessing: Resize to 224x224, normalization
        - Simulated CNN predictions with realistic probability distributions
        - 4-class classification: Glioma, Meningioma, Pituitary, No Tumor
        - Interactive visualizations with Plotly
        - Comprehensive medical information database
        
        **Full Version Features:**
        - Real CNN with trained weights
        - TensorFlow/Keras implementation
        - Batch normalization and dropout
        - Progressive feature extraction
        - Medical-grade accuracy optimization
        
        **Architecture (Full Version):**
        - Input Layer: 224x224x3 RGB images
        - 4 Convolutional Blocks with BatchNormalization
        - Progressive filters: 32→64→128→256
        - Dense layers with regularization
        - Softmax output for 4 classes
        """)

if __name__ == "__main__":
    main()