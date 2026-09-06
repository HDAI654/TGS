from django.contrib.admin.views.decorators import staff_member_required
from django.shortcuts import redirect, render
from django.contrib import messages
from .forms import WorkerConfigurationForm
from .services import get_configuration, update_schedule


@staff_member_required
def worker_configuration(request):
    configuration = get_configuration()
    if request.method == "POST":
        form = WorkerConfigurationForm(request.POST, instance=configuration)
        if form.is_valid():
            update_schedule(form.cleaned_data["interval_minutes"])
            messages.success(request, "Worker schedule updated successfully.")
            return redirect("worker_configuration")
    else:
        form = WorkerConfigurationForm(instance=configuration)
    return render(
        request,
        "admin/worker_control/configuration.html",
        {"form": form, "configuration": configuration},
    )
