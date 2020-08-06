from django.test import SimpleTestCase, TestCase
from django.urls import reverse, resolve

from .views import (
    HomePageView, ExerciseView
)

# for selenium tests
from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from selenium import webdriver
from selenium.webdriver.firefox.options import Options


class HomePageTests(SimpleTestCase):

    def setUp(self):
        url = reverse('home')
        self.response = self.client.get(url)

    def test_homepage_template(self):
        self.assertEqual(self.response.status_code, 200)
        self.assertTemplateUsed(self.response, 'home.html')
        self.assertContains(self.response, 'Sign Up')
        self.assertNotContains(self.response, 'Log Out')

    def test_homepage_view(self):
        view = resolve('/')
        self.assertEqual(
            view.func.__name__,
            HomePageView.as_view().__name__
        )


class ExercisePageTests(TestCase):

    def setUp(self):
        url = reverse('exercise')
        self.response = self.client.get(url)
        # Todo: fix warning
        print('WARNING in exercise view test')

    def test_exercise_template(self):
        self.assertEqual(self.response.status_code, 200)
        self.assertTemplateUsed(self.response, 'exercise.html')
        self.assertContains(self.response, 'Sign Up')
        self.assertNotContains(self.response, 'Log Out')

    def test_exercise_view(self):
        view = resolve('/exercise')
        self.assertEqual(
            view.func.__name__,
            ExerciseView.as_view().__name__
        )
