from django.shortcuts import render, redirect
from django.http import JsonResponse
from ..models import Program, ProgramImage, MOD
from ..models import QrDonation  # if you have donations
from django.contrib import messages
from ..forms import CrowdfundingProjectForm,  ProgramForm
from django.http import JsonResponse
from django.template.loader import render_to_string

# ... other imports ...
# community.py

from django.http import JsonResponse
from django.template.loader import render_to_string
# ... other imports

def edit_program(request, pk):
    program = get_object_or_404(Program, pk=pk)
    
    if request.method == "POST":
        form = ProgramForm(request.POST, instance=program)
        if form.is_valid():
            program = form.save()
            if request.headers.get("x-requested-with") == "XMLHttpRequest":
                return JsonResponse({
                    "success": True, 
                    "program": {
                        "id": program.id,
                        "title": program.title,
                        "caption": program.caption,
                        "description": program.description,
                    }
                })
            return redirect("programs")
        else:
             if request.headers.get("x-requested-with") == "XMLHttpRequest":
                return JsonResponse({"success": False, "errors": form.errors})

    else: # GET request
        form = ProgramForm(instance=program)

    if request.headers.get("x-requested-with") == "XMLHttpRequest":
        # THIS IS THE FIX 👇
        html_form = render_to_string(
            "community_involvement/_edit_program_form.html",
            {"form": form, "program": program},
            request=request  # Ensure this keyword argument is present
        )
        return JsonResponse({"html_form": html_form})

    return render(request, "community_involvement/edit_program.html", {"form": form, "program": program})

def delete_program(request, pk):
    program = get_object_or_404(Program, pk=pk)
    if request.method == "POST":
        program.delete()
        return redirect("programs")
    # This renders a confirmation page before deleting
    return render(request, "community_involvement/admin/confirm_delete_program.html", {"program": program})
def edit_project(request, pk):
    project = get_object_or_404(CrowdfundingProject, pk=pk)
    if request.method == "POST":
        form = CrowdfundingProjectForm(request.POST, request.FILES, instance=project)
        if form.is_valid():
            form.save()
            return redirect("crowdfunding_list")
    else:
        form = CrowdfundingProjectForm(instance=project)
    return render(request, "community_involvement/edit_project.html", {"form": form, "project": project})


def delete_project(request, pk):
    project = get_object_or_404(CrowdfundingProject, pk=pk)
    if request.method == "POST":
        project.delete()
        return redirect("crowdfunding_list")
    return render(request, "community_involvement/confirm_delete.html", {"project": project})
def add_event(request):
    if request.method == "POST" and request.headers.get("x-requested-with") == "XMLHttpRequest":
        title = request.POST.get("title", "Community Event")
        description = request.POST.get("description", "")



        project = CrowdfundingProject.objects.create(
            title=title,
            description=description,
        )

        images_urls = []
        if request.FILES.getlist("images"):
            for f in request.FILES.getlist("images"):
                channel = DonationChannel.objects.create(
                    project=project,
                    imageCrowdfunding=f
                )
                images_urls.append(channel.imageCrowdfunding.url)

        return JsonResponse({
            "success": True,
            "project": {
                "id": project.id,
                "title": project.title,
                "description": project.description,
                "images": images_urls,
            }
        })

    # GET request
    projects = CrowdfundingProject.objects.all().order_by("-created_at")
    return render(request, "community_involvement/crowdfunding_list.html", {"projects": projects})
def add_programs(request):
    if request.method == "POST":
        title = request.POST.get("title", "Untitled Event")
        caption = request.POST.get("caption", "")
        description = request.POST.get("description", "")
        
        program = Program.objects.create(
            title=title,
            caption=caption,
            description=description,
        )

        for file in request.FILES.getlist("images"):
            ProgramImage.objects.create(program=program, image=file)

        # Always check for AJAX
        if request.headers.get("x-requested-with") == "XMLHttpRequest":
            images = [img.image.url for img in program.images.all()]
            return JsonResponse({
                "success": True,
                "message": "Program added!",
                "program": {
                    "title": program.title,
                    "caption": program.caption,
                    "description": program.description,
                    "images": images
                }
            })
        else:
            # If not AJAX, redirect or render as needed
            return redirect("programs")

    # fallback GET
    if request.headers.get("x-requested-with") == "XMLHttpRequest":
        return JsonResponse({"success": False, "error": "Invalid request method"}, status=400)
    return redirect("programs")


def programs(request):

    loadPrograms = Program.objects.filter(archive=False).order_by("-date_time")

    # Get all QR donation records
    qrCodeID = QrDonation.objects.all()

    # Choose base template based on user role
    base_template = "adminmain.html" if request.user.is_staff or request.user.is_superuser else "main.html"

    # Boolean flag indicating if the user is an admin/staff
    is_staff_user = request.user.is_staff

    # Render the page with context
    return render(
        request,
        "community_involvement/programs.html",
        {
            "url": "programs",
            "title": "Programs",
            "loadPrograms": loadPrograms,
            "qrCodeID": qrCodeID,
            "base_template": base_template,
        },
    )

from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse
from ..models import CrowdfundingProject, Donation, DonationChannel
from django.views.decorators.csrf import csrf_exempt

def crowdfunding_list(request):
    """List all active crowdfunding projects"""
    base_template = "adminmain.html" if request.user.is_staff or request.user.is_superuser else "main.html"
    projects = CrowdfundingProject.objects.filter(active=True).order_by("-created_at")

    context = {
        "projects": projects,
        "base_template": base_template,
    }

    return render(
        request,
        "community_involvement/crowdfunding_list.html",
        context
    )


def crowdfunding_detail(request, pk):
    """Single project page with donation channels"""
    project = get_object_or_404(CrowdfundingProject, pk=pk, active=True)
    return render(
        request,
        "community_involvement/crowdfunding_detail.html",
        {"project": project},
    )
def donate_view(request):
    # Fetch all QR codes to display in GCash/Bank/Volunteer sections
    qrCodeID = QrDonation.objects.all()

    return render(request, "community_involvement/donate.html", {
        "qrCodeID": qrCodeID,
        "user": request.user,   # so {% if user %} works in template
    })

def donate(request, pk):
    """Donation form (anonymous or with name)"""
    project = get_object_or_404(CrowdfundingProject, pk=pk, active=True)

    if request.method == "POST":
        amount = request.POST.get("amount")
        donor_name = request.POST.get("donor_name", "").strip()

        if amount:
            donation = Donation.objects.create(
                project=project,
                amount=amount,
                donor_name=donor_name if donor_name else None,
            )
            # Update project’s current amount
            project.current_amount += float(amount)
            project.save()

            if request.headers.get("x-requested-with") == "XMLHttpRequest":
                return JsonResponse(
                    {
                        "success": True,
                        "message": "Donation successful!",
                        "new_amount": project.current_amount,
                        "progress": project.progress(),
                    }
                )

            return redirect("crowdfunding_detail", pk=project.pk)

    return render(
        request,
        "community_involvement/donate.html",
        {"project": project},
    )


def gcash_mode(request):
    if request.method == "POST":
        MOD(request.POST)

        donated = request.POST["title"]
        name = request.POST["name"]
        gcash_number = request.POST["gcash_number"]
        amount = request.POST["amount"]
        image_details = request.FILES.getlist("images")

        for image in image_details:

            donation = MOD(
                donation_type="GCash",
                donated=donated,
                name=name,
                gcash_number=gcash_number,
                amount=amount,
                image_details=image,
            )

            donation.save()

    return redirect("programs")
def gcash_mode_admin(request, id):
    qr = request.FILES.getlist("images")
    for image in qr:
        if QrDonation.objects.count() == 0 or id == 0:  # first time upload
            qrCode = QrDonation(gcash=image)
        else:
            qrCode = QrDonation.objects.get(qr_id=id)
            qrCode.gcash = image
        qrCode.save()
    return redirect("programs")



def bank_mode(request):
    if request.method == "POST":
        MOD(request.POST)

        donated = request.POST["title"]
        name = request.POST["name"]
        bank_card = request.POST["banks"]
        bank_number = request.POST["bank_number"]
        amount = request.POST["amount"]
        image_details = request.FILES.getlist("images")

        for image in image_details:

            donation = MOD(
                donation_type="Bank",
                donated=donated,
                name=name,
                bank_number=bank_number,
                bank_card=bank_card,
                amount=amount,
                image_details=image,
            )

            donation.save()

    return redirect("programs")

def bank_mode_admin(request, id):
    qr = request.FILES.getlist("images")
    banks = request.POST.get("banks")

    for image in qr:
        if id == 0 or not QrDonation.objects.exists():
            # Create a new QrDonation
            if banks == "BPI":
                qrCode = QrDonation(bpi=image)
            elif banks == "BDO":
                qrCode = QrDonation(bdo=image)
            elif banks == "LANDBACK":
                qrCode = QrDonation(landbank=image)
            elif banks == "PNB":
                qrCode = QrDonation(pnb=image)
            elif banks == "METRO BANK":
                qrCode = QrDonation(metro=image)
            elif banks == "UNION BANK":
                qrCode = QrDonation(union=image)
            elif banks == "CHINA BANK":
                qrCode = QrDonation(china=image)
        else:
            qrCode = QrDonation.objects.get(qr_id=id)
            if banks == "BPI":
                qrCode.bpi = image
            elif banks == "BDO":
                qrCode.bdo = image
            elif banks == "LANDBACK":
                qrCode.landbank = image
            elif banks == "PNB":
                qrCode.pnb = image
            elif banks == "METRO BANK":
                qrCode.metro = image
            elif banks == "UNION BANK":
                qrCode.union = image
            elif banks == "CHINA BANK":
                qrCode.china = image

        qrCode.save()

    return redirect("programs")

def volunteer_mode(request):
    if request.method == "POST":

        donated = request.POST["title"]
        name = request.POST["name"]
        contact_number = request.POST["contact_number"]
        confirmation_photo = request.FILES.getlist("images")
        what_kind = request.POST["what_kind"]

        for image in confirmation_photo:
            if what_kind == "RELIEF GOODS":
                MOD.objects.create(
                    donation_type="Volunteer",
                    donated=donated,
                    name=name,
                    contact_number=contact_number,
                    what_kind=what_kind,
                    recepient_things=request.POST["recepient_things"],
                    image_details=image,
                )

            if what_kind == "BELONGINGS":
                MOD.objects.create(
                    donation_type="Volunteer",
                    donated=donated,
                    name=name,
                    contact_number=contact_number,
                    what_kind=what_kind,
                    recepient_things=request.POST["recepient_things"],
                    image_details=image,
                )

            if what_kind == "EQUIPMENTS":
                MOD.objects.create(
                    donation_type="Volunteer",
                    donated=donated,
                    name=name,
                    contact_number=contact_number,
                    what_kind=what_kind,
                    recepient_things=request.POST["recepient_things"],
                    image_details=image,
                )

            if what_kind == "MONEY":
                recepient_name = request.POST["recepient_name"]

                MOD.objects.create(
                    donation_type="Volunteer",
                    donated=donated,
                    name=name,
                    contact_number=contact_number,
                    amount=request.POST["volunteer_amount"],
                    what_kind=what_kind,
                    recepient=recepient_name,
                    image_details=image,
                )

        if what_kind == "SERVICE":
            MOD.objects.create(
                donation_type="Volunteer",
                donated=donated,
                name=name,
                contact_number=contact_number,
                what_kind=what_kind,
                date_sched=request.POST["date_sched"],
            )

        # date_sched = request.POST["date_sched"]
        # amount = request.POST["amount"]

    return redirect("programs")



def reports(request):
    user = request.user.is_staff

    # loadDonations = MOD.objects.all()

    # for i in loadDonations:
    #     print(i.date_time)

    return render(
        request,
        "community_involvement/reports.html",
        {"url": "report", "user": user},
    )


def reports_all(request):
    loadDonations = MOD.objects.all()
    return render(
        request,
        "community_involvement/reports.html",
        {
            "url": "report",
            "loadDonations": loadDonations,
        },
    )


def reports_find(request):

    if request.method == "POST":
        month = request.POST.get("month")
        year = request.POST.get("year")

        loadDonations = MOD.objects.filter(date__month=month, date__year=year)
    return render(
        request,
        "community_involvement/reports.html",
        {
            "url": "report",
            "loadDonations": loadDonations,
        },
    )


def archive_project(request, id):

    Program.objects.filter(id=id).update(archive=True)

    return redirect("project")


def archive_program(request, id):
    Program.objects.filter(id=id).update(archive=True)

    return redirect("program")
def donation_validate(request):
    loadDonations = MOD.objects.filter(status=None)

    context = {}

    if int(MOD.objects.count()) == 0:
        cotext = {"url": "report"}
    else:
        for status in loadDonations:
            if status == None:
                context = {
                    "url": "report",
                    "loadDonations": loadDonations,
                    "status": status,
                }
            else:
                context = {
                    "url": "report",
                    "loadDonations": loadDonations,
                }

    return render(
        request,
        "community_involvement/admin/donation-validate.html",
        context,
    )


def donation_accept(request, id):
    MOD.objects.filter(id=id).update(status="Accepted")

    return redirect("donation-validate")


def donation_decline(request, id):
    MOD.objects.filter(id=id).update(status="Declined")

    return redirect("donation-validate")


def donation_filter(request):
    if request.method == "POST":
        statusFilter = request.POST.get("filterStatus")

        # print(statusFilter)
        if statusFilter == "Accepted" or statusFilter == "Declined":
            status = "Yes"
        else:
            status = None

        filterStatus = MOD.objects.filter(status=statusFilter)

    return render(
        request,
        "community_involvement/admin/donation-validate.html",
        {"loadDonations": filterStatus, "status": status},
    )



def archive_program(request, id):
    Program.objects.filter(id=id).update(archive=True)

    return redirect("program")



def dashboard(request):
    user = request.user.is_staff
    return render(
        request,
        "community_involvement/admin/dashboard.html",
        {"user": user},
    )


def donation_dashboard(request):
    loadGcashDonations = MOD.objects.filter(donation_type="GCash", status="Accepted")
    loadBankDonations = MOD.objects.filter(donation_type="Bank", status="Accepted")
    loadVolunteer = MOD.objects.filter(donation_type="Volunteer", status="Accepted")

    return render(
        request,
        "community_involvement/admin/donation.html",
        {
            "loadGcashDonations": loadGcashDonations,
            "loadBankDonations": loadBankDonations,
            "loadVolunteer": loadVolunteer,
        },
    )



def gcash_dashboard(request):
    loadGcashDonations = MOD.objects.filter(donation_type="GCash", status="Accepted")

    return render(
        request,
        "community_involvement/admin/gcash-dashboard.html",
        {"loadGcashDonations": loadGcashDonations},
    )



def banks_dashboard(request):
    loadBanksDonations = MOD.objects.filter(donation_type="Bank", status="Accepted")

    return render(
        request,
        "community_involvement/admin/banks-dashboard.html",
        {"loadBanksDonations": loadBanksDonations},
    )



def volunteer_dashboard(request):
    loadVolunteerDonations = MOD.objects.filter(
        donation_type="Volunteer", status="Accepted"
    )

    return render(
        request,
        "community_involvement/admin/volunteer-dashboard.html",
        {"loadVolunteerDonations": loadVolunteerDonations},
    )
