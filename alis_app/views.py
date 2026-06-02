from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from .forms import CustomUserCreationForm, CustomAuthenticationForm
from .models import User, Assessment, Question, Subject, Concept, RecommendationItem, AssessmentResult, TutorMessage
from django.contrib import messages
from django.http import JsonResponse
import json
from django.views.decorators.csrf import csrf_exempt
from .services.intelligence import IntelligenceService

def index_view(request):
    return render(request, 'alis_app/index.html')

def showcase_view(request):
    return render(request, 'alis_app/showcase.html')

def intro_view(request):
    return render(request, 'alis_app/intro.html')

def register_view(request):
    if request.method == 'POST':
        data = request.POST.copy()
        if 'password' in data and 'password1' not in data:
            data['password1'] = data['password']
            data['password2'] = data['password']
            
        form = CustomUserCreationForm(data)
        if form.is_valid():
            user = form.save()
            login(request, user)
            
            redirect_name = 'teacher_dashboard' if user.role == 'teacher' else 'dashboard'
            return redirect(redirect_name)
        
    return render(request, 'alis_app/login.html', {'tab': 'signup'})

def login_view(request):
    if request.method == 'POST':
        email = request.POST.get('username')
        password = request.POST.get('password')
        
        user = authenticate(request, username=email, password=password)
        
        if user is not None:
            if not hasattr(user, 'backend'):
                user.backend = 'django.contrib.auth.backends.ModelBackend'
            
            login(request, user)
            request.session.save()
            
            user_role = getattr(user, 'role', 'student')
            if user_role == 'admin':
                return redirect('admin_dashboard')
            elif user_role == 'teacher':
                return redirect('teacher_dashboard')
            return redirect('dashboard')
        else:
            messages.error(request, "Please enter a correct email and password.")
            
    return render(request, 'alis_app/login.html', {'tab': 'login'})

def logout_view(request):
    print(f"\n[AUTH TRACE] >>> GET /logout/ for user: {request.user}")
    logout(request)
    return redirect('login')

@login_required
def student_dashboard(request):
    print(f"\n[AUTH TRACE] >>> Student Dashboard Access")
    
    user_role = getattr(request.user, 'role', 'student')
    if user_role == 'admin':
        return redirect('admin_dashboard')
    if user_role == 'teacher':
        return redirect('teacher_dashboard')
    
    # Core Data
    recommendations = IntelligenceService.get_recommendations(request.user)
    available_assessments = Assessment.objects.filter(is_published=True)
    study_plan = IntelligenceService.get_study_plan(request.user)
    
    # Advanced Metrics
    predictions = IntelligenceService.get_performance_predictions(request.user)
    career_index = IntelligenceService.get_career_index(request.user)
    history = AssessmentResult.objects.filter(student=request.user).order_by('-completed_at')[:5]
    chat_history = TutorMessage.objects.filter(student=request.user).order_by('timestamp')[:30]

    return render(request, 'alis_app/dashboard.html', {
        'recommendations': recommendations,
        'assessments': available_assessments,
        'study_plan': study_plan,
        'predictions': predictions,
        'career_index': career_index,
        'history': history,
        'chat_history': chat_history
    })

@csrf_exempt
@login_required
def voice_ai_api(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        query = data.get('query') or data.get('question', '')
        mode = data.get('mode', 'Beginner')
        
        if not query:
            return JsonResponse({'error': 'Empty question'}, status=400)

        # Save User Message
        TutorMessage.objects.create(student=request.user, role='user', content=query)
        
        # Generate Gemini Response
        answer = IntelligenceService.voice_ai_response(request.user, query, mode)
        
        # Save AI Message
        TutorMessage.objects.create(student=request.user, role='ai', content=answer)
        
        return JsonResponse({'answer': answer, 'response': answer}) # Return both for compatibility
    return JsonResponse({'error': 'Invalid request'}, status=400)

@login_required
def teacher_dashboard(request):
    print(f"\n[AUTH TRACE] >>> Teacher Dashboard Access")
    print(f" - User: {request.user.username}, Authenticated: {request.user.is_authenticated}, Role: {getattr(request.user, 'role', 'N/A')}")
    print(f" - Session Key: {request.session.session_key}")
    
    user_role = getattr(request.user, 'role', 'student')
    if user_role == 'admin':
        return redirect('admin_dashboard')
    if user_role != 'teacher':
        return redirect('dashboard')
    
    students = User.objects.filter(role='student')
    analytics = IntelligenceService.get_class_analytics(request.user)
    
    return render(request, 'alis_app/teacher-dashboard.html', {
        'students': students,
        'analytics': analytics
    })

@login_required
def admin_dashboard(request):
    print(f"\n[AUTH TRACE] >>> Admin Dashboard Access")
    print(f" - User: {request.user.username}, Authenticated: {request.user.is_authenticated}, Role: {getattr(request.user, 'role', 'N/A')}")
    print(f" - Session Key: {request.session.session_key}")
    
    user_role = getattr(request.user, 'role', 'student')
    if user_role != 'admin':
        print(f" - ROLE MISMATCH: User role is {user_role}, expected admin. Redirecting to student dashboard.")
        return redirect('dashboard')
    
    total_users = User.objects.count()
    total_assessments = Assessment.objects.count()
    total_results = AssessmentResult.objects.count()
    
    return render(request, 'alis_app/teacher-dashboard.html', {
        'is_admin': True,
        'total_users': total_users,
        'total_assessments': total_assessments,
        'total_results': total_results
    })

@login_required
def student_profile(request, student_id):
    if request.user.role != 'teacher':
        return redirect('dashboard')
    
    student = get_object_or_404(User, id=student_id, role='student')
    results = student.assessment_results.all().order_by('-completed_at')
    
    return render(request, 'alis_app/student-profile.html', {
        'student': student,
        'results': results
    })

@login_required
def quiz_view(request, assessment_id=None):
    if assessment_id:
        assessment = get_object_or_404(Assessment, id=assessment_id, is_published=True)
        return render(request, 'alis_app/quiz.html', {'assessment': assessment})
    return render(request, 'alis_app/quiz.html')

@csrf_exempt
@login_required
def save_quiz_result(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        assessment_id = data.get('assessment_id')
        answers = data.get('answers')
        
        if assessment_id and answers:
            assessment = get_object_or_404(Assessment, id=assessment_id)
            result = IntelligenceService.process_assessment_result(request.user, assessment, answers)
            return JsonResponse({
                'status': 'success',
                'score': result.score,
                'level': request.user.level
            })
        
        # Fallback for old hardcoded quiz if needed (or just deprecate)
        return JsonResponse({'status': 'failed', 'message': 'Missing data'}, status=400)
    return JsonResponse({'status': 'failed'}, status=400)

@login_required
def create_assessment(request):
    if request.user.role != 'teacher':
        return redirect('dashboard')
        
    if request.method == 'POST':
        # Simplified creation for prototype
        title = request.POST.get('title')
        subject_id = request.POST.get('subject')
        difficulty = request.POST.get('difficulty')
        
        subject = get_object_or_404(Subject, id=subject_id)
        assessment = Assessment.objects.create(
            teacher=request.user,
            subject=subject,
            title=title,
            difficulty=difficulty,
            is_published=True
        )
        messages.success(request, f"Assessment '{title}' published successfully.")
        return redirect('teacher_dashboard')
        
    subjects = Subject.objects.all()
    return render(request, 'alis_app/create-assessment.html', {'subjects': subjects})

@login_required
def get_assessment_questions(request, assessment_id):
    assessment = get_object_or_404(Assessment, id=assessment_id)
    questions = assessment.questions.all()
    data = []
    for q in questions:
        data.append({
            'id': q.id,
            'text': q.text,
            'options': [q.option_a, q.option_b, q.option_c, q.option_d],
            'difficulty': q.difficulty,
            'concept': q.concept.name if q.concept else "General"
        })
    return JsonResponse({'questions': data})
