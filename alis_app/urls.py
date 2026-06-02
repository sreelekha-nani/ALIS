from django.urls import path
from . import views

urlpatterns = [
    path('', views.intro_view, name='intro'),
    path('marketing/', views.index_view, name='index'),
    path('showcase/', views.showcase_view, name='showcase'),
    path('login/', views.login_view, name='login'),
    path('register/', views.register_view, name='register'),
    path('logout/', views.logout_view, name='logout'),
    
    # Student Dashboard
    path('dashboard/', views.student_dashboard, name='dashboard'),
    
    # Teacher Dashboard
    path('teacher-dashboard/', views.teacher_dashboard, name='teacher_dashboard'),
    path('admin-dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('student-profile/<int:student_id>/', views.student_profile, name='student_profile'),
    path('create-assessment/', views.create_assessment, name='create_assessment'),
    
    # Assessment Engine
    path('quiz/', views.quiz_view, name='quiz'),
    path('quiz/<int:assessment_id>/', views.quiz_view, name='quiz_detail'),
    path('api/questions/<int:assessment_id>/', views.get_assessment_questions, name='api_questions'),
    path('save-quiz-result/', views.save_quiz_result, name='save_quiz_result'),
    path('api/ai-tutor/', views.voice_ai_api, name='ai_tutor_api'),
]
