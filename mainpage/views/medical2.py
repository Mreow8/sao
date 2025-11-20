# Standard library imports
import json
import re
import random
import uuid
from django.core.exceptions import FieldError
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from ..decorators import profile_complete_required
import os
from django.db import IntegrityError
import calendar
import csv
from datetime import datetime, date, timedelta
from ..models import staffInfo as Faculty
# Django imports
from django.conf import settings
from django.contrib import messages
from django.contrib.auth import get_user_model, authenticate, login, logout
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.messages import get_messages
from django.core.mail import send_mail
from django.db import models
from django.db.models import Q
from django.http import JsonResponse, HttpResponse, Http404, HttpResponseForbidden
from django.shortcuts import render, redirect, get_object_or_404
from django.template.loader import render_to_string
from django.urls import reverse
from django.utils import timezone
from django.utils.crypto import get_random_string
from django.views.decorators.csrf import ensure_csrf_cookie
from django.views.decorators.http import require_http_methods

# Local application imports
from ..forms import UploadFileForm
from ..models import (
    studentInfo,
    staffInfo,
    SystemSettings,
    EmailVerification,
    Patient,
    PhysicalExamination,
    MedicalHistory,
    FamilyMedicalHistory,
    RiskAssessment,
    MentalHealthRecord,FacultyRequest,
    PatientRequest,
    DentalRecords,
    PrescriptionRecord,
    EmergencyHealthAssistanceRecord,
    MedicalRequirement,
    EligibilityForm,
    MedicalCertificate
)
from ..views import can_access_medical_admin
from utils import send_verification_email, send_password_reset_email

# Get the User model
User = get_user_model()


# @ensure_csrf_cookie
# def login_view(request):
#     if request.method == 'POST':
#         username = request.POST.get('email')
#         password = request.POST.get('password')
#         next_url = request.POST.get('next', '')

#         user = authenticate(request, username=username, password=password)
        
#         if user is None:
#             try:
#                 user_obj = User.objects.get(email=username)
#                 user = authenticate(request, username=user_obj.username, password=password)
#             except User.DoesNotExist:
#                 user = None

#         if user is not None:
#             # Check if OTP verification is required
#             system_settings = SystemSettings.get_settings()
            
#             if system_settings.require_otp_verification:
#                 # Generate and send OTP for login
#                 try:
#                     verification = EmailVerification.objects.get(user=user)
#                 except EmailVerification.DoesNotExist:
#                     verification = EmailVerification.objects.create(user=user)
                
#                 # Generate new OTP
#                 otp = ''.join([str(random.randint(0, 9)) for _ in range(6)])
#                 verification.otp = otp
#                 verification.created_at = timezone.now()
#                 verification.save()
                
#                 # Send verification email
#                 send_verification_email(user, verification)
                
#                 # Store email in session for OTP verification
#                 request.session['verification_email'] = user.email
                
#                 return JsonResponse({
#                     'status': 'success',
#                     'message': 'OTP sent to your email',
#                     'show_otp': True
#                 })
#             else:
#                 # OTP verification is disabled, log the user in directly
#                 login(request, user)
                
#                 # Determine redirect URL based on user role
#                 if user.is_superuser or user.is_staff:
#                     redirect_url = reverse('admin_dashboard')
#                 else:
#                     redirect_url = reverse('main')
                
#                 return JsonResponse({
#                     'status': 'success',
#                     'message': 'Login successful',
#                     'redirect_url': redirect_url
#                 })
#         else:
#             return JsonResponse({
#                 'status': 'error',
#                 'message': 'Invalid ID number/Email or password'
#             })

#     # Get messages and convert them to a list of dictionaries
#     messages_list = []
#     for message in get_messages(request):
#         messages_list.append({
#             'message': message.message,
#             'tags': message.tags
#         })

#     return render(request, 'login.html', {
#         'messages': messages_list,
#         'next': request.GET.get('next', '')
#     })


def resend_verification(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        try:
            user = User.objects.get(email=email)
            verification, created = EmailVerification.objects.get_or_create(user=user)
            
            if not created and verification.is_verified:
                messages.info(request, 'Email is already verified.')
                return redirect('login')
            
            # Generate new OTP
            otp = ''.join([str(random.randint(0, 9)) for _ in range(6)])
            
            # Update OTP and timestamp
            verification.otp = otp
            verification.created_at = timezone.now()
            verification.save()
            
            # Send new verification email
            send_verification_email(user, verification)
            
            messages.success(request, 'A new verification code has been sent.')
            return redirect('verify_otp')
            
        except User.DoesNotExist:
            messages.error(request, 'No account found with this email address.')
            return redirect('login')
    
    return render(request, 'resend_verification.html')

def recovery(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        try:
            user = User.objects.get(email=email)
            # Generate a unique token
            token = str(uuid.uuid4())
            # Store the token in the session
            request.session['reset_token'] = token
            request.session['reset_email'] = email
            
            # Send password reset email
            send_password_reset_email(user, token)
            
            # Return JSON response for success
            return JsonResponse({
                'status': 'success',
                'message': 'Password reset instructions have been sent to your email.'
            })
            
        except User.DoesNotExist:
            # Return JSON response for error (user not found)
            return JsonResponse({
                'status': 'error',
                'message': 'No account found with this email address.'
            })
        except Exception as e:
             # Return JSON response for other errors
            return JsonResponse({
                'status': 'error',
                'message': f'An error occurred: {str(e)}'
            })
            
    return render(request, 'recovery.html')

def password_reset(request, token):
    # First check if the session has the required data
    if not request.session.get('reset_token') or not request.session.get('reset_email'):
        return JsonResponse({
            'status': 'error',
            'message': 'Your password reset session has expired. Please request a new password reset link.'
        })

    if request.method == 'POST':
        try:
            new_password = request.POST.get('new_password')
            confirm_password = request.POST.get('confirm_password')
            
            if not new_password or not confirm_password:
                return JsonResponse({
                    'status': 'error',
                    'message': 'Both password fields are required.'
                })
            
            # Password validation
            password_errors = []
            
            # Check password length
            if len(new_password) < 8:
                password_errors.append('Password must be at least 8 characters long.')
            
            # Check for uppercase letter
            if not re.search(r'[A-Z]', new_password):
                password_errors.append('Password must contain at least one uppercase letter.')
            
            # Check for lowercase letter
            if not re.search(r'[a-z]', new_password):
                password_errors.append('Password must contain at least one lowercase letter.')
            
            # Check for digit
            if not re.search(r'\d', new_password):
                password_errors.append('Password must contain at least one number.')
            
            # Check for special character
            if not re.search(r'[!@#$%^&*(),.?":{}|<>]', new_password):
                password_errors.append('Password must contain at least one special character (!@#$%^&*(),.?":{}|<>).')
            
            # If there are password validation errors, return them
            if password_errors:
                return JsonResponse({
                    'status': 'error',
                    'message': 'Password validation failed:',
                    'errors': password_errors
                })
            
            if new_password != confirm_password:
                return JsonResponse({
                    'status': 'error',
                    'message': 'Passwords do not match.'
                })
            
            # Verify the token matches
            if request.session.get('reset_token') != token:
                return JsonResponse({
                    'status': 'error',
                    'message': 'Invalid or expired reset link. Please request a new password reset.'
                })

            # Get the email from session
            reset_email = request.session.get('reset_email')
            
            # Find the user with this email
            try:
                user = User.objects.get(email=reset_email)
            except User.DoesNotExist:
                return JsonResponse({
                    'status': 'error',
                    'message': 'User not found. Please request a new password reset.'
                })

            # Update the password
            user.set_password(new_password)
            user.save()
            
            # Clear the session
            del request.session['reset_token']
            del request.session['reset_email']
            
            # Return success response
            return JsonResponse({
                'status': 'success',
                'message': 'Your password has been reset successfully! You can now log in with your new password.',
                'redirect_url': reverse('login')
            })
        
        except Exception as e:
            print(f"Password reset error: {str(e)}")  # For debugging
            return JsonResponse({
                'status': 'error',
                'message': 'An error occurred while resetting your password. Please try again.'
            })
    
    # For GET requests, render the form
    return render(request, 'password-reset.html', {'token': token})

@login_required
def main_view(request):
    print(f"Entering main_view for user: {request.user.username}")

    profile_complete = False  # Assume incomplete

    try:
        patient = Patient.objects.get(user=request.user)
        print(f"Found patient record for {request.user.username}")

        # Check if related records exist
        try:
            physical_exam = patient.examination
            medical_history = physical_exam.medicalhistory
            family_history = physical_exam.familymedicalhistory
            risk_assessment = RiskAssessment.objects.get(clearance=patient)

            # If we reach here → all good
            profile_complete = True
            print("Profile is complete")

        except Exception as e:
            print(f"Incomplete profile for {request.user.username}: {e}")
            profile_complete = False

    except Patient.DoesNotExist:
        print(f"No patient record found for {request.user.username}")
        profile_complete = False

    # Decide where to go
    if not profile_complete:
        print("Redirecting to patient form due to incomplete profile")
        messages.info(request, 'Please complete your medical profile first.')
        return redirect('patient_form')

    print("Redirecting to dashboard")
    if hasattr(request.user, 'profile') and request.user.profile.role == 'Faculty':
        return redirect('faculty_dashboard')
    else:
        return redirect('student_dashboard')


@login_required
def patient_form(request):
    patient = None
    admin_initiated_patient_id = request.GET.get('patient_id')
    from_admin_register_flag = request.GET.get('from_admin_register') == 'true'

    if admin_initiated_patient_id and request.user.is_authenticated and (request.user.is_staff or request.user.is_superuser):
        try:
            patient = Patient.objects.get(id=admin_initiated_patient_id)
        except Patient.DoesNotExist:
            messages.error(request, 'Invalid patient ID provided for registration.')
            return redirect('admin_dashboard') # Redirect admin back if ID is bad
    else:
        try:
            patient, created = Patient.objects.get_or_create(user=request.user)

            if patient.student is None and patient.faculty is None:
                print(f"Patient record {patient.id} is unlinked. Trying to link...")
                try:
                    student_profile = studentInfo.objects.get(user=request.user)
                    patient.student = student_profile
                    patient.save()
                    print(f"Found and linked student profile: {student_profile.studID}")
                except studentInfo.DoesNotExist:
                    try:
                        faculty_profile = staffInfo.objects.get(user=request.user)
                        patient.faculty = faculty_profile
                        patient.save()
                        print(f"Found and linked faculty profile: {faculty_profile.staffID}")
                    except staffInfo.DoesNotExist:
                        print(f"No matching student or faculty profile found for user: {request.user.username}")

            if created:
                messages.info(request, "A new medical profile record has been created for your account. Please fill out the form.")

        except IntegrityError:
            messages.error(request, "Error: Multiple patient records found for your account. Please contact an administrator.")


    if patient is None:
        messages.error(request, 'Could not retrieve or create patient record.')
        return redirect('login')

    if request.method == 'GET':
        profile_complete = True # Assume complete initially, prove otherwise
        if patient.examination:
            try:
                physical_exam = patient.examination
                medical_history = physical_exam.medicalhistory
                family_history = physical_exam.familymedicalhistory
                risk_assessment = patient.riskassessment
            except (MedicalHistory.RelatedObjectDoesNotExist,
                    FamilyMedicalHistory.DoesNotExist,
                    RiskAssessment.DoesNotExist):
                profile_complete = False
            except Exception as e:
                print(f"PatientForm GET: Unexpected error checking related medical records: {e}")
                profile_complete = False
        else:
            profile_complete = False

        if profile_complete and not from_admin_register_flag:
            messages.info(request, 'Your medical profile is already complete.')
            if hasattr(request.user, 'profile') and request.user.profile.role == 'Faculty':
                return redirect('faculty_dashboard')
            else:
                return redirect('student_dashboard')

        today = date.today()
        context = {
            'current_date': today,
            'patient': patient,
            'is_admin_onboarding': from_admin_register_flag
        }
        return render(request, 'medical/medicalv2/patient_form.html', context)

    if request.method == 'POST':
        try:
            # Ensure we are working with the correct patient object for POST requests as well
            patient = None
            admin_initiated_patient_id = request.POST.get('patient_id')

            if admin_initiated_patient_id and request.user.is_authenticated and (request.user.is_staff or request.user.is_superuser):
                try:
                    patient = Patient.objects.get(id=admin_initiated_patient_id)
                    print(f"POST: Retrieved patient by ID for admin onboarding: {patient.id}")
                except Patient.DoesNotExist:
                    messages.error(request, 'Invalid patient ID provided for form submission.')
                    return JsonResponse({'status': 'error', 'message': 'Invalid patient ID for submission.'})
            else:
                try:
                    patient = Patient.objects.get(user=request.user)
                    print(f"POST: Retrieved patient for current user: {patient.id}")
                except Patient.DoesNotExist:
                    messages.error(request, 'Patient record not found for current user.')
                    return JsonResponse({'status': 'error', 'message': 'Patient record not found.'})
            
            if patient is None:
                messages.error(request, 'Could not determine patient record for submission.')
                return JsonResponse({'status': 'error', 'message': 'Could not determine patient record.'})

            patient.birth_date = request.POST.get('birth_date')
            patient.age = calculate_age(request.POST.get('birth_date')) if patient.birth_date else None
            patient.weight = float(request.POST.get('weight')) if request.POST.get('weight') else None
            patient.height = float(request.POST.get('height')) if request.POST.get('height') else None
            patient.bloodtype = request.POST.get('bloodtype')
            patient.allergies = process_checkboxes(request.POST.getlist('allergies'), request.POST.get('other_allergies'))
            patient.medications = request.POST.get('medications', '')
            patient.home_address = request.POST.get('home_address')
            patient.city = request.POST.get('city')
            patient.state_province = request.POST.get('state_province')
            patient.postal_zipcode = request.POST.get('postal_zipcode')
            patient.country = request.POST.get('country')
            patient.nationality = request.POST.get('nationality')
            patient.civil_status = request.POST.get('civil_status')
            num_children_str = request.POST.get('number_of_children')
            patient.number_of_children = int(num_children_str) if num_children_str and num_children_str.isdigit() else None

            if not patient.academic_year:
                patient.academic_year = f"{timezone.now().year}-{timezone.now().year + 1}"

            patient.section = request.POST.get('section', '')
            patient.parent_guardian = request.POST.get('parent_guardian')
            patient.parent_guardian_contact_number = request.POST.get('parent_guardian_contact', '')

            patient.save() # Save updated patient info first
            print(f"POST: Patient {patient.id} basic info saved.")

            # --- Physical Examination logic ---
            physical_exam, created_pe = PhysicalExamination.objects.get_or_create(patient=patient)
            print(f"POST: PhysicalExamination get_or_create - created: {created_pe}")
            exam_date_str = request.POST.get('date_of_physical_examination')
            if exam_date_str:
                physical_exam.date_of_physical_examination = exam_date_str
            else:
                if not physical_exam.date_of_physical_examination:
                    physical_exam.date_of_physical_examination = timezone.now().strftime('%Y-%m-%d')
            physical_exam.save()

            # Ensure the examination is linked to the patient
            if patient.examination != physical_exam:
                patient.examination = physical_exam
                patient.save() # Save patient again to establish the link if not already linked
                print(f"POST: Patient {patient.id} linked to PhysicalExamination {physical_exam.id}.")
            
            # --- Medical History logic ---
            med_hist_list = request.POST.getlist('medical_history')
            medical_history, created_mh = MedicalHistory.objects.get_or_create(examination=physical_exam)
            print(f"POST: MedicalHistory get_or_create - created: {created_mh}")
            medical_history.tuberculosis = 'tuberculosis' in med_hist_list
            medical_history.hypertension = 'hypertension' in med_hist_list
            medical_history.heart_disease = 'heart_disease' in med_hist_list
            medical_history.hernia = 'hernia' in med_hist_list
            medical_history.epilepsy = 'epilepsy' in med_hist_list
            medical_history.peptic_ulcer = 'peptic_ulcer' in med_hist_list
            medical_history.kidney_disease = 'kidney_disease' in med_hist_list
            medical_history.asthma = 'asthma' in med_hist_list
            medical_history.insomnia = 'insomnia' in med_hist_list
            medical_history.malaria = 'malaria' in med_hist_list
            medical_history.venereal_disease = 'venereal_disease' in med_hist_list
            medical_history.nervous_breakdown = 'nervous_breakdown' in med_hist_list
            medical_history.jaundice = 'jaundice' in med_hist_list
            medical_history.others = request.POST.get('other_medical', '')
            medical_history.no_history = 'No Medical History' in med_hist_list
            medical_history.save()
            print(f"POST: MedicalHistory {medical_history.id} saved.")

            # --- Family Medical History logic ---
            fam_hist_list = request.POST.getlist('family_history')
            family_history, created_fmh = FamilyMedicalHistory.objects.get_or_create(examination=physical_exam)
            print(f"POST: FamilyMedicalHistory get_or_create - created: {created_fmh}")
            family_history.hypertension = 'hypertension' in fam_hist_list
            family_history.asthma = 'asthma' in fam_hist_list
            family_history.cancer = 'cancer' in fam_hist_list
            family_history.tuberculosis = 'tuberculosis' in fam_hist_list
            family_history.diabetes = 'diabetes' in fam_hist_list
            family_history.bleeding_disorder = 'bleeding_disorder' in fam_hist_list
            family_history.epilepsy = 'epilepsy' in fam_hist_list
            family_history.mental_disorder = 'mental_disorder' in fam_hist_list
            family_history.no_history = 'No Family History' in fam_hist_list
            family_history.other_medical_history = request.POST.get('other_family_medical', '')
            family_history.save()
            print(f"POST: FamilyMedicalHistory {family_history.id} saved.")

            # --- Risk Assessment logic ---
            risk_list = request.POST.getlist('risk_assessment')
            risk_assessment, created_ra = RiskAssessment.objects.get_or_create(clearance=patient)
            print(f"POST: RiskAssessment get_or_create - created: {created_ra}")
            risk_assessment.cardiovascular_disease = 'cardiovascular' in risk_list
            risk_assessment.chronic_lung_disease = 'chronic_lung' in risk_list
            risk_assessment.chronic_renal_disease = 'chronic_kidney' in risk_list
            risk_assessment.chronic_liver_disease = 'chronic_liver' in risk_list
            risk_assessment.cancer = 'cancer' in risk_list
            risk_assessment.autoimmune_disease = 'autoimmune' in risk_list
            risk_assessment.pwd = 'pwd' in risk_list
            risk_assessment.disability = request.POST.get('disability', '')
            risk_assessment.save()
            print(f"POST: RiskAssessment {risk_assessment.id} saved.")

            # After successfully saving all related data and linking examination, redirect
            messages.success(request, 'Medical information submitted successfully!')
            
            # Check if the form submission came from an admin-initiated registration
            from_admin_register_flag = request.POST.get('from_admin_register') == 'true'
            if from_admin_register_flag:
                # If initiated by admin, redirect back to admin dashboard
                print("POST: Redirecting to admin dashboard after admin-initiated patient form submission.")
                return redirect('admin_dashboard')
            else:
                # Otherwise, redirect based on the user's role (existing logic)
                if hasattr(request.user, 'profile') and request.user.profile.role == 'Faculty':
                    print("POST: Redirecting to faculty dashboard for non-admin patient form submission.")
                    return redirect('faculty_dashboard')
                else:
                    print("POST: Redirecting to student dashboard for non-admin patient form submission.")
                    return redirect('student_dashboard')
            
        except Exception as e:
            print(f"Error saving patient information in POST: {e}")
            messages.error(request, f'Error saving patient information: {str(e)}')
        today = date.today()
        context = {
            'current_date': today,
            'patient': patient,
            'is_admin_onboarding': from_admin_register_flag
        }
        return render(request, 'patient_form.html', context)

def calculate_age(birthdate):
    born = datetime.strptime(birthdate, '%Y-%m-%d').date()
    today = date.today()
    return today.year - born.year - ((today.month, today.day) < (born.month, born.day))

def process_checkboxes(checkbox_list, other_value):
    if 'None' in checkbox_list:
        return 'None'
    result = ', '.join(filter(None, checkbox_list))
    if other_value:
        result = f"{result}, {other_value}" if result else other_value
    return result or 'None'

@user_passes_test(can_access_medical_admin)
def admin_dashboard_view(request):
    
    # --- START OF FIX ---
    def get_sort_date(req_data):
        """
        Gets the first available date and ensures it's a 'date' object.
        """
        date_val = (
            getattr(req_data['request'], 'date_requested', None) or
            getattr(req_data['request'], 'date_assisted', None) or
            getattr(req_data['request'], 'date_submitted', None)
        )
        
        # If it's a full datetime object, get just the .date() part
        if isinstance(date_val, datetime):
            return date_val.date()
        
        # If it's already a date object, just return it
        if isinstance(date_val, date):
            return date_val
        
        # If it's None, return the minimum possible date
        # (this will sort it to the end since reverse=True)
        return date.min
    # --- END OF FIX ---

    # Get total patients count (both students and faculty)
    total_patients = Patient.objects.count()
    
    # Get total medical records
    total_records = PhysicalExamination.objects.count()
    
    # Get all requests that are not completed or rejected
    upcoming_patient_requests = PatientRequest.objects.select_related(
        'patient__user'
    ).exclude(status__in=['completed', 'rejected']).order_by('date_requested')

    upcoming_faculty_requests = FacultyRequest.objects.select_related(
        'faculty__user'
    ).exclude(status__in=['completed', 'rejected']).order_by('date_requested')

    # Get dental service requests
    dental_requests = DentalRecords.objects.select_related(
        'patient__user'
    ).filter(appointed=False).order_by('date_requested')

    # Get emergency health assistance records - no status filter needed
    emergency_requests = EmergencyHealthAssistanceRecord.objects.select_related(
        'patient__user'
    ).order_by('-date_assisted')

    # Process all requests into a unified format
    all_requests = []
    
    # Process patient requests
    for req in upcoming_patient_requests:
        request_data = {
            'request': req,
            'user_info': {
                'id': 'N/A',
                'name': 'Unknown User'
            },
            'type': 'documentary'
            }
        if req.patient and req.patient.user:
            try:
                student = studentInfo.objects.filter(studID=req.patient.user.username).first()
                print(f"Processing patient request {req.request_id} for user {req.patient.user.username}")
                if student:
                    request_data['user_info'] = {
                        'id': student.studID,
                        'name': f"{student.lastname}, {student.firstname}"
                    }
                else:
                    faculty = Faculty.objects.filter(user=req.patient.user).first()
                    if faculty:
                        request_data['user_info'] = {
                            'id': faculty.faculty_id,
                            'name': f"{faculty.user.last_name}, {faculty.user.first_name}"
                        }
            except Exception as e:
                print(f"Error processing patient request {req.request_id}: {str(e)}")
        all_requests.append(request_data)
    
    # Process faculty requests
    for req in upcoming_faculty_requests:
        request_data = {
            'request': req,
            'user_info': {
                'id': 'N/A',
                'name': 'Unknown User'
            },
            'type': 'documentary'
            }
        if req.faculty and req.faculty.user:
            request_data['user_info'] = {
                'id': req.faculty.faculty_id,
                'name': f"{req.faculty.user.last_name}, {req.faculty.user.first_name}"
            }
        all_requests.append(request_data)

    # Process dental requests
    for req in dental_requests:
        request_data = {
            'request': req,
            'user_info': {
                'id': 'N/A',
                'name': 'Unknown User'
            },
            'type': 'dental'
        }
        if req.patient and req.patient.user:
            try:
                student = studentInfo.objects.filter(studID=req.patient.user.username).first()
                print(f"Processing dental request {req.id} for user {req.patient.user.username}")
                if student:
                    request_data['user_info'] = {
                        'id': student.studID,
                        'name': f"{student.lastname}, {student.firstname}"
                    }
                else:
                    faculty = Faculty.objects.filter(user=req.patient.user).first()
                    if faculty:
                        request_data['user_info'] = {
                            'id': faculty.faculty_id,
                            'name': f"{faculty.user.last_name}, {faculty.user.first_name}"
                        }
            except Exception as e:
                print(f"Error processing dental request {req.id}: {str(e)}")
        all_requests.append(request_data)

    # Process emergency requests
    for req in emergency_requests:
        request_data = {
            'request': req,
            'user_info': {
                'id': 'N/A',
                'name': 'Unknown User'
            },
            'type': 'emergency'
            }
        if req.patient and req.patient.user:
            try:
                student = studentInfo.objects.filter(studID=req.patient.user.username).first()
                if student:
                    request_data['user_info'] = {
                        'id': student.studID,
                        'name': f"{student.lastname}, {student.firstname}"
                    }
                else:
                    faculty = Faculty.objects.filter(user=req.patient.user).first()
                    if faculty:
                        request_data['user_info'] = {
                            'id': faculty.faculty_id,
                            'name': f"{faculty.user.last_name}, {faculty.user.first_name}"
                        }
            except Exception as e:
                print(f"Error processing emergency request {req.id}: {str(e)}")
        all_requests.append(request_data)

    # --- START OF FIX 2 ---
    # Sort all requests by date using the helper function
    all_requests.sort(key=get_sort_date, reverse=True)
    # --- END OF FIX 2 ---

    # Get counts for dashboard cards
    pending_requests_total = len([r for r in all_requests 
                                if hasattr(r['request'], 'status') 
                                and getattr(r['request'], 'status', None) == 'pending'])
    
    # Get today's schedule count
    today = timezone.now().date()
    todays_schedule_total = len([r for r in all_requests 
                               if hasattr(r['request'], 'date_responded') 
                               and getattr(r['request'], 'date_responded', None)
                               and getattr(r['request'], 'date_responded').date() == today])

    # Get urgent cases count (faculty requests with high priority)
    urgent_cases = len([r for r in all_requests 
                       if hasattr(r['request'], 'priority_level') 
                       and getattr(r['request'], 'priority_level', None) == 'high'])

    # Get active tab from URL parameter
    active_tab = request.GET.get('tab', 'all')

    # Prepare events for the calendar
    calendar_events = []
    for req_data in all_requests:
        date_field = None
        status_field = None

        if req_data['type'] == 'emergency':
            date_field = getattr(req_data['request'], 'date_assisted', None)
            status_field = 'emergency' # Custom status for emergency
        elif req_data['type'] == 'dental':
            date_field = getattr(req_data['request'], 'date_requested', None)
            status_field = 'completed' if getattr(req_data['request'], 'appointed', False) else 'pending'
        else: # documentary requests (patient and faculty requests)
            date_field = getattr(req_data['request'], 'date_requested', None)
            status_field = getattr(req_data['request'], 'status', None)
        
        if date_field and status_field:
            # Ensure date is a date object for formatting
            if isinstance(date_field, datetime):
                date_str = date_field.strftime('%Y-%m-%d')
            elif isinstance(date_field, date):
                date_str = date_field.strftime('%Y-%m-%d')
            else:
                date_str = None # Handle cases where date_field is not a date/datetime object

            if date_str:
                calendar_events.append({
                    'date': date_str,
                    'status': status_field
            })
    
    context = {
        'total_patients': total_patients,
        'total_records': total_records,
        'pending_requests': pending_requests_total,
        'todays_schedule': todays_schedule_total,
        'urgent_cases': urgent_cases,
        'all_upcoming_requests': all_requests,
        'active_tab': active_tab,
        'events': calendar_events, # Pass events to the template
    }
    
    return render(request, "medical/medicalv2/admin_dashboard.html", context)
@profile_complete_required
@login_required
def dashboard_view(request):
    try:
        # Get the Patient record linked to the logged-in User
        patient = Patient.objects.get(user=request.user)

        # Get related medical data through the patient object
        # Check if physical examination exists before trying to access related models
        physical_exam = None
        medical_history = None
        family_history = None
        risk_assessment = None
        patient_requests = None

        if patient.examination:
            physical_exam = patient.examination
            # Now get related models through physical_exam if it exists
            medical_history = MedicalHistory.objects.filter(examination=physical_exam).first()
            family_history = FamilyMedicalHistory.objects.filter(examination=physical_exam).first()
            # Risk assessment is linked to Patient through clearance field
            try:
                risk_assessment = RiskAssessment.objects.get(clearance=patient)
            except RiskAssessment.DoesNotExist:
                risk_assessment = None

            # Get patient requests (linked to Patient directly)
            # Only get requests for this specific patient
            patient_requests = PatientRequest.objects.filter(
                patient=patient
            ).order_by('-date_requested')
            
            # Fetch other request types for the patient
            medical_requirements = MedicalRequirement.objects.filter(patient=patient)
            eligibility_forms = EligibilityForm.objects.filter(patient=patient)
            medical_certificates = MedicalCertificate.objects.filter(patient=patient)
            dental_records = DentalRecords.objects.filter(patient=patient)
            emergency_records = EmergencyHealthAssistanceRecord.objects.filter(patient=patient)
            mental_health_records = MentalHealthRecord.objects.filter(patient=patient)

            # Combine all requests into a single list and standardize their format
            all_patient_requests = []

            for req in patient_requests:
                all_patient_requests.append({
                    'request_type': req.request_type,
                    'date_requested': req.date_requested.date(),  # Use .date()
                    'status': req.status
                })
            
            for req in medical_requirements:
                all_patient_requests.append({
                    'request_type': 'Medical Requirement',
                    'date_requested': (req.reviewed_date if req.reviewed_date else timezone.now()).date(),
                    'status': req.status
                })
            
            # ✅ --- FIX IS HERE ---
            for req in eligibility_forms:
                date_obj = None
                try:
                    # Convert the string 'YYYY-MM-DD' into a date object
                    date_obj = datetime.strptime(req.date_of_examination, '%Y-%m-%d').date()
                except (ValueError, TypeError):
                    # Fallback if data is bad or empty
                    date_obj = timezone.now().date() 

                all_patient_requests.append({
                    'request_type': 'Eligibility Form',
                    'date_requested': date_obj, # This is now a date object
                    'status': 'completed' 
                })
            # ✅ --- END FIX ---
            
            for req in medical_certificates:
                all_patient_requests.append({
                    'request_type': 'Medical Certificate',
                    'date_requested': req.date_created.date(), # Use .date()
                    'status': 'completed' 
                })
            
            for req in dental_records:
                all_patient_requests.append({
                    'request_type': f'Dental - {req.service_type}',
                    'date_requested': req.date_requested.date(), # Use .date()
                    'status': 'accepted' if req.appointed else 'pending'
                })

            for req in emergency_records:
                all_patient_requests.append({
                    'request_type': f'Emergency Assistance - {req.reason}',
                    'date_requested': req.date_assisted, # This is already a .date
                    'status': 'completed'
                })

            for req in mental_health_records:
                all_patient_requests.append({
                    'request_type': 'Mental Health Record',
                    'date_requested': req.date_submitted.date(), # Use .date()
                    'status': req.status
                })

            # Sort all requests by date_requested in descending order
            all_patient_requests.sort(key=lambda x: x['date_requested'], reverse=True)

        # Get student information
        try:
            student = studentInfo.objects.get(user=request.user)
            print(f"Student info found for user {request.user.username}")
        except studentInfo.DoesNotExist:
            student = None
            pass

        # Get appointments for calendar
        appointments = PatientRequest.objects.filter(
            patient=patient,
            status='accepted'
        ).values(
            'date_responded',
            'request_type'
        ).order_by('date_responded')

        # Format appointments for calendar
        calendar_events = []
        for appointment in appointments:
            if appointment['date_responded']:
                calendar_events.append({
                    'title': appointment['request_type'],
                    'start': appointment['date_responded'].strftime('%Y-%m-%d'),
                    'description': appointment['request_type']
                })

        context = {
            'user': request.user,
            'student': student,
            'patient': patient,
            'medical_history': medical_history,
            'family_history': family_history,
            'risk_assessment': risk_assessment,
            'physical_exam': physical_exam,
            'patient_requests': all_patient_requests, # Pass the combined list
            'appointments_json': json.dumps(calendar_events), # Pass JSON string of appointments
            'medical_profile_incomplete': not patient.examination
        }
            
        return render(request, 'medical/medicalv2/student_dashboard.html', context)
            
    except Patient.DoesNotExist:
        messages.info(request, 'Your medical profile is incomplete. Please complete it.')
        return render(request, 'medical/medicalv2/student_dashboard.html', {'medical_profile_incomplete': True})
    except Exception as e:
        print(f"Error in dashboard_view: {e}")
        messages.error(request, 'Error loading dashboard data.')
        # Instead of redirecting to login, just render the dashboard with a flag
        return render(
            request,
            'medical/medicalv2/student_dashboard.html',
            {'medical_profile_incomplete': True}
        )


@user_passes_test(can_access_medical_admin)
def mental_health_view(request):
    print("--- DEBUG: Entering mental_health_view ---")

    # Initialize variables
    fetched_student = None
    fetched_faculty = None
    fetched_mental_health_record = None
    
    # Get search ID
    search_id = request.GET.get('search_id') or request.POST.get('search_id')
    
    # --- 1. QUERYSETS (FILTERS OFF FOR DEBUGGING) ---
    # We are grabbing ALL records to see if the database is returning anything at all
    student_qs = MentalHealthRecord.objects.filter(
        patient__isnull=False
        # is_availing_mental_health=True  <-- COMMENTED OUT TO SHOW ALL
    ).select_related('patient__user').order_by('-pk')
    
    print(f"DEBUG: Total Student Records Found in DB: {student_qs.count()}")

    faculty_qs = MentalHealthRecord.objects.filter(
        faculty__isnull=False
        # is_availing_mental_health=True <-- COMMENTED OUT TO SHOW ALL
    ).select_related('faculty__user').order_by('-pk')

    print(f"DEBUG: Total Faculty Records Found in DB: {faculty_qs.count()}")

    # --- 2. PAGINATION ---
    student_paginator = Paginator(student_qs, 10)
    student_page = request.GET.get('student_page')
    try:
        student_mhr_list = student_paginator.page(student_page)
    except PageNotAnInteger:
        student_mhr_list = student_paginator.page(1)
    except EmptyPage:
        student_mhr_list = student_paginator.page(student_paginator.num_pages)

    faculty_paginator = Paginator(faculty_qs, 10)
    faculty_page = request.GET.get('faculty_page')
    try:
        faculty_mhr_list = faculty_paginator.page(faculty_page)
    except PageNotAnInteger:
        faculty_mhr_list = faculty_paginator.page(1)
    except EmptyPage:
        faculty_mhr_list = faculty_paginator.page(faculty_paginator.num_pages)

    # --- 3. ENRICHMENT LOOP (STUDENTS) ---
    for record in student_mhr_list:
        # Default values
        record.id_number_display = "N/A"
        record.name_display = "Unknown"
        
        if record.patient and record.patient.user:
            user = record.patient.user
            try:
                # Try to get Student Info
                student_obj = studentInfo.objects.get(studID=user.username)
                record.id_number_display = student_obj.studID
                record.name_display = f'{student_obj.firstname} {student_obj.lastname}'
            except studentInfo.DoesNotExist:
                # FALLBACK: If not in studentInfo, use User data
                record.id_number_display = user.username
                record.name_display = user.get_full_name() or user.username
            except Exception as e:
                print(f"Error processing record {record.pk}: {e}")

    # --- 4. ENRICHMENT LOOP (FACULTY) ---
    for record in faculty_mhr_list:
        if record.faculty:
            record.id_number_display = record.faculty.staffID
            if record.faculty.user:
                 record.name_display = f"{record.faculty.firstname} {record.faculty.lastname}"
            else:
                 record.name_display = f"{record.faculty.firstname} {record.faculty.lastname}"
        else:
            record.id_number_display = "N/A"
            record.name_display = "Faculty Data Missing"

    # --- 5. SEARCH LOGIC ---
    if search_id:
        try:
            student_obj = studentInfo.objects.filter(studID=search_id).first()
            if student_obj:
                fetched_student = student_obj
                user_obj = User.objects.filter(username=student_obj.studID).first()
                if user_obj:
                    patient_obj = Patient.objects.filter(user=user_obj).first()
                    if patient_obj:
                         fetched_mental_health_record = MentalHealthRecord.objects.filter(patient=patient_obj).first()

            if not fetched_mental_health_record:
                faculty_obj = Faculty.objects.filter(staffID=search_id).first()
                if faculty_obj:
                    fetched_faculty = faculty_obj
                    fetched_mental_health_record = MentalHealthRecord.objects.filter(faculty=faculty_obj).first()       
        except Exception as e:
            messages.error(request, f"Error searching for ID {search_id}: {e}")

    # --- 6. POST LOGIC ---
    if request.method == 'POST' and 'record_id' in request.POST:
        try:
            record_id = request.POST.get('record_id')
            action = request.POST.get('action')
            mhr = MentalHealthRecord.objects.get(pk=record_id)
            mhr.prescription_remarks = request.POST.get('prescription_remarks')
            mhr.certification_remarks = request.POST.get('certification_remarks')

            if action == 'approved':
                mhr.status = 'approved'
                messages.success(request, "Record approved.")
            elif action == 'rejected':
                mhr.status = 'rejected'
                messages.error(request, "Record rejected.")
            elif action == 'save_remarks':
                messages.success(request, "Remarks saved.")
            
            mhr.save()
            fetched_mental_health_record = mhr 
        except Exception as e:
            messages.error(request, f"An error occurred: {e}")

    pending_count = MentalHealthRecord.objects.filter(status='pending').count()

    context = {
        'student_mhr_list': student_mhr_list, 
        'faculty_mhr_list': faculty_mhr_list, 
        'pending_count': pending_count,
        'search_id': search_id,
        'fetched_student': fetched_student,
        'fetched_faculty': fetched_faculty,
        'fetched_mental_health_record': fetched_mental_health_record,
        'active_tab': request.GET.get('tab', 'student') 
    }
    
    print("--- DEBUG: Rendering Template ---")
    return render(request, 'medical/admin/mental_health.html', context)

@login_required
def mental_health_submit(request):
    if request.method == 'POST':
        try:
            patient = Patient.objects.get(student__student_id=request.user.username)
            prescription = request.FILES.get('prescription')
            certification = request.FILES.get('certification')
            
            if not prescription or not certification:
                messages.error(request, 'Both prescription and certification are required.')
                return redirect('mental_health')
            
            record = MentalHealthRecord.objects.create(
                patient=patient,
                prescription=prescription,
                certification=certification
            )
            
            # Send notification email to student
            subject = 'Mental Health Record Submission Confirmation'
            message = f"""
            Dear {patient.student.firstname},

            This email confirms that we have received your mental health record submission.

            Submission Details:
            - Date Submitted: {record.date_submitted.strftime('%B %d, %Y')}
            - Status: Pending Review

            Our medical team will review your submission and you will be notified of the outcome.

            Best regards,
            Medical Services Team
            """
            
            send_mail(
                subject,
                message,
                settings.EMAIL_HOST_USER,
                [patient.student.email],
                fail_silently=False,
            )
            
            messages.success(request, 'Mental health documents submitted successfully.')
            return redirect('student_dashboard')
            
        except Patient.DoesNotExist:
            messages.error(request, 'Patient profile not found.')
            return redirect('patient_form')
            
    return render(request, 'mental_health_submit.html')

@user_passes_test(can_access_medical_admin)

def mental_health_review(request, record_id):
    record = get_object_or_404(MentalHealthRecord, id=record_id)
    
    if request.method == 'POST':
        status = request.POST.get('status', '').lower()
        notes = request.POST.get('notes', '')
        prescription_remarks = request.POST.get('prescription_remarks', '')
        certification_remarks = request.POST.get('certification_remarks', '')
        
        # Validate status
        valid_statuses = ['approved', 'rejected', 'pending']
        if status not in valid_statuses:
            messages.error(request, f'Invalid status provided. Must be one of: {", ".join(valid_statuses)}')
            return redirect('mental_health')
        
        # Update record
        record.status = status
        record.notes = notes
        record.prescription_remarks = prescription_remarks
        record.certification_remarks = certification_remarks
        record.reviewed_by = request.user
        record.reviewed_at = timezone.now()
        record.save()
        
        # Initialize email variables
        subject = ''
        message = ''
        
        # Prepare email content based on status
        if status == 'approved':
            subject = 'Mental Health Record - Approved'
            message = f"""
            Dear {record.patient.student.firstname},

            We are pleased to inform you that your mental health record has been approved.

            Review Details:
            - Date Reviewed: {record.reviewed_at.strftime('%B %d, %Y')}
            - Status: Approved
            - Reviewer: {record.reviewed_by.get_full_name()}

            Document Review:
            - Prescription Document: {prescription_remarks if prescription_remarks else 'Approved'}
            - Certification Document: {certification_remarks if certification_remarks else 'Approved'}

            Additional Notes:
            {notes if notes else 'No additional notes provided.'}

            Your mental health record is now complete and on file.

            Best regards,
            Medical Services Team
            """
        elif status == 'rejected':
            subject = 'Mental Health Record - Additional Information Required'
            message = f"""
            Dear {record.patient.student.firstname},

            We regret to inform you that your mental health record requires additional information or clarification.

            Review Details:
            - Date Reviewed: {record.reviewed_at.strftime('%B %d, %Y')}
            - Status: Additional Information Required
            - Reviewer: {record.reviewed_by.get_full_name()}

            Document Review:
            - Prescription Document: {prescription_remarks if prescription_remarks else 'No remarks provided'}
            - Certification Document: {certification_remarks if certification_remarks else 'No remarks provided'}

            Additional Notes:
            {notes if notes else 'No specific reason provided.'}

            Please submit the required information or clarification through the student portal.

            Best regards,
            Medical Services Team
            """
        elif status == 'pending':
            subject = 'Mental Health Record - Status Updated'
            message = f"""
            Dear {record.patient.student.firstname},
            
            Your mental health record status has been updated to pending review.

            Review Details:
            - Date Updated: {record.reviewed_at.strftime('%B %d, %Y')}
            - Status: Pending Review
            - Updated By: {record.reviewed_by.get_full_name()}

            Document Review:
            - Prescription Document: {prescription_remarks if prescription_remarks else 'Under Review'}
            - Certification Document: {certification_remarks if certification_remarks else 'Under Review'}

            Additional Notes:
            {notes if notes else 'No additional notes provided.'}

            We will notify you once the review is complete.
        
            Best regards,
            Medical Services Team
            """
        
        try:
            send_mail(
                subject,
                message,
                settings.EMAIL_HOST_USER,
                [record.patient.student.email],
                fail_silently=False,
            )
            messages.success(request, 'Record reviewed successfully and notification sent.')
        except Exception as e:
            messages.error(request, f'Record reviewed but failed to send email: {str(e)}')
        
        return redirect('mental_health')
        
    return render(request, 'admin/mental_health_review.html', {'record': record})

def logout_view(request):
    logout(request)
    return redirect('login')

def email_verification(request):
    return render(request, 'email_verification.html')

@login_required
def upload_profile_picture_view(request):
    if request.method == 'POST' and request.FILES.get('profile_picture'):
        try:
            student = studentInfo.objects.get(emailadd=request.user.email)
            student.profile_picture = request.FILES['profile_picture']
            student.save()
            return JsonResponse({'status': 'success'})
        except studentInfo.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'Student profile not found'})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)})
    return JsonResponse({'status': 'error', 'message': 'Invalid request'})

@login_required
def faculty_dashboard_view(request):
    if not request.user.profile.role == 'Faculty':
        messages.error(request, 'Access denied. Faculty access only.')
        return redirect('login')

    try:
        # Get faculty information
        faculty = Faculty.objects.get(user=request.user)
        
        # Get the Patient record for the faculty user (may not exist or be complete)
        patient = Patient.objects.filter(user=request.user).first()
        medical_profile_incomplete = patient is None or not patient.examination

        # Get faculty's own requests
        faculty_requests = FacultyRequest.objects.filter(
            faculty=faculty
        ).order_by('-date_requested')

        # Fetch dental records associated with the faculty's patient
        dental_records = []
        if patient:
            dental_records = DentalRecords.objects.filter(patient=patient)

        # Combine all requests into a single list and standardize their format
        all_faculty_requests = []

        for req in faculty_requests:
            all_faculty_requests.append({
                'request_type': req.request_type,
                'date_requested': req.date_requested,
                'status': req.status
            })

        for req in dental_records:
            all_faculty_requests.append({
                'request_type': f'Dental - {req.service_type}',
                'date_requested': req.date_requested,
                'status': 'accepted' if req.appointed else 'pending'  # Assuming "accepted" if appointed, else "pending"
            })

        # Sort all requests by date_requested in descending order
        all_faculty_requests.sort(key=lambda x: x['date_requested'], reverse=True)

        # Get appointments for calendar (only faculty's accepted requests)
        appointments = FacultyRequest.objects.filter(
            faculty=faculty,
            status='accepted'
        ).values(
            'date_responded',
            'request_type',
            'description'
        ).order_by('date_responded')

        # Format appointments for calendar
        calendar_events = []
        for appointment in appointments:
            if appointment['date_responded']:
                calendar_events.append({
                    'title': appointment['request_type'],
                    'start': appointment['date_responded'].strftime('%Y-%m-%d'),
                    'description': appointment['description'] or appointment['request_type']
                })

        # Get faculty's medical information (handle cases where patient or examination might not exist)
        physical_exam = None
        medical_history = None
        family_history = None
        risk_assessment = None

        if patient and patient.examination:
            try:
                physical_exam = patient.examination
                medical_history = MedicalHistory.objects.filter(examination=physical_exam).first()
                family_history = FamilyMedicalHistory.objects.filter(examination=physical_exam).first()
            except (MedicalHistory.DoesNotExist, 
                    FamilyMedicalHistory.DoesNotExist):
                pass # Handle gracefully if history records are missing

        if patient:
            try:
                # Risk assessment is linked to Patient through clearance field
                risk_assessment = RiskAssessment.objects.get(clearance=patient)
            except RiskAssessment.DoesNotExist:
                pass # Handle gracefully if risk assessment is missing

        # Get faculty's medical requirements and mental health records
        faculty_medical_requirements = MedicalRequirement.objects.filter(faculty=faculty).first()
        faculty_mental_health_record = MentalHealthRecord.objects.filter(faculty=faculty).first()

        context = {
            'faculty': faculty,
            'patient': patient,
            'medical_history': medical_history,
            'family_history': family_history,
            'risk_assessment': risk_assessment,
            'physical_exam': physical_exam,
            'faculty_medical_requirements': faculty_medical_requirements,
            'faculty_mental_health_record': faculty_mental_health_record,
            'faculty_requests': all_faculty_requests, # Pass the combined list
            'appointments': calendar_events,
            'medical_profile_incomplete': medical_profile_incomplete,
        }
        
        return render(request, 'faculty_dashboard.html', context)
        
    except Faculty.DoesNotExist:
        messages.error(request, 'Faculty profile not found.')
        return redirect('login')
    except Exception as e:
        print(f"Error in faculty_dashboard_view: {e}")
        messages.error(request, 'Error loading dashboard data.')
        return redirect('login')
@user_passes_test(can_access_medical_admin)

@require_http_methods(["POST"])
def send_faculty_registration_link(request):
    try:
        data = json.loads(request.body)
        email = data.get('email')

        if not email:
            return JsonResponse({'status': 'error', 'message': 'Email address is required.'})

        # Optional: Add more robust email validation if needed
        if not re.match(r"^[\w.-]+@([\w-]+\.)+[\w-]{2,4}$", email):
            return JsonResponse({'status': 'error', 'message': 'Please enter a valid email address.'})

        # Construct the faculty registration link
        registration_link = request.build_absolute_uri(reverse('register') + '?role=faculty')

        subject = 'Faculty Registration Link for HealthHub Connect'
        message = f"""
Dear Faculty Member,

You have been invited to register for the HealthHub Connect system as a Faculty member.

Please use the following link to complete your registration:
{registration_link}

This link is specifically for faculty registration. If you believe this email was sent to you in error, please disregard it.

Thank you,
HealthHub Connect Team
"""

        send_mail(
            subject,
            message,
            settings.EMAIL_HOST_USER, # From email defined in settings.py
            [email],
            fail_silently=False,
        )

        return JsonResponse({'status': 'success', 'message': f'Registration link sent to {email}'})

    except Exception as e:
        print(f"Error sending faculty registration link: {e}")
        return JsonResponse({'status': 'error', 'message': f'Failed to send registration link: {str(e)}'})