"""
This module contains the models: Question and Choice for the polls application.
"""

import datetime

from django.db import models
from django.utils import timezone


class Question(models.Model):
    """Question Model has two attributes: question_text, pub_date"""
    question_text = models.CharField(max_length=200)
    pub_date = models.DateTimeField("date published")

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
