from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from .forms import LoginForm, SignUpForm, NotesheetForm
from django.contrib.auth import get_user_model
from django import template
from .forms import NotesheetForm
from .models import profile, notesheet
from .utils import find_next_reviewer
from django.http import HttpResponseRedirect
from .models import profile, notesheet, Review
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, HttpResponseRedirect
from django.template import loader
from django.urls import reverse
from django.contrib.auth.models import User

def login_view(request):
    form = LoginForm(request.POST or None)
    msg = None

    if request.method == "POST":
        if form.is_valid():
            email = form.cleaned_data.get("email")
            password = form.cleaned_data.get("password")

            # Get the user model dynamically
            User = get_user_model()

            try:
                user = User.objects.get(email=email)
            except User.DoesNotExist:
                user = None

            if user is not None and user.check_password(password):
                login(request, user)
                return redirect("/")
            else:
                msg = 'Invalid credentials'
        else:
            msg = 'Error validating the form'

    return render(request, "accounts/login.html", {"form": form, "msg": msg})

def register_user(request):
    msg = None
    success = False

    if request.method == "POST":
        form = SignUpForm(request.POST)
        if form.is_valid():
            form.save()
            first_name = form.cleaned_data.get("first_name")
            last_name = form.cleaned_data.get("last_name")
            username = form.cleaned_data.get("username")
            raw_password = form.cleaned_data.get("password1")
            user = authenticate(username=username, password=raw_password)

            # Set the first name and last name for the user
            user.first_name = first_name
            user.last_name = last_name
            user.save()

            msg = 'User created - please <a href="/login">login</a>.'
            success = True

            # return redirect("/login/")

        else:
            msg = 'Form is not valid'
    else:
        form = SignUpForm()

    return render(request, "accounts/register.html", {"form": form, "msg": msg, "success": success})



@login_required(login_url="/login/")
def create_notesheet(request):
    if request.method == 'POST':
        form = NotesheetForm(request.POST, user=request.user)
        if form.is_valid():
            notesheet_instance = form.save(commit=False)

            # If current reviewer is not set, set it based on selected channels
            if not notesheet_instance.current_reviewer:
                selected_channels = form.cleaned_data['channels']
                if selected_channels:
                    notesheet_instance.current_reviewer = selected_channels[0]

            notesheet_instance.save()  # Save the notesheet to generate an ID

            # Clear existing channels
            notesheet_instance.channels.clear()

            # Add the selected channels
            selected_channels = form.cleaned_data['channels']
            notesheet_instance.channels.add(*selected_channels)

            print(notesheet_instance.channels.all())
            print(notesheet_instance.current_reviewer)  # Check if current_reviewer is set

            return redirect('progress_page')
    else:
        user_profile = profile.objects.get(user=request.user)
        initial_data = {
            'name': request.user.username,
            'faculty': user_profile.faculty,
            'department': user_profile.department
        }
        form = NotesheetForm(initial=initial_data, user=request.user)
    return render(request, "home/create.html", {'form': form})


@login_required(login_url="/login/")
def review_notesheet(request, notesheet_id):
    notesheets = notesheet.objects.get(pk=notesheet_id)

    # Check if the user is the current reviewer for this notesheet
    if request.user == notesheets.current_reviewer:
        if request.method == 'POST':
            status = request.POST.get('status')
            comment = request.POST.get('comment')
            review = Review(Notesheet=notesheets, reviewer=request.user, status=status, comment=comment)
            review.save()

            # If the current reviewer accepted the notesheet, find the next reviewer
            if status == 'accepted':
                next_reviewer = find_next_reviewer(notesheets)
                notesheets.current_reviewer = next_reviewer
                notesheets.save()

            # Redirect the user to the "Pending Page"
            return redirect('pending_page')

        return render(request, 'home/review_notesheet.html', {'notesheet': notesheets})
    else:
        return redirect('pending_page')

def find_next_reviewer(notesheets):
    # Assuming channels is a ManyToManyField in the Notesheet model
    channels = notesheets.channels.all()

    current_reviewer_index = -1
    for i, channel in enumerate(channels):
        if channel == notesheets.current_reviewer:
            current_reviewer_index = i
            break

    next_reviewer_index = (current_reviewer_index + 1) % len(channels)
    return channels[next_reviewer_index]


@login_required(login_url="/login/")
def pending_page(request):
    notesheets = notesheet.objects.filter(channels=request.user)
    return render(request, 'home/pending_work.html', {'notesheets': notesheets})


@login_required(login_url="/login/")
def progress_page(request):
    user_name = request.user.username
    user_notesheets = notesheet.objects.filter(name=user_name)

    notesheet_status = {}

    for ns in user_notesheets:
        reviews = Review.objects.filter(Notesheet=ns)
        if reviews.exists():
            accepted_reviews = reviews.filter(status='accepted')
            rejected_reviews = reviews.filter(status='rejected')

            if accepted_reviews.count() == reviews.count():
                status = 'accepted'
            elif rejected_reviews.count() > 0:
                status = 'rejected'
            else:
                status = 'pending'

            latest_review = reviews.latest('id')  # Get the latest review
            reviewer = latest_review.reviewer
            action = 'accepted' if latest_review.status == 'accepted' else 'rejected'
            comment = latest_review.comment
        else:
            status = 'pending'
            reviewer = ''
            action = ''
            comment = ''

        notesheet_status[ns] = {'status': status, 'reviewer': reviewer, 'action': action, 'comment': comment}

    return render(request, 'home/progress_page.html', {'notesheet_status': notesheet_status})

    
def no_notesheet(request):
    return render(request, 'home/no_notesheet.html')

@login_required(login_url="/login/")
def index(request):
    context = {'segment': 'index'}

    html_template = loader.get_template('home/index.html')
    return HttpResponse(html_template.render(context, request))

@login_required(login_url="/login/")
def pages(request):
    context = {}
    # All resource paths end in .html.
    # Pick out the html file name from the URL. And load that template.
    try:
        load_template = request.path.split('/')[-1]

        if load_template == 'admin':
            return HttpResponseRedirect(reverse('admin:index'))
        context['segment'] = load_template

        html_template = loader.get_template('home/' + load_template)
        return HttpResponse(html_template.render(context, request))

    except template.TemplateDoesNotExist:

        html_template = loader.get_template('home/page-404.html')
        return HttpResponse(html_template.render(context, request))

    except:
        html_template = loader.get_template('home/page-500.html')
        return HttpResponse(html_template.render(context, request))
