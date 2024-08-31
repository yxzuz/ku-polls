"""
This module contains the models: Question and Choice for the polls application.
"""

import datetime

from django.db import models
from django.utils import timezone


class Question(models.Model):
    """Question Model has two attributes: question_text, pub_date and end_date"""
    question_text = models.CharField(max_length=200)
    pub_date = models.DateTimeField("date published", default=timezone.now)
    end_date = models.DateTimeField("end date", null=True, blank=True)

    def is_published(self):
        """
        Returns True if the current date-time is on
        or after question’s publication date by using local date/time.
        """
        return timezone.localtime(timezone.now()) >= self.pub_date

    def can_vote(self):
        """
        Returns True if voting is allowed for this question.
        That means, the current date/time is between the pub_date and end_date.
        If end_date is null then can vote anytime after pub_date.
        """
        if self.end_date is not None:
            return self.pub_date <= timezone.now() <= self.end_date
        return self.end_date is None


    def was_published_recently(self):
        """
        Check whether the publication date is within 24 hrs
        Return Boolean
        """
        return timezone.now() - datetime.timedelta(days=1) <= self.pub_date <= timezone.now()

    def __str__(self):
        """Return string representation of Question's model"""
        return str(self.question_text) if self.question_text is not None else ''


class Choice(models.Model):
    """Choice model has three attributes: question, choice_text, and votes"""
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    choice_text = models.CharField(max_length=200)
    votes = models.IntegerField(default=0)

    def __str__(self):
        """Return string representation of Choice's model"""
        return str(self.choice_text) if self.choice_text is not None else ''
