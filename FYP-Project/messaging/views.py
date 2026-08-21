from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q

from .models import Message, Block
from accounts.models import Profile


@login_required
def inbox(request):
    sent     = Message.objects.filter(sender=request.user).values_list('receiver', flat=True)
    received = Message.objects.filter(receiver=request.user).values_list('sender', flat=True)
    user_ids = set(list(sent) + list(received))
    contacts = User.objects.filter(id__in=user_ids)

    contacts_data = []
    for c in contacts:
        unread = Message.objects.filter(
            sender=c, receiver=request.user, is_read=False
        ).count()
        contacts_data.append((c, unread))

    return render(request, 'messaging/messages_inbox.html', {
        'contacts_data': contacts_data,
    })


@login_required
def chat(request, username):
    other_user = get_object_or_404(User, username=username)

    is_blocked = Block.objects.filter(blocker=request.user, blocked=other_user).exists()
    has_blocked_me = Block.objects.filter(blocker=other_user, blocked=request.user).exists()

    Message.objects.filter(
        sender=other_user, receiver=request.user, is_read=False
    ).update(is_read=True)

    messages_qs = Message.objects.filter(
        sender__in=[request.user, other_user],
        receiver__in=[request.user, other_user]
    ).order_by('sent_at')

    other_profile, created = Profile.objects.get_or_create(user=other_user)

    return render(request, 'messaging/chat.html', {
        'other_user':     other_user,
        'messages':       messages_qs,
        'other_profile':  other_profile,
        'is_blocked':     is_blocked,
        'has_blocked_me': has_blocked_me,
    })


@login_required
def send_message(request):
    if request.method == 'POST':
        receiver_username = request.POST.get('receiver')
        content           = request.POST.get('content', '').strip()
        attachment        = request.FILES.get('attachment')

        if content or attachment:
            receiver = get_object_or_404(User, username=receiver_username)

            is_blocked = Block.objects.filter(blocker=request.user, blocked=receiver).exists()
            has_blocked_me = Block.objects.filter(blocker=receiver, blocked=request.user).exists()

            if is_blocked or has_blocked_me:
                messages.error(request, 'Cannot send message. A block is in place.')
                return redirect('chat', username=receiver_username)

            Message.objects.create(
                sender=request.user,
                receiver=receiver,
                content=content,
                attachment=attachment,
            )
        return redirect('chat', username=receiver_username)
    return redirect('inbox')


@login_required
def toggle_block(request, username):
    if request.method == 'POST':
        other_user = get_object_or_404(User, username=username)
        block_obj = Block.objects.filter(blocker=request.user, blocked=other_user).first()
        if block_obj:
            block_obj.delete()
            messages.success(request, f'You have unblocked {other_user.username}.')
        else:
            Block.objects.create(blocker=request.user, blocked=other_user)
            messages.success(request, f'You have blocked {other_user.username}.')
    return redirect('chat', username=username)
