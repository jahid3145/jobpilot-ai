from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm

from apps.resumes.models import Resume
from apps.users.models import CandidateProfile

User = get_user_model()


class RegistrationForm(UserCreationForm):
    email = forms.EmailField(required=True)
    first_name = forms.CharField(max_length=150, required=False)
    last_name = forms.CharField(max_length=150, required=False)

    class Meta(UserCreationForm.Meta):
        model = User
        fields = ("username", "email", "first_name", "last_name")


class CandidateProfileForm(forms.ModelForm):
    skills_text = forms.CharField(required=False, help_text="Separate skills with commas.")
    preferred_locations_text = forms.CharField(required=False, help_text="Separate locations with commas.")
    desired_job_titles_text = forms.CharField(required=False, help_text="Separate job titles with commas.")

    class Meta:
        model = CandidateProfile
        fields = (
            "full_name", "professional_headline", "location", "years_of_experience", "employment_type",
            "minimum_salary", "maximum_salary",
        )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance.pk:
            self.fields["skills_text"].initial = ", ".join(self.instance.skills)
            self.fields["preferred_locations_text"].initial = ", ".join(self.instance.preferred_locations)
            self.fields["desired_job_titles_text"].initial = ", ".join(self.instance.desired_job_titles)

    def save(self, commit=True):
        profile = super().save(commit=False)
        for form_name, model_name in (
            ("skills_text", "skills"),
            ("preferred_locations_text", "preferred_locations"),
            ("desired_job_titles_text", "desired_job_titles"),
        ):
            setattr(profile, model_name, [item.strip() for item in self.cleaned_data[form_name].split(",") if item.strip()])
        if commit:
            profile.save()
        return profile


class ResumeUploadForm(forms.ModelForm):
    class Meta:
        model = Resume
        fields = ("title", "file", "is_primary")

    def clean_file(self):
        uploaded_file = self.cleaned_data["file"]
        if not uploaded_file.name.lower().endswith(".pdf"):
            raise forms.ValidationError("Please select a PDF file.")
        if uploaded_file.size > 5 * 1024 * 1024:
            raise forms.ValidationError("The PDF must be 5 MB or smaller.")
        return uploaded_file

