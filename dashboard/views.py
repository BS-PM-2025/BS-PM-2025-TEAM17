from django.shortcuts import render, redirect
from django.contrib.auth import get_user_model
from django.contrib import messages

User = get_user_model()

#custme dashboard : done 
def dashboard(request):
    if request.user.is_superuser:
        users = User.objects.exclude(id=request.user.id)  # exclude self from list

        # Handle deletion
        if request.method == 'POST' and 'delete_user_id' in request.POST:
            user_id = request.POST.get('delete_user_id')
            try:
                user = User.objects.get(id=user_id)
                user.delete()
                messages.success(request, 'User deleted successfully.')
            except User.DoesNotExist:
                messages.error(request, 'User not found.')
            return redirect('dashboard')

        # Handle role update
        if request.method == 'POST' and 'update_user_id' in request.POST:
            user_id = request.POST.get('update_user_id')
            new_role = request.POST.get('role')
            try:
                user = User.objects.get(id=user_id)
                user.is_student = new_role == 'student'
                user.is_lect = new_role == 'lecturer'
                user.is_superuser = new_role == 'superuser'
                user.save()
                messages.success(request, 'User role updated.')
            except User.DoesNotExist:
                messages.error(request, 'User not found.')
            return redirect('dashboard')

        return render(request, 'dashboard/dashboard.html', {'users': users})

    return render(request, 'dashboard/dashboard.html')
