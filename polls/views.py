
from django.http import HttpResponse
from django.shortcuts import render, get_object_or_404

from .models import Question

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
    response = "You're looking at the results of question %s."
    return HttpResponse(response % question_id)

def vote(request, question_id):
    """handles voting for a particular choice in a particular question."""
    return HttpResponse("You're voting on question %s." % question_id)