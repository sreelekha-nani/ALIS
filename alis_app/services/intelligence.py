import os
import json
import logging
import google.generativeai as genai
from dotenv import load_dotenv
from ..models import User, Assessment, Question, AssessmentResult, Concept, RecommendationItem

# Load environment variables
load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# Configure Logging
logger = logging.getLogger(__name__)

if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)
else:
    logger.warning("GEMINI_API_KEY not found in environment variables.")

class IntelligenceService:
    @staticmethod
    def voice_ai_response(student, query, mode='Beginner'):
        """
        Generates a live AI response using Google Gemini API.
        """
        if not GEMINI_API_KEY:
            logger.error("Attempted AI request without GEMINI_API_KEY.")
            return "My neural core is currently offline (API key missing). Please contact the system administrator."

        try:
            # Prompt Engineering based on Mode
            mode_instructions = {
                "Beginner": "Explain in simple student-friendly language with relatable examples. Avoid heavy jargon.",
                "Intermediate": "Provide moderate technical depth with concise definitions and process explanations.",
                "Advanced": "Provide detailed technical explanation with architectural nuances, performance considerations, and professional terminology."
            }
            
            instruction = mode_instructions.get(mode, mode_instructions['Beginner'])
            
            system_context = f"""
            You are Alis, an advanced cognitive AI tutor for the ALIS Intelligence OS. 
            You are tutoring a student whose current level is {student.level or 'Stable'}.
            Your task is to: {instruction}
            Always stay in character as a sophisticated, helpful AI.
            User Question: {query}
            """

            # Initialize Model (gemini-1.5-flash as per latest stable recommendation)
            model = genai.GenerativeModel('gemini-1.5-flash')
            
            logger.info(f"GEMINI REQUEST: Mode={mode}, User={student.email}, Query='{query}'")
            
            response = model.generate_content(
                system_context,
                generation_config=genai.types.GenerationConfig(
                    temperature=0.7,
                    max_output_tokens=500,
                )
            )

            if response and response.text:
                logger.info(f"GEMINI SUCCESS: Response length={len(response.text)}")
                return response.text.strip()
            else:
                logger.error("GEMINI ERROR: Empty response received.")
                return "I processed your request but my neural filters returned an empty result. Could you rephrase that?"

        except Exception as e:
            error_msg = str(e)
            logger.error(f"GEMINI API FAILURE: {error_msg}")
            
            if "rate_limit" in error_msg.lower():
                return "My cognitive circuits are a bit overloaded right now (Rate Limit reached). Let's try again in a moment."
            elif "timeout" in error_msg.lower():
                return "The neural link timed out. Please check your connection and retry."
            
            return "I encountered a synchronization error while processing your request. My neural link is stabilizing."

    @staticmethod
    def process_assessment_result(student, assessment, answers):
        """
        answers: list of dicts [{'question_id': id, 'choice': 'A'}]
        """
        questions = {q.id: q for q in assessment.questions.all()}
        correct_count = 0
        total_count = len(questions)
        
        concept_stats = {} # {concept_id: {total: 0, correct: 0}}
        
        for ans in answers:
            q_id = int(ans['question_id'])
            choice = ans['choice']
            
            if q_id in questions:
                q = questions[q_id]
                concept_id = q.concept.id if q.concept else None
                
                if concept_id:
                    if concept_id not in concept_stats:
                        concept_stats[concept_id] = {'total': 0, 'correct': 0, 'name': q.concept.name}
                    concept_stats[concept_id]['total'] += 1
                
                if q.correct_option == choice:
                    correct_count += 1
                    if concept_id:
                        concept_stats[concept_id]['correct'] += 1
        
        accuracy = int((correct_count / total_count * 100)) if total_count > 0 else 0
        
        strong_concepts = []
        weak_concepts = []
        
        for cid, stats in concept_stats.items():
            concept_accuracy = (stats['correct'] / stats['total'] * 100)
            if concept_accuracy >= 80:
                strong_concepts.append(stats['name'])
            elif concept_accuracy < 50:
                weak_concepts.append(stats['name'])
        
        # Save Result
        result = AssessmentResult.objects.create(
            student=student,
            assessment=assessment,
            score=accuracy,
            strong_concepts=strong_concepts,
            weak_concepts=weak_concepts
        )
        
        # Update Student DNA
        IntelligenceService.update_student_dna(student, accuracy, weak_concepts, assessment.subject.name)
        
        return result

    @staticmethod
    def update_student_dna(student, last_score, weak_areas, subject_name):
        student.last_quiz_score = last_score
        student.last_subject = subject_name
        
        # Merge weak areas
        current_weak = set(student.weak_areas or [])
        current_weak.update(weak_areas)
        student.weak_areas = list(current_weak)
        
        # Update Proficiency Level
        if last_score >= 80:
            student.level = "Strong"
        elif last_score >= 50:
            student.level = "Average"
        else:
            student.level = "Weak"
            
        # AI Calculations (Simulated logic for prototype)
        student.risk_score = max(0, min(100, (100 - last_score) * 0.8 + (student.risk_score * 0.2)))
        student.learning_speed = 85.0 if last_score > 70 else 60.0
        student.retention_score = last_score * 0.9 + 5
        
        # XP & Achievement System
        xp_gained = last_score * 10
        student.xp += xp_gained
        student.total_xp += xp_gained
        
        # Leveling logic (1000 XP per level)
        if student.xp >= 1000:
            student.user_level += 1
            student.xp -= 1000
            if "Level Up" not in (student.badges or []):
                student.badges = (student.badges or []) + ["Level Up"]
        
        # Streak Logic
        import datetime
        today = datetime.date.today()
        if student.last_activity_date:
            if student.last_activity_date == today - datetime.timedelta(days=1):
                student.streak_days += 1
            elif student.last_activity_date < today - datetime.timedelta(days=1):
                student.streak_days = 1
        else:
            student.streak_days = 1
        student.last_activity_date = today

        # Career Readiness Index Updates
        if "Coding" in subject_name or "DBMS" in subject_name:
            student.technical_readiness = min(100, student.technical_readiness * 0.7 + last_score * 0.3)
        elif "Math" in subject_name or "Logic" in subject_name:
            student.aptitude_readiness = min(100, student.aptitude_readiness * 0.7 + last_score * 0.3)
        
        # Simulated Communication readiness increase
        student.communication_readiness = min(100, student.communication_readiness + (last_score/20))

        # Update trend
        trend = student.learning_trend or []
        trend.append({
            'date': today.strftime("%Y-%m-%d"),
            'score': last_score
        })
        student.learning_trend = trend[-10:] 
        
        student.save()

    @staticmethod
    def get_performance_predictions(student):
        # Predicted Score: weighted average of trend
        trend = student.learning_trend or []
        if not trend:
            return {"predicted_score": 75, "readiness": 60, "confidence": 70}
        
        scores = [t['score'] for t in trend]
        avg_score = sum(scores) / len(scores)
        
        return {
            "predicted_score": int(min(100, avg_score + 5)),
            "readiness": int(student.retention_score * 0.8 + student.learning_speed * 0.2),
            "confidence": int(80 if len(trend) > 5 else 60)
        }

    @staticmethod
    def get_career_index(student):
        overall = (student.technical_readiness + student.aptitude_readiness + student.communication_readiness) / 3
        return {
            "technical": int(student.technical_readiness),
            "aptitude": int(student.aptitude_readiness),
            "communication": int(student.communication_readiness),
            "overall": int(overall)
        }

    @staticmethod
    def voice_ai_response(student, query, mode='Beginner'):
        """
        Generates a live AI response using Google Gemini API with depth-aware prompt engineering.
        """
        if not GEMINI_API_KEY:
            logger.error("Attempted AI request without GEMINI_API_KEY.")
            return "My neural core is currently offline (API key missing). Please contact the system administrator."

        try:
            # Mode-specific technical depth instructions
            mode_prompts = {
                "Beginner": "Explain this in very simple, student-friendly terms. Use relatable analogies and metaphors. Avoid technical jargon where possible.",
                "Intermediate": "Provide a clear technical explanation with moderate depth. Include key definitions and explain how the concept works in practice.",
                "Advanced": "Provide a rigorous technical deep-dive. Discuss architectural nuances, low-level performance considerations, and professional edge cases."
            }
            
            depth_instruction = mode_prompts.get(mode, mode_prompts['Beginner'])
            
            # Construct the system prompt
            prompt = f"""
            SYSTEM ROLE: You are Alis, the highly sophisticated AI Tutor for the ALIS Intelligence OS.
            TARGET AUDIENCE: A student with a current proficiency level of '{student.level or 'Stable'}'.
            
            INSTRUCTION: {depth_instruction}
            
            CONSTRAINTS:
            1. Keep the response concise but informative (max 300 words).
            2. Stay strictly in character as a professional yet encouraging cognitive assistant.
            3. If the user asks about their performance, refer to their '{student.last_subject or 'recent'}' studies.
            
            USER QUERY: {query}
            """

            model = genai.GenerativeModel('gemini-1.5-flash')
            
            logger.info(f"GEMINI LIVE REQUEST: Mode={mode}, Query='{query}'")
            
            response = model.generate_content(
                prompt,
                generation_config=genai.types.GenerationConfig(
                    temperature=0.75,
                    max_output_tokens=600,
                )
            )

            if response and response.text:
                return response.text.strip()
            else:
                return "I've analyzed your query, but my neural processors returned an empty response. Please rephrase your question."

        except Exception as e:
            logger.error(f"GEMINI API FAILURE: {str(e)}")
            return "My neural link is currently experiencing synchronization issues. Please try again in a few moments."

    @staticmethod
    def get_recommendations(student):
        weak_concepts = Concept.objects.filter(name__in=student.weak_areas)
        recommendations = RecommendationItem.objects.filter(concept__in=weak_concepts)
        return recommendations

    @staticmethod
    def get_study_plan(student):
        # Simulated intelligent study plan based on gaps
        plan = []
        if student.weak_areas:
            for area in student.weak_areas[:2]:
                plan.append({'task': f"Deep Dive: {area}", 'status': 'Required', 'priority': 'High'})
        
        # Add tasks based on level
        if student.level == 'Weak':
            plan.append({'task': "Foundational Concepts Review", 'status': 'Pending', 'priority': 'Medium'})
        elif student.level == 'Strong':
            plan.append({'task': "Advanced Mastery Challenge", 'status': 'Optional', 'priority': 'Low'})
        
        # Fallback/General tasks
        plan.append({'task': "Daily Cognitive Calibration", 'status': 'Pending', 'priority': 'Medium'})
        
        return plan[:4]

    @staticmethod
    def get_class_analytics(teacher):
        students = User.objects.filter(role='student')
        total_students = students.count()
        
        if total_students == 0:
            return {}
            
        at_risk = students.filter(risk_score__gt=60)
        
        # Aggregate weak concepts across all students
        all_weak = []
        for s in students:
            all_weak.extend(s.weak_areas or [])
            
        from collections import Counter
        common_weaknesses = Counter(all_weak).most_common(5)
        
        return {
            'total_students': total_students,
            'at_risk_count': at_risk.count(),
            'at_risk_students': at_risk,
            'common_weaknesses': common_weaknesses, # [(concept, count)]
            'class_avg_accuracy': sum([s.last_quiz_score or 0 for s in students]) / total_students
        }
