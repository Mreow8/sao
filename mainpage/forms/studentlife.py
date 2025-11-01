from django import forms
from mainpage.models import Schedule, ExcelData, Storage

class ScheduleForm(forms.ModelForm):
    class Meta:
        model = Schedule
        fields = ['title', 'description', 'start_date', 'end_date']
        widgets = {
            'start_date': forms.DateInput(attrs={'type': 'date'}),
            'end_date': forms.DateInput(attrs={'type': 'date'}),
        }
# PPMP TRACKER FORMS
from django import forms
from ..models import PPMPDocument
class PPMPDocumentForm(forms.ModelForm):
    class Meta:
        model = PPMPDocument
        fields = ['title', 'document', 'status']
    
    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)  # pass user when creating form
        super().__init__(*args, **kwargs)
        if not (user and user.is_staff):  # hide status if not admin
            self.fields['status'].widget = forms.HiddenInput()
            self.fields['status'].initial = 'Pending'
class UploadFileForm(forms.Form):
    file = forms.FileField()

# serial number 
class UpdateSerialNoForm(forms.ModelForm):
    class Meta:
        model = Storage
        fields = ['serial_no']

# form for learning & development (L&D)
class UploadExcelForm(forms.Form):
    excel_file = forms.FileField()

# ExcelData form
class ExcelDataForm(forms.ModelForm):
    admin_remarks = forms.CharField(label='Admin Remarks', widget=forms.Textarea, required=False)

    class Meta:
        model = ExcelData
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super(ExcelDataForm, self).__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.required = False