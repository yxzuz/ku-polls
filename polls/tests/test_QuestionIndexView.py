"""
This module contains Unittests for the polls application Index view.
"""

import datetime

from django.test import TestCase
from django.utils import timezone
from django.urls import reverse

from polls.models import Question, User


class QuestionIndexViewTests(TestCase):
    """Test to check the poll with client environment (no record yet)"""
    def test_no_questions(self):
        """
        If no questions exist, an appropriate message is displayed.
        """
        response = self.client.get(reverse("polls:index"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "No polls are available.")
        self.assertQuerySetEqual(response.context["latest_question_list"], [])

    def test_past_question(self):
        """
        Questions with a pub_date in the past are displayed on the
        index page.
        """
        question = create_question("Past Question", days=-30)
        response = self.client.get(reverse("polls:index"))
        self.assertQuerySetEqual(response.context["latest_question_list"], [question])
        self.assertTrue(question.is_published())

    def test_future_question(self):
        """
        Questions with a pub_date in the future aren't displayed on
        the index page.
        """
        question = create_question("Future Question", days=30)
        response = self.client.get(reverse("polls:index"))
        self.assertQuerySetEqual(response.context["latest_question_list"], [])

    def test_future_question_and_past_question(self):
        """
        Even if both past and future questions exist, only past questions
        are displayed.
        """
        question = create_question("Past Question", days=-1)
        question2 = create_question("Future Question", days=2)
        response = self.client.get(reverse("polls:index"))
        self.assertQuerySetEqual(response.context["latest_question_list"], [question])

    def test_two_past_questions(self):
        """
        The questions index page may display multiple questions.
        """
        question1 = create_question(question_text="Past question 1.", days=-30)
        question2 = create_question(question_text="Past question 2.", days=-5)
        response = self.client.get(reverse("polls:index"))
        self.assertQuerySetEqual(
            response.context["latest_question_list"],
            [question2, question1],
        )
    def test_future_question2(self):
        """
        question with future pub date with is_published method
        """
        question = create_question(question_text="Future", days=1)
        self.assertFalse(question.is_published())
        response = self.client.get(reverse('polls:index'))
        time = timezone.now() + datetime.timedelta(days=1, seconds=1)
        question2 = Question(question_text="",pub_date=time)
        self.assertNotContains(response, [question.question_text,question2.question_text])

def create_question(question_text, days):
    """
    Create a question with the given `question_text` and published the
    given number of `days` offset to now (negative for questions published
    in the past, positive for questions that have yet to be published).
    """
    time = timezone.now() + datetime.timedelta(days=days)
    return Question.objects.create(question_text=question_text, pub_date=time)
