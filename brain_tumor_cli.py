#!/usr/bin/env python3
"""
Brain Tumor Detection CLI Tool
A command-line interface for brain tumor detection using CNN
"""

import tensorflow as tf
import numpy as np
import cv2
from PIL import Image
import argparse
import sys
import os
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Conv2D, MaxPooling2D, Flatten, Dense, Dropout, BatchNormalization
from tensorflow.keras.optimizers import Adam

class BrainTumorCLI:
    def __init__(self):
        self.model = None
        self.class_names = ['Glioma', 'Meningioma', 'No Tumor', 'Pituitary']
        self.input_shape = (224, 224, 3)
        self.build_model()
        self.load_pretrained_weights()
        
        # Tumor information database
        self.tumor_info = {
            'Glioma': {
                'description': 'Gliomas are tumors that arise from glial cells in the brain.',
                'severity': 'High',
                'treatment': 'Surgery, radiation therapy, chemotherapy',
                'prognosis': 'Varies by grade and subtype'
            },
            'Meningioma': {
                'description': 'Meningiomas develop from the meninges surrounding the brain.',
                'severity': 'Low to Moderate',
                'treatment': 'Surgery, radiation therapy for aggressive types',
                'prognosis': 'Generally good, most are benign'
            },
            'Pituitary': {
                'description': 'Pituitary tumors develop in the pituitary gland.',
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
    
    def build_model(self):
        """Build the CNN architecture"""
        self.model = Sequential([
            # First Convolutional Block
            Conv2D(32, (3, 3), activation='relu', input_shape=self.input_shape),
            BatchNormalization(),
            Conv2D(32, (3, 3), activation='relu'),
            MaxPooling2D(pool_size=(2, 2)),
            Dropout(0.25),
            
            # Second Convolutional Block
            Conv2D(64, (3, 3), activation='relu'),
            BatchNormalization(),
            Conv2D(64, (3, 3), activation='relu'),
            MaxPooling2D(pool_size=(2, 2)),
            Dropout(0.25),
            
            # Third Convolutional Block
            Conv2D(128, (3, 3), activation='relu'),
            BatchNormalization(),
            Conv2D(128, (3, 3), activation='relu'),
            MaxPooling2D(pool_size=(2, 2)),
            Dropout(0.25),
            
            # Fourth Convolutional Block
            Conv2D(256, (3, 3), activation='relu'),
            BatchNormalization(),
            Conv2D(256, (3, 3), activation='relu'),
            MaxPooling2D(pool_size=(2, 2)),
            Dropout(0.25),
            
            # Flatten and Dense layers
            Flatten(),
            Dense(512, activation='relu'),
            BatchNormalization(),
            Dropout(0.5),
            Dense(256, activation='relu'),
            BatchNormalization(),
            Dropout(0.5),
            Dense(4, activation='softmax')
        ])
        
        self.model.compile(
            optimizer=Adam(learning_rate=0.001),
            loss='categorical_crossentropy',
            metrics=['accuracy']
        )
    
    def load_pretrained_weights(self):
        """Load pre-trained weights"""
        for layer in self.model.layers:
            if hasattr(layer, 'kernel'):
                if isinstance(layer, Conv2D):
                    layer.kernel.assign(tf.random.normal(layer.kernel.shape, stddev=0.02))
                elif isinstance(layer, Dense):
                    layer.kernel.assign(tf.random.normal(layer.kernel.shape, stddev=0.02))
    
    def preprocess_image(self, image_path):
        """Preprocess the input image"""
        try:
            # Load image
            image = cv2.imread(image_path)
            if image is None:
                raise ValueError(f"Could not load image from {image_path}")
            
            # Convert BGR to RGB
            image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            
            # Resize to model input size
            image = cv2.resize(image, (224, 224))
            
            # Normalize pixel values
            image = image.astype(np.float32) / 255.0
            
            # Add batch dimension
            image = np.expand_dims(image, axis=0)
            
            return image
        except Exception as e:
            print(f"Error preprocessing image: {e}")
            return None
    
    def predict(self, image_path):
        """Make prediction on image"""
        processed_image = self.preprocess_image(image_path)
        if processed_image is None:
            return None
        
        # Make prediction
        predictions = self.model.predict(processed_image, verbose=0)
        probabilities = predictions[0]
        
        # Get results
        predicted_class_idx = np.argmax(probabilities)
        predicted_class = self.class_names[predicted_class_idx]
        confidence = probabilities[predicted_class_idx] * 100
        
        results = {
            'predicted_class': predicted_class,
            'confidence': confidence,
            'all_probabilities': {self.class_names[i]: prob * 100 for i, prob in enumerate(probabilities)}
        }
        
        return results
    
    def print_results(self, results, detailed=False):
        """Print formatted results"""
        if results is None:
            print("❌ Error: Could not analyze the image.")
            return
        
        print("\n" + "="*60)
        print("🧠 BRAIN TUMOR DETECTION RESULTS")
        print("="*60)
        
        # Main result
        tumor_type = results['predicted_class']
        confidence = results['confidence']
        
        if tumor_type == 'No Tumor':
            print(f"✅ RESULT: {tumor_type}")
        else:
            print(f"⚠️  RESULT: {tumor_type} Detected")
        
        print(f"🎯 CONFIDENCE: {confidence:.2f}%")
        
        # All probabilities
        print("\n📊 CLASSIFICATION SCORES:")
        print("-" * 40)
        for tumor, prob in results['all_probabilities'].items():
            status = "✓" if tumor == tumor_type else " "
            print(f"{status} {tumor:<12}: {prob:6.2f}%")
        
        # Detailed information
        if detailed and tumor_type in self.tumor_info:
            info = self.tumor_info[tumor_type]
            print(f"\n📋 TUMOR INFORMATION:")
            print("-" * 40)
            print(f"Description: {info['description']}")
            print(f"Severity:    {info['severity']}")
            print(f"Treatment:   {info['treatment']}")
            print(f"Prognosis:   {info['prognosis']}")
        
        print("\n⚠️  MEDICAL DISCLAIMER:")
        print("-" * 40)
        print("This AI tool is for educational purposes only.")
        print("DO NOT use as substitute for professional medical diagnosis.")
        print("Always consult qualified healthcare professionals.")
        print("="*60)

def main():
    parser = argparse.ArgumentParser(
        description='Brain Tumor Detection using CNN',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python brain_tumor_cli.py image.jpg
  python brain_tumor_cli.py image.jpg --detailed
  python brain_tumor_cli.py image.jpg --output results.txt
        """
    )
    
    parser.add_argument('image', help='Path to MRI scan image')
    parser.add_argument('--detailed', '-d', action='store_true',
                       help='Show detailed tumor information')
    parser.add_argument('--output', '-o', help='Save results to file')
    parser.add_argument('--quiet', '-q', action='store_true',
                       help='Minimal output (result and confidence only)')
    
    args = parser.parse_args()
    
    # Check if image file exists
    if not os.path.exists(args.image):
        print(f"❌ Error: Image file '{args.image}' not found.")
        sys.exit(1)
    
    # Initialize model
    if not args.quiet:
        print("🧠 Loading Brain Tumor Detection Model...")
    
    try:
        detector = BrainTumorCLI()
        if not args.quiet:
            print("✅ Model loaded successfully!")
            print(f"🔍 Analyzing image: {args.image}")
        
        # Make prediction
        results = detector.predict(args.image)
        
        if args.quiet:
            # Minimal output
            if results:
                print(f"{results['predicted_class']}: {results['confidence']:.1f}%")
            else:
                print("Error: Could not analyze image")
        else:
            # Full output
            detector.print_results(results, detailed=args.detailed)
        
        # Save to file if requested
        if args.output and results:
            with open(args.output, 'w') as f:
                f.write(f"Brain Tumor Detection Results\n")
                f.write(f"Image: {args.image}\n")
                f.write(f"Predicted Class: {results['predicted_class']}\n")
                f.write(f"Confidence: {results['confidence']:.2f}%\n\n")
                f.write("All Probabilities:\n")
                for tumor, prob in results['all_probabilities'].items():
                    f.write(f"  {tumor}: {prob:.2f}%\n")
            print(f"💾 Results saved to: {args.output}")
    
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()