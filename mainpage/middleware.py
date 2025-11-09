
import logging
from .models import studentInfo
from .models.alumni import Alumni, graduateForm

logger = logging.getLogger(__name__)

class AlumniStatusMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Set default values for all users
        request.is_alumni_approved = False
        request.has_filled_tracer = False

        logger.debug("AlumniStatusMiddleware START path=%s user=%s authenticated=%s",
                     request.path,
                     getattr(request, 'user', None),
                     getattr(request.user, 'is_authenticated', False))

        # Check only if the user is logged in
        if getattr(request.user, 'is_authenticated', False):
            try:
                # 1. Find the student record
                student = studentInfo.objects.get(studID=int(request.user.username))

                # 2. Check if they are an APPROVED alumnus
                alumni = Alumni.objects.get(student=student, approved=True)
                request.is_alumni_approved = True

                # 3. If they are, check if they have filled the tracer form
                request.has_filled_tracer = graduateForm.objects.filter(student=student).exists()

            except (studentInfo.DoesNotExist, Alumni.DoesNotExist, ValueError, TypeError) as e:
                logger.debug("AlumniStatusMiddleware lookup failed: %s", e)

        logger.debug("AlumniStatusMiddleware END path=%s is_alumni_approved=%s has_filled_tracer=%s",
                     request.path, request.is_alumni_approved, request.has_filled_tracer)

        response = self.get_response(request)
        return response
# ...existing code...