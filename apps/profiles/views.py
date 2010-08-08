from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import render_to_response
from datetime import datetime, timedelta
from django.contrib.auth.models import User
from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext
from django.views.generic.simple import direct_to_template
from schedule.models import Event

from profiles.models import *
from profiles.forms import ProfileForm, ProfileSkillsForm
from django.contrib.auth.decorators import login_required
from django.utils import simplejson

def userprofile(request, username=None, template_name='profiles/profile.html'):
    form = ProfileForm()
    return render_to_response(template_name, locals(),
                              context_instance=RequestContext(request))

def ajax_view(request, profile_id, skill_id, verb):
    datadict = {'profile_id':profile_id, 'skill_id':skill_id, 'verb':verb}
    profile = Profile.objects.get(id = profile_id)
    skill = Skill.objects.get(id = skill_id)
    if verb == "remove":
        try:
            profile.skills.remove(skill)
        except Exception, e:
            datadict['status'] = "failure"
        else:
            datadict['status'] = "success"
        return HttpResponse(simplejson.dumps(datadict))
    else:
        return HttpResponse("verb unrecognized")

def _can_view_full_profile(user):
    # for now just check if user is logged in, later there may be karma and/or
    # other requirements.
    return user.is_authenticated()

def list_profiles(request, template_name='profiles/list_profiles.html'):
    users = User.objects.all()
    return render_to_response(template_name, locals(),
                              context_instance=RequestContext(request))

def view_profile(request, username, template_name='profiles/view_profile.html'):
    user = get_object_or_404(User, username=username)
    display_full_profile = _can_view_full_profile(request.user)
    events = Event.objects.filter(creator=user)
    start = datetime.now()
    end = start + timedelta(days=7)
    office_hours = reduce(lambda x,y: x+y, [e.get_occurrences(start, end)
                                            for e in events]) if events else []
    return render_to_response(template_name, locals(),
                              context_instance=RequestContext(request))


@login_required
def profile(request):
    user = request.user
    profile = user.profile
    if request.method == "POST":
        tag_list = request.POST.get('skills_text').split(',')
        for tag in tag_list:
            if tag and tag != '':
                skill, created = Skill.objects.get_or_create(name=tag)
                profile.skills.add(skill)
        psf = ProfileSkillsForm(request.POST)
        if psf.is_valid():
            skills_list = Skill.objects.filter(id__in = psf.cleaned_data.get('skills'))
            for skill in skills_list:
                profile.skills.add(skill)
        profile.save()
    profile_form = ProfileForm()
    skill_form = ProfileSkillsForm()
    skills = profile.skills.all()
    return direct_to_template(request, 'profiles/skills_test.html', 
                                        {'skill_form':skill_form,
                                         'profile_form':profile_form,
                                         'profile':profile,
                                         'skills':skills})