from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from django.contrib import messages
from ..forms import OfficerForm
from ..forms import ProjectForm
from ..forms import FinancialStatementForm, AdminLoginForm, LoginForm
from ..forms import AccreditationForm, AdviserForm
from ..models import Project, Accreditation, Adviser, OfficerLogin
from ..models import FinancialStatement, Officer, AdminLogin

# Create your views here.
def home(request):
    return render (request, "studentorg/VIEW/OrgMain.html")

#login

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

def admin_login(request):
    if request.method == 'POST':
        form = AdminLoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['admin_username']
            password = form.cleaned_data['admin_password']
            try:
                admin = AdminLogin.objects.get(admin_username=username, admin_password=password)
                return redirect('admin_manageofficer')
            except AdminLogin.DoesNotExist:
                messages.error(request, "Invalid username or password")
    else:
        form = AdminLoginForm()
    return render(request, 'studentorg/ADMIN/admin_login.html', {'form': form})

def register_officer(request):
    if request.method == 'POST':
        student_id = request.POST['student_id']
        student_lname = request.POST['student_lname']
        student_fname = request.POST['student_fname']
        student_mname = request.POST['student_mname']
        course = request.POST['course']
        year_lvl = request.POST['year_lvl']
        officer_position = request.POST['officer_position']
        organization = request.POST['organization']
        username = request.POST['username']
        password = request.POST['password']

        # Check if the officer's last name and first name exist in the Officer table
        try:
            officer = Officer.objects.get(surname=student_lname, firstname=student_fname)
        except Officer.DoesNotExist:
            messages.error(request, 'Officer with the provided last name and first name does not exist.')
            return render(request, 'studentorg/ADMIN/registerofficer.html')

        # Check if the officer's organization matches
        if officer.organization != organization:
            messages.error(request, 'The provided organization does not match the officer\'s organization.')
            return render(request, 'studentorg/ADMIN/registerofficer.html')
        
        if officer.status != 'approved':
            messages.error(request, 'Officer status must be approved to create an account.')
            return render(request, 'studentorg/ADMIN/registerofficer.html')

        # Check if student_id already exists in OfficerLogin
        if OfficerLogin.objects.filter(student_id=student_id).exists():
            messages.error(request, 'An officer with this student ID already exists.')
            return render(request, 'studentorg/ADMIN/registerofficer.html')

        officer_login = OfficerLogin(
            student_id=student_id,
            student_lname=student_lname,
            student_fname=student_fname,
            student_mname=student_mname,
            course=course,
            officer_position=officer_position,
            year_lvl=year_lvl,
            organization=organization,
            username=username,
            password=password
        )
        officer_login.save()
        messages.success(request, 'You have successfully created an officer account.')
        return redirect('officer_login')  # Use the name of the URL pattern for the officer login page
    
    return render(request, 'studentorg/ADMIN/registerofficer.html')    

def officer_login(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
           
            try:
                officer = OfficerLogin.objects.get(username=username, password=password)
                
                # Store officer details in session
                request.session['officer_id'] = officer.student_id
                request.session['organization'] = officer.organization
                
                # Success message
                messages.success(request, 'You have successfully logged in.')
                
                # Redirect based on organization
                if officer.organization == 'FSTLP':
                    return redirect('FSTLP_profile')
                elif officer.organization == 'SI++':
                    return redirect('SI_profile')
                elif officer.organization == 'THE EQUATIONERS':
                    return redirect('THEEQUATIONERS_profile')
                elif officer.organization == 'SSG':
                    return redirect('SSG_profile')
                elif officer.organization == 'TECHNOCRATS':
                    return redirect('TECHNOCRATS_profile')
                else:
                    messages.error(request, 'Invalid organization.')
                    return redirect('home')  # Fallback redirect to home if organization is invalid
            except OfficerLogin.DoesNotExist:
                messages.error(request, 'Invalid username or password.')
    else:
        form = LoginForm()
    return render(request, 'studentorg/ADMIN/officer_login.html', {'form': form})

# admin
def admin_manageofficer(request):
    officers = Officer.objects.all()
    if request.method == 'POST':
        officer_id = request.POST.get('officer_id')
        action = request.POST.get('action')
        officer = get_object_or_404(Officer, id=officer_id)
        if action == 'approve':
            officer.status = 'approved'
        elif action == 'decline':
            officer.status = 'declined'
        officer.save()
        return redirect('admin_manageofficer')
    return render(request, 'studentorg/ADMIN/admin_manageofficer.html', {'officers': officers})

def admin_manageadviser(request):
    advisers = Adviser.objects.all()
    if request.method == 'POST':
        adviser_id = request.POST.get('adviser_id')
        action = request.POST.get('action')
        adviser = get_object_or_404(Adviser, id=adviser_id)
        if action == 'approve':
            adviser.status = 'approved'
        elif action == 'decline':
            adviser.status = 'declined'
        adviser.save()
        return redirect('admin_manageadviser')
    return render(request, 'studentorg/ADMIN/admin_manageadviser.html', {'advisers': advisers})



def admin_manageproject(request):
    projects = Project.objects.all()
    if request.method == 'POST':
        project_id = request.POST.get('project_id')
        action = request.POST.get('action')
        project = get_object_or_404(Project, project_id=project_id)
        if action == 'approve':
            project.status = 'approved'
        elif action == 'decline':
            project.status = 'declined'
        project.save()
        return redirect('admin_manageproject')
    return render(request, 'studentorg/ADMIN/admin_manageproject.html', {'projects': projects})

def admin_managefinancial(request):
    statements = FinancialStatement.objects.all()
    if request.method == 'POST':
        financial_id = request.POST.get('financial_id')  
        action = request.POST.get('action')
        statement = get_object_or_404(FinancialStatement, financial_id=financial_id)  # Corrected variable name
        if action == 'approve':
            statement.status = 'approved'
        elif action == 'decline':
            statement.status = 'declined'
        statement.save()
        return redirect('admin_managefinancial')
    return render(request, 'studentorg/ADMIN/admin_managefinancial.html', {'statements': statements})

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
    
    return render(request, 'ADMIN/manage_accreditation.html', {'accreditations': accreditations})

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
    return render (request, "studentorg/THEEQUATIONER/THEEQUATIONER_CBL.html")

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

def Gen_Home(request):
     return render (request, "studentorg/VIEW/OrgMain.html")

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
    approved_projects = Project.objects.filter(status='approved', org='THE EQUATIONERS')
    return render(request, 'studentorg/VIEW/THEEQUATIONER_viewproject.html', {'projects': approved_projects})
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

