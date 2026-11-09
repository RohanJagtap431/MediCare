
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect


def user_login(request):

    if request.user.is_authenticated:
        return redirect("dashboard:dashboard")

    if request.method == "POST":

        username = request.POST.get("username", "").strip()
        password = request.POST.get("password", "")

        if not username or not password:
            messages.error(request, "Please enter username and password.")

        else:
            user = authenticate(
                request,
                username=username,
                password=password
            )

            if user is not None:
                if not user.is_active:
                    messages.error(request, "Your account is inactive.")
                else:
                    login(request, user)
                    messages.success(request, "Login successful!")

                    next_url = request.GET.get("next") or request.POST.get("next")

                    if next_url and next_url.startswith("/") and not next_url.startswith("//"):
                        return redirect(next_url)

                    return redirect("dashboard:dashboard")

            else:
                messages.error(request, "Invalid username or password.")

    return render(request, "accounts/login.html")


@login_required
def user_logout(request):

    if request.method == "POST":
        logout(request)
        messages.success(request, "You have been logged out.")
        return redirect("accounts:login")

    return redirect("dashboard:dashboard")
