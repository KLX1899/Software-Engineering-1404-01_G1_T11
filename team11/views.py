import json
import os
import logging
from django.http import JsonResponse
from django.shortcuts import render, get_object_or_404
from django.views.decorators.http import require_POST, require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
from core.auth import api_login_required
from .models import (
    Submission, WritingSubmission, ListeningSubmission, 
    AssessmentResult, SubmissionType, AnalysisStatus
)
from .services import assess_writing, assess_speaking

logger = logging.getLogger(__name__)

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
        
        # Create submission with pending status
        submission = Submission.objects.create(
            user_id=request.user.id,
            submission_type=SubmissionType.WRITING,
            status=AnalysisStatus.IN_PROGRESS
        )
        
        # Create writing details
        WritingSubmission.objects.create(
            submission=submission,
            topic=topic,
            text_body=text_body,
            word_count=word_count
        )
        
        logger.info(f"Processing writing submission {submission.submission_id} for user {request.user.id}")
        
        # Assess the writing using AI
        assessment_result = assess_writing(topic, text_body, word_count)
        
        if assessment_result['success']:
            # Update submission with overall score and completed status
            submission.overall_score = assessment_result['overall_score']
            submission.status = AnalysisStatus.COMPLETED
            submission.save()
            
            # Create assessment result
            AssessmentResult.objects.create(
                submission=submission,
                grammar_score=assessment_result['grammar_score'],
                vocabulary_score=assessment_result['vocabulary_score'],
                coherence_score=assessment_result['coherence_score'],
                fluency_score=assessment_result['fluency_score'],
                feedback_summary=assessment_result['feedback_summary'],
                suggestions=assessment_result['suggestions']
            )
            
            logger.info(f"Writing assessment completed: {submission.submission_id}, score: {submission.overall_score}")
            
            return JsonResponse({
                'success': True,
                'submission_id': str(submission.submission_id),
                'score': submission.overall_score,
                'message': 'Writing submitted and assessed successfully'
            })
        else:
            # Mark as failed
            submission.status = AnalysisStatus.FAILED
            submission.save()
            
            logger.error(f"Writing assessment failed: {submission.submission_id}, error: {assessment_result.get('error')}")
            
            return JsonResponse({
                'success': False,
                'submission_id': str(submission.submission_id),
                'error': assessment_result.get('error', 'Assessment failed'),
                'message': 'Submission saved but assessment failed. Please try again.'
            }, status=500)
        
    except Exception as e:
        logger.error(f"Error in submit_writing: {e}", exc_info=True)
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
        
        # Create submission with pending status
        submission = Submission.objects.create(
            user_id=request.user.id,
            submission_type=SubmissionType.LISTENING,
            status=AnalysisStatus.IN_PROGRESS
        )
        
        # Create listening details (without transcription initially)
        listening_detail = ListeningSubmission.objects.create(
            submission=submission,
            topic=topic,
            audio_file_url=audio_url,
            duration_seconds=duration
        )
        
        logger.info(f"Processing listening submission {submission.submission_id} for user {request.user.id}")
        
        # Convert URL to file path for processing
        # Assuming audio_url is a relative path or we need to download it
        # For now, we'll assume it's a local path accessible to the server
        if audio_url.startswith('http://') or audio_url.startswith('https://'):
            # For remote URLs, you would need to download the file first
            # This is a simplified version
            logger.warning(f"Remote audio URL provided: {audio_url}. Download logic needed.")
            audio_file_path = audio_url  # Placeholder - needs implementation
        else:
            # Local file path (relative to MEDIA_ROOT or absolute)
            if not audio_url.startswith('/') and not audio_url[1:3] == ':\\':
                # Relative path - join with MEDIA_ROOT
                audio_file_path = os.path.join(settings.MEDIA_ROOT, audio_url)
            else:
                audio_file_path = audio_url
        
        # Assess the speaking using AI (transcription + assessment)
        assessment_result = assess_speaking(topic, audio_file_path, duration)
        
        if assessment_result['success']:
            # Update listening detail with transcription
            listening_detail.transcription = assessment_result.get('transcription', '')
            listening_detail.save()
            
            # Update submission with overall score and completed status
            submission.overall_score = assessment_result['overall_score']
            submission.status = AnalysisStatus.COMPLETED
            submission.save()
            
            # Create assessment result
            AssessmentResult.objects.create(
                submission=submission,
                pronunciation_score=assessment_result['pronunciation_score'],
                fluency_score=assessment_result['fluency_score'],
                vocabulary_score=assessment_result['vocabulary_score'],
                grammar_score=assessment_result['grammar_score'],
                coherence_score=assessment_result['coherence_score'],
                feedback_summary=assessment_result['feedback_summary'],
                suggestions=assessment_result['suggestions']
            )
            
            logger.info(f"Speaking assessment completed: {submission.submission_id}, score: {submission.overall_score}")
            
            return JsonResponse({
                'success': True,
                'submission_id': str(submission.submission_id),
                'score': submission.overall_score,
                'transcription': assessment_result.get('transcription', ''),
                'message': 'Audio submitted and assessed successfully'
            })
        else:
            # Mark as failed
            submission.status = AnalysisStatus.FAILED
            submission.save()
            
            logger.error(f"Speaking assessment failed: {submission.submission_id}, error: {assessment_result.get('error')}")
            
            return JsonResponse({
                'success': False,
                'submission_id': str(submission.submission_id),
                'error': assessment_result.get('error', 'Assessment failed'),
                'message': 'Submission saved but assessment failed. Please try again.'
            }, status=500)
        
    except Exception as e:
        logger.error(f"Error in submit_listening: {e}", exc_info=True)
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