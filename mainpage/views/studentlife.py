from django.shortcuts import get_object_or_404, redirect, render
from django.contrib import messages
from django.utils import timezone
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
    ProcurementItem, Storage, ExcelData
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

# logger = logging.getLogger(__name__)
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

# Request for GoodMoral Certificate Student Side
def requestedgmc(request):
    student = None
    user = request.user

    if request.user.is_authenticated:
        try:
            student = studentInfo.objects.get(studID=int(user.username))
        except studentInfo.DoesNotExist:
            student = None
            messages.error(request, "Student not found")

    if request.method == "POST":
        reason = request.POST.get("reason")
        if reason:
            try:
                student = studentInfo.objects.get(studID=int(request.user.username))
                RequestedGMC.objects.create(student=student, reason=reason)
                messages.success(request, "Good Moral Certificate request submitted successfully")
                return redirect('requestgmc')
            except studentInfo.DoesNotExist:
                messages.error(request, "Student not found")

    context = {"student": student}
    return render(request, "officeOfStudentL/requestgmc.html", context)

# @sao_admin_required

# Processing Goodmoral Certificate Admin side 
def adminRequestedGmc(request):
    gmc_requests = RequestedGMC.objects.filter(processed=False)
    context = {"gmc_requests": gmc_requests}
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
        sched_res[schedule.sched_Id] = {
            'id': schedule.sched_Id,
            'title': schedule.title,
            'description': schedule.description,
            'start_datetime': schedule.start_datetime.strftime("%Y-%m-%dT%H:%M:%S"),
            'end_datetime': schedule.end_datetime.strftime("%Y-%m-%dT%H:%M:%S"),
            'sdate': schedule.start_datetime.strftime("%B %d, %Y %I:%M %p"),
            'edate': schedule.end_datetime.strftime("%B %d, %Y %I:%M %p")
        }

    context = {
        'sched_json': json.dumps(sched_res)
    }
    return render(request, "officeOfStudentL/monthlyCalendar.html", context)

# Calendar of Activities Admin 
# @sao_admin_required
def monthlyCalendarAdmin(request):
    schedules = Schedule.objects.all()
    sched_res = {}

    for schedule in schedules:
        sched_res[schedule.sched_Id] = {
            'id': schedule.sched_Id,
            'title': schedule.title,
            'description': schedule.description,
            'start_datetime': schedule.start_datetime.strftime("%Y-%m-%dT%H:%M:%S"),
            'end_datetime': schedule.end_datetime.strftime("%Y-%m-%dT%H:%M:%S"),
            'sdate': schedule.start_datetime.strftime("%B %d, %Y %I:%M %p"),
            'edate': schedule.end_datetime.strftime("%B %d, %Y %I:%M %p")
        }

    context = {
        'sched_json': json.dumps(sched_res)
    }
    return render(request, 'officeOfStudentL/adminUser/monthlyCalendarAdmin.html', context)


# Save Schedule
def save_schedule(request):
    if request.method == 'POST':
        schedule_id = request.POST.get('id')
        if schedule_id:
            schedule = get_object_or_404(Schedule, pk=schedule_id)
            form = ScheduleForm(request.POST, instance=schedule)
        else:
            form = ScheduleForm(request.POST)
         
        if form.is_valid():
            form.save()
            return redirect('officeOfStudentL_system:monthlyCalendarAdmin')
    else:
        form = ScheduleForm()
    return render(request, 'officeOfStudentL/adminUser/monthlyCalendarAdmin.html', {'form': form})


# Update schedule start and end datetime drag & drop
def update_schedule(request, schedule_id):
    if request.method == 'POST':
        schedule = get_object_or_404(Schedule, pk=schedule_id)
        start_datetime = request.POST.get('start_datetime')
        end_datetime = request.POST.get('end_datetime')

        if start_datetime and end_datetime:
            schedule.start_datetime = start_datetime
            schedule.end_datetime = end_datetime
            schedule.save()
            return JsonResponse({'status': 'success'})
        else:
            return JsonResponse({'status': 'error', 'message': 'Invalid data provided.'}, status=400)
    else:
        return JsonResponse({'status': 'error', 'message': 'Method not allowed.'}, status=405)

# Delete Schedule
def delete_schedule(request, schedule_id):
    schedule = get_object_or_404(Schedule, pk=schedule_id)
    schedule.delete()
    return redirect('officeOfStudentL_system:monthlyCalendarAdmin')

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
    if request.method == "GET" and "search" in request.GET:
        search_id = request.GET.get("search")
        if search_id:
            try:
                student = studentInfo.objects.get(studID=search_id)
            except studentInfo.DoesNotExist:
                messages.error(request, "Student not found")

    all_equipment = Equipment.objects.all()

    context = {
        'student': student,
        'all_equipment': all_equipment,
        'borrowing_records': borrowing_records
    }
    return render(request, 'officeOfStudentL/adminUser/equipmentTrackerAdmin.html', context)


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
            return redirect('officeOfStudentL_system:addEquipment')
        else:
            messages.error(request, "Please provide both equipment name and serial number")
    
    # Fetch all equipment objects from the database
    all_equipment = Equipment.objects.all()

    # Pass the equipment objects to the template context
    return render(request, 'adminUser/addEquipment.html', {'all_equipment': all_equipment})

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

    return redirect('officeOfStudentL_system:equipmentTrackerAdmin')


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
            return redirect('officeOfStudentL_system:display_storage_items')
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
            return redirect('officeOfStudentL_system:edit_excel_data')
    else:
        form = ExcelDataForm(instance=excel_data)
    return render(request, 'adminUser/ppmpTracker/update_excel_data.html', {'form': form})
