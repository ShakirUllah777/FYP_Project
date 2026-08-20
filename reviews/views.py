from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.utils import timezone

from .models import Review, Report
from .forms import ReviewForm, ReportForm
from posts.models import Post


@login_required
def leave_review(request, username):
    reviewed_user = get_object_or_404(User, username=username)
    post_id = request.GET.get('post') or request.POST.get('post')
    post = Post.objects.filter(pk=post_id).first() if post_id else None

    if reviewed_user == request.user:
        messages.error(request, "You can't review yourself.")
        return redirect('user_profile', username=username)

    existing = Review.objects.filter(
        reviewer=request.user, reviewed_user=reviewed_user, post=post
    ).first()

    if request.method == 'POST':
        form = ReviewForm(request.POST, instance=existing)
        if form.is_valid():
            review = form.save(commit=False)
            review.reviewer = request.user
            review.reviewed_user = reviewed_user
            review.post = post
            review.save()
            messages.success(request, f'Your review for {reviewed_user.first_name} was posted.')
            return redirect('user_profile', username=username)
    else:
        form = ReviewForm(instance=existing)

    return render(request, 'reviews/leave_review.html', {
        'form': form,
        'reviewed_user': reviewed_user,
        'post': post,
        'existing': existing,
    })


@login_required
def report_user(request, username):
    reported_user = get_object_or_404(User, username=username)
    post_id = request.GET.get('post') or request.POST.get('post')
    post = Post.objects.filter(pk=post_id).first() if post_id else None

    if reported_user == request.user:
        messages.error(request, "You can't report yourself.")
        return redirect('user_profile', username=username)

    if request.method == 'POST':
        form = ReportForm(request.POST)
        if form.is_valid():
            report = form.save(commit=False)
            report.reporter = request.user
            report.reported_user = reported_user
            report.post = post
            report.save()
            messages.success(request, 'Thanks - your report has been sent to our moderation team.')
            return redirect('user_profile', username=username)
    else:
        form = ReportForm()

    return render(request, 'reviews/report_user.html', {
        'form': form,
        'reported_user': reported_user,
        'post': post,
    })


def _is_staff(user):
    return user.is_authenticated and user.is_staff


@user_passes_test(_is_staff)
def moderation_queue(request):
    status_filter = request.GET.get('status', 'open')
    reports = Report.objects.select_related('reporter', 'reported_user', 'post')
    if status_filter and status_filter != 'all':
        reports = reports.filter(status=status_filter)

    return render(request, 'reviews/moderation_queue.html', {
        'reports': reports,
        'status_filter': status_filter,
        'status_choices': Report.STATUS_CHOICES,
        'open_count': Report.objects.filter(status='open').count(),
    })


@user_passes_test(_is_staff)
def update_report_status(request, pk):
    report = get_object_or_404(Report, pk=pk)
    if request.method == 'POST':
        new_status = request.POST.get('status')
        notes = request.POST.get('admin_notes', '')
        if new_status in dict(Report.STATUS_CHOICES):
            report.status = new_status
            report.admin_notes = notes
            if new_status in ('resolved', 'dismissed'):
                report.resolved_at = timezone.now()
            report.save()
            messages.success(request, f'Report #{report.pk} updated to "{report.get_status_display()}".')
    return redirect('moderation_queue')
