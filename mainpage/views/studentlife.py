from django.shortcuts import get_object_or_404, redirect, render
from django.contrib import messages
from django.utils import timezone
from django.utils.dateparse import parse_datetime, parse_date
from datetime import timedelta
import io
import os
from django.db.models import Q
from urllib.parse import urlencode
import platform
from django.http import HttpResponse
from reportlab.pdfgen import canvas
from django.core.paginator import Paginator
from reportlab.lib.pagesizes import A4
import time
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.timezone import localtime, now
from django.views import View
from django.db.models import Sum, F, Avg
from django.core.files.storage import FileSystemStorage
from django.contrib.auth.decorators import login_required
from django.core.mail import send_mail, BadHeaderError
from django.utils.decorators import method_decorator
from ..models import (
    studentInfo, Equipment, BorrowingRecord, RequestedGMC, Schedule,
    ProcurementItem, Storage, ExcelData, Organization
)
from ..forms import (
    ScheduleForm, UploadFileForm, UpdateSerialNoForm, UploadExcelForm, ExcelDataForm
)
from ..decorators import sao_admin_required

import json
import openpyxl
import pandas as pd
import logging

logger = logging.getLogger(__name__)
import calendar
# views.py
import io
import os
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from django.http import HttpResponse
# views.py
from django.shortcuts import render, redirect
from ..models import PPMPDocument
from ..forms import PPMPDocumentForm


@login_required
def ppmp_list(request):
    base_template = "adminmain.html" if request.user.is_staff or request.user.is_superuser else "main.html"

    if request.user.is_staff:  # Admin
        documents = PPMPDocument.objects.all().order_by('-uploaded_at')
    else:  # SAO user
        documents = PPMPDocument.objects.filter(uploaded_by=request.user).order_by('-uploaded_at')
    return render(request, 'officeOfStudentL/ppmp_list.html', {'documents': documents ,   'base_template': base_template,})

# views.py
@login_required
def ppmp_upload(request):
    if request.method == 'POST':
        form = PPMPDocumentForm(request.POST, request.FILES, user=request.user)
        if form.is_valid():
            ppmp = form.save(commit=False)
            ppmp.uploaded_by = request.user
            ppmp.save()
            return JsonResponse({"success": True})
        return JsonResponse({"success": False, "errors": form.errors}, status=400)
    return JsonResponse({"success": False, "error": "Invalid request"}, status=400)

@login_required
def ppmp_approve(request, pk):
    if not request.user.is_staff:
        return JsonResponse({"success": False, "error": "Permission denied"}, status=403)
    doc = get_object_or_404(PPMPDocument, pk=pk)
    doc.status = 'Approved'
    doc.save()
    return JsonResponse({"success": True})

@login_required
def ppmp_delete(request, pk):
    if not request.user.is_staff:
        return JsonResponse({"success": False, "error": "Permission denied"}, status=403)
    doc = get_object_or_404(PPMPDocument, pk=pk)
    doc.document.delete()  # delete file from storage
    doc.delete()
    return JsonResponse({"success": True})


def print_gmc(request):
    buffer = io.BytesIO()
    p = canvas.Canvas(buffer, pagesize=A4)

    p.setFont("Helvetica", 12)
    p.drawString(100, 750, "CERTIFICATION OF GOOD MORAL CHARACTER")
    p.drawString(100, 730, "Student Name: John Doe")
    p.drawString(100, 710, "Course: Bachelor of Science in IT")
    p.drawString(100, 690, "Date: 2025-08-20")
    p.showPage()
    p.save()

    buffer.seek(0)

    # ✅ If running on Windows, send directly to printer
    if platform.system() == "Windows":
        import tempfile
        import win32api

        temp_file = tempfile.mktemp(".pdf")
        with open(temp_file, "wb") as f:
            f.write(buffer.read())

        printer_name = "EPSON L3210 Series"
        win32api.ShellExecute(
            0,
            "printto",
            temp_file,
            f'"{printer_name}"',
            ".",
            0
        )

        return HttpResponse("PDF sent to Epson printer!")

    # ✅ On Linux/Render: just return the PDF
    response = HttpResponse(buffer, content_type="application/pdf")
    response["Content-Disposition"] = "inline; filename=gmc.pdf"
    return response
@sao_admin_required
def gmcform(request):
    return render(request, "adminUser/gmcform.html")
def update_return_status(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            record_id = data.get("record_id")
            if not record_id:
                return JsonResponse({"status": "error", "message": "Record ID not provided"}, status=400)
            
            record = BorrowingRecord.objects.get(id=record_id)
            record.is_returned = True
            record.date_returned = timezone.now().date()
            record.save()
            return JsonResponse({"status": "success", "date_returned": record.date_returned})
        except BorrowingRecord.DoesNotExist:
            return JsonResponse({"status": "error", "message": "Record not found"}, status=404)
        except Exception as e:
            logger.error(f"Error updating return status: {e}")
            return JsonResponse({"status": "error", "message": str(e)}, status=500)
    return JsonResponse({"status": "error", "message": "Invalid request"}, status=400)
def requestedgmc(request):
    student = None
    existing_request = None
    request_history = None  # <-- Initialize history
    user = request.user

    if request.user.is_authenticated:
        try:
            student = studentInfo.objects.get(studID=int(user.username))
            
            # Check for unprocessed request (same as before)
            existing_request = RequestedGMC.objects.filter(
                student=student, processed=False
            ).first()

            # --- NEW QUERY ---
            # Get all requests for this student, ordered by most recent
            request_history = RequestedGMC.objects.filter(student=student).order_by('-request_date')
            # --- END NEW QUERY ---

        except studentInfo.DoesNotExist:
            messages.error(request, "Student not found")

    if request.method == "POST":
        if existing_request:
            messages.error(request, "You already have a pending Good Moral Certificate request.")
            return redirect('requestgmc')

        reason = request.POST.get("reason")
        if reason:
            RequestedGMC.objects.create(student=student, reason=reason)
            messages.success(request, "Good Moral Certificate request submitted successfully")
            return redirect('requestgmc')

    context = {
        "student": student,
        "existing_request": existing_request,
        "request_history": request_history  # <-- Pass the history to the template
    }
    return render(request, "officeOfStudentL/requestgmc.html", context)

# In studentlife.py

# (Make sure Paginator, Q, and urlencode are imported at the top)
from django.core.paginator import Paginator
from django.db.models import Q
from urllib.parse import urlencode

def adminRequestedGmc(request):
    
    # --- 1. GET PARAMETERS ---
    search_query = request.GET.get('search', '')
    status_filter = request.GET.get('status', 'pending') # Default to pending
    sort_by = request.GET.get('sort', 'request_date')
    order = request.GET.get('order', 'desc')
    page_number = request.GET.get('page')

    # --- 2. START QUERYSET ---
    gmc_request_list = RequestedGMC.objects.select_related('student').all()
    
    # --- 3. APPLY STATUS FILTER ---
    if status_filter == 'pending':
        gmc_request_list = gmc_request_list.filter(processed=False)
    elif status_filter == 'processed':
        gmc_request_list = gmc_request_list.filter(processed=True)
    # if 'all', we do nothing

    # --- 4. APPLY SEARCH FILTER ---
    if search_query:
        gmc_request_list = gmc_request_list.filter(
            Q(student__studID__icontains=search_query) |
            Q(student__firstname__icontains=search_query) |
            Q(student__lastname__icontains=search_query) |
            Q(reason__icontains=search_query) |
            Q(or_num__icontains=search_query)
        )

    # --- 5. APPLY SORTING ---
    sort_fields = {
        'stud_id': 'student__studID',
        'stud_name': 'student__lastname',
        'course': 'student__degree',
        'year': 'student__yearlvl',
        'reason': 'reason',
        'request_date': 'request_date',
    }
    db_field = sort_fields.get(sort_by, 'request_date')
    
    if order == 'desc':
        db_field = f'-{db_field}'
    
    gmc_request_list = gmc_request_list.order_by(db_field)

    # --- 6. PREPARE QUERY STRINGS FOR LINKS (THE FIX) ---
    
    # 6a. For Pagination (preserves everything except 'page')
    pagination_params = request.GET.copy()
    if 'page' in pagination_params:
        del pagination_params['page']
    pagination_params_str = f"&{pagination_params.urlencode()}" if pagination_params else ""

    # 6b. For Sorting (preserves search/status, but not sort/order/page)
    sort_params = request.GET.copy()
    for key in ['sort', 'order', 'page']:
        if key in sort_params:
            del sort_params[key]
    sort_params_str = f"&{sort_params.urlencode()}" if sort_params else ""

    # 6c. For Status Filters (preserves search/sort, but not status/page)
    status_params = request.GET.copy()
    for key in ['status', 'page']:
        if key in status_params:
            del status_params[key]
    status_params_str = f"&{status_params.urlencode()}" if status_params else ""


    # --- 7. APPLY PAGINATION ---
    paginator = Paginator(gmc_request_list, 10) # 10 records per page
    page_obj = paginator.get_page(page_number)

    # --- 8. CONTEXT ---
    context = {
        'page_obj': page_obj,
        'current_sort': sort_by,
        'current_order': order,
        'current_status_filter': status_filter,
        'search_query': search_query,
        
        # --- NEW CONTEXT VARIABLES ---
        'pagination_params': pagination_params_str,
        'sort_params': sort_params_str,
        'status_params': status_params_str,
        
        'base_template': 'adminmain.html'
    }
    return render(request, "officeOfStudentL/adminUser/adminRequestedGmc.html", context)

# Making of Goodmoral Certificate

def generateGmc(request, request_id):
    try:
        gmc_request = RequestedGMC.objects.get(id=request_id)
        student = gmc_request.student
        or_num = request.GET.get('ornum', '')  # Capture the OR Number from the query parameters

        # Mark the request as processed
        gmc_request.or_num = or_num
        gmc_request.processed = True
        gmc_request.save()

        context = {
            "student_name": f"{student.firstname} {student.lastname}",
            "student_degree": student.degree,
            "request_date": localtime(gmc_request.request_date).strftime('%B %d, %Y'),
            "reason": gmc_request.reason,
            "year": student.yearlvl,
            "today_date": localtime(now()).strftime('%B %d, %Y'),
            "or_num": or_num  # Include the OR Number in the context
        }
        return render(request, "officeOfStudentL/adminUser/good_moral_certificate.html", context)
    except RequestedGMC.DoesNotExist:
        messages.error(request, "GMC Request not found")
        return redirect('adminRequestedGmc')

@sao_admin_required
def processed_gmc_transactions(request):
    # Fetch all processed GMC requests
    processed_gmcs = RequestedGMC.objects.filter(processed=True)
    
    return render(request, 'officeOfStudentL/adminUser/transactionsGMC.html', {
        'transaction_records': processed_gmcs
    })

# Calendar Of Activities Student Side 
def monthlyCalendar(request):
    schedules = Schedule.objects.all()
    sched_res = {}

    for schedule in schedules:
        
        # ⬇️ START OF CHANGES ⬇️
        # Add 1 day to the end date to make it exclusive for FullCalendar
        exclusive_end_date = schedule.end_date + timedelta(days=1)
    
        sched_res[schedule.sched_Id] = {
            'id': schedule.sched_Id,
            'title': schedule.title,
            'description': schedule.description,
            'start_datetime': schedule.start_date.strftime("%Y-%m-%d"), # FullCalendar reads this
            'end_datetime': exclusive_end_date.strftime("%Y-%m-%d"), # Use the new exclusive date
            'sdate': schedule.start_date.strftime("%B %d, %Y"),
            'edate': schedule.end_date.strftime("%B %d, %Y")
        }
     

    context = {
        'sched_json': json.dumps(sched_res)
    }
    return render(request, "officeOfStudentL/monthlyCalendar.html", context)
# Calendar of Activities Admin 
# @sao_admin_required

import json
from django.shortcuts import render
from ..models import Schedule  # adjust import path if needed
def monthlyCalendarAdmin(request):
    base_template = "adminmain.html" if request.user.is_staff or request.user.is_superuser else "main.html"

    schedules = Schedule.objects.all()
    sched_res = {}

    for schedule in schedules:
        
        # ⬇️ START OF CHANGES ⬇️
        # Add 1 day to the end date to make it exclusive for FullCalendar
        exclusive_end_date = schedule.end_date + timedelta(days=1)
        
        sched_res[schedule.sched_Id] = {
            'id': schedule.sched_Id,
            'title': schedule.title,
            'description': schedule.description,
            'start': schedule.start_date.strftime("%Y-%m-%d"),
            'end': exclusive_end_date.strftime("%Y-%m-%d"), # Use the new exclusive date
            'sdate': schedule.start_date.strftime("%B %d, %Y"),
            'edate': schedule.end_date.strftime("%B %d, %Y") # Keep this for display
        }
        # ⬆️ END OF CHANGES ⬆️
    context = {
        'sched_json': json.dumps(sched_res),
           'is_admin': request.user.is_authenticated and request.user.is_staff, 
                    'base_template': base_template,  # or your admin check

    }
    return render(request, 'officeOfStudentL/adminUser/monthlyCalendarAdmin.html', context)
# Save Schedule\
from django.views.decorators.csrf import csrf_exempt
from django.utils.timezone import make_aware
from django.http import JsonResponse
import json

# ...
@csrf_exempt
def save_schedule(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            title = data.get('title')
            description = data.get('description')
            
            # ⬇️ START OF CHANGES ⬇️
            start_str = data.get('start_date')
            end_str = data.get('end_date')

            # 1. Convert strings to date objects
            start_obj = parse_date(start_str)
            end_obj = parse_date(end_str)

            # 2. Check if parsing worked
            if not start_obj or not end_obj:
                raise ValueError("Invalid date format. Expected YYYY-MM-DD.")
            
            sched = Schedule.objects.create(
                title=title,
                description=description,
                start_date=start_obj,  # 3. Save the date OBJECT
                end_date=end_obj        # 4. Save the date OBJECT
            )

            return JsonResponse({
                'status': 'success',
                'id': sched.sched_Id,
                'title': sched.title,
                'description': sched.description,
                'start': sched.start_date.isoformat(), # 5. This will now work
                'end': sched.end_date.isoformat()       # 6. This will now work
            }, status=200)
            # ⬆️ END OF CHANGES ⬆️

        except Exception as e:
            logger.error(f"Error in save_schedule: {e}") 
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)

    return JsonResponse({'status': 'error', 'message': 'Invalid method'}, status=405)
@csrf_exempt  # Add this to allow POST requests from JavaScript
def update_schedule(request, schedule_id):
    if request.method == 'POST':
        try:
            # 1. Find the schedule object first
            schedule = get_object_or_404(Schedule, pk=schedule_id)
            
            # 2. Load the JSON data from the request.body
            data = json.loads(request.body)

            # 3. Get the data from the dictionary
            start_str = data.get('start_date')
            end_str = data.get('end_date')
            title = data.get('title')
            description = data.get('description')

            # 4. Check if we have the required date strings
            if not start_str or not end_str:
                return JsonResponse({'status': 'error', 'message': 'Invalid data: start_date or end_date missing.'}, status=400)

            # 5. Convert the date strings into real date objects
            start_obj = parse_date(start_str)
            end_obj = parse_date(end_str)

            if not start_obj or not end_obj:
                 return JsonResponse({'status': 'error', 'message': 'Invalid date format. Expected YYYY-MM-DD.'}, status=400)

            # 6. Update the schedule object with all new data
            schedule.title = title
            schedule.description = description
            schedule.start_date = start_obj
            schedule.end_date = end_obj  # <-- FIXED TYPO (was 'end_datet')
            schedule.save()
            
            # 7. Send back a full success response
            return JsonResponse({
                'status': 'success',
                'id': schedule.sched_Id,
                'title': schedule.title,
                'description': schedule.description,
                'start': schedule.start_date.isoformat(),
                'end': schedule.end_date.isoformat()
            })

        except Exception as e:
            logger.error(f"Error in update_schedule: {e}")
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)
    
    # If the request method is not POST
    return JsonResponse({'status': 'error', 'message': 'Method not allowed.'}, status=405)
# Delete Schedule
def delete_schedule(request, schedule_id):
    schedule = get_object_or_404(Schedule, pk=schedule_id)
    schedule.delete()
    return redirect('monthlyCalendarAdmin')

def equipmentTracker(request):
    # Get the logged-in user
    user = request.user

    # Initialize borrowing records
    borrowing_records = BorrowingRecord.objects.none()

    # Check if the user is authenticated
    if user.is_authenticated:
        # Get the studentInfo instance for the logged-in user
        try:
            student = studentInfo.objects.get(studID=int(user.username))
        except studentInfo.DoesNotExist:
            student = None

        # Filter borrowing records based on the studentInfo instance
        if student:
            borrowing_records = BorrowingRecord.objects.filter(student=student)

    context = {
        'borrowing_records': borrowing_records
    }
    return render(request, 'officeOfStudentL/equipmentTracker.html', context)

# @sao_admin_required
def equipmentTrackerAdmin(request):
    student = None
    borrowing_records = BorrowingRecord.objects.all()
    error_message = None  # <-- 1. Initialize error variable

    if request.method == "GET" and "search" in request.GET:
        search_id = request.GET.get("search")
        if search_id:
            try:
                student = studentInfo.objects.get(studID=search_id)
            except studentInfo.DoesNotExist:
                # 2. REMOVE this line:
                # messages.error(request, "Student not found")
                
                # 3. ADD this line instead:
                error_message = "Student not found"
        # (Optional) You can also handle empty searches
        # else:
        #     error_message = "Please enter a Student ID to search."

    all_equipment = Equipment.objects.all()

    context = {
        'student': student,
        'all_equipment': all_equipment,
        'borrowing_records': borrowing_records,
        'error_message': error_message,  # <-- 4. Pass the local error to the context
    }
    return render(request, 'officeOfStudentL/adminUser/equipmentTrackerAdmin.html', context)
from django.core.paginator import Paginator
# @sao_admin_required (uncomment this if you have your custom decorator)
def equipmentborrowed(request):
    
    # --- 1. GET PARAMETERS ---
    search_query = request.GET.get('search', '')
    sort_by = request.GET.get('sort', 'date_borrowed')
    order = request.GET.get('order', 'desc') # Default order for date is usually descending
    page_number = request.GET.get('page')

    # --- 2. START QUERYSET ---
    borrowing_records_list = BorrowingRecord.objects.all()
    
    # --- 3. APPLY SEARCH FILTER (Combined Name/ID Search) ---
    if search_query:
        # Use Q objects to perform a broad search across multiple fields
        borrowing_records_list = borrowing_records_list.filter(
            Q(equipment__itemId__icontains=search_query) |
            Q(student__studID__icontains=search_query) |
            Q(student__firstname__icontains=search_query) |
            Q(student__lastname__icontains=search_query) |
            Q(equipment__equipmentName__icontains=search_query)
        )

    # --- 4. APPLY SORTING ---
    # Map sort parameter to correct database field names (including foreign key lookups)
    sort_fields = {
        'item_id': 'equipment__itemId',
        'borrower_name': 'student__lastname', # Sorting by last name
        'equipment_name': 'equipment__equipmentName',
        'date_borrowed': 'date_borrowed',
        'status': 'is_returned',
    }
    
    db_field = sort_fields.get(sort_by, 'date_borrowed') # Use default if key is invalid
    
    # Apply direction
    if order == 'desc':
        db_field = f'-{db_field}'
    
    borrowing_records_list = borrowing_records_list.order_by(db_field)

    # --- 5. PREPARE QUERY STRING FOR PAGINATION LINKS ---
    query_params = request.GET.copy()
    
    # Remove 'page', 'sort', and 'order' so we can add them cleanly in the template
    for key in ['page', 'sort', 'order']:
        if key in query_params:
            del query_params[key]
            
    # Encode the remaining search/filter params, prefixed with '&' if not empty
    search_sort_params = f"&{urlencode(query_params)}" if query_params else ""

    # --- 6. APPLY PAGINATION ---
    paginator = Paginator(borrowing_records_list, 10) 
    page_obj = paginator.get_page(page_number)

    context = {
        'borrowing_records': page_obj.object_list, # Items for the current page
        'page_obj': page_obj,                     # Paginator object for controls

        # For link generation and header highlighting
        'current_sort': sort_by,
        'current_order': order,
        'search_sort_params': search_sort_params, # The prepared query string
        
        # Original search query for the search box value
        'search_query': search_query, 
    }

    return render(request, 'officeOfStudentL/adminUser/equipmentborrowed.html', context)

# Add Equipment
def addEquipment(request):
    if request.method == "POST":
        equipment_name = request.POST.get("equipmentname")
        serial = request.POST.get("serialnum")
        
        if equipment_name and serial:
            # Add to Equipment table
            new_equipment = Equipment(equipmentName=equipment_name, equipmentSN=serial)
            new_equipment.save()
            
            messages.success(request, "Equipment added successfully")
            return redirect('addEquipment')
        else:
            messages.error(request, "Please provide both equipment name and serial number")
    
    # Fetch all equipment objects from the database
    all_equipment = Equipment.objects.all()

    # Pass the equipment objects to the template context
    return render(request, 'officeOfStudentL/adminUser/addEquipment.html', {'all_equipment': all_equipment})

def save_equipment_borrowing(request):
    if request.method == "POST":
        student_id = request.POST.get("student_id")
        equipment_id = request.POST.get("equipmentname")
        date_borrowed = request.POST.get("dateborrowed")

        if student_id and equipment_id and date_borrowed:
            try:
                student = studentInfo.objects.get(studID=student_id)
                equip = Equipment.objects.get(itemId=equipment_id)
                BorrowingRecord.objects.create(student=student, equipment=equip, date_borrowed=date_borrowed)
                messages.success(request, "Equipment borrowing record saved successfully")
            except studentInfo.DoesNotExist:
                messages.error(request, "Student not found")
            except Equipment.DoesNotExist:
                messages.error(request, "Equipment not found")
        else:
            messages.success(request, "Equipment returned successfully")

    return redirect('equipmentTrackerAdmin')


#Transaction Report
@sao_admin_required
def transactionreport(request):
    return render(request, 'adminUSer/transactions.html')


#FOR PPMP TRACKER
@sao_admin_required
def upload_file(request):
    if request.method == 'POST':
        form = UploadFileForm(request.POST, request.FILES)
        if form.is_valid():
            uploaded_file = request.FILES['file']
            if not uploaded_file.name.endswith(('.xlsx', '.xls')):
                messages.error(request, 'File is not an excel file.')
            else:
                try:
                    handle_uploaded_file(uploaded_file)
                    messages.success(request, 'File uploaded successfully')
                except ValueError as e:
                    messages.error(request, str(e))
        else:
            messages.error(request, 'File upload failed')
    else:
        form = UploadFileForm()
    return render(request, 'adminUser/ppmpTracker/ppmp.html', {'form': form})

def handle_uploaded_file(f):
    df = pd.read_excel(f)

    for index, row in df.iterrows():
        procurement_item, created = ProcurementItem.objects.update_or_create(
            itemid=row['id'],
            defaults={
                'item': row['item'],
                'quantity': row['quantity'],
                'unit': row['unit'],
                'estimated_budget': row['estimated_budget'],
                'mode_of_procurement': row['mode_of_procurement'],
                'jan': row['jan'],
                'feb': row['feb'],
                'mar': row['mar'],
                'apr': row['apr'],
                'may': row['may'],
                'jun': row['jun'],
                'jul': row['jul'],
                'aug': row['aug'],
                'sep': row['sep'],
                'oct': row['oct'],
                'nov': row['nov'],
                'dec': row['dec'],
                'unit_price': row['unit_price']
            }
        )

    print("Database updated from Excel file.")

# display the items, though need pag further design for printing huhu

def display_items(request):
    items = ProcurementItem.objects.all()
    return render(request, 'adminUser/ppmpTracker/display_items.html', {'items': items})

# status

@method_decorator(csrf_exempt, name='dispatch')
class UpdateStatusView(View):
    def post(self, request):
        item_id = request.POST.get('item_id')
        new_status = request.POST.get('new_status')
        serial_no = request.POST.get('serial_no', None)

        try:
            item = ProcurementItem.objects.get(itemid=item_id)
            item.status = new_status
            item.save()

            if new_status == 'delivered':
                # Create a new Storage entry
                storage = Storage.objects.create(procurement_item=item, serial_no=serial_no)

                # Also create a new equipment entry
                equipment_name = item.item  # Assuming 'item' is the name of the equipment
                equipmentSN = serial_no if serial_no else 'No Serial Number'
                Equipment.objects.create(equipmentName=equipment_name, equipmentSN=equipmentSN)

            return JsonResponse({'status': 'success'}, status=200)
        except ProcurementItem.DoesNotExist:
            return JsonResponse({'error': 'Item not found'}, status=404)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
        
def display_storage_items(request):
    storage_items = Storage.objects.all()
    return render(request, 'adminUser/ppmpTracker/display_storage_items.html', {'storage_items': storage_items})

def update_serial_no(request, storage_id):
    storage_item = Storage.objects.get(id=storage_id)
    
    if request.method == 'POST':
        form = UpdateSerialNoForm(request.POST, instance=storage_item)
        if form.is_valid():
            form.save()
            return redirect('display_storage_items')
    else:
        form = UpdateSerialNoForm(instance=storage_item)

    return render(request, 'adminUser/ppmpTracker/update_serial_no.html', {'form': form, 'storage_item': storage_item})


# Day five: try to print the purchased items:)
# Day six: total cost per item purchased, final total cost

def purchased_items(request):
   items = ProcurementItem.objects.filter(status="purchased")
   for item in items:
        item.total_cost = item.quantity * item.unit_price

   total_cost_sum = items.aggregate(total_cost_sum=Sum(F('quantity') * F('unit_price')))['total_cost_sum']


   return render(request, 'adminUser/ppmpTracker/purchased_items.html', {'items': items, 'total_cost_sum': total_cost_sum})

def lnd_file(request):
    if request.method == 'POST':
        form = UploadExcelForm(request.POST, request.FILES)
        if form.is_valid():
            file = request.FILES['excel_file']
            fs = FileSystemStorage()
            filename = fs.save(file.name, file)
            file_path = fs.path(filename)
            
            wb = openpyxl.load_workbook(file_path)
            ws = wb.active
            
            for row in ws.iter_rows(min_row=7, max_col=10, values_only=True):
                title_of_l_d = row[0] if row[0] is not None else ''
                frequency = row[1] if row[1] is not None else ''
                category = row[2] if row[2] is not None else ''
                expected_number_of_participants = row[3] if row[3] is not None else ''
                duration = row[4] if row[4] is not None else ''
                registration_fees = row[5] if row[5] is not None else ''
                travelling_expenses = row[6] if row[6] is not None else ''
                planned_total_budget = row[7] if row[7] is not None else ''
                actual_total_budget = row[8] if row[8] is not None else ''

                excel_data, created = ExcelData.objects.update_or_create(
                    title_of_l_d=title_of_l_d,
                    defaults={
                        'frequency': frequency,
                        'category': category,
                        'expected_number_of_participants': expected_number_of_participants,
                        'duration': duration,
                        'registration_fees': registration_fees,
                        'travelling_expenses': travelling_expenses,
                        'planned_total_budget': planned_total_budget,
                        'actual_total_budget': actual_total_budget
                    }
                )
            
            messages.success(request, "L&D File Uploaded!")
           
    else:
        form = UploadExcelForm()
    return render(request, 'adminUser/ppmpTracker/learning_dev.html', {'form': form})

def edit_excel_data(request):
    excel_data = ExcelData.objects.all()
    return render(request, 'adminUser/ppmpTracker/edit_excel_data.html', {'excel_data': excel_data})

def update_excel_data(request, pk):
    excel_data = get_object_or_404(ExcelData, pk=pk)
    if request.method == 'POST':
        form = ExcelDataForm(request.POST, instance=excel_data)
        if form.is_valid():
            form.save()
            return redirect('edit_excel_data')
    else:
        form = ExcelDataForm(instance=excel_data)
    return render(request, 'adminUser/ppmpTracker/update_excel_data.html', {'form': form})
