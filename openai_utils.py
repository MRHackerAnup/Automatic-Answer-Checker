import json
import os
from openai import OpenAI

# The newest OpenAI model is "gpt-4o" which was released May 13, 2024.
# Do not change this unless explicitly requested by the user
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")
client = OpenAI(api_key=OPENAI_API_KEY)

def evaluate_short_answer(student_answer, reference_answer, max_points):
    """
    Evaluate a short answer response using OpenAI GPT model
    
    Args:
        student_answer (str): The student's answer to evaluate
        reference_answer (str): The reference answer (correct answer)
        max_points (int): Maximum points possible for this question
        
    Returns:
        tuple: (score, feedback) where score is a float and feedback is a string
    """
    try:
        # Create prompt for GPT evaluation
        prompt = f"""
        You are an expert educational evaluator tasked with grading a student's short answer response.
        
        Reference Answer (Correct): "{reference_answer}"
        
        Student Answer: "{student_answer}"
        
        Please evaluate the student's answer based on:
        1. Accuracy of information compared to the reference answer
        2. Completeness of response
        3. Clarity and coherence
        
        The maximum score is {max_points} points.
        
        Provide your evaluation as a JSON object with:
        1. "score": a float number between 0 and {max_points}
        2. "feedback": specific, constructive comments explaining the score 
        3. "explanation": a brief explanation of what was good/missing/incorrect
        
        Return ONLY the JSON with no additional text.
        """

        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "You are an educational grading assistant that evaluates student answers against reference answers."},
                {"role": "user", "content": prompt}
            ],
            response_format={"type": "json_object"},
            temperature=0.3,  # Lower temperature for more consistent evaluations
        )
        
        # Extract and parse result
        result = json.loads(response.choices[0].message.content)
        
        # Ensure the score is within bounds
        score = min(float(result["score"]), max_points)
        score = max(0, score)
        
        # Ensure score is properly formatted as a percentage 
        percentage_score = (score / max_points) * 100
        
        return percentage_score, result["feedback"]
    
    except Exception as e:
        print(f"OpenAI evaluation error: {e}")
        # Fall back to basic similarity comparison if API call fails
        from grading_engine import grade_short_answer
        return grade_short_answer(student_answer, reference_answer, max_points)


def generate_question_suggestions(topic, question_type="multiple_choice", count=3):
    """
    Generate suggested questions on a specific topic
    
    Args:
        topic (str): The topic to generate questions about
        question_type (str): Type of questions to generate (multiple_choice or short_answer)
        count (int): Number of questions to generate
        
    Returns:
        list: List of generated question dictionaries
    """
    try:
        # Create system message with detailed instructions
        system_message = """You are an educational assistant that helps create high-quality exam questions.
        Your task is to generate educational questions that are clear, concise, and appropriate for exams.
        Follow these guidelines:
        - Create questions that test understanding, not just memorization
        - For multiple-choice, ensure all options are plausible but only one is correct
        - For short answers, provide a comprehensive reference answer
        - Use appropriate terminology for the subject area
        """
        
        # Create prompt for question generation with proper formatting
        if question_type == "multiple_choice":
            prompt = f"""Generate {count} multiple-choice questions about {topic} for an educational exam.

For each question, include:
1. A clear question text
2. Four possible answer options
3. The correct answer (which must be one of the options)

Respond with a JSON object with a "questions" key containing an array of question objects.
Each question object should have the format:
{{
  "question_text": "The question text here",
  "options": ["Option A", "Option B", "Option C", "Option D"],
  "correct_answer": "The correct option here"
}}"""
        else:  # short_answer
            prompt = f"""Generate {count} short-answer questions about {topic} for an educational exam.

For each question, include:
1. A clear question text that requires a short paragraph response
2. A model/reference answer that would receive full marks

Respond with a JSON object with a "questions" key containing an array of question objects.
Each question object should have the format:
{{
  "question_text": "The question text here",
  "correct_answer": "The model/reference answer here"
}}"""

        # Make the API call with appropriate parameters
        response = client.chat.completions.create(
            model="gpt-4o", # The newest OpenAI model
            messages=[
                {"role": "system", "content": system_message},
                {"role": "user", "content": prompt}
            ],
            response_format={"type": "json_object"},
            temperature=0.7,  # Higher temperature for more creative questions
        )
        
        # Extract and parse result
        result = json.loads(response.choices[0].message.content)
        
        # Return the questions array or empty list if not found
        return result.get("questions", [])
    
    except Exception as e:
        print(f"OpenAI question generation error: {e}")
        return []