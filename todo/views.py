from django.shortcuts import render, get_object_or_404
from django.views.decorators.http import require_http_methods
from django.http import HttpResponse, QueryDict
from .models import Todo
from .forms import TodoForm

def todo_list(request):
    todos = Todo.objects.all()
    form = TodoForm()
    return render(request, 'todo/todo_list.html', {'todos': todos, 'form': form})

@require_http_methods(['POST'])
def add_todo(request):
    form = TodoForm(request.POST)
    if form.is_valid():
        todo = form.save()
        return render(request, 'todo/partials/todo_item.html', {'todo': todo})
    return HttpResponse('')

@require_http_methods(['PUT'])
def toggle_todo(request, pk):
    todo = get_object_or_404(Todo, pk=pk)
    todo.toggle()
    return render(request, 'todo/partials/todo_item.html', {'todo': todo})

@require_http_methods(['GET'])
def edit_todo(request, pk):
    todo = get_object_or_404(Todo, pk=pk)
    form = TodoForm(instance=todo)
    return render(request, 'todo/partials/todo_edit.html', {'todo': todo, 'form': form})

@require_http_methods(['GET'])
def cancel_edit(request, pk):
    todo = get_object_or_404(Todo, pk=pk)
    return render(request, 'todo/partials/todo_item.html', {'todo': todo})

@require_http_methods(['PUT'])
def update_todo(request, pk):
    todo = get_object_or_404(Todo, pk=pk)
    # Parse PUT data
    put_data = QueryDict(request.body)
    form = TodoForm(put_data, instance=todo)
    if form.is_valid():
        form.save()
        return render(request, 'todo/partials/todo_item.html', {'todo': todo})
    return render(request, 'todo/partials/todo_edit.html', {'todo': todo, 'form': form})

@require_http_methods(['DELETE'])
def delete_todo(request, pk):
    todo = get_object_or_404(Todo, pk=pk)
    todo.delete()
    return HttpResponse('')
