"""
This module contains Unittests for the polls application.
"""

import datetime

from django.test import TestCase
from django.utils import timezone
from django.urls import reverse

from .models import Question, User


class QuestionModelTests(TestCase):
    """Tests for Question Model to make sure that the poll is available at the right time"""
    def test_was_published_recently_with_old_question(self):
        """
        was_published_recently() returns False for questions whose pub_date
        is older than 1 day.
        """
        test = timezone.now() - datetime.timedelta(days=1, seconds=1)
        question = Question(pub_date=test)
        self.assertFalse(question.was_published_recently())

    def test_was_published_recently_with_future_question(self):
        """
        was_published_recently() returns False for questions whose pub_date
        is in the future.
        """
        time = timezone.now() + datetime.timedelta(days=30)
        future_question = Question(pub_date=time)
        self.assertIs(future_question.was_published_recently(), False)

    def test_was_published_recently_with_future_question2(self):
        """
        was_published_recently() returns False for questions whose pub_date
        is in the future (for 1 day and 1 second).
        """
        time = timezone.now() + datetime.timedelta(days=1, seconds=1)
        future_question = Question(pub_date=time)
        self.assertFalse(future_question.was_published_recently())

    def test_can_vote_no_end_date(self):
        """
        Method can_vote() returns True if the end_date attribute does not exceed or is None.
        Using questions with no end_date.
        """
        my_question = Question()
        self.assertTrue(my_question.can_vote())
        old = Question(pub_date=timezone.now()+datetime.timedelta(days=-1, seconds=1))
        self.assertTrue(old.can_vote())
        future = Question(pub_date=timezone.now()+datetime.timedelta(days=1, seconds=1))
        self.assertFalse(future.can_vote())

    def test_can_vote_end_date(self):
        """
        Method can_vote() returns True if the end_date attribute does not exceed or is None.
        Using questions with end_date.
        """
        no_vote_q = Question(pub_date=timezone.now()+datetime.timedelta(days=-30),
                             end_date=timezone.now()+datetime.timedelta(days=-1, seconds=1))
        self.assertFalse(no_vote_q.can_vote())

    def test_default_pub_date(self):
        """
        Testing when pub_date attribute was not inputted
        """
        question = Question.objects.create(question_text='default_pub')
        self.assertTrue(question.is_published())


def create_question(question_text, days):
    """
    Create a question with the given `question_text` and published the
    given number of `days` offset to now (negative for questions published
    in the past, positive for questions that have yet to be published).
    """
    time = timezone.now() + datetime.timedelta(days=days)
    return Question.objects.create(question_text=question_text, pub_date=time)


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
