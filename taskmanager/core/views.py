from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from .models import Profile, Project, Task
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .serializers import ProjectSerializer, TaskSerializer

def signup(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        role = request.POST['role']

        user = User.objects.create_user(username=username, password=password)
        Profile.objects.create(user=user, role=role)

        return redirect('login')
    return render(request, 'signup.html')


def login_view(request):
    if request.method == 'POST':
        user = authenticate(
            username=request.POST['username'],
            password=request.POST['password']
        )
        if user:
            login(request, user)
            return redirect('dashboard')
    return render(request, 'login.html')


@login_required
def dashboard(request):
    profile = Profile.objects.get(user=request.user)

    if profile.role == 'Admin':
        projects = Project.objects.filter(created_by=request.user)
        tasks = Task.objects.all()
    else:
        projects = []
        tasks = Task.objects.filter(assigned_to=request.user)

    return render(request, 'dashboard.html', {
        'projects': projects,
        'tasks': tasks,
        'role': profile.role
    })


@login_required
def create_project(request):
    profile = Profile.objects.get(user=request.user)
    if profile.role != 'Admin':
        return redirect('dashboard')

    if request.method == 'POST':
        name = request.POST['name']
        Project.objects.create(name=name, created_by=request.user)
        return redirect('dashboard')

    return render(request, 'create_project.html')


@login_required
def create_task(request):
    profile = Profile.objects.get(user=request.user)
    if profile.role != 'Admin':
        return redirect('dashboard')

    if request.method == 'POST':
        Task.objects.create(
            title=request.POST['title'],
            project_id=request.POST['project'],
            assigned_to_id=request.POST['user']
        )
        return redirect('dashboard')

    projects = Project.objects.filter(created_by=request.user)
    users = User.objects.all()

    return render(request, 'create_task.html', {
        'projects': projects,
        'users': users
    })


@api_view(['GET'])
def api_projects(request):
    projects = Project.objects.all()
    serializer = ProjectSerializer(projects, many=True)
    return Response(serializer.data)


@api_view(['GET'])
def api_tasks(request):
    tasks = Task.objects.all()
    serializer = TaskSerializer(tasks, many=True)
    return Response(serializer.data)

@login_required
def update_task(request, task_id):
    task = Task.objects.get(id=task_id)
    task.status = "Completed"
    task.save()
    return redirect('dashboard')

def logout_view(request):
    logout(request)
    return redirect('login')