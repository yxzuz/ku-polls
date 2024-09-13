"""
This module contains Unittests for the polls application Question Model.
"""

import datetime

from django.test import TestCase
from django.utils import timezone

from polls.models import Question


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
