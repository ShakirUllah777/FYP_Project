from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.http import JsonResponse, HttpResponseForbidden
from django.utils import timezone

from posts.models import Post
from .models import Team, TeamMembership, TaskItem, Milestone, ProjectFile, MeetingLink, Endorsement
from .forms import TaskItemForm, MilestoneForm, ProjectFileForm, MeetingLinkForm, EndorsementForm


def _member_required(user, team):
    return team.members.filter(pk=user.pk).exists()


@login_required
def start_team(request, post_id):
    """The post author converts a post into a live Team Workspace, or is
    redirected to the existing one."""
    post = get_object_or_404(Post, pk=post_id)
    team, created = Team.objects.get_or_create(post=post, defaults={'created_by': post.author})

    if created:
        TeamMembership.objects.create(team=team, user=post.author, role='owner')
        messages.success(request, 'Team workspace created! Add collaborators to get started.')

    if not _member_required(request.user, team):
        if request.user == post.author:
            TeamMembership.objects.get_or_create(team=team, user=request.user, defaults={'role': 'owner'})
        else:
            messages.error(request, 'Only the post author can add you to this workspace right now.')
            return redirect('user_profile', username=post.author.username)

    return redirect('team_detail', pk=team.pk)


@login_required
def team_detail(request, pk):
    team = get_object_or_404(Team.objects.select_related('post', 'created_by'), pk=pk)
    if not _member_required(request.user, team):
        return HttpResponseForbidden("You are not a member of this workspace.")

    tasks = team.tasks.select_related('assigned_to')
    columns = {
        'todo': tasks.filter(status='todo'),
        'in_progress': tasks.filter(status='in_progress'),
        'done': tasks.filter(status='done'),
    }
    milestones = team.post.milestones.all()
    files = team.files.select_related('uploaded_by')
    meetings = team.meetings.filter(scheduled_for__gte=timezone.now()).order_by('scheduled_for')

    return render(request, 'collaboration/team_detail.html', {
        'team': team,
        'columns': columns,
        'milestones': milestones,
        'files': files,
        'meetings': meetings,
        'task_form': TaskItemForm(team=team),
        'milestone_form': MilestoneForm(),
        'file_form': ProjectFileForm(),
        'meeting_form': MeetingLinkForm(),
        'is_owner': team.created_by_id == request.user.id,
    })


@login_required
def add_member(request, pk):
    team = get_object_or_404(Team, pk=pk)
    if team.created_by_id != request.user.id:
        return HttpResponseForbidden('Only the workspace owner can add members.')
    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        user = User.objects.filter(username=username).first()
        if not user:
            messages.error(request, f'No student found with username "{username}".')
        elif TeamMembership.objects.filter(team=team, user=user).exists():
            messages.info(request, f'{user.username} is already in this workspace.')
        else:
            TeamMembership.objects.create(team=team, user=user, role='collaborator')
            messages.success(request, f'{user.username} was added to the team.')
    return redirect('team_detail', pk=pk)


@login_required
def add_task(request, pk):
    team = get_object_or_404(Team, pk=pk)
    if not _member_required(request.user, team):
        return HttpResponseForbidden()
    if request.method == 'POST':
        form = TaskItemForm(request.POST, team=team)
        if form.is_valid():
            task = form.save(commit=False)
            task.team = team
            task.created_by = request.user
            task.save()
            messages.success(request, 'Task added to the board.')
    return redirect('team_detail', pk=pk)


@login_required
def update_task_status(request, pk, task_id):
    team = get_object_or_404(Team, pk=pk)
    task = get_object_or_404(TaskItem, pk=task_id, team=team)
    if not _member_required(request.user, team):
        return JsonResponse({'error': 'forbidden'}, status=403)
    if request.method == 'POST':
        new_status = request.POST.get('status')
        if new_status in dict(TaskItem.STATUS_CHOICES):
            task.status = new_status
            task.save()
            return JsonResponse({'ok': True, 'status': task.status})
    return JsonResponse({'error': 'bad request'}, status=400)


@login_required
def delete_task(request, pk, task_id):
    team = get_object_or_404(Team, pk=pk)
    task = get_object_or_404(TaskItem, pk=task_id, team=team)
    if _member_required(request.user, team):
        task.delete()
        messages.success(request, 'Task removed.')
    return redirect('team_detail', pk=pk)


@login_required
def add_milestone(request, pk):
    team = get_object_or_404(Team, pk=pk)
    if not _member_required(request.user, team):
        return HttpResponseForbidden()
    if request.method == 'POST':
        form = MilestoneForm(request.POST)
        if form.is_valid():
            m = form.save(commit=False)
            m.post = team.post
            m.save()
            messages.success(request, 'Milestone added.')
    return redirect('team_detail', pk=pk)


@login_required
def update_milestone(request, pk, milestone_id):
    team = get_object_or_404(Team, pk=pk)
    milestone = get_object_or_404(Milestone, pk=milestone_id, post=team.post)
    if _member_required(request.user, team) and request.method == 'POST':
        status = request.POST.get('status')
        if status in dict(Milestone.STATUS_CHOICES):
            milestone.status = status
            milestone.save()
    return redirect('team_detail', pk=pk)


@login_required
def upload_file(request, pk):
    team = get_object_or_404(Team, pk=pk)
    if not _member_required(request.user, team):
        return HttpResponseForbidden()
    if request.method == 'POST':
        form = ProjectFileForm(request.POST, request.FILES)
        if form.is_valid():
            f = form.save(commit=False)
            f.team = team
            f.uploaded_by = request.user
            f.save()
            messages.success(request, 'File uploaded to the workspace.')
    return redirect('team_detail', pk=pk)


@login_required
def delete_file(request, pk, file_id):
    team = get_object_or_404(Team, pk=pk)
    pfile = get_object_or_404(ProjectFile, pk=file_id, team=team)
    if _member_required(request.user, team) and (pfile.uploaded_by_id == request.user.id or team.created_by_id == request.user.id):
        pfile.file.delete(save=False)
        pfile.delete()
        messages.success(request, 'File removed.')
    return redirect('team_detail', pk=pk)


@login_required
def schedule_meeting(request, pk):
    team = get_object_or_404(Team, pk=pk)
    if not _member_required(request.user, team):
        return HttpResponseForbidden()
    if request.method == 'POST':
        form = MeetingLinkForm(request.POST)
        if form.is_valid():
            meeting = form.save(commit=False)
            meeting.team = team
            meeting.created_by = request.user
            meeting.save()
            messages.success(request, 'Call scheduled and shared with the team.')
    return redirect('team_detail', pk=pk)


# ---------------------------------------------------------------------
# Supervisor / Faculty endorsement workflow
# ---------------------------------------------------------------------

def _is_supervisor(user):
    return user.is_authenticated and hasattr(user, 'profile') and user.profile.is_supervisor


@user_passes_test(_is_supervisor)
def supervisor_dashboard(request):
    profile = request.user.profile
    fyp_posts = Post.objects.filter(post_type='fyp')
    if profile.department:
        fyp_posts = fyp_posts.filter(author__profile__department=profile.department)
    fyp_posts = fyp_posts.select_related('author__profile').prefetch_related('endorsements')

    return render(request, 'collaboration/supervisor_dashboard.html', {
        'fyp_posts': fyp_posts,
    })


@user_passes_test(_is_supervisor)
def endorse_post(request, post_id):
    post = get_object_or_404(Post, pk=post_id, post_type='fyp')
    existing = Endorsement.objects.filter(post=post, supervisor=request.user).first()
    if request.method == 'POST':
        form = EndorsementForm(request.POST, instance=existing)
        if form.is_valid():
            endorsement = form.save(commit=False)
            endorsement.post = post
            endorsement.supervisor = request.user
            endorsement.save()
            messages.success(request, f'Endorsement saved for "{post.title}".')
            return redirect('supervisor_dashboard')
    else:
        form = EndorsementForm(instance=existing)

    return render(request, 'collaboration/endorse_post.html', {
        'form': form, 'post': post, 'existing': existing,
    })
