import re
import string
import nltk
import os
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer

# Flag to enable/disable OpenAI grading
USE_OPENAI_GRADING = True

# Download NLTK resources
try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    nltk.download('punkt')

try:
    nltk.data.find('corpora/stopwords')
except LookupError:
    nltk.download('stopwords')

try:
    nltk.data.find('corpora/wordnet')
except LookupError:
    nltk.download('wordnet')


def grade_multiple_choice(student_answer, correct_answer, max_points):
    """
    Grade multiple choice questions
    
    Args:
        student_answer (str): The student's selected answer
        correct_answer (str): The correct answer
        max_points (int): Maximum points for this question
        
    Returns:
        tuple: (score, feedback)
    """
    if student_answer.strip() == correct_answer.strip():
        return max_points, "Correct answer!"
    else:
        return 0, f"Incorrect. The correct answer is: {correct_answer}"


def preprocess_text(text):
    """
    Preprocess text by removing punctuation, converting to lowercase,
    removing stopwords, and lemmatizing
    
    Args:
        text (str): The text to preprocess
        
    Returns:
        list: List of preprocessed tokens
    """
    # Convert to lowercase and remove punctuation
    text = text.lower()
    text = re.sub(f'[{re.escape(string.punctuation)}]', '', text)
    
    # Tokenize
    tokens = word_tokenize(text)
    
    # Remove stopwords
    stop_words = set(stopwords.words('english'))
    tokens = [token for token in tokens if token not in stop_words]
    
    # Lemmatize
    lemmatizer = WordNetLemmatizer()
    tokens = [lemmatizer.lemmatize(token) for token in tokens]
    
    return tokens


def calculate_similarity(student_tokens, correct_tokens):
    """
    Calculate similarity between student answer and correct answer
    using a basic bag-of-words approach
    
    Args:
        student_tokens (list): List of tokens from student answer
        correct_tokens (list): List of tokens from correct answer
        
    Returns:
        float: Similarity score between 0 and 1
    """
    if not student_tokens or not correct_tokens:
        return 0.0
    
    # Count matching tokens
    matches = sum(1 for token in student_tokens if token in correct_tokens)
    
    # Calculate Jaccard similarity
    union_size = len(set(student_tokens).union(set(correct_tokens)))
    if union_size == 0:
        return 0.0
    
    return matches / union_size


def grade_short_answer_with_nltk(student_answer, correct_answer, max_points):
    """
    Grade short answer questions using NLTK similarity
    
    Args:
        student_answer (str): The student's answer
        correct_answer (str): The correct answer
        max_points (int): Maximum points for this question
        
    Returns:
        tuple: (score, feedback)
    """
    # Handle empty answers
    if not student_answer.strip():
        return 0, "No answer provided."
    
    # Preprocess both answers
    student_tokens = preprocess_text(student_answer)
    correct_tokens = preprocess_text(correct_answer)
    
    # Calculate similarity
    similarity = calculate_similarity(student_tokens, correct_tokens)
    
    # Assign score based on similarity
    score = max_points * similarity
    
    # Generate feedback
    if similarity >= 0.9:
        feedback = "Excellent answer!"
    elif similarity >= 0.7:
        feedback = "Good answer, but missing some key points."
    elif similarity >= 0.5:
        feedback = "Partial credit. Your answer covers some aspects but misses important details."
    elif similarity >= 0.3:
        feedback = "Your answer is on the right track but needs significant improvement."
    else:
        feedback = "Your answer differs substantially from the expected response."
    
    return score, feedback


def grade_short_answer(student_answer, correct_answer, max_points):
    """
    Grade short answer questions, optionally using OpenAI for enhanced evaluation
    
    Args:
        student_answer (str): The student's answer
        correct_answer (str): The correct answer
        max_points (int): Maximum points for this question
        
    Returns:
        tuple: (score, feedback)
    """
    # Handle empty answers
    if not student_answer.strip():
        return 0, "No answer provided."
    
    # Check if we should use OpenAI for grading
    if USE_OPENAI_GRADING and os.environ.get("OPENAI_API_KEY"):
        try:
            from openai_utils import evaluate_short_answer
            return evaluate_short_answer(student_answer, correct_answer, max_points)
        except Exception as e:
            print(f"Error using OpenAI for grading: {e}")
            # Fall back to NLTK grading if OpenAI fails
            return grade_short_answer_with_nltk(student_answer, correct_answer, max_points)
    else:
        # Use NLTK-based grading as fallback
        return grade_short_answer_with_nltk(student_answer, correct_answer, max_points)
