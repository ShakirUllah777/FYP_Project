from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse

from posts.models import Post, ProjectFile, Milestone
from .models import Team, TaskItem


@login_required
def workspace(request, post_pk):
    post = get_object_or_404(Post, pk=post_pk)
    team = Team.objects.filter(post=post).first()

    is_author   = post.author == request.user
    is_member   = team and request.user in team.members.all() if team else False
    can_access  = is_author or is_member

    tasks_todo  = team.task_items.filter(status='todo')       if team else []
    tasks_prog  = team.task_items.filter(status='in_progress') if team else []
    tasks_done  = team.task_items.filter(status='done')       if team else []
    milestones  = post.milestones.all()
    files       = post.project_files.all().order_by('-uploaded_at')

    return render(request, 'teams/workspace.html', {
        'post':        post,
        'team':        team,
        'is_author':   is_author,
        'is_member':   is_member,
        'can_access':  can_access,
        'tasks_todo':  tasks_todo,
        'tasks_prog':  tasks_prog,
        'tasks_done':  tasks_done,
        'milestones':  milestones,
        'files':       files,
    })


@login_required
def create_team(request, post_pk):
    post = get_object_or_404(Post, pk=post_pk, author=request.user)
    if request.method == 'POST':
        team, created = Team.objects.get_or_create(post=post)
        team.members.add(request.user)
        post.status = 'in_progress'
        post.save()
        messages.success(request, f'Team workspace created for "{post.title}"!')
    return redirect('workspace', post_pk=post_pk)


@login_required
def join_team(request, post_pk):
    post = get_object_or_404(Post, pk=post_pk)
    if request.method == 'POST':
        team = get_object_or_404(Team, post=post)
        team.members.add(request.user)
        messages.success(request, f'You joined the team for "{post.title}"!')
    return redirect('workspace', post_pk=post_pk)


@login_required
def kanban(request, post_pk):
    post = get_object_or_404(Post, pk=post_pk)
    team = get_object_or_404(Team, post=post)
    return redirect('workspace', post_pk=post_pk)


@login_required
def add_task(request, post_pk):
    post = get_object_or_404(Post, pk=post_pk)
    team = get_object_or_404(Team, post=post)

    is_author = post.author == request.user
    is_member = request.user in team.members.all()
    if not (is_author or is_member):
        messages.error(request, 'You are not a member of this team.')
        return redirect('workspace', post_pk=post_pk)

    if request.method == 'POST':
        title    = request.POST.get('title', '').strip()
        desc     = request.POST.get('description', '').strip()
        status   = request.POST.get('status', 'todo')
        priority = request.POST.get('priority', 'medium')
        due_date = request.POST.get('due_date') or None
        assignee_id = request.POST.get('assignee') or None
        assignee = None
        if assignee_id:
            from django.contrib.auth.models import User
            assignee = User.objects.filter(id=assignee_id).first()

        if title:
            TaskItem.objects.create(
                team=team, title=title, description=desc,
                status=status, priority=priority,
                due_date=due_date, assignee=assignee,
                created_by=request.user
            )
            messages.success(request, 'Task added!')
        else:
            messages.error(request, 'Task title is required.')

    return redirect('workspace', post_pk=post_pk)


@login_required
def update_task(request, task_pk):
    task = get_object_or_404(TaskItem, pk=task_pk)
    post = task.team.post
    is_author = post.author == request.user
    is_member = request.user in task.team.members.all()

    if not (is_author or is_member):
        return JsonResponse({'error': 'Forbidden'}, status=403)

    if request.method == 'POST':
        new_status = request.POST.get('status')
        new_title  = request.POST.get('title', task.title).strip()
        new_desc   = request.POST.get('description', task.description).strip()
        new_prio   = request.POST.get('priority', task.priority)
        new_due    = request.POST.get('due_date') or None

        if new_status in dict(TaskItem.STATUS_CHOICES):
            task.status = new_status
        task.title       = new_title or task.title
        task.description = new_desc
        task.priority    = new_prio
        task.due_date    = new_due
        task.save()
        messages.success(request, 'Task updated!')

    return redirect('workspace', post_pk=post.pk)


@login_required
def delete_task(request, task_pk):
    task = get_object_or_404(TaskItem, pk=task_pk)
    post = task.team.post
    if request.method == 'POST':
        if post.author == request.user or task.created_by == request.user:
            task.delete()
            messages.success(request, 'Task deleted.')
    return redirect('workspace', post_pk=post.pk)


@login_required
def team_files(request, post_pk):
    post = get_object_or_404(Post, pk=post_pk)
    return redirect('workspace', post_pk=post_pk)


@login_required
def upload_file(request, post_pk):
    post = get_object_or_404(Post, pk=post_pk)
    team = Team.objects.filter(post=post).first()

    is_author = post.author == request.user
    is_member = team and request.user in team.members.all()
    if not (is_author or is_member):
        messages.error(request, 'Access denied.')
        return redirect('workspace', post_pk=post_pk)

    if request.method == 'POST' and request.FILES.get('file'):
        desc = request.POST.get('description', '').strip()
        ProjectFile.objects.create(
            post=post,
            uploader=request.user,
            file=request.FILES['file'],
            description=desc,
        )
        messages.success(request, 'File uploaded successfully!')

    return redirect('workspace', post_pk=post_pk)


@login_required
def delete_file(request, file_pk):
    pf = get_object_or_404(ProjectFile, pk=file_pk)
    post = pf.post
    if request.method == 'POST':
        if pf.uploader == request.user or post.author == request.user:
            pf.file.delete(save=False)
            pf.delete()
            messages.success(request, 'File deleted.')
    return redirect('workspace', post_pk=post.pk)


@login_required
def milestones(request, post_pk):
    post = get_object_or_404(Post, pk=post_pk)
    return redirect('workspace', post_pk=post_pk)


@login_required
def add_milestone(request, post_pk):
    post = get_object_or_404(Post, pk=post_pk)

    is_author = post.author == request.user
    team = Team.objects.filter(post=post).first()
    is_member = team and request.user in team.members.all()
    if not (is_author or is_member):
        messages.error(request, 'Access denied.')
        return redirect('workspace', post_pk=post_pk)

    if request.method == 'POST':
        title    = request.POST.get('title', '').strip()
        due_date = request.POST.get('due_date')
        status   = request.POST.get('status', 'pending')

        if title and due_date:
            Milestone.objects.create(post=post, title=title, due_date=due_date, status=status)
            messages.success(request, 'Milestone added!')
        else:
            messages.error(request, 'Title and due date are required.')

    return redirect('workspace', post_pk=post_pk)


@login_required
def update_milestone(request, ms_pk):
    milestone = get_object_or_404(Milestone, pk=ms_pk)
    post = milestone.post
    if request.method == 'POST':
        if post.author == request.user:
            milestone.title    = request.POST.get('title', milestone.title).strip()
            milestone.due_date = request.POST.get('due_date', milestone.due_date)
            milestone.status   = request.POST.get('status', milestone.status)
            milestone.save()
            messages.success(request, 'Milestone updated!')
    return redirect('workspace', post_pk=post.pk)


@login_required
def delete_milestone(request, ms_pk):
    milestone = get_object_or_404(Milestone, pk=ms_pk)
    post = milestone.post
    if request.method == 'POST':
        if post.author == request.user:
            milestone.delete()
            messages.success(request, 'Milestone deleted.')
    return redirect('workspace', post_pk=post.pk)
