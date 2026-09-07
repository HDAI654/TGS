from django.contrib.admin.views.decorators import staff_member_required
from django.shortcuts import render
from .services import channels_status, recent_logs, system_status, worker_status


@staff_member_required
def dashboard(request):
    return render(
        request,
        "admin/monitoring/dashboard.html",
        {
            "system": system_status(),
            "channels": channels_status(),
            "workers": worker_status(),
        },
    )


@staff_member_required
def logs(request):
    return render(request, "admin/monitoring/logs.html", {"logs": recent_logs()})


@staff_member_required
def channels(request):
    return render(
        request, "admin/monitoring/channels.html", {"channels": channels_status()}
    )


@staff_member_required
def workers(request):
    return render(
        request, "admin/monitoring/workers.html", {"workers": worker_status()}
    )
