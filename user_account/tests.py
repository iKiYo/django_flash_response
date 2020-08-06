from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm
from django.test import TestCase, SimpleTestCase, Client
from django.urls import reverse, resolve

from .views import SignupPageView, DashboardView


class CustomUserTests(TestCase):

    def test_create_user(self):
        User = get_user_model()
        user = User.objects.create_user(
            username = 'Ken',
            email = 'ken@email.com',
            password = 'testpass123'
        )
        self.assertEqual(user.username, 'Ken')
        self.assertEqual(user.email, 'ken@email.com')
        self.assertTrue(user.is_active)
        self.assertFalse(user.is_staff)
        self.assertFalse(user.is_superuser)


    def test_create_superuser(self):

        User = get_user_model()
        superuser = User.objects.create_superuser(
            username = 'superadmin',
            email = 'superadmin@email.com',
            password = 'testpass123'
        )
        self.assertEqual(superuser.username, 'superadmin')
        self.assertEqual(superuser.email, 'superadmin@email.com')
        self.assertTrue(superuser.is_active)
        self.assertTrue(superuser.is_staff)
        self.assertTrue(superuser.is_superuser)
        


class SignupPageTest(SimpleTestCase):

    username = 'newuser'
    email = 'newuser@email.com'

    def setUp(self):
        url = reverse('signup')
        self.response = self.client.get(url)


    def test_signup_template(self):
        self.assertEqual(self.response.status_code, 200)
        self.assertTemplateUsed(self.response, 'signup.html')
        self.assertContains(self.response, 'Sign Up')
        self.assertNotContains(self.response, 'Sign In')

    def test_signup_form(self):
        form = self.response.context.get('form')
        self.assertIsInstance(form, UserCreationForm)
        self.assertContains(self.response, 'csrfmiddlewaretoken')

        
    def test_signup_view(self):
        view = resolve('/accounts/signup/')
        self.assertEqual(
            view.func.__name__,
            SignupPageView.as_view().__name__
        )

        
class DashboardPageTest(TestCase):
    
    def setUp(self):        
        url = reverse('dashboard')

        # anonymous user
        self.response = self.client.get(url)

        # logged in user
        user = get_user_model().objects.create_user(username = 'testuser')
        user.set_password('testpass123')
        user.save()
        self.client.login(username='testuser', password='testpass123')
        self.logged_in_response = self.client.get(url)        
        
        
    def test_dashboard_template(self):
        # anonymous user
        self.assertEqual(self.response.status_code, 200)
        self.assertTemplateUsed(self.response, 'dashboard.html')
        self.assertContains(self.response, 'Guest User')
        self.assertContains(self.response, 'Sign Up')
        self.assertContains(self.response, 'Log In')
        self.assertNotContains(self.response, 'Log Out')
        self.assertNotContains(self.response, 'Dashboard')
        self.assertNotContains(self.response, 'パスワード変更')

        # check logged in properly
        self.assertEqual(self.logged_in_response.status_code, 200)
        self.assertTemplateUsed(self.logged_in_response, 'dashboard.html')
        self.assertContains(self.logged_in_response, 'testuser')
        self.assertContains(self.logged_in_response, 'Log Out')
        self.assertContains(self.logged_in_response, 'Dashboard')
        self.assertNotContains(self.logged_in_response, 'Sign Up')
        self.assertNotContains(self.logged_in_response, 'Log In')

        
    def test_dashboard_view(self):
        view = resolve('/accounts/')
        self.assertEqual(
            view.func.__name__,
            DashboardView.as_view().__name__
        )
