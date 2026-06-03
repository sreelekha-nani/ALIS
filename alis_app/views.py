from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from .forms import CustomUserCreationForm, CustomAuthenticationForm
from .models import User, Assessment, Question, Subject, Concept, RecommendationItem, AssessmentResult, TutorMessage, ClassGroup, Assignment, PlatformMetric
from django.contrib import messages
from django.http import JsonResponse
from django.utils import timezone
import json
from django.views.decorators.csrf import csrf_exempt
from .services.intelligence import IntelligenceService
from .decorators import student_required, teacher_required, admin_required, owner_required

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
            destination = 'dashboard'
            if user_role == 'admin':
                destination = 'admin_dashboard'
            elif user_role == 'teacher':
                destination = 'teacher_dashboard'
            elif user_role == 'owner':
                destination = 'owner_dashboard'

            print("LOGIN SUCCESS:", user.email)
            print("USER ROLE:", user.role)
            print("REDIRECTING TO:", destination)
            
            return redirect(destination)
        else:
            messages.error(request, "Please enter a correct email and password.")
            
    return render(request, 'alis_app/login.html', {'tab': 'login'})

def logout_view(request):
    print(f"\n[AUTH TRACE] >>> GET /logout/ for user: {request.user}")
    logout(request)
    return redirect('login')

@login_required
@student_required
def student_dashboard(request):
    # Core Data
    available_assessments = Assessment.objects.filter(is_published=True)
    results = AssessmentResult.objects.filter(student=request.user).order_by('-completed_at')
    
    # Summary Metrics
    stats = {
        'dna_score': request.user.retention_score,
        'ai_readiness': request.user.technical_readiness,
        'completed_count': results.count(),
        'avg_score': sum(r.score for r in results) / results.count() if results.exists() else 0,
        'streak': request.user.streak_days,
    }

    # Study Planner Summary (Mock for now)
    planner_summary = [
        {'title': 'Quantum Physics Quiz', 'time': '2:00 PM'},
        {'title': 'Chemistry Lab Report', 'time': '4:30 PM'},
    ]

    return render(request, 'alis_app/dashboard.html', {
        'assessments': available_assessments,
        'stats': stats,
        'planner_summary': planner_summary,
        'history': results[:5],
    })

@login_required
@student_required
def study_planner_view(request):
    daily_tasks = [
        {'title': 'Advanced Calculus Practice', 'subject': 'Mathematics', 'duration': '45m', 'time': '10:00 AM'},
        {'title': 'Organic Chemistry Review', 'subject': 'Science', 'duration': '1h 20m', 'time': '1:30 PM'},
        {'title': 'History of AI Lecture', 'subject': 'Computer Science', 'duration': '30m', 'time': '4:00 PM'},
    ]
    return render(request, 'alis_app/study_planner.html', {
        'daily_tasks': daily_tasks
    })

@login_required
@student_required
def resources_view(request):
    resource_categories = [
        {
            'name': 'Mathematics',
            'items': [
                {'title': 'Calculus III Notes', 'type': 'PDF', 'size_or_duration': '2.4 MB', 'url': '#'},
                {'title': 'Linear Algebra Bootcamp', 'type': 'Video', 'size_or_duration': '45:00', 'url': '#'},
            ]
        },
        {
            'name': 'Physics',
            'items': [
                {'title': 'Quantum Mechanics Intro', 'type': 'PDF', 'size_or_duration': '1.8 MB', 'url': '#'},
                {'title': 'Thermodynamics Laws', 'type': 'Note', 'size_or_duration': '15 KB', 'url': '#'},
            ]
        }
    ]
    return render(request, 'alis_app/resources.html', {
        'resource_categories': resource_categories
    })

@login_required
@student_required
def achievements_view(request):
    earned_badges = [
        {'name': 'Fast Learner', 'icon': '⚡', 'date': 'May 12, 2026'},
        {'name': 'Quiz Master', 'icon': '🏆', 'date': 'May 20, 2026'},
        {'name': '7-Day Streak', 'icon': '🔥', 'date': 'June 01, 2026'},
    ]
    return render(request, 'alis_app/achievements.html', {
        'earned_badges': earned_badges
    })

@login_required
def settings_view(request):
    return render(request, 'alis_app/settings.html')

@login_required
def ai_tutor_view(request):
    chat_history = TutorMessage.objects.filter(student=request.user).order_by('timestamp')[:50]
    return render(request, 'alis_app/ai_tutor.html', {
        'chat_history': chat_history
    })

@login_required
def analytics_view(request):
    history = AssessmentResult.objects.filter(student=request.user).order_by('-completed_at')
    return render(request, 'alis_app/analytics.html', {
        'history': history
    })

@login_required
def learning_dna_view(request):
    return render(request, 'alis_app/learning_dna.html')

@csrf_exempt
@login_required
def voice_ai_api(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            query = data.get('query') or data.get('question', '')
            mode = data.get('mode', 'Beginner')
            
            if not query:
                return JsonResponse({'error': 'Empty question'}, status=400)

            # Fetch Conversation History (Last 10 messages for context)
            history = list(TutorMessage.objects.filter(student=request.user).order_by('-timestamp')[:10])
            history.reverse() # Restore chronological order

            print(f"[VOICE_AI] User: {request.user.username} | Query: {query}")
            
            # Save User Message
            TutorMessage.objects.create(student=request.user, role='user', content=query)
            
            # Generate Gemini Response
            answer = IntelligenceService.voice_ai_response(request.user, query, mode, history=history)
            
            # Save AI Message
            TutorMessage.objects.create(student=request.user, role='ai', content=answer)
            
            print(f"[VOICE_AI] AI Response: {answer[:100]}...")
            
            return JsonResponse({'answer': answer, 'response': answer})
        except Exception as e:
            print(f"[VOICE_AI] Error: {str(e)}")
            return JsonResponse({'error': str(e)}, status=500)
            
    return JsonResponse({'error': 'Invalid request'}, status=400)

@login_required
@teacher_required
def teacher_dashboard(request):
    students = User.objects.filter(role='student')
    classes = ClassGroup.objects.filter(teacher=request.user)
    assignments = Assignment.objects.filter(teacher=request.user)
    assessments = Assessment.objects.filter(teacher=request.user)
    
    # Summary Metrics
    stats = {
        'total_students': students.count(),
        'active_students': students.filter(last_activity_date__gte=timezone.now().date() - timezone.timedelta(days=7)).count(),
        'assessment_count': assessments.count(),
        'assignment_count': assignments.count(),
    }

    return render(request, 'alis_app/teacher-dashboard.html', {
        'students': students[:5],
        'stats': stats,
        'classes': classes,
        'assignments': assignments,
    })

@login_required
@teacher_required
def teacher_students(request):
    students = User.objects.filter(role='student')
    return render(request, 'alis_app/teacher_students.html', {
        'students': students
    })

@login_required
@teacher_required
def teacher_classes(request):
    classes = ClassGroup.objects.filter(teacher=request.user)
    return render(request, 'alis_app/teacher_classes.html', {
        'classes': classes
    })

@login_required
@teacher_required
def teacher_assignments(request):
    assignments = Assignment.objects.filter(teacher=request.user)
    return render(request, 'alis_app/teacher_assignments.html', {
        'assignments': assignments
    })

@login_required
@admin_required
def admin_dashboard(request):
    total_users = User.objects.count()
    student_count = User.objects.filter(role='student').count()
    teacher_count = User.objects.filter(role='teacher').count()
    
    stats = {
        'total_users': total_users,
        'student_count': student_count,
        'teacher_count': teacher_count,
        'active_sessions': total_users // 3, # Mock for prototype
    }

    logs = [
        {'timestamp': timezone.now() - timezone.timedelta(minutes=5), 'message': 'New teacher account approved: dr_smith@alis.ai'},
        {'timestamp': timezone.now() - timezone.timedelta(minutes=45), 'message': 'Bulk course upload successful: Quantum Physics 101'},
        {'timestamp': timezone.now() - timezone.timedelta(hours=2), 'message': 'System backup completed successfully.'},
    ]

    return render(request, 'alis_app/admin_dashboard.html', {
        'stats': stats,
        'logs': logs
    })

@login_required
@owner_required
def owner_dashboard(request):
    # Simulated Executive Data
    metrics = PlatformMetric.objects.first()
    
    return render(request, 'alis_app/owner_dashboard.html', {
        'metrics': metrics
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

# ==========================================
# PHASE 1: GENERIC DASHBOARDS FOR OTHER ROLES
# ==========================================

# --- TEACHER VIEWS ---
@login_required
@teacher_required
def teacher_performance(request): return render(request, 'alis_app/generic_dashboard.html', {'page_title': 'Performance Reports'})

@login_required
@teacher_required
def teacher_ai_insights(request): return render(request, 'alis_app/generic_dashboard.html', {'page_title': 'AI Insights'})

@login_required
@teacher_required
def teacher_analytics(request): return render(request, 'alis_app/generic_dashboard.html', {'page_title': 'Learning Analytics'})

# --- ADMIN VIEWS ---
@login_required
@admin_required
def admin_users(request): return render(request, 'alis_app/generic_dashboard.html', {'page_title': 'Manage Users'})

@login_required
@admin_required
def admin_students(request): return render(request, 'alis_app/generic_dashboard.html', {'page_title': 'Manage Students'})

@login_required
@admin_required
def admin_teachers(request): return render(request, 'alis_app/generic_dashboard.html', {'page_title': 'Manage Teachers'})

@login_required
@admin_required
def admin_courses(request): return render(request, 'alis_app/generic_dashboard.html', {'page_title': 'Manage Courses'})

@login_required
@admin_required
def admin_assessments(request): return render(request, 'alis_app/generic_dashboard.html', {'page_title': 'Manage Assessments'})

@login_required
@admin_required
def admin_reports(request): return render(request, 'alis_app/generic_dashboard.html', {'page_title': 'Platform Reports'})

@login_required
@admin_required
def admin_analytics(request): return render(request, 'alis_app/generic_dashboard.html', {'page_title': 'Platform Analytics'})

@login_required
@admin_required
def admin_ai_monitoring(request): return render(request, 'alis_app/generic_dashboard.html', {'page_title': 'AI Monitoring'})

@login_required
@admin_required
def admin_settings(request): return render(request, 'alis_app/settings.html', {'page_title': 'Admin Settings'})

# --- OWNER VIEWS ---
@login_required
@owner_required
def owner_org_analytics(request): return render(request, 'alis_app/generic_dashboard.html', {'page_title': 'Organization Analytics'})

@login_required
@owner_required
def owner_revenue(request): return render(request, 'alis_app/generic_dashboard.html', {'page_title': 'Revenue Insights'})

@login_required
@owner_required
def owner_growth(request): return render(request, 'alis_app/generic_dashboard.html', {'page_title': 'User Growth'})

@login_required
@owner_required
def owner_platform_monitoring(request): return render(request, 'alis_app/generic_dashboard.html', {'page_title': 'Platform Monitoring'})

@login_required
@owner_required
def owner_ai_center(request): return render(request, 'alis_app/generic_dashboard.html', {'page_title': 'AI Intelligence Center'})

@login_required
@owner_required
def owner_system_health(request): return render(request, 'alis_app/generic_dashboard.html', {'page_title': 'System Health'})

@login_required
@owner_required
def owner_security(request): return render(request, 'alis_app/generic_dashboard.html', {'page_title': 'Security Center'})

@login_required
@owner_required
def owner_settings(request): return render(request, 'alis_app/settings.html', {'page_title': 'Owner Settings'})
