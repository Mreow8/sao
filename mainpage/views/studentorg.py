from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from django.contrib import messages
from ..forms import OfficerForm
from ..forms import ProjectForm
from ..forms import FinancialStatementForm
from ..forms import AccreditationForm, AdviserForm, OrganizationForm
from ..models import Project, Accreditation, Adviser
from ..models import FinancialStatement, Officer
from ..models import Organization
import base64, uuid
from django.core.files.base import ContentFile
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required, user_passes_test
# Create your views here.
from django.shortcuts import render, get_object_or_404
# views.py
# views.py
def is_superadmin(user):
    return user.is_authenticated and user.role == 'superadmin'
from django.shortcuts import render, redirect, get_object_or_404
from django.shortcuts import render, redirect, get_object_or_404
from ..models import Organization, Accreditation, Adviser, Requirement
from ..forms import AccreditationForm

def view_adviser(request, org_slug):
    # Get the organization by slug
    organization = get_object_or_404(Organization, slug=org_slug)

    # Filter advisers for this organization
    approved_advisers = Adviser.objects.filter(status='approved', organization=organization)

    return render(request, 'studentorg/main/view_adviser.html', {
        'advisers': approved_advisers,
        'organization': organization
    })
def upload_accreditation(request, slug):
    org = get_object_or_404(Organization, slug=slug)

    # Get the latest uploaded accreditation (if any) for showing links
    uploaded_files = Accreditation.objects.filter(organization=org).last()

    if request.method == "POST":
        form = AccreditationForm(request.POST, request.FILES)
        if form.is_valid():
            accreditation = form.save(commit=False)
            accreditation.organization = org
            accreditation.save()
            return redirect("organization_accreditations", slug=org.slug)
    else:
        form = AccreditationForm()

    return render(request, "studentorg/main/accreditation_form.html", {
        "form": form,
        "organization": org,
        "uploaded_files": uploaded_files,
    })


# 2. Show details of a single accreditation
def accreditation_detail(request, accreditation_id):
    accreditation = get_object_or_404(Accreditation, pk=accreditation_id)
    base_template = "adminmain.html" if request.user.is_staff or request.user.is_superuser else "main.html"


    return render(request, "main/accreditation_detail.html", {
        "accreditation": accreditation,
    })
def view_financial(request, slug):
    print("🔍 view_financial called with slug:", slug)
    base_template = "adminmain.html" if request.user.is_staff or request.user.is_superuser else "main.html"

    try:
        org_obj = Organization.objects.get(slug=slug)
        print("✅ Organization found:", org_obj.name)
    except Organization.DoesNotExist:
        print("❌ ERROR: Organization not found for slug:", slug)
        messages.error(request, "Organization not found.")
        return redirect('home')

    approved_statements = FinancialStatement.objects.filter(status='approved', org=org_obj)
    print("📊 Found", approved_statements.count(), "approved statements for", org_obj.name)

    if request.method == 'POST':
        print("📩 POST request received.")
        form = FinancialStatementForm(request.POST)
        if form.is_valid():
            print("✅ Form is valid. Saving financial statement...")
            try:
                instance = form.save(commit=False)
                instance.organization_slug = slug
                instance.org = org_obj
                instance.save()
                print("💾 Financial statement saved successfully!")
                messages.success(request, "Financial statement submitted successfully!")
                return redirect('view_financial_by_slug', slug=slug)
            except Exception as e:
                print("❌ ERROR while saving FinancialStatement:", e)
                messages.error(request, "An error occurred while saving the financial statement.")
        else:
            print("❌ Form is invalid. Errors:", form.errors)
            messages.error(request, "There was an error submitting the form.")
    else:
        print("📄 GET request – displaying form.")
        form = FinancialStatementForm()

    print("➡️ Rendering template with", approved_statements.count(), "approved statements.")
    return render(request, 'studentorg/MAIN/view_financial.html', {
        'form': form,
        'statements': approved_statements,
        'org': org_obj,
        'slug': slug,
        'base_template': base_template,
    })


# Add these imports at the top of studentorg.py
from django.forms import inlineformset_factory
from django.contrib import messages
from ..models import (
    Organization, Adviser, AdviserEducation, AdviserWorkExperience, 
    AdviserOrganization, AdviserAdvisory
)
from ..forms import (
    AdviserForm, AdviserEducationForm, AdviserWorkExperienceForm, 
    AdviserOrganizationForm, AdviserAdvisoryForm
)

def register_adviser(request, slug):
    organization = get_object_or_404(Organization, slug=slug)
    base_template = "adminmain.html" if request.user.is_staff or request.user.is_superuser else "main.html"

    # --- Create the Formsets ---
    # We tell each formset how many "extra" (blank) forms to create
    # This matches your old HTML (5 education slots, 5 work slots, etc.)
    EducationFormSet = inlineformset_factory(
        Adviser, AdviserEducation, form=AdviserEducationForm, 
        extra=5, can_delete=False
    )
    WorkFormSet = inlineformset_factory(
        Adviser, AdviserWorkExperience, form=AdviserWorkExperienceForm, 
        extra=5, can_delete=False
    )
    OrgFormSet = inlineformset_factory(
        Adviser, AdviserOrganization, form=AdviserOrganizationForm, 
        extra=2, can_delete=False
    )
    AdvisoryFormSet = inlineformset_factory(
        Adviser, AdviserAdvisory, form=AdviserAdvisoryForm, 
        extra=3, can_delete=False
    )

    if request.method == 'POST':
        # Bind all forms and formsets with the POST data
        adviser_form = AdviserForm(request.POST, request.FILES)
        education_formset = EducationFormSet(request.POST, prefix='education')
        work_formset = WorkFormSet(request.POST, prefix='work')
        org_formset = OrgFormSet(request.POST, prefix='org')
        advisory_formset = AdvisoryFormSet(request.POST, prefix='advisory')

        # Check if all forms are valid
        if (adviser_form.is_valid() and education_formset.is_valid() and 
            work_formset.is_valid() and org_formset.is_valid() and 
            advisory_formset.is_valid()):
            
            # Save the main adviser form
            adviser = adviser_form.save(commit=False)
            adviser.organization = organization
            adviser.save() # Save the adviser to get a PK

            # Link the formsets to the new adviser instance
            education_formset.instance = adviser
            work_formset.instance = adviser
            org_formset.instance = adviser
            advisory_formset.instance = adviser

            # Save all the formsets
            education_formset.save()
            work_formset.save()
            org_formset.save()
            advisory_formset.save()

            messages.success(request, "Adviser successfully registered!")
            return redirect('register_adviser', slug=slug)
        else:
            # If any form is invalid, show the errors
            messages.error(request, "Please correct the errors below.")

    else:
        # GET Request: Create all blank forms
        adviser_form = AdviserForm()
        education_formset = EducationFormSet(prefix='education')
        work_formset = WorkFormSet(prefix='work')
        org_formset = OrgFormSet(prefix='org')
        advisory_formset = AdvisoryFormSet(prefix='advisory')

    context = {
        'organization': organization,
        'base_template': base_template,
        'slug': slug,
        'adviser_form': adviser_form,
        'education_formset': education_formset,
        'work_formset': work_formset,
        'org_formset': org_formset,
        'advisory_formset': advisory_formset,
    }
    # Use the *new* template name
    return render(request, 'studentorg/Main/register_adviser_new.html', context)
def adviser_form(request, slug):
    organization = get_object_or_404(Organization, slug=slug)

    if request.method == 'POST':
        form = AdviserForm(request.POST, request.FILES)
        if form.is_valid():
            adviser = form.save(commit=False)
            adviser.organization = organization  # if Adviser has FK to Organization
            adviser.save()
            return redirect('adviser_form', slug=slug)
    else:
        form = AdviserForm()

    return render(request, f'studentorg/adviserform/{slug}_adviserdata.html', {
        'form': form,
        'organization': organization,
        'slug': slug,
    })
from django.shortcuts import render, redirect
from ..forms import OfficerForm, OfficerMembershipForm, OfficerSeminarForm
from django.contrib import messages
from django.shortcuts import render, redirect

def officer_create(request):
    if request.method == "POST":
        officer_form = OfficerForm(request.POST)
        membership_form = OfficerMembershipForm(request.POST)
        seminar_form = OfficerSeminarForm(request.POST)

        if (officer_form.is_valid() and membership_form.is_valid() and seminar_form.is_valid()):
            officer = officer_form.save()  # Save Officer first

            # Link related models
            membership = membership_form.save(commit=False)
            membership.officer = officer
            membership.save()

            seminar = seminar_form.save(commit=False)
            seminar.officer = officer
            seminar.save()

            # ✅ Success popup
            messages.success(request, "Officer record was successfully created 🎉")
            return redirect("officer_list")

        else:
            # ❌ Error popup
            messages.error(request, "There was an error saving the officer. Please check the form.")

    else:
        officer_form = OfficerForm()
        membership_form = OfficerMembershipForm()
        seminar_form = OfficerSeminarForm()

    return render(request, "studentorg/Main/officer_formcopy.html", {
        "officer_form": officer_form,
        "membership_form": membership_form,
        "seminar_form": seminar_form,
    })

from django.shortcuts import render, redirect, get_object_or_404
from ..forms import OfficerForm, OfficerMembershipForm, OfficerSeminarForm
from ..models import Organization,studentInfo

# Make sure you have all these imports at the top of your views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.http import JsonResponse
#
# ADD THIS NEW VIEW TO YOUR views.py
#
def search_students(request):
    """
    This view is called by the JavaScript autocomplete.
    It returns a JSON list of students matching the search 'term'.
    """
    term = request.GET.get("term")
    
    if term:
        # Search for students whose studID *starts with* the term
        students = studentInfo.objects.filter(studID__startswith=term)[:10]
    else:
        students = studentInfo.objects.none()

    results = []
    for student in students:
        # Check for 'surname' or 'lastname' on your student model
        student_surname = getattr(student, 'surname', getattr(student, 'lastname', 'N/A'))
        
        results.append({
            "id": student.pk,  # The studentInfo primary key (e.g., 1, 2, 3)
            "label": f"{student.studID} - {student_surname}, {student.firstname}",
            "value": student.studID,
            
            # --- Extra data for autofill ---
            "firstname": student.firstname,
            "surname": student_surname,
            "year": student.yearlvl    # Assumes your student model has 'yearlvl'
        })

    return JsonResponse(results, safe=False)
#
# THIS IS YOUR MAIN VIEW, UPDATED
#
def officer_form(request, slug=None):
    base_template = (
        "adminmain.html"
        if request.user.is_staff or request.user.is_superuser
        else "main.html"
    )

    organization = None
    if slug:
        organization = get_object_or_404(Organization, slug=slug)

    # This block finds the student record for the LOGGED-IN USER
    student = None
    if request.user.is_authenticated:
        try:
            student = studentInfo.objects.get(studID=int(request.user.username))
        except (studentInfo.DoesNotExist, ValueError):
            # Admin or unlinked user. 'student' remains None.
            student = None

    if request.method == "POST":
        officer_form = OfficerForm(request.POST, request.FILES)
        membership_form = OfficerMembershipForm(request.POST)
        seminar_form = OfficerSeminarForm(request.POST)

        # The is_valid() check now also fails if the hidden 'student'
        # field is empty, because it's a required model field.
        if officer_form.is_valid():
            officer = officer_form.save(commit=False)

            if organization:
                officer.organization = organization

            # --- KEY LOGIC ---
            if student:
                # If the logged-in user IS a student, link them
                # This overrides any admin search.
                officer.student = student
            
            # If the user is an admin ('student' is None),
            # 'officer.student' was already set from the form.
            # We can now safely save.
            
            officer.save()

            # --- Save related forms ---
            if membership_form.is_valid() and membership_form.cleaned_data:
                membership = membership_form.save(commit=False)
                membership.officer = officer
                membership.save()

            if seminar_form.is_valid() and seminar_form.cleaned_data:
                seminar = seminar_form.save(commit=False)
                seminar.officer = officer
                seminar.save()

            messages.success(request, "Officer has been successfully added!")

            if organization:
                # Redirect to the org profile on success
                return redirect("org_profile", slug=organization.slug)
            else:
                return redirect("home") # Or your admin dashboard

        else:
            # Form was invalid (e.g., admin didn't select a student,
            # or mobile number was wrong)
            print(officer_form.errors)
            messages.error(request, "There was an error. Please check the form fields.")

    else:
        # GET request: show blank forms
        officer_form = OfficerForm()
        membership_form = OfficerMembershipForm()
        seminar_form = OfficerSeminarForm()

    return render(
        request,
        "studentorg/Main/officer_formcopy.html",
        {
            "officer_form": officer_form,
            "membership_form": membership_form,
            "seminar_form": seminar_form,
            "organization": organization,
            "base_template": base_template,
        },
    )
# def officer_forms(request):
#     organizations = Organization.objects.all()  # list of all orgs

#     if request.method == 'POST':
#         form = OfficerForm(request.POST, request.FILES)
#         if form.is_valid():
#             officer = form.save(commit=False)
            
#             # get org_id from dropdown
#             org_id = request.POST.get("organization")
#             organization = get_object_or_404(Organization, pk=org_id)

#             officer.organization = organization
#             officer.save()
#             return redirect('admin_manageofficer')  # go back after save

#     else:
#         form = OfficerForm()

#     return render(request, 'studentorg/Main/officer_formcopy.html', {
#         'form': form,
#         'organizations': organizations,
#     })
# def officer_form(request, slug):
#     base_template = "adminmain.html" if request.user.is_staff or request.user.is_superuser else "main.html"

#     organization = get_object_or_404(Organization, slug=slug)

#     if request.method == 'POST':
#         form = OfficerForm(request.POST, request.FILES)
#         if form.is_valid():
#             officer = form.save(commit=False)
#             officer.organization = organization
#             officer.save()
#             return redirect('officer_form', slug=slug)

#     return render(request, 'studentorg/Main/officer_form.html', {'organization': organization,   'base_template': base_template,})

def view_officers(request, slug):
    org = get_object_or_404(Organization, slug=slug)
    statements = Officer.objects.filter(organization=org, status="approved")

    return render(request, 'studentorg/Main/view_officer.html', {
        'org': org,
        'statements': statements
    })
def edit_org(request, slug):
    org = get_object_or_404(Organization, slug=slug)
    if request.method == 'POST':
        form = OrganizationForm(request.POST, request.FILES, instance=org)
        if form.is_valid():
            form.save()
            return redirect('FSTLP_profile')  # or use `slug` dynamically
    else:
        form = OrganizationForm(instance=org)
    return render(request, 'studentorg/Main/OrgMain.html', {'form': form})
def view_project_by_slug(request, slug):
    base_template = "adminmain.html" if request.user.is_staff or request.user.is_superuser else "main.html"
    org = get_object_or_404(Organization, slug=slug)

    # --- START OF NEW CODE ---
    if request.method == 'POST':
        # Check if the user is allowed to submit
        if not (request.user.is_authenticated and (request.user.role == 'superadmin' or (request.user.role == 'org_member' and request.user.organization == org))):
            messages.error(request, "You are not authorized to submit projects for this organization.")
            return redirect('view_project_by_slug', slug=slug)

        # Get all the data from the form
        try:
            new_project = Project(
                org=org,  # Link the organization
                objective=request.POST.get('objective'),
                activities=request.POST.get('activities'),
                target=request.POST.get('target'),
                involved_officer=request.POST.get('involved_officer'),
                p_budget=request.POST.get('p_budget'),
                expected_output=request.POST.get('expected_output'),
                remarks=request.POST.get('remarks'),
                actual_accomplishment=request.FILES.get('actual_accomplishment')
                # The 'status' field will use its default value, which is likely 'pending'
            )
            new_project.save()
            messages.success(request, "Project submitted successfully! It is now pending approval.")
            return redirect('view_project_by_slug', slug=slug)

        except Exception as e:
            messages.error(request, f"An error occurred: {e}")

    # --- END OF NEW CODE ---

    # This part runs on a normal page load (GET request)
    projects = Project.objects.filter(status='approved', org=org)
    return render(request, 'studentorg/Main/view_projects.html', {
        'org': org,
        'projects': projects,
        'base_template': base_template,
    })
# Add this function to scholarship.py
from django.db.models import Q # Make sure Q is imported at the top of the file

@login_required

def org_profile(request, slug):
    base_template = "adminmain.html" if request.user.is_staff or request.user.is_superuser else "main.html"
    org = get_object_or_404(Organization, slug=slug)

    # Check if user can edit this org
    user = request.user
    can_edit = (
        user.role == 'superadmin' or
        (user.role == 'org_member' and user.organization == org)
    )

    is_edit = request.GET.get('edit') == 'true' and can_edit

    if request.method == 'POST':
        if not can_edit:
            return redirect('org_profile', slug=slug)  # Prevent unauthorized post

        form = OrganizationForm(request.POST, request.FILES, instance=org)

        # Process key elements
        key_elements_raw = request.POST.getlist('key_elements[]')
        key_elements_cleaned = []
        for item in key_elements_raw:
            if ':' in item:
                title, desc = item.split(':', 1)
                key_elements_cleaned.append({'title': title.strip(), 'description': desc.strip()})
            elif item.strip():
                key_elements_cleaned.append({'title': None, 'description': item.strip()})

        org.key_elements = key_elements_cleaned  # Assuming this is a JSONField

        if form.is_valid():
            form.save()
            return redirect('org_profile', slug=org.slug)
    else:
        form = OrganizationForm(instance=org)

    return render(request, 'studentorg/Main/OrgMain.html', {
        'org': org,
        'form': form,
        'is_edit': is_edit,
             'base_template': base_template, 
        'key_elements': org.key_elements or [],
    })

import json

def org_profile_view(request, org_id, mode='view'):
    org = get_object_or_404(Organization, id=org_id)
    
    if mode == 'edit':
        if request.method == 'POST':
            form = OrganizationForm(request.POST, request.FILES, instance=org)
            if form.is_valid():
                form.save()
                return redirect('org_profile', org_id=org.id)
        else:
            form = OrganizationForm(instance=org)
        return render(request, 'studentorg/org_profile.html', {
            'org': org,
            'form': form,
            'is_edit': True,
        })
    
    else:
        # View Mode
        key_elements = []
        if org.key_elements:
            try:
                key_elements = json.loads(org.key_elements)
            except:
                key_elements = org.key_elements.split(",")
        return render(request, 'studentorg/org_profile.html', {
            'org': org,
            'key_elements': key_elements,
            'is_edit': False,
        })

def Gen_Home(request):
    base_template = "adminmain.html" if request.user.is_staff or request.user.is_superuser else "main.html"
    orgs = Organization.objects.all()
    return render(request, "studentorg/VIEW/OrgMain.html", {"orgs": orgs,
        'base_template': base_template,  # pass base template to HTML
    })
# def home(request):
#     return render (request, "studentorg/VIEW/OrgMain.html")

#login
@login_required
@user_passes_test(is_superadmin)

@csrf_exempt
def add_organization(request):
    if request.method == "POST":
        name = request.POST.get("name")
        img_data = request.POST.get("imgData")

        if not name or not img_data:
            return JsonResponse({"success": False, "error": "Missing fields."})

        format, imgstr = img_data.split(";base64,")
        ext = format.split("/")[-1]
        file_name = f"{uuid.uuid4()}.{ext}"
        image_file = ContentFile(base64.b64decode(imgstr), name=file_name)

        org = Organization(name=name, logo=image_file)
        org.save()

        return JsonResponse({
            "success": True,
            "name": org.name,
            "slug": org.slug,
            "image_url": org.logo.url
        })

    return JsonResponse({"success": False, "error": "Invalid request."})

def admin_transactionreport(request):
    financial_statements = FinancialStatement.objects.all()
    projects = Project.objects.all()
    accreditations = Accreditation.objects.all()

   
    total_financial_transactions = financial_statements.count() + projects.count() + accreditations.count()
    total_projects = projects.count()
    total_accreditations = accreditations.count()
    total_budget = sum(project.p_budget for project in projects)
    total_amount_financial_statements = sum(statement.amount for statement in financial_statements)

  
    return render(request, 'studentorg/ADMIN/transaction_report.html', {
        'financial_statements': financial_statements,
        'projects': projects,
        'accreditations': accreditations,
        'total_financial_transactions': total_financial_transactions,
        'total_projects': total_projects,
        'total_accreditations': total_accreditations,
        'total_budget': total_budget,
        'total_amount_financial_statements': total_amount_financial_statements,
    })

# def register_officer(request):
#     if request.method == 'POST':
#         student_id = request.POST['student_id']
#         student_lname = request.POST['student_lname']
#         student_fname = request.POST['student_fname']
#         student_mname = request.POST['student_mname']
#         course = request.POST['course']
#         year_lvl = request.POST['year_lvl']
#         officer_position = request.POST['officer_position']
#         organization = request.POST['organization']
#         username = request.POST['username']
#         password = request.POST['password']

#         try:
#             officer = Officer.objects.get(surname=student_lname, firstname=student_fname)
#         except Officer.DoesNotExist:
#             messages.error(request, 'Officer with the provided last name and first name does not exist.')
#             return render(request, 'studentorg/ADMIN/registerofficer.html')

#         # ✅ Check if student_id matches the officer’s ID in the Officer table
#         if str(officer.student_id) != str(student_id):
#             messages.error(request, 'Student ID does not match the officer\'s record.')
#             return render(request, 'studentorg/ADMIN/registerofficer.html')

#         # Check if the officer's organization matches
#         if officer.organization != organization:
#             messages.error(request, 'The provided organization does not match the officer\'s organization.')
#             return render(request, 'studentorg/ADMIN/registerofficer.html')
        
#         if officer.status != 'approved':
#             messages.error(request, 'Officer status must be approved to create an account.')
#             return render(request, 'studentorg/ADMIN/registerofficer.html')

#         # Check if student_id already exists in OfficerLogin
#         if OfficerLogin.objects.filter(student_id=student_id).exists():
#             messages.error(request, 'An officer with this student ID already exists.')
#             return render(request, 'studentorg/ADMIN/registerofficer.html')

#         officer_login = OfficerLogin(
#             student_id=student_id,
#             student_lname=student_lname,
#             student_fname=student_fname,
#             student_mname=student_mname,
#             course=course,
#             officer_position=officer_position,
#             year_lvl=year_lvl,
#             organization=organization,
#             username=username,
#             password=password
#         )
#         officer_login.save()
#         messages.success(request, 'You have successfully created an officer account.')
#         return redirect('officer_login')
    
#     return render(request, 'studentorg/ADMIN/registerofficer.html')


# def officer_login(request):
#     if request.method == 'POST':
#         form = LoginForm(request.POST)
#         if form.is_valid():
#             username = form.cleaned_data['username']
#             password = form.cleaned_data['password']
           
#             try:
#                 officer = OfficerLogin.objects.get(username=username, password=password)
                
#                 # Store officer details in session
#                 request.session['officer_id'] = officer.student_id
#                 request.session['organization'] = officer.organization
                
#                 # Success message
#                 messages.success(request, 'You have successfully logged in.')
                
#                 # Redirect based on organization
#                 if officer.organization == 'FSTLP':
#                     return redirect('FSTLP_profile')
#                 elif officer.organization == 'SI++':
#                     return redirect('SI_profile')
#                 elif officer.organization == 'THE EQUATIONERS':
#                     return redirect('THEEQUATIONERS_profile')
#                 elif officer.organization == 'SSG':
#                     return redirect('SSG_profile')
#                 elif officer.organization == 'TECHNOCRATS':
#                     return redirect('TECHNOCRATS_profile')
#                 else:
#                     messages.error(request, 'Invalid organization.')
#                     return redirect('home')  # Fallback redirect to home if organization is invalid
#             except OfficerLogin.DoesNotExist:
#                 messages.error(request, 'Invalid username or password.')
#     else:
#         form = LoginForm()
#     return render(request, 'studentorg/ADMIN/officer_login.html', {'form': form})

def admin_manageofficer(request):

    if request.method == 'POST':
        officer_pk = request.POST.get('officer_id')
        action = request.POST.get('action')
        
        officer = get_object_or_404(Officer, officer_id=officer_pk)
        
        if action == 'approve':
            officer.status = 'approved'
        elif action == 'decline':
            officer.status = 'declined'
        officer.save()
        
        return redirect(request.get_full_path())

    
    search_query = request.GET.get('search', None)
    org_filter = request.GET.get('org', None)
    sort_by = request.GET.get('sort', 'officer_id')
    order = request.GET.get('order', 'asc')

    officer_list = Officer.objects.select_related('organization').all()

    if search_query:
        officer_list = officer_list.filter(
            Q(officer_id__icontains=search_query) |
            Q(surname__icontains=search_query) |
            Q(firstname__icontains=search_query) |
            Q(course__icontains=search_query) |
            Q(position__icontains=search_query) |
            Q(organization__name__icontains=search_query)
        )
    
    if org_filter:
        officer_list = officer_list.filter(organization__slug=org_filter)

    valid_sort_map = {
        'officer_id': 'officer_id',
        'surname': 'surname',
        'firstname': 'firstname',
        'course': 'course',
        'position': 'position',
        'organization': 'organization__name', 
        'status': 'status',
    }
    
    sort_field = valid_sort_map.get(sort_by, 'officer_id')
    
    if order == 'desc':
        sort_field = f"-{sort_field}"
        
    officer_list = officer_list.order_by(sort_field)
        
    paginator = Paginator(officer_list, 10)
    page_number = request.GET.get('page')
    
    try:
        page_obj = paginator.page(page_number)
    except PageNotAnInteger:
        page_obj = paginator.page(1)
    except EmptyPage:
        page_obj = paginator.page(paginator.num_pages)

    search_params = ""
    if search_query:
        search_params += f"&search={search_query}"
        
    if org_filter:
        search_params += f"&org={org_filter}"

    all_orgs = Organization.objects.all()

    context = {
        'page_obj': page_obj, 
        'user': request.user,
        'current_sort': sort_by,
        'current_order': order,
        'search_params': search_params,
        'all_organizations': all_orgs, 
    }
    
    return render(request, 'studentorg/ADMIN/admin_manageofficer.html', context)
from django.shortcuts import render, redirect, get_object_or_404
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import Q
from ..models import Adviser # Assumes your model is named Adviser
def admin_manageadviser(request):

    # --- POST Logic (for Approve/Decline) ---
    if request.method == 'POST':
        # [FIX] Use adviser_id here, which your template sends
        adviser_pk = request.POST.get('adviser_id') 
        action = request.POST.get('action')
        
        # [FIX] Filter by the primary key 'adviser_id'
        adviser = get_object_or_404(Adviser, adviser_id=adviser_pk)
        
        if action == 'approve':
            adviser.status = 'approved'
            # TODO: Add logic here to create a user account for the adviser
            # user = User.objects.create_user(...)
        elif action == 'decline':
            adviser.status = 'declined'
        adviser.save()
        
        return redirect(request.get_full_path())

    # --- GET Logic (for Display, Sort, Filter, Paginate) ---
    
    # 1. Get parameters from URL
    search_query = request.GET.get('search', None)
    status_filter = request.GET.get('status', None)
    
    # [FIX] Default sort field is now 'adviser_id'
    sort_by = request.GET.get('sort', 'adviser_id') 
    order = request.GET.get('order', 'asc')

    # 2. Start with base query
    adviser_list = Adviser.objects.all()

    # 3. Apply Filters
    if search_query:
        # [FIX] Search by 'adviser_id' instead of 'id'
        adviser_list = adviser_list.filter(
            Q(adviser_id__icontains=search_query) | 
            Q(surname__icontains=search_query) |
            Q(firstname__icontains=search_query) |
            Q(department__icontains=search_query)
        )
    
    if status_filter:
        adviser_list = adviser_list.filter(status=status_filter)

    # 4. Apply Sorting
    # [FIX] Use 'adviser_id' in the map
    valid_sort_map = {
        'adviser_id': 'adviser_id',
        'surname': 'surname',
        'firstname': 'firstname',
        'department': 'department',
        'position': 'position',
        'status': 'status',
    }
    
    # [FIX] Default sort field is 'adviser_id'
    sort_field = valid_sort_map.get(sort_by, 'adviser_id')
    
    if order == 'desc':
        sort_field = f"-{sort_field}"
        
    adviser_list = adviser_list.order_by(sort_field)
        
    # 5. Apply Pagination
    paginator = Paginator(adviser_list, 10) # 10 items per page
    page_number = request.GET.get('page')
    
    try:
        page_obj = paginator.page(page_number)
    except PageNotAnInteger:
        page_obj = paginator.page(1)
    except EmptyPage:
        page_obj = paginator.page(paginator.num_pages)

    # 6. Build Search/Sort parameters string for template links
    search_params = ""
    if search_query:
        search_params += f"&search={search_query}"
    if status_filter:
        search_params += f"&status={status_filter}"

    # 7. Build Context
    context = {
        'page_obj': page_obj, 
        'user': request.user,
        'current_sort': sort_by,
        'current_order': order,
        'search_params': search_params
    }
    
    return render(request, 'studentorg/ADMIN/admin_manageadviser.html', context)

def admin_manageproject(request):

    # --- POST Logic (for Approve/Decline) ---
    if request.method == 'POST':
        project_id = request.POST.get('project_id')
        action = request.POST.get('action')
        
        project = get_object_or_404(Project, project_id=project_id)
        
        if action == 'approve':
            project.status = 'approved'
        elif action == 'decline':
            project.status = 'declined'
        project.save()
        
        # [FIX] Redirect back to the same page, preserving any filters/sort
        return redirect(request.get_full_path())

    # --- GET Logic (for Display, Sort, Filter, Paginate) ---
    
    # 1. Get parameters from URL
    search_query = request.GET.get('search', None)
    status_filter = request.GET.get('status', None)
    sort_by = request.GET.get('sort', 'project_id') 
    order = request.GET.get('order', 'asc')

    # 2. Start with base query (use select_related for foreign keys)
    project_list = Project.objects.select_related('org').all()

    # 3. Apply Filters
    if search_query:
        project_list = project_list.filter(
            Q(project_id__icontains=search_query) |
            Q(objective__icontains=search_query) |
            Q(org__name__icontains=search_query) |
            Q(involved_officer__icontains=search_query)
        )
    
    if status_filter:
        project_list = project_list.filter(status=status_filter)

    # 4. Apply Sorting
    valid_sort_map = {
        'project_id': 'project_id',
        'objective': 'objective',
        'org': 'org__name', # Sort by the organization's name
        'target': 'target',
        'p_budget': 'p_budget',
        'status': 'status',
    }
    
    sort_field = valid_sort_map.get(sort_by, 'project_id')
    
    if order == 'desc':
        sort_field = f"-{sort_field}"
        
    project_list = project_list.order_by(sort_field)
        
    # 5. Apply Pagination
    paginator = Paginator(project_list, 10) # 10 items per page
    page_number = request.GET.get('page')
    
    try:
        page_obj = paginator.page(page_number)
    except PageNotAnInteger:
        page_obj = paginator.page(1)
    except EmptyPage:
        page_obj = paginator.page(paginator.num_pages)

    # 6. Build Search/Sort parameters string for template links
    search_params = ""
    if search_query:
        search_params += f"&search={search_query}"
    if status_filter:
        search_params += f"&status={status_filter}"

    # 7. Build Context
    context = {
        'page_obj': page_obj, # This replaces 'projects'
        'user': request.user,
        'current_sort': sort_by,
        'current_order': order,
        'search_params': search_params
    }
    
    return render(request, 'studentorg/ADMIN/admin_manageproject.html', context)


def admin_managefinancial(request):

    # --- POST Logic (for Approve/Decline) ---
    if request.method == 'POST':
        financial_id = request.POST.get('financial_id')  
        action = request.POST.get('action')
        statement = get_object_or_404(FinancialStatement, financial_id=financial_id)
        
        if action == 'approve':
            statement.status = 'approved'
        elif action == 'decline':
            statement.status = 'declined'
        statement.save()
        
        # [FIX] Redirect back to the same page, preserving filters/sort
        return redirect(request.get_full_path())

    # --- GET Logic (for Display, Sort, Filter, Paginate) ---
    
    # 1. Get parameters from URL
    search_query = request.GET.get('search', None)
    status_filter = request.GET.get('status', None)
    sort_by = request.GET.get('sort', 'financial_id') 
    order = request.GET.get('order', 'asc')

    # 2. Start with base query (use select_related for foreign keys)
    statement_list = FinancialStatement.objects.select_related('org').all()

    # 3. Apply Filters
    if search_query:
        statement_list = statement_list.filter(
            Q(financial_id__icontains=search_query) |
            Q(purpose__icontains=search_query) |
            Q(org__name__icontains=search_query)
        )
    
    if status_filter:
        statement_list = statement_list.filter(status=status_filter)

    # 4. Apply Sorting
    valid_sort_map = {
        'financial_id': 'financial_id',
        'date': 'date',
        'purpose': 'purpose',
        'org': 'org__name', # Sort by the organization's name
        'amount': 'amount',
        'status': 'status',
    }
    
    sort_field = valid_sort_map.get(sort_by, 'financial_id')
    
    if order == 'desc':
        sort_field = f"-{sort_field}"
        
    statement_list = statement_list.order_by(sort_field)
        
    # 5. Apply Pagination
    paginator = Paginator(statement_list, 10) # 10 items per page
    page_number = request.GET.get('page')
    
    try:
        page_obj = paginator.page(page_number)
    except PageNotAnInteger:
        page_obj = paginator.page(1)
    except EmptyPage:
        page_obj = paginator.page(paginator.num_pages)

    # 6. Build Search/Sort parameters string for template links
    search_params = ""
    if search_query:
        search_params += f"&search={search_query}"
    if status_filter:
        search_params += f"&status={status_filter}"

    # 7. Build Context
    context = {
        'page_obj': page_obj, # This replaces 'statements'
        'user': request.user,
        'current_sort': sort_by,
        'current_order': order,
        'search_params': search_params
    }
    
    return render(request, 'studentorg/ADMIN/admin_managefinancial.html', context)

def admin_manage_accreditations(request):
    accreditations = Accreditation.objects.all() 
    if request.method == 'POST':
        accreditation_id = request.POST.get('accreditation_id')
        action = request.POST.get('action')
        accreditation = get_object_or_404(Accreditation, accreditation_id=accreditation_id)
        
        if action == 'approve':
            accreditation.status = 'approved'
            accreditation.save()
            
         
            organization = accreditation.organization
            if organization == 'FSTLP':
                return redirect('FSTLP_certification')
            elif organization == 'SI':
                return redirect('SI_certification')
            elif organization == 'THEEQUATIONERS':
                return redirect('THEEQUATIONERS_certification')
            elif organization == 'SSG':
                return redirect('SSG_certification')
            elif organization == 'TECHNOCRATS':
                return redirect('TECHNOCRATS_certification')
            else:
             
                return redirect('admin_manage_accreditations')  # Default redirect if no match
        elif action == 'decline':
            accreditation.status = 'declined'
            accreditation.save()
            return redirect('admin_manage_accreditations')
    
    return render(request, 'studentorg/ADMIN/manage_accreditation.html', {'accreditations': accreditations})

def FSTLP_certification(request):
    return render(request, 'studentorg/FSTLP/FSTLP_certification.html')

def SI_certification(request):
    return render(request, 'studentorg/SI++/SI++_certification.html')

def SSG_certification(request):
    return render(request, 'studentorg/SSG/SSG_certification.html')

def THEEQUATIONERS_certification(request):
    return render(request, 'studentorg/THEEQUATIONER/THEEQUATIONER_certification.html')

def TECHNOCRATS_certification(request):
    return render(request, 'studentorg/studentorg/TECHNOCRATS/TECHNOCRATS_certification.html')




def admin_view_accreditations(request):
    approved_accreditations= Accreditation.objects.all()
    return render(request, 'studentorg/ADMIN/view_accreditation.html', {'accreditations': approved_accreditations})

#FSLTP
def FSTLP_profile(request):
    return render (request, "studentorg/FSTLP/FSTLP_profile.html")

def FSTLP_accreditation(request):
    if request.method == 'POST':
        form = AccreditationForm(request.POST, request.FILES)
        if form.is_valid():
            accreditation = form.save()
            return redirect('FSTLP_accreditation')
        else:
            print(form.errors)
    else:
        form = AccreditationForm()

    context = {'form': form}

    if request.method == 'POST':
        context['uploaded_files'] = {
            'letter_of_intent': request.FILES.get('letter_of_intent'),
            'list_of_officers': request.FILES.get('list_of_officers'),
            'certificate_of_registration': request.FILES.get('certificate_of_registration'),
            'list_of_members': request.FILES.get('list_of_members'),
            'accomplishment_report': request.FILES.get('accomplishment_report'),
            'calendar_of_activities': request.FILES.get('calendar_of_activities'),
            'financial_statement': request.FILES.get('financial_statement'),
            'bank_passbook': request.FILES.get('bank_passbook'),
            'inventory_of_properties': request.FILES.get('inventory_of_properties'),
            'organization_bylaws': request.FILES.get('organization_bylaws'),
            'faculty_adviser_appointment': request.FILES.get('faculty_adviser_appointment'),
            'other_documents': request.FILES.get('other_documents'),
        }

    return render (request, "studentorg/FSTLP/FSTLP_accreditation.html", context)

def FSTLP_CBL(request):
    return render (request, "studentorg/FSTLP/FSTLP_CBL.html")

#FSLTP ADD
def FSTLP_projects(request):
    if request.method == 'POST':
        form = ProjectForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('FSTLP_projects') 
    else:
        form = ProjectForm()
    return render(request, "studentorg/FSTLP/FSTLP_projects.html", {'form': form})
def FSTLP_financial(request):
    if request.method == 'POST':
        form = FinancialStatementForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('FSTLP_financial')
    else:
        form = FinancialStatementForm()
    return render (request, "studentorg/FSTLP/FSTLP_financial_statement.html", {'form': form})

def FSTLP_officerdata(request):
    if request.method == 'POST':
        form = OfficerForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('FSTLP_officerdata') 
    else:
        form = OfficerForm()
    return render(request, 'studentorg/FSTLP/FSTLP_officerdata.html', {'form': form})

def FSTLP_adviserdata(request):
    if request.method == 'POST':
        form = AdviserForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('FSTLP_adviserdata')
    else:
        form = AdviserForm()
    return render(request,'studentorg/FSTLP/FSTLP_adviserdata.html',{'form': form})

#FSLTP VIEW
def FSTLP_viewproject(request):
    approved_projects = Project.objects.filter(status='approved', org='FSTLP')
    return render(request, 'studentorg/FSTLP/FSTLP_viewproject.html', {'projects': approved_projects})
def FSTLP_viewfinancial(request):
    approved_projects = FinancialStatement.objects.filter(status='approved', org='FSTLP')
    return render(request, 'studentorg/FSTLP/FSTLP_viewfinancial.html', {'statements': approved_projects})
def FSTLP_viewofficer(request):
    approved_projects = Officer.objects.filter(status='approved', organization='FSTLP')
    return render(request, 'studentorg/FSTLP/FSTLP_viewofficer.html', {'statements': approved_projects})
def FSTLP_viewadviser(request):
    approved_projects = Adviser.objects.filter(status='approved', organization='FSTLP')
    return render(request, 'studentorg/FSTLP/FSTLP_viewadviser.html', {'advisers': approved_projects})



#SI++
def SI_profile(request):
    return render (request, "SI++/SI++_profile.html")

def SI_accreditation(request):
    if request.method == 'POST':
        form = AccreditationForm(request.POST, request.FILES)
        if form.is_valid():
            accreditation = form.save()
            return redirect('SI_accreditation')
        else:
            print(form.errors)
    else:
        form = AccreditationForm()

    context = {'form': form}

    if request.method == 'POST':
        context['uploaded_files'] = {
            'letter_of_intent': request.FILES.get('letter_of_intent'),
            'list_of_officers': request.FILES.get('list_of_officers'),
            'certificate_of_registration': request.FILES.get('certificate_of_registration'),
            'list_of_members': request.FILES.get('list_of_members'),
            'accomplishment_report': request.FILES.get('accomplishment_report'),
            'calendar_of_activities': request.FILES.get('calendar_of_activities'),
            'financial_statement': request.FILES.get('financial_statement'),
            'bank_passbook': request.FILES.get('bank_passbook'),
            'inventory_of_properties': request.FILES.get('inventory_of_properties'),
            'organization_bylaws': request.FILES.get('organization_bylaws'),
            'faculty_adviser_appointment': request.FILES.get('faculty_adviser_appointment'),
            'other_documents': request.FILES.get('other_documents'),
        }
    return render (request, "studentorg/SI++/SI++_accreditation.html", context)

def SI_CBL(request):
    return render (request, "studentorg/SI++/SI++_CBL.html")

#SI++ ADD

def SI_projects(request):
    if request.method == 'POST':
        form = ProjectForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('SI_projects') 
    else:
        form = ProjectForm()
    return render(request, "studentorg/SI++/SI++_projects.html", {'form': form})
    
     
def SI_financial(request):
    if request.method == 'POST':
        form = FinancialStatementForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('SI_financial')
    else:
        form = FinancialStatementForm()
    return render (request, "studentorg/SI++/SI++_financial_statement.html", {'form': form})
def SI_officerdata(request):
    if request.method == 'POST':
        form = OfficerForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('SI_officerdata')
    else:
        form = OfficerForm()
    return render(request, 'studentorg/SI++/SI++_officerdata.html', {'form': form})

def SI_adviserdata(request):
    if request.method == 'POST':
        form = AdviserForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('SI_adviserdata')
    else:
        form = AdviserForm()
    return render(request,'studentorg/SI++/SI++_adviserdata.html',{'form': form})

#SI++ VIEW
def SI_viewproject(request):
    approved_projects = Project.objects.filter(status='approved', org='SI++')
    return render(request, 'studentorg/SI++/SI++_viewproject.html', {'projects': approved_projects})
def SI_viewfinancial(request):
    approved_projects = FinancialStatement.objects.filter(status='approved', org='SI++')
    return render(request, 'studentorg/SI++/SI++_viewfinancial.html', {'statements': approved_projects})
def SI_viewofficer(request):
    approved_projects = Officer.objects.filter(status='approved', organization='SI++')
    return render(request, 'studentorg/SI++/SI++_viewofficer.html', {'statements': approved_projects})
def SI_viewadviser(request):
    approved_projects = Adviser.objects.filter(status='approved', organization='SI++')
    return render(request, 'studentorg/SI++/SI++_viewadviser.html', {'advisers': approved_projects})




#THE EQUATIONERS
def THEEQUATIONERS_profile(request):
    return render (request, "THEEQUATIONER/THEEQUATIONER_profile.html")

def THEEQUATIONERS_accreditation(request):
    if request.method == 'POST':
        form = AccreditationForm(request.POST, request.FILES)
        if form.is_valid():
            accreditation = form.save()
            return redirect('THEEQUATIONERS_accreditation')
        else:
            print(form.errors)
    else:
        form = AccreditationForm()

    context = {'form': form}

    if request.method == 'POST':
        context['uploaded_files'] = {
            'letter_of_intent': request.FILES.get('letter_of_intent'),
            'list_of_officers': request.FILES.get('list_of_officers'),
            'certificate_of_registration': request.FILES.get('certificate_of_registration'),
            'list_of_members': request.FILES.get('list_of_members'),
            'accomplishment_report': request.FILES.get('accomplishment_report'),
            'calendar_of_activities': request.FILES.get('calendar_of_activities'),
            'financial_statement': request.FILES.get('financial_statement'),
            'bank_passbook': request.FILES.get('bank_passbook'),
            'inventory_of_properties': request.FILES.get('inventory_of_properties'),
            'organization_bylaws': request.FILES.get('organization_bylaws'),
            'faculty_adviser_appointment': request.FILES.get('faculty_adviser_appointment'),
            'other_documents': request.FILES.get('other_documents'),
        }
    return render (request, "studentorg/THEEQUATIONER/THEEQUATIONER_accreditation.html", context)

def THEEQUATIONERS_CBL(request):
    return render (request, "studentorg/THEEQUATIONER/CBLTheEquationers.html")

#THE EQUATIONERS ADD
def THEEQUATIONERS_projects(request):
    if request.method == 'POST':
        form = ProjectForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('THEEQUATIONERS_projects') 
    else:
        form = ProjectForm()
    return render(request, "studentorg/THEEQUATIONER/THEEQUATIONER_projects.html", {'form': form})

def THEEQUATIONERS_financial(request):
    if request.method == 'POST':
        form = FinancialStatementForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('THEEQUATIONERS_financial')
    else:
        form = FinancialStatementForm()
    return render (request, "studentorg/THEEQUATIONER/THEEQUATIONER_financial_statement.html", {'form': form})
def THEEQUATIONERS_officerdata(request):
    if request.method == 'POST':
        form = OfficerForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('THEEQUATIONERS_officerdata')
    else:
        form = OfficerForm()
    return render(request, 'studentorg/THEEQUATIONER/THEEQUATIONER_officerdata.html', {'form': form})

def THEEQUATIONERS_adviserdata(request):
    if request.method == 'POST':
        form = AdviserForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('THEEQUATIONERS_adviserdata')
    else:
        form = AdviserForm()
    return render(request,'studentorg/THEEQUATIONER/THEEQUATIONER_adviserdata.html',{'form': form})


#THE EQUATIONERS VIEW
def THEEQUATIONERS_viewproject(request):
    approved_projects = Project.objects.filter(status='approved', org='THE EQUATIONERS')
    return render(request, 'studentorg/THEEQUATIONER/THEEQUATIONER_viewproject.html', {'projects': approved_projects})
def THEEQUATIONERS_viewfinancial(request):
    approved_projects = FinancialStatement.objects.filter(status='approved', org='THE EQUATIONERS')
    return render(request, 'studentorg/THEEQUATIONER/THEEQUATIONER_viewfinancial.html', {'statements': approved_projects})
def THEEQUATIONERS_viewofficer(request):
    approved_projects = Officer.objects.filter(status='approved', organization='THE EQUATIONERS')
    return render(request, 'studentorg/THEEQUATIONER/THEEQUATIONER_viewofficer.html', {'statements': approved_projects})
def THEEQUATIONERS_viewadviser(request):
    approved_projects = Adviser.objects.filter(status='approved', organization='THE EQUATIONERS')
    return render(request, 'studentorg/THEEQUATIONER/THEEQUATIONER_viewadviser.html', {'advisers': approved_projects})



#SUPREME STUDENT GOV (SSG)
def SSG_profile(request):
    return render (request, "studentorg/SSG/SSG_profile.html")

def SSG_accreditation(request):
    if request.method == 'POST':
        form = AccreditationForm(request.POST, request.FILES)
        if form.is_valid():
            accreditation = form.save()
            return redirect('SSG_accreditation')
        else:
            print(form.errors)
    else:
        form = AccreditationForm()

    context = {'form': form}

    if request.method == 'POST':
        context['uploaded_files'] = {
            'letter_of_intent': request.FILES.get('letter_of_intent'),
            'list_of_officers': request.FILES.get('list_of_officers'),
            'certificate_of_registration': request.FILES.get('certificate_of_registration'),
            'list_of_members': request.FILES.get('list_of_members'),
            'accomplishment_report': request.FILES.get('accomplishment_report'),
            'calendar_of_activities': request.FILES.get('calendar_of_activities'),
            'financial_statement': request.FILES.get('financial_statement'),
            'bank_passbook': request.FILES.get('bank_passbook'),
            'inventory_of_properties': request.FILES.get('inventory_of_properties'),
            'organization_bylaws': request.FILES.get('organization_bylaws'),
            'faculty_adviser_appointment': request.FILES.get('faculty_adviser_appointment'),
            'other_documents': request.FILES.get('other_documents'),
        }
    return render (request, "studentorg/SSG/SSG_accreditation.html", context)

def SSG_CBL(request):
    return render (request, "studentorg/SSG/SSG_CBL.html")

#SSG ADD
def SSG_projects(request):
    if request.method == 'POST':
        form = ProjectForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('SSG_projects') 
    else:
        form = ProjectForm()
    return render(request, "studentorg/SSG/SSG_projects.html", {'form': form})
def SSG_financial(request):
    if request.method == 'POST':
        form = FinancialStatementForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('SSG_financial')
    else:
        form = FinancialStatementForm()
    return render (request, "studentorg/SSG/SSG_financial_statement.html", {'form': form})
def SSG_officerdata(request):
    if request.method == 'POST':
        form = OfficerForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('SSG_officerdata')
    else:
        form = OfficerForm()
    return render(request, 'studentorg/SSG/SSG_officerdata.html', {'form': form})
def SSG_adviserdata(request):
    if request.method == 'POST':
        form = AdviserForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('SSG_adviserdata')
    else:
        form = AdviserForm()
    return render(request,'studentorg/SSG/SSG_adviserdata.html',{'form': form})



#SSG VIEW
def SSG_viewproject(request):
    approved_projects = Project.objects.filter(status='approved', org='SSG')
    return render(request, 'studentorg/SSG/SSG_viewproject.html', {'projects': approved_projects})
def SSG_viewfinancial(request):
    approved_projects = FinancialStatement.objects.filter(status='approved', org='SSG')
    return render(request, 'studentorg/SSG/SSG_viewfinancial.html', {'statements': approved_projects})
def SSG_viewofficer(request):
    approved_projects = Officer.objects.filter(status='approved', organization='SSG')
    return render(request, 'studentorg/SSG/SSG_viewofficer.html', {'statements': approved_projects})
def SSG_viewadviser(request):
    approved_projects = Adviser.objects.filter(status='approved', organization='SSG')
    return render(request, 'studentorg/SSG/SSG_viewadviser.html', {'advisers': approved_projects})



#TECHNOCRATS
def TECHNOCRATS_profile(request):
    return render (request, "studentorg/TECHNOCRATS/TECHNOCRATS_profile.html")

def TECHNOCRATS_accreditation(request):
    if request.method == 'POST':
        form = AccreditationForm(request.POST, request.FILES)
        if form.is_valid():
            accreditation = form.save()
            return redirect('TECHNOCRATS_accreditation')
        else:
            print(form.errors)
    else:
        form = AccreditationForm()

    context = {'form': form}

    if request.method == 'POST':
        context['uploaded_files'] = {
            'letter_of_intent': request.FILES.get('letter_of_intent'),
            'list_of_officers': request.FILES.get('list_of_officers'),
            'certificate_of_registration': request.FILES.get('certificate_of_registration'),
            'list_of_members': request.FILES.get('list_of_members'),
            'accomplishment_report': request.FILES.get('accomplishment_report'),
            'calendar_of_activities': request.FILES.get('calendar_of_activities'),
            'financial_statement': request.FILES.get('financial_statement'),
            'bank_passbook': request.FILES.get('bank_passbook'),
            'inventory_of_properties': request.FILES.get('inventory_of_properties'),
            'organization_bylaws': request.FILES.get('organization_bylaws'),
            'faculty_adviser_appointment': request.FILES.get('faculty_adviser_appointment'),
            'other_documents': request.FILES.get('other_documents'),
        }
    return render (request, "studentorg/TECHNOCRATS/TECHNOCRATS_accreditation.html", context)

def TECHNOCRATS_CBL(request):
    return render (request, "studentorg/TECHNOCRATS/TECHNOCRATS_CBL.html")

#TECNOCRATS ADD
def TECHNOCRATS_projects(request):
    if request.method == 'POST':
        form = ProjectForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('TECHNOCRATS_projects') 
    else:
        form = ProjectForm()
    return render(request, "studentorg/TECHNOCRATS/TECHNOCRATS_projects.html", {'form': form})
def TECHNOCRATS_financial(request):
    if request.method == 'POST':
        form = FinancialStatementForm(request.POST)
        if form.is_valid():
            form.save()
    else:
        form = FinancialStatementForm()
    return render (request, "studentorg/TECHNOCRATS/TECHNOCRATS_financial_statement.html", {'form': form})
def TECHNOCRATS_officerdata(request):
    if request.method == 'POST':
        form = OfficerForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('TECHNOCRATS_officerdata')
    else:
        form = OfficerForm()
    return render(request, 'studentorg/TECHNOCRATS/TECHNOCRATS_officerdata.html', {'form': form})

def TECHNOCRATS_adviserdata(request):
    if request.method == 'POST':
        form = AdviserForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('TECHNOCRATS_adviserdata')
    else:
        form = AdviserForm()
    return render(request,'studentorg/TECHNOCRATS/TECHNOCRATS_adviserdata.html',{'form': form})

#TECNOCRATS VIEW
def TECHNOCRATS_viewproject(request):
    approved_projects = Project.objects.filter(status='approved', org='TECHNOCRATS')
    return render(request, 'studentorg/TECHNOCRATS/TECHNOCRATS_viewproject.html', {'projects': approved_projects})
def TECHNOCRATS_viewfinancial(request):
    approved_projects = FinancialStatement.objects.filter(status='approved', org='TECHNOCRATS')
    return render(request, 'studentorg/TECHNOCRATS/TECHNOCRATS_viewfinancial.html', {'statements': approved_projects})
def TECHNOCRATS_viewofficer(request):
    approved_projects = Officer.objects.filter(status='approved', organization='TECHNOCRATS')
    return render(request, 'studentorg/TECHNOCRATS/TECHNOCRATS_viewofficer.html', {'statements': approved_projects})
def TECHNOCRATS_viewadviser(request):
    approved_projects = Adviser.objects.filter(status='approved', organization='TECHNOCRATS')
    return render(request, 'studentorg/TECHNOCRATS/TECHNOCRATS_viewadviser.html', {'advisers': approved_projects})

#General View



def Gen_FSTLP_profile(request):
    return render (request, "studentorg/VIEW/FSTLP_profile.html")
def Gen_SI_profile(request):
    return render (request, "studentorg/VIEW/SI++_profile.html")
def Gen_SSG_profile(request):
    return render (request, "studentorg/VIEW/SSG_profile.html")
def Gen_TECHNOCRATS_profile(request):
    return render (request, "studentorg/VIEW/TECHNOCRATS_profile.html")
def Gen_THEEQUATIONERS_profile(request):
    return render (request, "studentorg/VIEW/THEEQUATIONER_profile.html")


def Gen_FSTLP_viewproject(request):
    approved_projects = Project.objects.filter(status='approved', org='FSTLP')
    return render(request, 'studentorg/VIEW/FSTLP_viewproject.html', {'projects': approved_projects})
def Gen_FSTLP_viewfinancial(request):
    approved_projects = FinancialStatement.objects.filter(status='approved', org='FSTLP')
    return render(request, 'studentorg/VIEW/FSTLP_viewfinancial.html', {'statements': approved_projects})
def Gen_FSTLP_viewofficer(request):
    approved_projects = Officer.objects.filter(status='approved', organization='FSTLP')
    return render(request, 'studentorg/VIEW/FSTLP_viewofficer.html', {'statements': approved_projects})
def Gen_FSTLP_viewadviser(request):
    approved_projects = Adviser.objects.filter(status='approved', organization='FSTLP')
    return render(request, 'studentorg/VIEW/FSTLP_viewadviser.html', {'advisers': approved_projects})

def Gen_SI_viewproject(request):
    approved_projects = Project.objects.filter(status='approved', org='SI++')
    return render(request, 'studentorg/VIEW/SI++_viewproject.html', {'projects': approved_projects})
def Gen_SI_viewfinancial(request):
    approved_projects = FinancialStatement.objects.filter(status='approved', org='SI++')
    return render(request, 'studentorg/VIEW/SI++_viewfinancial.html', {'statements': approved_projects})
def Gen_SI_viewofficer(request):
    approved_projects = Officer.objects.filter(status='approved', organization='SI++')
    return render(request, 'studentorg/VIEW/SI++_viewofficer.html', {'statements': approved_projects})
def Gen_SI_viewadviser(request):
    approved_projects = Adviser.objects.filter(status='approved', organization='BSIT')
    return render(request, 'studentorg/VIEW/SI++_viewadviser.html', {'advisers': approved_projects})

def Gen_THEEQUATIONERS_viewproject(request):
    try:
        org = Organization.objects.get(name='THE EQUATIONERS')
        approved_projects = Project.objects.filter(status='approved', org=org)
    except Organization.DoesNotExist:
        approved_projects = []

    return render(request, 'studentorg/VIEW/THEEQUATIONER_viewproject.html', {
        'projects': approved_projects
    })
def Gen_THEEQUATIONERS_viewfinancial(request):
    approved_projects = FinancialStatement.objects.filter(status='approved', org='THE EQUATIONERS')
    return render(request, 'studentorg/VIEW/THEEQUATIONER_viewfinancial.html', {'statements': approved_projects})
def Gen_THEEQUATIONERS_viewofficer(request):
    approved_projects = Officer.objects.filter(status='approved', organization='THE EQUATIONERS')
    return render(request, 'studentorg/VIEW/THEEQUATIONER_viewofficer.html', {'statements': approved_projects})
def Gen_THEEQUATIONERS_viewadviser(request):
    approved_projects = Adviser.objects.filter(status='approved', organization='THE EQUATIONERS')
    return render(request, 'studentorg/VIEW/THEEQUATIONER_viewadviser.html', {'advisers': approved_projects})

def Gen_SSG_viewproject(request):
    approved_projects = Project.objects.filter(status='approved', org='SSG')
    return render(request, 'studentorg/VIEW/SSG_viewproject.html', {'projects': approved_projects})
def Gen_SSG_viewfinancial(request):
    approved_projects = FinancialStatement.objects.filter(status='approved', org='SSG')
    return render(request, 'studentorg/VIEW/SSG_viewfinancial.html', {'statements': approved_projects})
def Gen_SSG_viewofficer(request):
    approved_projects = Officer.objects.filter(status='approved', organization='SSG')
    return render(request, 'studentorg/VIEW/SSG_viewofficer.html', {'statements': approved_projects})
def Gen_SSG_viewadviser(request):
    approved_projects = Adviser.objects.filter(status='approved', organization='SSG')
    return render(request, 'studentorg/VIEW/SSG_viewadviser.html', {'advisers': approved_projects})

def Gen_TECHNOCRATS_viewproject(request):
    approved_projects = Project.objects.filter(status='approved', org='TECHNOCRATS')
    return render(request, 'studentorg/VIEW/TECHNOCRATS_viewproject.html', {'projects': approved_projects})
def Gen_TECHNOCRATS_viewfinancial(request):
    approved_projects = FinancialStatement.objects.filter(status='approved', org='TECHNOCRATS')
    return render(request, 'studentorg/VIEW/TECHNOCRATS_viewfinancial.html', {'statements': approved_projects})
def Gen_TECHNOCRATS_viewofficer(request):
    approved_projects = Officer.objects.filter(status='approved', organization='TECHNOCRATS')
    return render(request, 'studentorg/VIEW/TECHNOCRATS_viewofficer.html', {'statements': approved_projects})
def Gen_TECHNOCRATS_viewadviser(request):
    approved_projects = Adviser.objects.filter(status='approved', organization='TECHNOCRATS')
    return render(request, 'studentorg/VIEW/TECHNOCRATS_viewadviser.html', {'advisers': approved_projects})

