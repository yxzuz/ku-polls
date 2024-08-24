from django.db.models import F
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, get_object_or_404
from django.urls import reverse

from .models import Question, Choice

def index(request):
    """displays the latest few questions."""
    latest_question_list = Question.objects.order_by("-pub_date")[:5]
    # output = ", ".join([q.question_text for q in latest_question_list])
    context = {"latest_question_list": latest_question_list}
    return render(request, "polls/index.html", context)

def detail(request, question_id):
    """displays a question text, with no results but with a form to vote"""

    # try:
    #     question = Question.objects.get(pk=question_id)
    # except:  # error
    #     raise Http404("The Question does not exist")
    question = get_object_or_404(Question, pk=question_id)
    return render(request, "polls/detail.html", {"question": question})

def results(request, question_id):
    """displays results for a particular question."""
    question = get_object_or_404(Question, pk=question_id)

    return render(request, "polls/results.html",{"question": question})

def vote(request, question_id):
    """handles voting for a particular choice in a particular question."""
    question = get_object_or_404(Question, pk=question_id)
    try:
        # find the selected choice from form in polls/templates/polls/detail.html
        selected_choice = question.choice_set.get(pk=request.POST['choice'])
    except (KeyError, Choice.DoesNotExist):  # didn't pick any
        # Redisplay the question voting form and inform that they didn't select the choice
        context = {
                "question": question,
                "error_message": "You didn't select a choice.",
            }
        # when they search for templates they alr in template dir
        return render(request, "polls/detail.html", context)
    else:
        selected_choice.votes = F("votes") + 1  # add the vote to database
        selected_choice.save()
        # Always return an HttpResponseRedirect after successfully dealing
        # with POST data.This prevents data from being posted twice if a
        # user hits the Back button.

        # After voted redirects to the results page for the question
        return HttpResponseRedirect(reverse("polls:results", args=(question.id,)))