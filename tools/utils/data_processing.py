#!/usr/bin/env python3
"""
Utility functions for data processing in the climate economy ecosystem tools.
These functions are used by multiple analysis tools to standardize data processing.
"""

import re
import json
import logging
from datetime import datetime, timedelta
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer, CountVectorizer
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from nltk.stem import PorterStemmer, WordNetLemmatizer

# Configure logging
logger = logging.getLogger(__name__)

# Common climate stopwords to exclude from analysis
CLIMATE_STOPWORDS = [
    "climate", "change", "global", "warming", "energy", "carbon", "emissions",
    "renewable", "sustainable", "sustainability", "environment", "environmental",
    "green", "clean", "fossil", "fuel", "fuels", "power", "solar", "wind", "hydro",
    "nuclear", "coal", "natural", "gas", "oil", "electric", "electricity", "policy",
    "policies", "report", "reports", "study", "studies", "research", "analysis",
    "analyses", "data", "figure", "figures", "table", "tables", "section", "sections",
    "page", "pages", "abstract", "introduction", "conclusion", "conclusions", "result",
    "results", "method", "methods", "methodology", "methodologies", "approach",
    "approaches", "model", "models", "modeling", "modelling", "scenario", "scenarios"
]

def setup_nltk():
    """Download required NLTK resources if not already present."""
    try:
        import nltk
        nltk.download('punkt', quiet=True)
        nltk.download('stopwords', quiet=True)
        nltk.download('wordnet', quiet=True)
        logger.info("NLTK resources downloaded successfully")
    except Exception as e:
        logger.error(f"Error downloading NLTK resources: {str(e)}")

def clean_text(text, remove_climate_stopwords=False):
    """
    Clean text data by removing special characters, numbers, and stopwords.
    
    Args:
        text (str): The input text to clean
        remove_climate_stopwords (bool): Whether to remove climate-specific stopwords
        
    Returns:
        str: The cleaned text
    """
    if not text or not isinstance(text, str):
        return ""
    
    # Convert to lowercase
    text = text.lower()
    
    # Remove URLs
    text = re.sub(r'https?://\S+|www\.\S+', '', text)
    
    # Remove email addresses
    text = re.sub(r'\S+@\S+', '', text)
    
    # Remove special characters and numbers
    text = re.sub(r'[^a-zA-Z\s]', '', text)
    
    # Tokenize
    tokens = word_tokenize(text)
    
    # Remove stopwords
    stop_words = set(stopwords.words('english'))
    if remove_climate_stopwords:
        stop_words.update(CLIMATE_STOPWORDS)
    
    tokens = [token for token in tokens if token not in stop_words and len(token) > 2]
    
    # Rejoin tokens
    cleaned_text = ' '.join(tokens)
    
    return cleaned_text

def lemmatize_text(text):
    """
    Lemmatize text data to reduce words to their base form.
    
    Args:
        text (str): The input text to lemmatize
        
    Returns:
        str: The lemmatized text
    """
    if not text or not isinstance(text, str):
        return ""
    
    # Tokenize
    tokens = word_tokenize(text.lower())
    
    # Lemmatize
    lemmatizer = WordNetLemmatizer()
    lemmatized_tokens = [lemmatizer.lemmatize(token) for token in tokens]
    
    # Rejoin tokens
    lemmatized_text = ' '.join(lemmatized_tokens)
    
    return lemmatized_text

def stem_text(text):
    """
    Stem text data to reduce words to their root form.
    
    Args:
        text (str): The input text to stem
        
    Returns:
        str: The stemmed text
    """
    if not text or not isinstance(text, str):
        return ""
    
    # Tokenize
    tokens = word_tokenize(text.lower())
    
    # Stem
    stemmer = PorterStemmer()
    stemmed_tokens = [stemmer.stem(token) for token in tokens]
    
    # Rejoin tokens
    stemmed_text = ' '.join(stemmed_tokens)
    
    return stemmed_text

def extract_climate_keywords(text, top_n=20):
    """
    Extract climate-related keywords from text using TF-IDF.
    
    Args:
        text (str): The input text to extract keywords from
        top_n (int): The number of top keywords to return
        
    Returns:
        list: A list of tuples containing (keyword, score)
    """
    if not text or not isinstance(text, str):
        return []
    
    # Clean the text
    cleaned_text = clean_text(text)
    
    # Create a TF-IDF vectorizer
    vectorizer = TfidfVectorizer(max_features=100, stop_words='english')
    
    try:
        # Transform the text
        tfidf_matrix = vectorizer.fit_transform([cleaned_text])
        
        # Get feature names
        feature_names = vectorizer.get_feature_names_out()
        
        # Get TF-IDF scores
        scores = tfidf_matrix.toarray()[0]
        
        # Create a list of (word, score) tuples
        word_scores = [(feature_names[i], scores[i]) for i in range(len(feature_names))]
        
        # Sort by score and take top N
        word_scores.sort(key=lambda x: x[1], reverse=True)
        return word_scores[:top_n]
    except Exception as e:
        logger.error(f"Error extracting keywords: {str(e)}")
        return []

def calculate_term_frequency(documents, top_n=50, ngram_range=(1, 2)):
    """
    Calculate term frequency across a collection of documents.
    
    Args:
        documents (list): A list of document texts
        top_n (int): The number of top terms to return
        ngram_range (tuple): The n-gram range to consider
        
    Returns:
        dict: A dictionary with term frequency information
    """
    if not documents:
        return {"most_common": [], "climate_related": []}
    
    # Clean the documents
    cleaned_docs = [clean_text(doc) for doc in documents if doc and isinstance(doc, str)]
    
    if not cleaned_docs:
        return {"most_common": [], "climate_related": []}
    
    # Create a Count Vectorizer for general terms
    count_vectorizer = CountVectorizer(max_features=1000, ngram_range=ngram_range, stop_words='english')
    
    # Create a Count Vectorizer for climate-related terms (without climate stopwords)
    climate_vectorizer = CountVectorizer(max_features=500, ngram_range=ngram_range, stop_words=list(set(stopwords.words('english'))))
    
    try:
        # Transform the documents for general terms
        count_matrix = count_vectorizer.fit_transform(cleaned_docs)
        
        # Get feature names for general terms
        feature_names = count_vectorizer.get_feature_names_out()
        
        # Calculate term frequencies
        term_frequencies = count_matrix.sum(axis=0).A1
        
        # Create a list of (term, frequency) tuples for general terms
        term_freq_general = [(feature_names[i], int(term_frequencies[i])) for i in range(len(feature_names))]
        
        # Sort by frequency and take top N
        term_freq_general.sort(key=lambda x: x[1], reverse=True)
        most_common = term_freq_general[:top_n]
        
        # Transform the documents for climate-related terms
        climate_matrix = climate_vectorizer.fit_transform(cleaned_docs)
        
        # Get feature names for climate-related terms
        climate_feature_names = climate_vectorizer.get_feature_names_out()
        
        # Calculate term frequencies for climate-related terms
        climate_term_frequencies = climate_matrix.sum(axis=0).A1
        
        # Create a list of (term, frequency) tuples for climate-related terms
        term_freq_climate = [(climate_feature_names[i], int(climate_term_frequencies[i])) for i in range(len(climate_feature_names))]
        
        # Filter for likely climate-related terms
        climate_terms = []
        climate_keywords = [
            "emission", "emissions", "renewable", "renewables", "solar", "wind", 
            "carbon", "greenhouse", "ghg", "energy", "clean", "sustainable", 
            "transition", "adaptation", "mitigation", "resilience", "esg", 
            "fossil", "electrification", "decarbonization", "climate", "warming"
        ]
        
        for term, freq in term_freq_climate:
            if any(keyword in term for keyword in climate_keywords):
                climate_terms.append((term, freq))
        
        # Sort by frequency and take top N
        climate_terms.sort(key=lambda x: x[1], reverse=True)
        climate_related = climate_terms[:top_n]
        
        return {
            "most_common": most_common,
            "climate_related": climate_related
        }
    except Exception as e:
        logger.error(f"Error calculating term frequency: {str(e)}")
        return {"most_common": [], "climate_related": []}

def calculate_cosine_similarity(vec1, vec2):
    """
    Calculate cosine similarity between two vectors.
    
    Args:
        vec1 (array): The first vector
        vec2 (array): The second vector
        
    Returns:
        float: The cosine similarity
    """
    if not isinstance(vec1, np.ndarray) or not isinstance(vec2, np.ndarray):
        return 0.0
    
    # Check if vectors are empty
    if vec1.size == 0 or vec2.size == 0:
        return 0.0
    
    # Calculate dot product
    dot_product = np.dot(vec1, vec2)
    
    # Calculate magnitudes
    mag1 = np.linalg.norm(vec1)
    mag2 = np.linalg.norm(vec2)
    
    # Check if magnitudes are zero
    if mag1 == 0 or mag2 == 0:
        return 0.0
    
    # Calculate cosine similarity
    return dot_product / (mag1 * mag2)

def extract_organization_names(text, known_organizations):
    """
    Extract organization names from text based on a list of known organizations.
    
    Args:
        text (str): The input text to extract organization names from
        known_organizations (list): A list of known organization names
        
    Returns:
        list: A list of extracted organization names
    """
    if not text or not isinstance(text, str) or not known_organizations:
        return []
    
    # Convert text to lowercase
    text_lower = text.lower()
    
    # Create a list to store extracted organizations
    extracted_orgs = []
    
    # Check for each known organization
    for org in known_organizations:
        # Convert organization name to lowercase
        org_lower = org.lower()
        
        # Check if organization name is in the text
        if org_lower in text_lower:
            # Add organization to extracted list
            extracted_orgs.append(org)
    
    return extracted_orgs

def filter_recent_data(data, days=30, date_field="created_at"):
    """
    Filter data to only include items from the last N days.
    
    Args:
        data (list): A list of data items with a date field
        days (int): The number of days to look back
        date_field (str): The name of the date field in the data items
        
    Returns:
        list: A filtered list of data items
    """
    if not data:
        return []
    
    # Calculate the cutoff date
    cutoff_date = datetime.now() - timedelta(days=days)
    
    # Filter the data
    filtered_data = []
    for item in data:
        if date_field not in item:
            continue
        
        # Parse the date string
        try:
            date_value = item[date_field]
            if isinstance(date_value, str):
                item_date = datetime.fromisoformat(date_value.replace('Z', '+00:00'))
            elif isinstance(date_value, datetime):
                item_date = date_value
            else:
                continue
            
            # Check if the item date is after the cutoff date
            if item_date >= cutoff_date:
                filtered_data.append(item)
        except Exception as e:
            logger.error(f"Error parsing date: {str(e)}")
            continue
    
    return filtered_data

def serialize_for_json(obj):
    """
    Convert an object to a JSON-serializable format.
    
    Args:
        obj: The object to serialize
        
    Returns:
        object: A JSON-serializable representation of the object
    """
    if isinstance(obj, (datetime, np.datetime64)):
        return obj.isoformat()
    elif isinstance(obj, np.ndarray):
        return obj.tolist()
    elif isinstance(obj, np.integer):
        return int(obj)
    elif isinstance(obj, np.floating):
        return float(obj)
    elif isinstance(obj, (set, frozenset)):
        return list(obj)
    else:
        try:
            json.dumps(obj)
            return obj
        except (TypeError, OverflowError):
            return str(obj) 