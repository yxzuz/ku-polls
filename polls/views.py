"""This module contains views of polls app"""

import logging
from django.http import HttpResponseRedirect
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse
from django.views import generic
from django.utils import timezone
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.signals import user_logged_in, user_logged_out, user_login_failed
from django.dispatch import receiver

from .models import Question, Choice, Vote

logger = logging.getLogger(__name__)
def get_client_ip(request):
    """Get the visitor’s IP address using request headers."""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip

@receiver(user_logged_in)
def log_user_login(sender, request, user, **kwargs):
    """Log information when a user logs in."""
    logger.info(f"User: {user.username} successfully login from IP address {get_client_ip(request)}")

@receiver(user_logged_out)
def log_user_logout(sender, request, user, **kwargs):
    """Log information when a user logs out."""
    logger.info(f"User: {user.username} logout from IP address {get_client_ip(request)}")

@receiver((user_login_failed))
def log_user_login_failed(sender,credentials, request, **kwargs):
    """Log gives warning when user attempts to log in but failed."""
    logger.warning(f"Failed login attempt for user: {credentials.get('username')} from IP address {get_client_ip(request)}")

class IndexView(generic.ListView):
    """Take request to index.html which displays all questions."""
    template_name = "polls/index.html"
    # originally, the context name would be question_list
    context_object_name = "latest_question_list"

    def get_queryset(self):
        """
        Return the last five published questions
        (not including those set to be published in the future).
        """
        return Question.objects.filter(pub_date__lte=timezone.now()).order_by("-pub_date")[:5]


class DetailView(generic.DetailView):
    """
    Display the choices for a poll and allow voting
    """
    model = Question
    template_name = "polls/detail.html"
    # context var is question

    def get_queryset(self):
        """
        Excludes any questions that aren't published yet.
        """
        return Question.objects.filter(pub_date__lte=timezone.now())

    def get(self, request, *args, **kwargs):
        """
        Override get method from generic view to can_vote
        and is_published condition.Then redirect it to index
        if it's necessary
        """
        question = self.get_object()
        if not question.can_vote():
            messages.warning(request, "This poll is already closed.")
            return redirect(reverse("polls:index"))
        if not question.is_published():
            messages.warning(request, 'This poll is not available.')
            return redirect(reverse("polls:index"))
        return super(DetailView, self).get(request, *args, **kwargs)  # render the page


class ResultsView(generic.DetailView):
    """
    Take request to results.html
    which displays results for a particular question.
    """
    model = Question
    template_name = "polls/results.html"
    # context var is question


@login_required
def vote(request, question_id):
    """Handles voting for a particular choice in a particular question."""
    question = get_object_or_404(Question, pk=question_id)

    try:
        # find the selected choice from form
        # in polls/templates/polls/detail.html
        selected_choice = question.choice_set.get(pk=request.POST['choice'])
        logger.info(f"User {request.user} voted for choice id:{request.POST['choice']} in polls {question_id}")
    except (KeyError, Choice.DoesNotExist):  # didn't pick any
        # Redisplay the question voting form
        # and inform that they didn't select the choice
        context = {
                "question": question,
                "error_message": "You didn't select a choice.",
            }
        # when they search for templates, they already in template dir
        # only let them vote by some conditions
        logger.exception(f"Invalid question id:{question_id} or choice not selected for user: {request.user}")
        return render(request, "polls/detail.html", context)

    # Reference to the current user
    my_user = request.user

    # Get the user's vote
    try:
        vote = Vote.objects.get(user=my_user, choice__question=question)
        # user alr has a vote for this question!Update his choice.
        # check if select same choice mai???
        if vote.choice.pk != selected_choice.pk:
            vote.choice = selected_choice
            vote.save()
            messages.success(request, f"Your vote was changed to {selected_choice.choice_text}")
    except Vote.DoesNotExist:
        # does not have a vote yet
        # automatically saved
        Vote.objects.create(user=my_user, choice=selected_choice)
        messages.success(request, f"You voted for {selected_choice.choice_text}")

    # After voted redirects to the "results" page for the question
    return HttpResponseRedirect(reverse("polls:results", args=(question.id,)))
