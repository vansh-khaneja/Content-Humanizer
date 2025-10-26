#!/bin/bash
# Pre-download models interactively before starting server

echo "=================================================="
echo "Pre-downloading Models for Text Humanizer API"
echo "=================================================="
echo ""
echo "This will download ~1.4 GB of models"
echo "This ensures the server starts immediately!"
echo ""

# Download Parrot model
echo "📥 Step 1/2: Downloading Parrot model..."
python3 -c "
from parrot import Parrot
print('Downloading Parrot model (this may take 5-10 minutes)...')
parrot = Parrot(model_tag='prithivida/parrot_paraphraser_on_T5', use_gpu=False)
print('✅ Parrot model ready!')
"

echo ""
echo "📥 Step 2/2: Loading spaCy model..."
python3 -c "
import spacy
print('Downloading spaCy model...')
nlp = spacy.load('en_core_web_sm')
print('✅ spaCy model ready!')
"

echo ""
echo "🎉 All models downloaded successfully!"
echo "You can now start the server with:"
echo "  uvicorn main:app --host 0.0.0.0 --port 8000"

