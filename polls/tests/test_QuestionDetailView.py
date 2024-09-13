"""
This module contains Unittests for the polls application detail view.
"""

import datetime

from django.test import TestCase
from django.utils import timezone
from django.urls import reverse

from polls.models import Question, User

def create_question(question_text, days):
    """
    Create a question with the given `question_text` and published the
    given number of `days` offset to now (negative for questions published
    in the past, positive for questions that have yet to be published).
    """
    time = timezone.now() + datetime.timedelta(days=days)
    return Question.objects.create(question_text=question_text, pub_date=time)


class QuestionDetailViewTests(TestCase):
    """
    Ensure that a question with a future publication date returns a 404 error and
    a question with a past publication date is accessible and its text is displayed correctly.
    """

    def setUp(self):
        """Create a user and log them in."""
        self.user = User.objects.create_user(username='testuser', password='12345')
        self.client.login(username='testuser', password='12345')

    def test_past_question(self):
        """
        The detail view of a question with a pub_date in the past
        displays the question's text.
        """
        question = create_question(question_text="Past question", days=-30)
        response = self.client.get(reverse("polls:detail", args=(question.id,)))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, question.question_text)
        self.assertTemplateUsed(response, "polls/detail.html")

    def test_cannot_vote_after_end_date(self):
        """Cannot vote if the end_date is in the past."""
        pub = timezone.now() + datetime.timedelta(days=-80)
        end_t = timezone.now() - datetime.timedelta(days=1, seconds=1)  # yesterday + 1 sec
        question = Question.objects.create(question_text="Cannot vote", pub_date=pub, end_date=end_t)
        response = self.client.get(reverse("polls:detail", args=(question.id,)))
        self.assertFalse(question.can_vote())
        # redirect (does not allow seeing details of a closed poll)
        self.assertEqual(response.status_code, 302)

    def test_cannot_vote_before_pub_date(self):
        """
        The detail view of a question with a pub_date in the future
        redirects to index.
        """
        question = create_question(question_text="Future question", days=1)
        response = self.client.get(reverse("polls:detail", args=(question.id,)))
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse("polls:index"))

    def test_can_vote_with_default_pub_date(self):
        """Default pub_date can vote with no end date and with end date"""
        question = Question.objects.create(question_text="Can_vote")
        response = self.client.get(reverse("polls:detail", args=(question.id,)))
        self.assertEqual(response.status_code, 200)
        self.assertTrue(question.is_published())
        self.assertTrue(question.can_vote())


    def test_can_vote_no_end_date(self):
        """No end_date parameter was inputted but can vote"""
        question = Question.objects.create(question_text="Can_vote")
        response = self.client.get(reverse("polls:detail", args=(question.id,)))
        question2 = create_question(question_text="Can_vote2", days=-1)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(question2.can_vote())
        self.assertTrue(question.is_published())
        self.assertTrue(question.can_vote())
