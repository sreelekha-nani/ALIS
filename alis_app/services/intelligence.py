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
    def voice_ai_response(student, query, mode='Beginner', history=None):
        """
        Generates a live AI response using Google Gemini API with conversation history.
        """
        if not GEMINI_API_KEY:
            logger.error("CRITICAL: GEMINI_API_KEY missing.")
            return "Neural link offline. Please configure the AI API Key."

        try:
            # Mode-specific depth
            mode_prompts = {
                "Beginner": "Explain in simple student-friendly terms. Use analogies. Avoid jargon.",
                "Intermediate": "Provide technical depth with clear definitions and process explanations.",
                "Advanced": "Provide a rigorous deep-dive with architectural nuances and performance considerations."
            }
            depth_instruction = mode_prompts.get(mode, mode_prompts['Beginner'])

            # Initialize Model
            model = genai.GenerativeModel('gemini-2.5-flash')
            
            # Format History
            chat_context = ""
            if history:
                chat_context = "PREVIOUS CONVERSATION:\n"
                for msg in history:
                    role_label = "Student" if msg.role == 'user' else "Alis (You)"
                    chat_context += f"{role_label}: {msg.content}\n"
            
            # Final Prompt Construction
            full_prompt = f"""
            SYSTEM ROLE: You are Alis, an elite AI Cognitive Tutor for the ALIS Intelligence OS.
            TONE: Professional, authoritative, yet encouraging. Use precise technical terminology.
            
            STUDENT_PROFILE:
            - Level: {student.level or 'Stable'}
            - Recent Focus: {student.last_subject or 'General Studies'}
            
            CONSTRAINTS:
            1. Provide direct, high-signal answers. Avoid conversational filler or redundant greetings.
            2. If previous context is provided, maintain a seamless flow without re-introducing yourself.
            3. Structure complex explanations with clear sections or bullet points if necessary.
            4. Stay strictly in character as the ALIS Intelligence core.

            {chat_context}
            STUDENT_QUERY: {query}
            ALIS_NEURAL_RESPONSE:
            """

            # Debug Logs
            logger.info(f"[AI_TUTOR] Request from {student.email} | Mode: {mode}")
            logger.info(f"[AI_TUTOR] Prompt: {full_prompt[:200]}...") # Log start of prompt
            
            response = model.generate_content(
                full_prompt,
                generation_config=genai.types.GenerationConfig(
                    temperature=0.7,
                    max_output_tokens=800,
                )
            )

            if response and response.text:
                ai_text = response.text.strip()
                logger.info(f"[AI_TUTOR] Success | Response Length: {len(ai_text)}")
                return ai_text
            else:
                logger.warning("[AI_TUTOR] Empty response from Gemini.")
                return "I've processed your query, but my response generation was filtered. Could you try rephrasing?"

        except Exception as e:
            logger.error(f"[AI_TUTOR] API Error: {str(e)}", exc_info=True)
            return f"SYSTEM_ERROR: My cognitive processors encountered an issue ({str(e)}). Please try again in a moment."

    @staticmethod
    def get_recommendations(student):
        weak_concepts = Concept.objects.filter(name__in=student.weak_areas)
        recommendations = RecommendationItem.objects.filter(concept__in=weak_concepts)
        return recommendations

    @staticmethod
    def process_assessment_result(student, assessment, answers):
        """
        Calculates score and updates student DNA based on quiz performance.
        """
        questions = {q.id: q for q in assessment.questions.all()}
        correct_count = 0
        total_count = len(questions)
        concept_stats = {}

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
        weak_concepts = [stats['name'] for cid, stats in concept_stats.items() if (stats['correct'] / stats['total'] * 100) < 50]
        strong_concepts = [stats['name'] for cid, stats in concept_stats.items() if (stats['correct'] / stats['total'] * 100) >= 80]

        result = AssessmentResult.objects.create(
            student=student,
            assessment=assessment,
            score=accuracy,
            strong_concepts=strong_concepts,
            weak_concepts=weak_concepts
        )

        IntelligenceService.update_student_dna(student, accuracy, weak_concepts, assessment.subject.name)
        return result

    @staticmethod
    def update_student_dna(student, last_score, weak_areas, subject_name):
        student.last_quiz_score = last_score
        student.last_subject = subject_name
        current_weak = set(student.weak_areas or [])
        current_weak.update(weak_areas)
        student.weak_areas = list(current_weak)

        if last_score >= 80: student.level = "Strong"
        elif last_score >= 50: student.level = "Average"
        else: student.level = "Weak"

        student.risk_score = max(0, min(100, (100 - last_score) * 0.8 + (student.risk_score * 0.2)))
        student.learning_speed = 85.0 if last_score > 70 else 60.0
        student.retention_score = last_score * 0.9 + 5
        
        xp_gained = last_score * 10
        student.xp += xp_gained
        student.total_xp += xp_gained
        if student.xp >= 1000:
            student.user_level += 1
            student.xp -= 1000

        import datetime
        student.last_activity_date = datetime.date.today()
        student.save()

    @staticmethod
    def get_performance_predictions(student):
        trend = student.learning_trend or []
        avg_score = sum([t['score'] for t in trend]) / len(trend) if trend else 70
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


