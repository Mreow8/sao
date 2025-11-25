from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.core.mail import send_mail, BadHeaderError
from django.utils import timezone
from django.contrib.auth.decorators import login_required
from django.db.models import Avg
import socket
from mainpage.models import studentInfo
from mainpage.models.alumni import Alumni, graduateForm, Event, JobFair, Yearbook
from ..decorators import sao_admin_required, tracer_gatekeeper_required, alumni_admin_required
from django.shortcuts import render
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import Q
@login_required
def delete_event(request, id):
    # Use eventID because that is the name of the field in your model
    event = get_object_or_404(Event, eventID=id) 
    
    if request.method == "POST":
        event.delete()
        messages.success(request, "Event deleted successfully!")
        return redirect('alumni_events_admin') # Ensure this matches your URL name for the list
    
    return redirect('alumni_events_admin')

@login_required
def alumni_dashboard(request):
    """
    Dashboard view for Alumni users.
    Aggregates data for ID status, Tracer status, and recent events/jobs.
    """
    user = request.user
    student = None
    alumni_acct = None
    tracer_entry = None

    # 1. Fetch Student & Alumni Profile Data
    if user.is_authenticated:
        try:
            student = studentInfo.objects.get(studID=user.username)
            
            # Check for existing Alumni ID Request
            alumni_acct = Alumni.objects.filter(student=student).first()
            
            # Check for existing Graduate Tracer submission
            tracer_entry = graduateForm.objects.filter(student=student).first()
            
        except studentInfo.DoesNotExist:
            # Handle case where user exists but isn't linked to studentInfo (e.g., pure admin)
            student = None

    # 2. Fetch Recent Content for the "Latest Updates" widget
    # Fetch top 3 most recent events
    recent_events = Event.objects.all().order_by('-eventID')[:3] 
    
    # Fetch top 3 most recent job postings
    recent_jobs = JobFair.objects.order_by('-posted_date')[:3]

    context = {
        'student': student,
        'alumni': alumni_acct,       # To show ID status (Pending/Approved)
        'tracer': tracer_entry,      # To show if they need to update tracer
        'recent_events': recent_events,
        'recent_jobs': recent_jobs,
    }
    
    return render(request, 'alumni/alumni_dashboard.html', context)
@alumni_admin_required
@login_required
def admin_id_request(request):
    
    search_query = request.GET.get('search', None)
    sort_by = request.GET.get('sort', 'alumnidate')
    order = request.GET.get('order', 'desc')
    
    alumni_list = Alumni.objects.select_related('student').all()

    if search_query:
        alumni_list = alumni_list.filter(
            Q(student__studID__icontains=search_query) |
            Q(student__lastname__icontains=search_query) |
            Q(student__firstname__icontains=search_query) |
            Q(graduateID__icontains=search_query)  # <-- Fixed
        )

    valid_sort_map = {
        'alumniID': 'graduateID',  # <-- Fixed
        'student__studID': 'student__studID',
        'student__firstname': 'student__firstname',
        'student__lastname': 'student__lastname',
        'alumnidate': 'alumnidate',
        'claimed_date': 'claimed_date',
    }
    
    sort_field = valid_sort_map.get(sort_by, 'alumnidate')
    
    if order == 'desc':
        sort_field = f"-{sort_field}"
        
    alumni_list = alumni_list.order_by(sort_field)
        
    paginator = Paginator(alumni_list, 10)
    page_number = request.GET.get('page')
    
    try:
        page_obj = paginator.page(page_number)
    except PageNotAnInteger:
        page_obj = paginator.page(1)
    except EmptyPage:
        page_obj = paginator.page(paginator.num_pages)

    context = {
        'page_obj': page_obj,
        'user': request.user,
        'current_sort': sort_by,
        'current_order': order,
        'search_params': f"&search={search_query}" if search_query else ""
    }
    
    return render(request, 'alumni/users/admin_idRequest.html', context)
@alumni_admin_required
@login_required
def admin_tracer_list(request):
    
    all_forms = graduateForm.objects.all().order_by('approval_status', 'dategraduated')
    context = {
        'graduate_requests': all_forms,
    }
    return render(request, 'alumni/users/admin_gradTracer.html', context)

@alumni_admin_required
@login_required
def update_form_status(request, pk):
    """
    Handles the Accept/Decline/Pending button clicks from the modal.
    """
    if request.method == 'POST':
        form_to_update = get_object_or_404(graduateForm, pk=pk)
        new_status = request.POST.get('status')

        if new_status in ['Accepted', 'Declined', 'Pending']:
            form_to_update.approval_status = new_status
            form_to_update.save()
            messages.success(request, f"Form status for {form_to_update.firstname} updated to {new_status}.")
        else:
            messages.error(request, "Invalid status submitted.")
            
    # IMPORTANT: Redirects back to the main LIST page
    return redirect('admin_tracer_list')
from datetime import date
from datetime import date # Make sure this import is at the top of your file

@login_required
@tracer_gatekeeper_required
def idRequest(request):
    user = request.user
    student = None
    alumni = None

    if user.is_authenticated:
        try:
            # 1. Get the student profile
            student = studentInfo.objects.get(studID=user.username)
            
            # 2. Try to get their existing alumni record
            try:
                alumni = Alumni.objects.get(student=student)
            except Alumni.DoesNotExist:
                alumni = None # This is fine, it just means they haven't submitted the ID form yet

        except studentInfo.DoesNotExist:
            # This 'except' matches the first 'try'
            student = None
            messages.error(request, 'Your user account is not linked to a student profile.')
            return redirect('homepage') 

    # --- This code is for your form's date validation ---
    today = date.today()
    sixteen_years_ago = date(today.year - 16, today.month, today.day)

    context = {
        'student': student,
        'alumni': alumni, # This will be None or the existing Alumni object
        'today': today,
        'sixteen_years_ago': sixteen_years_ago,
    }
    return render(request, 'alumni/users/id_alumni.html', context)
@login_required
def search_id(request):
    if request.method == 'GET':
        student_id = request.GET.get('student_id')
        if student_id:
            try:
                student_obj = studentInfo.objects.get(studID=student_id)
                return render(request, 'alumni/users/id_alumni.html', {'student': student_obj})
            except studentInfo.DoesNotExist:
                
                messages.error(request, 'No student found with the provided ID.')
                return render(request, 'alumni/users/id_alumni.html')
        else:
            
            messages.error(request, 'Please provide a student ID.')
            return render(request, 'alumni/users/id_alumni.html')
    else:
        
        return render(request, 'alumni/users/id_alumni.html')
    
@login_required
@tracer_gatekeeper_required
def add_alumni(request):
    if request.method == 'POST':
        student_id = request.POST.get('student_id')
        
        student = get_object_or_404(studentInfo, studID=student_id)

        # Use update_or_create:
        # This finds the Alumni record for the student and UPDATES it.
        # If one somehow doesn't exist, it creates it.
        alumni, created = Alumni.objects.update_or_create(
            student=student,  # This is the field to look up
            defaults={        # These are the fields to update/set
                'firstname': request.POST.get('firstname'),
                'lastname': request.POST.get('lastname'),
                'alumnidate': request.POST.get('alumnidate'),
                'alumnibirthday': request.POST.get('alumnibirthday'),
                'alumnicontact': request.POST.get('alumnicontact'),
                'sssgsis': request.POST.get('sssgsis'),
                'tin': request.POST.get('tin'),
                'parentguardian': request.POST.get('parentguardian'),
                'alumniaddress': request.POST.get('alumniaddress'),
                'email_add': request.POST.get('email_add'),
                'degree': request.POST.get('degree'),
                'sex': request.POST.get('sex')
            }
        )
        
        alumni_id = alumni.alumniID
        
        # Updated the message to be more accurate
        messages.success(request, f'Your alumni information has been successfully updated! Your ID is {alumni_id}')
        
        return redirect('idRequest')
    else:
        return redirect('idRequest')
    
@tracer_gatekeeper_required
@login_required
def graduateTracer(request):
    # No login check needed.
    
    try:
        student_id = request.user.username
        student = get_object_or_404(studentInfo, studID=student_id)
        
        # ALL THE CHECKS ARE GONE.
 
        

        # In graduateTracer(request):

        existing_form = graduateForm.objects.filter(student=student).first()
        
        if existing_form:
            return render(request, 'alumni/users/graduateTracer.html', {
                'student': student,  # <--- FIX
                'student_id': student_id,
                'already_submitted': True,
                'submitted_form': existing_form,
            })
        
        return render(request, 'alumni/users/graduateTracer.html', {
            'student': student,  # <--- FIX
            'student_id': student_id,
            'already_submitted': False,
        })
        
    except studentInfo.DoesNotExist:
        messages.error(request, 'Your user account is not linked to a student profile.')
        return render(request, 'alumni/users/graduateTracer.html', {'already_submitted': False})
    
    except Exception as e:
        messages.error(request, f'An error occurred: {str(e)}')
        return render(request, 'alumni/users/graduateTracer.html', {'already_submitted': False})
@login_required
def search_id2(request):
    user = request.user
    if not user.is_authenticated:
        messages.error(request, 'Please log in to continue.')
        return redirect('login')  # or wherever your login URL is

    try:
        student_id = user.username
        alumni_obj = Alumni.objects.get(student__studID=student_id)

        if graduateForm.objects.filter(student__studID=student_id).exists():
            messages.error(request, 'You have already filled out this form.')
            return render(request, 'alumni/users/graduateTracer.html', {
                'alumni': alumni_obj,
                'student_id': student_id
            })

        return render(request, 'alumni/users/graduateTracer.html', {
            'alumni': alumni_obj,
            'student_id': student_id
        })
        
    except Alumni.DoesNotExist:
        messages.error(request, 'Not Found! Please request first for alumni ID.')
        return render(request, 'alumni/users/graduateTracer.html')

    except Exception as e:
        messages.error(request, f'An error occurred: {str(e)}')
        return render(request, 'alumni/users/graduateTracer.html')
@login_required
def graduateTracer_submit(request):
    if request.method == 'POST':
        # --- Data Retrieval (No Change Here) ---
        student_id = request.POST.get('student_id')
        firstname = request.POST.get('firstname')
        lastname = request.POST.get('lastname')
        degree = request.POST.get('degree')
        email_add = request.POST.get('email_add')
        contactnum = request.POST.get('contactnum')
        sex = request.POST.get('sex')
        alumniaddress = request.POST.get('alumniaddress')
        dategraduated = request.POST.get('dategraduated')
        nameoforganization = request.POST.get('nameoforganization')
        employmenttype = request.POST.get('employmentype')
        occupationalClass = request.POST.get('occupationalClass')
        organizationType = request.POST.get('organizationType')
        gradscholrelated = request.POST.get('gradscholrelated')
        yearscompany = request.POST.get('yearscompany')
        placework = request.POST.get('placework')
        firstjobgraduate = request.POST.get('firstjobgraduate')
        reasonstayingjob = request.POST.get('reasonstayingjob')
        designation = request.POST.get('designation')
        status = request.POST.get('status')
        monthlyincome = request.POST.get('monthlyincome')
        workwhileworking = request.POST.get('workwhileworking')
        ifnotworking = request.POST.get('ifnotworking')
        reasontimegap = request.POST.get('reasontimegap')
        natureemployment = request.POST.get('natureemployment')
        numberofyears = request.POST.get('numberofyears')
        monthlyincome2 = request.POST.get('monthlyincome2')
        academicprofession = request.POST.get('academicprofession')
        researchcapability = request.POST.get('researchcapability')
        learningefficiency = request.POST.get('learningefficiency')
        peopleskills = request.POST.get('peopleskills')
        problemsolvingskills = request.POST.get('problemsolvingskills')
        informationtechnologyskills = request.POST.get('informationtechnologyskills')
        meetingprofessionalneeds = request.POST.get('meetingprofessionalneeds')
        communityfield = request.POST.get('communityfield')
        globalfield = request.POST.get('globalfield')
        criticalskills = request.POST.get('criticalskills')
        rangeofcourses = request.POST.get('rangeofcourses')
        relevanceprofession = request.POST.get('relevanceprofession')
        extracurricular = request.POST.get('extracurricular')
        premiumresearch = request.POST.get('premiumresearch')
        interlearning = request.POST.get('interlearning')
        teachingenvironment = request.POST.get('teachingenvironment')
        qualityinstruction = request.POST.get('qualityinstruction')
        teachrelationship = request.POST.get('teachrelationship')
        libraryresources = request.POST.get('libraryresources')
        labresources = request.POST.get('labresources')
        classize = request.POST.get('classize')
        profexpertise = request.POST.get('profexpertise')
        profsubjectmatter = request.POST.get('profsubjectmatter')
        raw_enrollmentdate = request.POST.get('enrollmentdate')
        enrollmentdate = raw_enrollmentdate if raw_enrollmentdate else None

        studiesdegree = request.POST.get('studiesdegree')
        universityinstitution = request.POST.get('universityinstitution')
        studiesAddress = request.POST.get('studiesAddress')
        pursuingstudies = request.POST.get('pursuingstudies')  
        department = request.POST.get('department')  
        salaryimprovement = request.POST.get('salaryimprovement')  
        opportunitiesabroad = request.POST.get('opportunitiesabroad')  
        personalitydevelopment = request.POST.get('personalitydevelopment')  
        technologiesvaluesformation = request.POST.get('technologiesvaluesformation')  
        
        # --- Core Logic to Fetch Records (No Change) ---
        try:
            student = get_object_or_404(studentInfo, studID=student_id)
        except:
            messages.error(request, 'Student ID not found.')
            return redirect('graduateTracer')

        # This is the only check you need.
        existing_form = graduateForm.objects.filter(student=student).first()
        if existing_form:
            messages.error(request, "You have already submitted the graduate tracer form.")
            return redirect('graduateTracer')
            
        gradform = graduateForm.objects.create( student=student,
                                    degree=degree,
                                    email_add=email_add,
                                    contactnum=contactnum,
                                    sex=sex,
                                    firstname=firstname,
                                    lastname=lastname,
                                    alumniaddress=alumniaddress,
                                    dategraduated=dategraduated,
                                    nameoforganization=nameoforganization,
                                    employmenttype=employmenttype,
                                    organizationType=organizationType,
                                    occupationalClass=occupationalClass,
                                    gradscholrelated=gradscholrelated,
                                    yearscompany=yearscompany,
                                    placework=placework,
                                    firstjobgraduate=firstjobgraduate,
                                    reasonstayingjob=reasonstayingjob,
                                    designation=designation,
                                    status=status,
                                    monthlyincome=monthlyincome,
                                    workwhileworking=workwhileworking,
                                    ifnotworking=ifnotworking,
                                    reasontimegap=reasontimegap,
                                    numberofyears=numberofyears,
                                    monthlyincome2=monthlyincome2,
                                    academicprofession=academicprofession,
                                    researchcapability=researchcapability,
                                    learningefficiency=learningefficiency,
                                    peopleskills=peopleskills,
                                    problemsolvingskills=problemsolvingskills,
                                    informationtechnologyskills=informationtechnologyskills,
                                    communityfield=communityfield,
                                    globalfield=globalfield,
                                    criticalskills=criticalskills,
                                    rangeofcourses=rangeofcourses,
                                    relevanceprofession=relevanceprofession,
                                    extracurricular=extracurricular,
                                    premiumresearch=premiumresearch,
                                    interlearning=interlearning,
                                    teachingenvironment=teachingenvironment,
                                    qualityinstruction=qualityinstruction,
                                    teachrelationship=teachrelationship,
                                    libraryresources=libraryresources,
                                    labresources=labresources,
                                    classize=classize,
                                    profexpertise=profexpertise,
                                    profsubjectmatter=profsubjectmatter,
                                    enrollmentdate=enrollmentdate,
                                    studiesdegree=studiesdegree,
                                    universityinstitution=universityinstitution,
                                    studiesAddress=studiesAddress,
                                    pursuingstudies=pursuingstudies,
                                    department=department,
                                    natureemployment = natureemployment,
                                    meetingprofessionalneeds=meetingprofessionalneeds,
                                    salaryimprovement=salaryimprovement,
                                    opportunitiesabroad=opportunitiesabroad,
                                    approval_status='Pending',
                                    personalitydevelopment=personalitydevelopment,
                                    technologiesvaluesformation=technologiesvaluesformation,
                                    
        )
        
        # --- CRITICAL CHANGE HERE ---
        # The user successfully completed the TRACER FORM.
        # We do NOT mention the Alumni ID.
        messages.success(request, f'Thank you! Your Graduate Tracer Form has been submitted successfully. You can now access other Alumni features.')
        return redirect('graduateTracer')
    else:
        return redirect('graduateTracer')
@tracer_gatekeeper_required
@login_required
def alumni_events(request):
    events = Event.objects.all()    
    return render(request, 'alumni/users/alumni_events.html', {'events': events}) 
@alumni_admin_required   
@login_required
def alumni_events_admin(request):
    events = Event.objects.all()    
    return render(request, 'alumni/users/alumni_events_admin.html', {'events': events})    
def jobfairs(request):
    job_fairs = JobFair.objects.order_by('-posted_date')
    return render(request, 'alumni/users/jobfairs.html', {'job_fairs': job_fairs})



@login_required
def yearbook(request):
    return render(request, 'alumni/users/yearbook.html')


@login_required
def search_yearbook(request):
    if request.method == 'GET':
        first_name = request.GET.get('yeargetfirstname')
        last_name = request.GET.get('yeargetlastname')

        if first_name and last_name:
            try:
               
                first_name = first_name.lower()
                last_name = last_name.lower()

       
                yearbook_entry = Yearbook.objects.get(yearbookFirstname__iexact=first_name, yearbookLastname__iexact=last_name)
                return render(request, 'alumni/users/yearbook.html', {'yearbook_entry': yearbook_entry})
            except Yearbook.DoesNotExist:
                return render(request, 'alumni/users/yearbook.html', {'error_message': 'No yearbook entry found.'})
        else:
            return render(request, 'alumni/users/yearbook.html', {'error_message': 'Please provide both first name and last name in the search.'})
    else:
        return render(request, 'alumni/users/yearbook.html')

@sao_admin_required
def transaction_alumni(request):
    return render(request, 'alumni/users/transaction_alumni.html')
@sao_admin_required
@login_required
def transac_search(request):
    context = {}
    
    if request.method == 'POST':
        transac_choice = request.POST.get('transac_choice')
        transac_frequency = request.POST.get('transac_frequency')

        current_month = timezone.now().month

        # Alumni ID Requests
        if transac_choice == 'Alumni ID Requests':
            if transac_frequency == 'Monthly':
                alumni_requests = Alumni.objects.filter(alumnidate__month=current_month)
            elif transac_frequency == 'Yearly':
                alumni_requests = Alumni.objects.filter(alumnidate__year=timezone.now().year)
            else:
                alumni_requests = Alumni.objects.all()

            total_count = alumni_requests.count()
            context = {
                'alumni_requests': alumni_requests,
                'transac_frequency': transac_frequency,
                'total_count': total_count,
                'transac_choice': transac_choice
            }

        # Graduate Tracer
        elif transac_choice == 'Graduate Tracer':
            if transac_frequency == 'Monthly':
                graduate_tracer_data = graduateForm.objects.filter(enrollmentdate__month=current_month)
            elif transac_frequency == 'Yearly':
                graduate_tracer_data = graduateForm.objects.filter(enrollmentdate__year=timezone.now().year)
            else:
                graduate_tracer_data = graduateForm.objects.all()

            total_count = graduate_tracer_data.count()
            has_reports = total_count > 0

            # Aggregate weighted means
            weighted_means = {
                'academicprofession': graduate_tracer_data.aggregate(Avg('academicprofession'))['academicprofession__avg'],
                'researchcapability': graduate_tracer_data.aggregate(Avg('researchcapability'))['researchcapability__avg'],
                'learningefficiency': graduate_tracer_data.aggregate(Avg('learningefficiency'))['learningefficiency__avg'],
                'peopleskills': graduate_tracer_data.aggregate(Avg('peopleskills'))['peopleskills__avg'],
                'problemsolvingskills': graduate_tracer_data.aggregate(Avg('problemsolvingskills'))['problemsolvingskills__avg'],
                'informationtechnologyskills': graduate_tracer_data.aggregate(Avg('informationtechnologyskills'))['informationtechnologyskills__avg'],
                'meetingprofessionalneeds': graduate_tracer_data.aggregate(Avg('meetingprofessionalneeds'))['meetingprofessionalneeds__avg'],
                'communityfield': graduate_tracer_data.aggregate(Avg('communityfield'))['communityfield__avg'],
                'globalfield': graduate_tracer_data.aggregate(Avg('globalfield'))['globalfield__avg'],
                'criticalskills': graduate_tracer_data.aggregate(Avg('criticalskills'))['criticalskills__avg'],
                'salaryimprovement': graduate_tracer_data.aggregate(Avg('salaryimprovement'))['salaryimprovement__avg'],
                'opportunitiesabroad': graduate_tracer_data.aggregate(Avg('opportunitiesabroad'))['opportunitiesabroad__avg'],
                'personalitydevelopment': graduate_tracer_data.aggregate(Avg('personalitydevelopment'))['personalitydevelopment__avg'],
                'technologiesvaluesformation': graduate_tracer_data.aggregate(Avg('technologiesvaluesformation'))['technologiesvaluesformation__avg'],
                'rangeofcourses': graduate_tracer_data.aggregate(Avg('rangeofcourses'))['rangeofcourses__avg'],
                'relevanceprofession': graduate_tracer_data.aggregate(Avg('relevanceprofession'))['relevanceprofession__avg'],
                'extracurricular': graduate_tracer_data.aggregate(Avg('extracurricular'))['extracurricular__avg'],
                'premiumresearch': graduate_tracer_data.aggregate(Avg('premiumresearch'))['premiumresearch__avg'],
                'interlearning': graduate_tracer_data.aggregate(Avg('interlearning'))['interlearning__avg'],
                'teachingenvironment': graduate_tracer_data.aggregate(Avg('teachingenvironment'))['teachingenvironment__avg'],
                'qualityinstruction': graduate_tracer_data.aggregate(Avg('qualityinstruction'))['qualityinstruction__avg'],
                'teachrelationship': graduate_tracer_data.aggregate(Avg('teachrelationship'))['teachrelationship__avg'],
                'libraryresources': graduate_tracer_data.aggregate(Avg('libraryresources'))['libraryresources__avg'],
                'labresources': graduate_tracer_data.aggregate(Avg('labresources'))['labresources__avg'],
                'classize': graduate_tracer_data.aggregate(Avg('classize'))['classize__avg'],
                'profexpertise': graduate_tracer_data.aggregate(Avg('profexpertise'))['profexpertise__avg'],
                'profsubjectmatter': graduate_tracer_data.aggregate(Avg('profsubjectmatter'))['profsubjectmatter__avg']
            }

            context = {
                'graduate_tracer_data': graduate_tracer_data,
                'transac_frequency': transac_frequency,
                'total_count': total_count,
                'transac_choice': transac_choice,
                'weighted_means': weighted_means,
                'has_reports': has_reports
            }

    return render(request, 'alumni/users/transaction_alumni.html', context)


# admin alumni
# @sao_admin_required
@alumni_admin_required
@login_required
def approve_alumni_request(request, alumni_id):
    if request.method == 'POST':
        alumni = get_object_or_404(Alumni, pk=alumni_id)
        email_add = alumni.email_add

        try:
            send_mail(
                'Alumni ID Request Approved',
                f'Hello {alumni.firstname} {alumni.lastname},\n\nYour alumni ID request has been approved. Your ID is ready to claim.\n\nThank you!',
                'alumni_ctuac@ctu.edu.ph',
                [email_add],
                fail_silently=False,
            )
            alumni.approved = True  # Mark as approved
            alumni.save()

        except (socket.error, BadHeaderError) as e:
            messages.error(request, f'Error sending email: {e}')
        
        return redirect('admin_idRequest')

    return redirect('admin_idRequest')
    
@login_required
def claim_alumni_id(request, alumni_id):
    if request.method == 'POST':
        alumni = get_object_or_404(Alumni, pk=alumni_id)
        alumni.claimed_date = timezone.now()
        alumni.save()
        return redirect('admin_idRequest')

    return redirect('admin_idRequest')

@alumni_admin_required
@login_required
def admin_gradTracer(request):
    graduate_requests = graduateForm.objects.select_related('student').all()
    return render(request, 'alumni/users/admin_gradTracer.html', {'graduate_requests': graduate_requests})

from ..forms import EventForm
from ..forms import EventForm
@alumni_admin_required
@login_required
def admin_events(request):
    if request.method == 'POST':
        # 1. Bind the form to the POST data
        form = EventForm(request.POST, request.FILES)
        
        if form.is_valid():
            # 2. SUCCESS: Save and redirect
            form.save()
            messages.success(request, 'Successfully Added!')
            return redirect('admin_events')
        
        # 3. FAIL: If invalid, the code continues here. 
        # The 'form' variable now has the data and errors.
    
    else:
        # 4. GET Request: Show a blank form
        form = EventForm()

    # 5. Pass the form (either new or with errors) to the template
    context = {'form': form}
    return render(request, 'alumni/users/admin_events.html', context)
@alumni_admin_required
@login_required
def admin_jobfairs(request):
    if request.method == "POST":
        jobtitle = request.POST.get("jobtitle")
        companyname = request.POST.get("companyname")
        joblocation = request.POST.get("joblocation")
        jobsalary = request.POST.get("jobsalary")
        employmenttype = request.POST.get("employmenttype")
        jobdescription = request.POST.get("jobdescription")
        applicationdeadline = request.POST.get('applicationdeadline')
        posted_date = request.POST.get('posted_date')

        jobfair = JobFair.objects.create(
            jobtitle=jobtitle,
            companyname=companyname,
            joblocation=joblocation,
            jobsalary=jobsalary,
            employmenttype=employmenttype,
            jobdescription=jobdescription,
            posted_date=posted_date,
            applicationdeadline=applicationdeadline
        )

        messages.success(request, "Successfully Added!")
        return redirect("admin_jobfairs")

    job_fairs = JobFair.objects.order_by('-posted_date')
    return render(request, "alumni/users/admin_jobfairs.html", {"job_fairs": job_fairs})



# @sao_admin_required
@login_required
def admin_yearbook(request):
    if request.method == 'POST':
        yearbookFirstname = request.POST.get('yearfirstname')
        yearbookLastname = request.POST.get('yearlastname')
        yearbookAddress = request.POST.get('yearaddress')
        yearbookCourse = request.POST.get('yearcourse')
        yearbookImage = request.FILES.get('yearImage')  
        yearbookGender = request.POST.get('yeargender')
        yearbookYearGrad = request.POST.get('yeargraduated')

        # Check if an entry with the same first name and last name already exists
        if Yearbook.objects.filter(yearbookFirstname=yearbookFirstname, yearbookLastname=yearbookLastname).exists():
            messages.error(request, 'An entry with this name already exists.')
        else:
            yearbook_entry = Yearbook.objects.create(
                yearbookFirstname=yearbookFirstname,
                yearbookLastname=yearbookLastname,
                yearbookAddress=yearbookAddress,
                yearbookCourse=yearbookCourse,
                yearbookImage=yearbookImage,
                yearbookGender=yearbookGender,
                yearbookYearGrad=yearbookYearGrad
            )
            messages.success(request, 'Successfully Added!')
        
        return redirect('admin_yearbook')

    return render(request, 'alumni/users/admin_yearbook.html')
