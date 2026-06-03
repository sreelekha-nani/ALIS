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
    path('ai-tutor/', views.ai_tutor_view, name='ai_tutor'),
    path('analytics/', views.analytics_view, name='analytics'),
    path('learning-dna/', views.learning_dna_view, name='learning_dna'),
    path('study-planner/', views.study_planner_view, name='study_planner'),
    path('resources/', views.resources_view, name='resources'),
    path('achievements/', views.achievements_view, name='achievements'),
    path('settings/', views.settings_view, name='settings'),
    
    # Teacher Routes
    path('teacher-dashboard/', views.teacher_dashboard, name='teacher_dashboard'),
    path('teacher/students/', views.teacher_students, name='teacher_students'),
    path('teacher/classes/', views.teacher_classes, name='teacher_classes'),
    path('teacher/assignments/', views.teacher_assignments, name='teacher_assignments'),
    path('teacher/performance/', views.teacher_performance, name='teacher_performance'),
    path('teacher/ai-insights/', views.teacher_ai_insights, name='teacher_ai_insights'),
    path('teacher/analytics/', views.teacher_analytics, name='teacher_analytics'),
    path('student-profile/<int:student_id>/', views.student_profile, name='student_profile'),
    path('create-assessment/', views.create_assessment, name='create_assessment'),
    
    # Admin Routes
    path('admin-dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('admin/users/', views.admin_users, name='admin_users'),
    path('admin/students/', views.admin_students, name='admin_students'),
    path('admin/teachers/', views.admin_teachers, name='admin_teachers'),
    path('admin/courses/', views.admin_courses, name='admin_courses'),
    path('admin/assessments/', views.admin_assessments, name='admin_assessments'),
    path('admin/reports/', views.admin_reports, name='admin_reports'),
    path('admin/analytics/', views.admin_analytics, name='admin_analytics'),
    path('admin/ai-monitoring/', views.admin_ai_monitoring, name='admin_ai_monitoring'),
    path('admin/settings/', views.admin_settings, name='admin_settings'),
    
    # Owner Routes
    path('owner-dashboard/', views.owner_dashboard, name='owner_dashboard'),
    path('owner/org-analytics/', views.owner_org_analytics, name='owner_org_analytics'),
    path('owner/revenue/', views.owner_revenue, name='owner_revenue'),
    path('owner/growth/', views.owner_growth, name='owner_growth'),
    path('owner/platform-monitoring/', views.owner_platform_monitoring, name='owner_platform_monitoring'),
    path('owner/ai-center/', views.owner_ai_center, name='owner_ai_center'),
    path('owner/system-health/', views.owner_system_health, name='owner_system_health'),
    path('owner/security/', views.owner_security, name='owner_security'),
    path('owner/settings/', views.owner_settings, name='owner_settings'),

    # Assessment Engine
    path('quiz/', views.quiz_view, name='quiz'),
    path('quiz/<int:assessment_id>/', views.quiz_view, name='quiz_detail'),
    path('api/questions/<int:assessment_id>/', views.get_assessment_questions, name='api_questions'),
    path('save-quiz-result/', views.save_quiz_result, name='save_quiz_result'),
    path('api/ai-tutor/', views.voice_ai_api, name='ai_tutor_api'),
]
