from django.shortcuts import render, redirect
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from shop_chat.forms import ChatUserCreationForm


@login_required
def chat_index_page(request, room_name):
    return render(request, 'chat_room.html', {'room_name': room_name})


def register(request):
    form = ChatUserCreationForm()
    if request.method == 'POST':
        form = ChatUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('chat_page', room_name='initial_room')

    return render(request, 'registartion/register.html', {'form': form})
