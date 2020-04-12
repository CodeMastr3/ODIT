from django.shortcuts import render, HttpResponse, redirect
from django.db.models import Q #allows complex query lookups
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout
from django.core.exceptions import ObjectDoesNotExist

from . import models
from . import forms

# Create your views here.
def index(request, page=0):
	context = {
		"title":"ODIT - On Demand IT",
		"info":"A new way to find IT professionals.",
		"how":"How it works: ",
		"desc":"Send in a request --> A registered ODITer who has the skills needed receives the request --> They help out. ",
	}
   
	return render(request, "index.html", context=context)

@login_required
def submit(request):
	if request.method == "POST":
		form = forms.IssueForm(request.POST)
		if form.is_valid():
			form.save(request.user) #pass in user for foreign key relationship
			form = forms.IssueForm()
	else:
		form = forms.IssueForm()

	context = {
		"title":"ODIT - Submit Request",
		"form":form
	}
	return render(request, "submit.html", context=context)

@login_required
def viewissues(request):
	if request.method == "POST":
		form = forms.IssueFilter(request.POST)
		if form.is_valid():
			issues_list = models.Issue_Model.objects.all()
			if (form.cleaned_data['keyword']):
				issues_list = issues_list.filter(
					Q(title__contains=form.cleaned_data['keyword']) |
					Q(description__contains=form.cleaned_data['keyword']) |
					Q(assigned_user__contains=form.cleaned_data['keyword']) |
					Q(affected_user__contains=form.cleaned_data['keyword'])
				)
			if (form.cleaned_data['issue_type']):
				issues_list = issues_list.filter(
					Q(issue_type__exact=form.cleaned_data['issue_type'])
				)
		else:
			form = forms.IssueFilter()
			issues_list = models.Issue_Model.objects.all()
	else:
		form = forms.IssueFilter()
		issues_list = models.Issue_Model.objects.all()

	context = {
		"title":"ODIT - View Requests",
		"issues_list":issues_list,
		"form":form,
		"is_technician": models.Profile.objects.get(user__exact=request.user).user_type,
	}
	return render(request, "viewissues.html", context=context)

@login_required
def self_assign(request,issue_id):
	if models.Profile.objects.get(user__exact=request.user).user_type: #confirm that user is a technician
		try:
			this_issue = models.Issue_Model.objects.get(id__exact=issue_id)
			this_issue.assigned_user = request.user
			this_issue.save()
		except ObjectDoesNotExist:
			pass
	return redirect("/viewissues.html")

def about(request):
	context = {
		"title":"ODIT - About",
	}
	return render(request, "aboutodit.html", context=context)

def register(request):
    if request.method == "POST":
        form_instance = forms.RegistrationForm(request.POST)
        if form_instance.is_valid():
            form_instance.save()
            return redirect("/login/")

    else:
        form_instance = forms.RegistrationForm()
    context = {
		"title":"ODIT - Register",
        "form":form_instance,
    }
    return render(request, "registration/register.html", context=context)

def logoff(request):
	logout(request)
	return redirect("/login")

@login_required
def profile_page(request):
	this_user = models.Profile.objects.get(user__exact=request.user)
	context = {
		"title": "ODIT - {}".format(request.user.username),
		"user_name": request.user.username,
		"bio": this_user.bio,
		"email": request.user.email,
		"is_technician": this_user.user_type,
    }
	return render(request, "profile.html", context=context)

@login_required
def become_technician(request):
	try:
		this_user = models.Profile.objects.get(user__exact=request.user)
		this_user.user_type = True
		this_user.save()
	except ObjectDoesNotExist:
		pass
	return redirect("/profile.html")
