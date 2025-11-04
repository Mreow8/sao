from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.template.loader import render_to_string
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.contrib import messages
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from ..models import (
    Program, ProgramImage, MOD, QrDonation,
    CrowdfundingProject, Donation, DonationChannel
)
from ..forms import CrowdfundingProjectForm,  ProgramForm

# --- All View Functions Below ---

@login_required
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
        html_form = render_to_string(
            "community_involvement/_edit_program_form.html",
            {"form": form, "program": program},
            request=request
        )
        return JsonResponse({"html_form": html_form})

    return render(request, "community_involvement/edit_program.html", {"form": form, "program": program})

@login_required
def delete_program(request, pk):
    program = get_object_or_404(Program, pk=pk)
    if request.method == "POST":
        program.delete()
        return redirect("programs")
    # This renders a confirmation page before deleting
    return render(request, "community_involvement/admin/confirm_delete_program.html", {"program": program})

@login_required
def edit_project(request, pk):
    project = get_object_or_404(CrowdfundingProject, pk=pk)
    is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'

    if request.method == "POST":
        form = CrowdfundingProjectForm(request.POST, request.FILES, instance=project)
        
        if form.is_valid():
            # Save the form to get the updated project instance
            project = form.save() 
            
            if is_ajax:
                # --- FIX: Return the updated project data ---
                # This matches the logic from your edit_program view.
                return JsonResponse({
                    "success": True,
                    "project": {
                        "id": project.id,
                        "title": project.title,
                        "description": project.description,
                        # Format the date/time if you plan to update it
                        # "date_time": project.date_time.strftime("%b. %d, %Y, %I:%M %p") 
                    }
                })
            else:
                return redirect("crowdfunding_list")
        else: # Form is invalid
            if is_ajax:
                form_html = render_to_string(
                    "community_involvement/_edit_project_form.html",
                    {"form": form, "project": project},
                    request=request,
                )
                return JsonResponse({"success": False, "form_html": form_html}, status=400)
            else:
                # Handle non-AJAX form error if needed
                pass 
    
    else: # GET request
        form = CrowdfundingProjectForm(instance=project)

    if is_ajax:
        form_html = render_to_string(
            "community_involvement/_edit_project_form.html",
            {"form": form, "project": project},
            request=request,
        )
        return JsonResponse({"form_html": form_html})

    context = {"form": form, "project": project}
    return render(request, "community_involvement/admin/edit_project.html", context)
@login_required
def delete_project(request, pk):
    project = get_object_or_404(CrowdfundingProject, pk=pk)
    if request.method == "POST":
        project.delete()
        return redirect("crowdfunding_list")
    return render(request, "community_involvement/confirm_delete.html", {"project": project})

@login_required
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
                # --- FIX --- Added created_at so JS can display it
                "created_at": project.created_at.strftime("%b. %d, %Y, %I:%M %p")
            }
        })

    # GET request
    projects = CrowdfundingProject.objects.all().order_by("-created_at")
    return render(request, "community_involvement/crowdfunding_list.html", {"projects": projects})

@login_required
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
            return redirect("programs")

    if request.headers.get("x-requested-with") == "XMLHttpRequest":
        return JsonResponse({"success": False, "error": "Invalid request method"}, status=400)
    return redirect("programs")

@login_required
def programs(request):
    program_list = Program.objects.filter(archive=False).order_by("-date_time")
    items_per_page = 5 
    paginator = Paginator(program_list, items_per_page)
    page_number = request.GET.get('page')

    try:
        page_obj = paginator.page(page_number)
    except PageNotAnInteger:
        page_obj = paginator.page(1)
    except EmptyPage:
        page_obj = paginator.page(paginator.num_pages)

    qrCodeID = QrDonation.objects.all()
    base_template = "adminmain.html" if request.user.is_staff or request.user.is_superuser else "main.html"

    return render(
        request,
        "community_involvement/programs.html",
        {
            "url": "programs",
            "title": "Programs",
            "page_obj": page_obj,
            "qrCodeID": qrCodeID, 
            "base_template": base_template,
            "user": request.user,
        },
    )

@login_required
def crowdfunding_list(request):
    project_list = CrowdfundingProject.objects.filter(active=True).order_by("-created_at")
    items_per_page = 5
    paginator = Paginator(project_list, items_per_page)
    page_number = request.GET.get('page')

    try:
        page_obj = paginator.page(page_number)
    except PageNotAnInteger:
        page_obj = paginator.page(1)
    except EmptyPage:
        page_obj = paginator.page(paginator.num_pages)

    base_template = "adminmain.html" if request.user.is_staff or request.user.is_superuser else "main.html"

    context = {
        "page_obj": page_obj,
        "base_template": base_template,
        "user": request.user,
    }

    return render(
        request,
        "community_involvement/crowdfunding_list.html",
        context
    )


@login_required
def crowdfunding_detail(request, pk):
    project = get_object_or_404(CrowdfundingProject, pk=pk, active=True)
    return render(
        request,
        "community_involvement/crowdfunding_detail.html",
        {"project": project},
    )

@login_required
def donate_view(request):
    qrCodeID = QrDonation.objects.all()
    return render(request, "community_involvement/donate.html", {
        "qrCodeID": qrCodeID,
        "user": request.user,
    })

@login_required
def donate(request, pk):
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
            # This will cause an error if current_amount is not on your model
            # project.current_amount += float(amount)
            # project.save()

            if request.headers.get("x-requested-with") == "XMLHttpRequest":
                return JsonResponse(
                    {
                        "success": True,
                        "message": "Donation successful!",
                        # "new_amount": project.current_amount,
                        # "progress": project.progress(),
                    }
                )
            return redirect("crowdfunding_detail", pk=project.pk)
    return render(
        request,
        "community_involvement/donate.html",
        {"project": project},
    )

@login_required
def gcash_mode(request):
    if request.method == "POST":
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

@login_required
def gcash_mode_admin(request, id):
    # It's good practice to ensure this is a POST request
    if request.method != "POST":
        messages.error(request, "Invalid request.")
        return redirect("crowdfunding_list")

    qr = request.FILES.getlist("images")

    # --- Check if any file was uploaded ---
    if not qr:
        messages.warning(request, "No file was selected. Please choose an image.")
        return redirect("crowdfunding_list")

    try:
        for image in qr:
            if QrDonation.objects.count() == 0 or id == 0:
                qrCode = QrDonation(gcash=image)
            else:
                # Get the existing object to update it
                qrCode = QrDonation.objects.get(pk=id) 
                qrCode.gcash = image
            
            qrCode.save() # Save the object

        # --- Add Success Message ---
        messages.success(request, "GCash QR code uploaded successfully!")

    except QrDonation.DoesNotExist:
        messages.error(request, f"Upload failed: Could not find a QR object with ID {id}.")
    except Exception as e:
        # --- Add Generic Error Message ---
        messages.error(request, f"An error occurred: {e}")

    # This will redirect and the message will be displayed on the next page
    return redirect("crowdfunding_list")

@login_required
def bank_mode(request):
    if request.method == "POST":
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

@login_required
def bank_mode_admin(request, id):
    qr = request.FILES.getlist("images")
    banks = request.POST.get("banks")

    for image in qr:
        if id == 0 or not QrDonation.objects.exists():
            if banks == "BPI":
                qrCode = QrDonation(bpi=image)
            elif banks == "BDO":
                qrCode = QrDonation(bdo=image)
            # --- FIX --- Corrected typo
            elif banks == "LANDBANK":
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
            qrCode = QrDonation.objects.get(pk=id) # Use pk, not qr_id
            if banks == "BPI":
                qrCode.bpi = image
            elif banks == "BDO":
                qrCode.bdo = image
            # --- FIX --- Corrected typo
            elif banks == "LANDBANK":
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

@login_required
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
            elif what_kind == "BELONGINGS":
                MOD.objects.create(
                    donation_type="Volunteer",
                    donated=donated,
                    name=name,
                    contact_number=contact_number,
                    what_kind=what_kind,
                    recepient_things=request.POST["recepient_things"],
                    image_details=image,
                )
            elif what_kind == "EQUIPMENTS":
                MOD.objects.create(
                    donation_type="Volunteer",
                    donated=donated,
                    name=name,
                    contact_number=contact_number,
                    what_kind=what_kind,
                    recepient_things=request.POST["recepient_things"],
                    image_details=image,
                )
            elif what_kind == "MONEY":
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
    return redirect("programs")

@login_required
def reports(request):
    user = request.user.is_staff
    return render(
        request,
        "community_involvement/reports.html",
        {"url": "report", "user": user},
    )

@login_required
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

@login_required
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

@login_required
def archive_project(request, id):
    Program.objects.filter(id=id).update(archive=True)
    return redirect("project") # This URL name might be wrong

@login_required
def archive_program(request, id):
    Program.objects.filter(id=id).update(archive=True)
    return redirect("programs") # Changed from "program" to "programs"

@login_required
def donation_validate(request):
  
    
    filter_status = request.GET.get('filterStatus')

    if filter_status in ['Accepted', 'Declined']:
        donation_list = MOD.objects.filter(status=filter_status).order_by('-date')
    else:
        donation_list = MOD.objects.filter(status=None).order_by('-date')

    paginator = Paginator(donation_list, 10) 

    page_number = request.GET.get('page')

    try:
        loadDonations = paginator.page(page_number)
    except PageNotAnInteger:
        loadDonations = paginator.page(1)
    except EmptyPage:
        loadDonations = paginator.page(paginator.num_pages)

    context = {
        "url": "report", 
        "loadDonations": loadDonations,
    
        "selected_status": filter_status 
    }
    
    return render(
        request,
        "community_involvement/admin/donation-validate.html",
        context,
    )

@login_required
def donation_accept(request, id):
    MOD.objects.filter(id=id).update(status="Accepted")
    return redirect("donation-validate")

@login_required
def donation_decline(request, id):
    MOD.objects.filter(id=id).update(status="Declined")
    return redirect("donation-validate")

@login_required
def donation_filter(request):
    if request.method == "POST":
        statusFilter = request.POST.get("filterStatus")
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

# --- FIX --- Removed the duplicate archive_program function

@login_required
def dashboard(request):
    user = request.user.is_staff
    return render(
        request,
        "community_involvement/admin/dashboard.html",
        {"user": user},
    )

@login_required
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
# @login_required
@login_required
def gcash_dashboard(request):
    # 1. Base QuerySet
    # Assuming your model has a 'date' field to order by
    donation_list = MOD.objects.filter(donation_type="GCash", status="Accepted").order_by('-date')

    # 2. Get current page number
    page_number = request.GET.get('page')

    # 3. Initialize Paginator (15 items per page)
    paginator = Paginator(donation_list, 15)
    
    # 4. Get the Page object
    page_obj = paginator.get_page(page_number)
    
    context = {
        # Pass the Page object to the template
        "page_obj": page_obj,
        # 'loadGcashDonations' is no longer needed, use page_obj.object_list in the template
    }
    
    return render(
        request,
        "community_involvement/admin/gcash-dashboard.html",
        context,
    )

@login_required
def banks_dashboard(request):
    loadBanksDonations = MOD.objects.filter(donation_type="Bank", status="Accepted")
    return render(
        request,
        "community_involvement/admin/banks-dashboard.html",
        {"loadBanksDonations": loadBanksDonations},
    )

@login_required
def volunteer_dashboard(request):
    loadVolunteerDonations = MOD.objects.filter(
        donation_type="Volunteer", status="Accepted"
    )
    return render(
        request,
        "community_involvement/admin/volunteer-dashboard.html",
        {"loadVolunteerDonations": loadVolunteerDonations},
    )