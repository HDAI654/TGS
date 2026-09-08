import json
from django.contrib.admin.views.decorators import staff_member_required
from django.http import JsonResponse
from django.shortcuts import redirect, render
from django.views.decorators.http import require_GET, require_POST

from .services import (
    get_worker_status,
    restart_worker,
    start_worker,
    stop_worker,
)


@staff_member_required
def dashboard(request):
    """Render the background worker dashboard."""
    return render(
        request,
        "admin/background_workers/dashboard.html",
        {
            "worker": get_worker_status(),
        },
    )


@require_GET
def status(request):
    """Return the current background worker status."""
    return JsonResponse(get_worker_status())


@require_POST
def start(request):
    """Start the background worker."""
    start_worker()

    return redirect("background_worker_dashboard")


@require_POST
def stop(request):
    """Stop the background worker."""
    stop_worker()

    return redirect("background_worker_dashboard")


@require_POST
def restart(request):
    """Change the interval and restart the background worker."""
    try:
        interval_minutes = int(request.POST["interval_minutes"])
    except (KeyError, TypeError, ValueError):
        return JsonResponse(
            {
                "error": "interval_minutes must be a positive integer.",
            },
            status=400,
        )

    if interval_minutes <= 0:
        return JsonResponse(
            {
                "error": "interval_minutes must be greater than zero.",
            },
            status=400,
        )

    restart_worker(interval_minutes)

    return redirect("background_worker_dashboard")