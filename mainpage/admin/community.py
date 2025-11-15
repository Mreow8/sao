from django.contrib import admin
from django.utils.html import format_html
from ..models import (
    Program, ProgramImage,
    CrowdfundingProject, DonationChannel, Donation,
    MOD, QrDonation
)

# --- Program and Program Images ---

class ProgramImageInline(admin.TabularInline):
    model = ProgramImage
    extra = 1  # How many new image slots to show
    readonly_fields = ('image_preview',)  # Add a read-only field for the preview

    def image_preview(self, obj):
        if obj.image:
            # Create a clickable thumbnail
            return format_html('<a href="{0}" target="_blank"><img src="{0}" style="max-height: 100px; max-width: 100px;" /></a>', obj.image.url)
        return "(No image)"
    image_preview.short_description = 'Preview'

@admin.register(Program)
class ProgramAdmin(admin.ModelAdmin):
    inlines = [ProgramImageInline]  # Add the ProgramImage manager here
    list_display = ('title', 'created_at', 'archive')
    search_fields = ('title', 'description', 'caption')
    list_filter = ('archive', 'created_at')
    list_editable = ('archive',)  # Allow editing 'archive' from the list

# --- Crowdfunding, Channels, and Donations ---

class DonationChannelInline(admin.TabularInline):
    model = DonationChannel
    extra = 1
    readonly_fields = ('image_preview',)

    def image_preview(self, obj):
        if obj.imageCrowdfunding:
            # Create a clickable thumbnail
            return format_html('<a href="{0}" target="_blank"><img src="{0}" style="max-height: 100px; max-width: 100px;" /></a>', obj.imageCrowdfunding.url)
        return "(No image)"
    image_preview.short_description = 'QR/Image Preview'

class DonationInline(admin.TabularInline):
    """
    Shows donations made *directly* to this project
    (This is different from the 'MOD' proof system)
    """
    model = Donation
    extra = 0  # Don't show new slots
    can_add = False  # Don't allow adding new ones here (they come from users)
    readonly_fields = ('donor_name', 'amount', 'created_at')
    
@admin.register(CrowdfundingProject)
class CrowdfundingProjectAdmin(admin.ModelAdmin):
    inlines = [DonationChannelInline, DonationInline]
    list_display = ('title', 'active', 'created_at')
    search_fields = ('title', 'description')
    list_filter = ('active', 'created_at')
    list_editable = ('active',)

# --- Donation Proof (MOD) Validation ---

@admin.register(MOD)
class MODAdmin(admin.ModelAdmin):
    list_display = ('name', 'donated', 'donation_type', 'amount', 'status', 'date', 'image_preview')
    list_filter = ('status', 'donation_type', 'what_kind', 'date')
    search_fields = ('name', 'donated', 'contact_number', 'gcash_number', 'bank_number')
    
    # Allows for quick status changes in the list view
    list_editable = ('status',)
    
    # Adds the "Accept" and "Decline" actions to the dropdown
    actions = ['accept_donations', 'decline_donations']
    
    # Make user-submitted fields read-only
    readonly_fields = ('image_preview', 'name', 'donated', 'donation_type', 'amount', 'date', 
                       'gcash_number', 'bank_number', 'bank_card', 'what_kind', 'recepient', 
                       'recepient_things', 'contact_number', 'date_sched')

    def image_preview(self, obj):
        if obj.image_details:
            return format_html('<a href="{0}" target="_blank"><img src="{0}" style="max-height: 100px; max-width: 100px;" /></a>', obj.image_details.url)
        return "(No receipt)"
    image_preview.short_description = 'Receipt Preview'

    # Admin action function to Accept
    @admin.action(description='Mark selected donations as ACCEPTED')
    def accept_donations(self, request, queryset):
        queryset.update(status='Accepted')

    # Admin action function to Decline
    @admin.action(description='Mark selected donations as DECLINED')
    def decline_donations(self, request, queryset):
        queryset.update(status='Declined')
            
# --- Site-wide QR Code Management ---

@admin.register(QrDonation)
class QrDonationAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'id')
    
    # This handy function prevents admins from creating more than one QR set.
    # Your gcash_mode_admin view assumes there is only one.
    def has_add_permission(self, request):
        return QrDonation.objects.count() == 0

# You can also register the other models if you want to see them separately,
# but the inlines above are a better way to manage them.
# admin.site.register(Donation)
# admin.site.register(ProgramImage)
# admin.site.register(DonationChannel)