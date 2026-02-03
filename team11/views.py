import json
from django.http import JsonResponse
from django.shortcuts import render, get_object_or_404
from django.views.decorators.http import require_POST, require_http_methods
from django.views.decorators.csrf import csrf_exempt
from core.auth import api_login_required
from .models import (
    Submission, WritingSubmission, ListeningSubmission, 
    AssessmentResult, SubmissionType, AnalysisStatus
)

TEAM_NAME = "team11"

# Static questions for now
WRITING_TOPICS = [
    "Describe your favorite holiday destination and explain why you enjoy it.",
    "What are the advantages and disadvantages of working from home?",
    "Discuss the impact of social media on modern communication.",
]

LISTENING_TOPICS = [
    "Describe a memorable experience from your childhood.",
    "Talk about your career goals and how you plan to achieve them.",
    "Explain the importance of learning a foreign language.",
]


@api_login_required
def ping(request):
    return JsonResponse({"team": TEAM_NAME, "ok": True})


def base(request):
    """Landing page for Team 11 microservice"""
    return render(request, f"{TEAM_NAME}/index.html")


@api_login_required
def dashboard(request):
    """Dashboard showing user's submission history"""
    user_id = request.user.id
    
    # Get all submissions for the user
    submissions = Submission.objects.filter(user_id=user_id).select_related(
        'assessment_result'
    ).prefetch_related('writing_details', 'listening_details')
    
    context = {
        'submissions': submissions,
    }
    return render(request, f"{TEAM_NAME}/dashboard.html", context)


@api_login_required
def start_exam(request):
    """Page to select exam type (writing or listening)"""
    context = {
        'writing_topics': WRITING_TOPICS,
        'listening_topics': LISTENING_TOPICS,
    }
    return render(request, f"{TEAM_NAME}/start_exam.html", context)


@api_login_required
def writing_exam(request):
    """Page for writing exam"""
    topic_index = int(request.GET.get('topic', 0))
    topic = WRITING_TOPICS[topic_index] if 0 <= topic_index < len(WRITING_TOPICS) else WRITING_TOPICS[0]
    
    context = {
        'topic': topic,
        'topic_index': topic_index,
    }
    return render(request, f"{TEAM_NAME}/writing_exam.html", context)


@api_login_required
def listening_exam(request):
    """Page for listening exam"""
    topic_index = int(request.GET.get('topic', 0))
    topic = LISTENING_TOPICS[topic_index] if 0 <= topic_index < len(LISTENING_TOPICS) else LISTENING_TOPICS[0]
    
    context = {
        'topic': topic,
        'topic_index': topic_index,
    }
    return render(request, f"{TEAM_NAME}/listening_exam.html", context)


@csrf_exempt
@require_POST
@api_login_required
def submit_writing(request):
    """API endpoint to submit writing task"""
    try:
        data = json.loads(request.body)
        topic = data.get('topic', '')
        text_body = data.get('text_body', '')
        
        if not text_body:
            return JsonResponse({'error': 'Text body is required'}, status=400)
        
        word_count = len(text_body.split())
        
        # Create submission
        submission = Submission.objects.create(
            user_id=request.user.id,
            submission_type=SubmissionType.WRITING,
            overall_score=90.0,  # Static score for now
            status=AnalysisStatus.COMPLETED
        )
        
        # Create writing details
        WritingSubmission.objects.create(
            submission=submission,
            topic=topic,
            text_body=text_body,
            word_count=word_count
        )
        
        # Create assessment result
        AssessmentResult.objects.create(
            submission=submission,
            grammar_score=90.0,
            vocabulary_score=90.0,
            coherence_score=90.0,
            fluency_score=90.0,
            feedback_summary="Great work! Your writing demonstrates good command of the language.",
            suggestions=[
                "Try to use more complex sentence structures",
                "Expand your vocabulary with synonyms",
                "Pay attention to paragraph transitions"
            ]
        )
        
        return JsonResponse({
            'success': True,
            'submission_id': str(submission.submission_id),
            'score': 90.0,
            'message': 'Writing submitted successfully'
        })
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@csrf_exempt
@require_POST
@api_login_required
def submit_listening(request):
    """API endpoint to submit listening (audio) task"""
    try:
        data = json.loads(request.body)
        topic = data.get('topic', '')
        audio_url = data.get('audio_url', '')
        duration = data.get('duration_seconds', 0)
        
        if not audio_url:
            return JsonResponse({'error': 'Audio URL is required'}, status=400)
        
        # Create submission
        submission = Submission.objects.create(
            user_id=request.user.id,
            submission_type=SubmissionType.LISTENING,
            overall_score=90.0,  # Static score for now
            status=AnalysisStatus.COMPLETED
        )
        
        # Create listening details
        ListeningSubmission.objects.create(
            submission=submission,
            topic=topic,
            audio_file_url=audio_url,
            duration_seconds=duration
        )
        
        # Create assessment result
        AssessmentResult.objects.create(
            submission=submission,
            pronunciation_score=90.0,
            fluency_score=90.0,
            vocabulary_score=90.0,
            grammar_score=90.0,
            coherence_score=90.0,
            feedback_summary="Excellent speaking performance! Your pronunciation is clear.",
            suggestions=[
                "Work on your intonation patterns",
                "Try to speak more naturally",
                "Reduce filler words like 'um' and 'uh'"
            ]
        )
        
        return JsonResponse({
            'success': True,
            'submission_id': str(submission.submission_id),
            'score': 90.0,
            'message': 'Audio submitted successfully'
        })
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@api_login_required
def submission_detail(request, submission_id):
    """View detailed results for a specific submission"""
    submission = get_object_or_404(
        Submission.objects.select_related('assessment_result'),
        submission_id=submission_id,
        user_id=request.user.id
    )
    
    # Get type-specific details
    details = None
    if submission.submission_type == SubmissionType.WRITING:
        details = WritingSubmission.objects.filter(submission=submission).first()
    else:
        details = ListeningSubmission.objects.filter(submission=submission).first()
    
    context = {
        'submission': submission,
        'details': details,
        'result': submission.assessment_result,
    }
    return render(request, f"{TEAM_NAME}/submission_detail.html", context)