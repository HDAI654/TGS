from django import forms
from .models import WorkerConfiguration


class WorkerConfigurationForm(forms.ModelForm):
    class Meta:
        model = WorkerConfiguration
        fields = ("interval_minutes",)

    def clean_interval_minutes(self) -> int:
        value = self.cleaned_data["interval_minutes"]
        if not 1 <= value <= 1440:
            raise forms.ValidationError("Interval must be between 1 and 1440 minutes.")
        return value
