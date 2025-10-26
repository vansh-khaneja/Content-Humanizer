"""
Pre-download models before starting the server
Run this first, then start the server
"""
import warnings
warnings.filterwarnings("ignore")

print("=" * 60)
print("Downloading Models for Text Humanizer API")
print("=" * 60)

print("\n📥 Loading Parrot model...")
print("This will download ~1.4 GB. Please be patient...")
from parrot import Parrot
parrot = Parrot(model_tag="prithivida/parrot_paraphraser_on_T5", use_gpu=False)
print("✅ Parrot model downloaded successfully!")

print("\n📥 Loading spaCy model...")
import spacy
nlp = spacy.load("en_core_web_sm")
print("✅ spaCy model downloaded successfully!")

print("\n🎉 All models are ready!")
print("You can now start the server with:")
print("  uvicorn main:app --host 0.0.0.0 --port 8000")

