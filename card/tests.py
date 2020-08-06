from django.contrib.auth import get_user_model
from django.test import SimpleTestCase, TestCase
from django.urls import reverse, resolve
from django.utils import timezone

from .views import (
    CardImport, UploadSuccessedView,
    CardCreateView, CardUpdateView, CardListView,
    CardDetailView, CardDeleteView
)
from .models import Card

# for selenium tests
from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from selenium import webdriver
from selenium.webdriver.firefox.options import Options


class SeleinumFunctionalTests(StaticLiveServerTestCase):
    fixtures = ['user_account/fixtures/custom_users.json',
                'card/fixtures/test_cards.json',
    ]

    # def setUp(self):
    #     # register a user for log in
    #     user = get_user_model().objects.create_user(username='testuser')
    #     user.set_password('testpass123')
    #     user.save()

    @classmethod
    def setUpClass(cls):
        # initiate driver in headless mode
        super().setUpClass()
        options = Options()
        options.headless = True
        cls.selenium = webdriver.Firefox(options=options)
        cls.selenium.implicitly_wait(5)

    @classmethod
    def tearDownClass(cls):
        cls.selenium.quit()
        super().tearDownClass()

    def test_login(self):
        self.selenium.get('%s%s' % (self.live_server_url, '/accounts/login/'))
        username_input = self.selenium.find_element_by_name("username")
        username_input.send_keys('testuser')
        password_input = self.selenium.find_element_by_name("password")
        password_input.send_keys('testpass123')
        self.selenium.save_screenshot('test-results/put_uname_pswd.png')
        self.selenium.find_element_by_id(
            'login_button').click()
        self.selenium.implicitly_wait(3)
        self.selenium.save_screenshot('test-results/dash_board.png')

    # Todo: complete
    # def test_upload_audio_asynchronous_task(self):
    #     self.selenium.get('%s%s' % (self.live_server_url, '/accounts/login/'))
    #     username_input = self.selenium.find_element_by_name("username")
    #     username_input.send_keys('testuser')
    #     password_input = self.selenium.find_element_by_name("password")
    #     password_input.send_keys('testpass123')
    #     self.selenium.get('%s%s' % (self.live_server_url, '/card_upload'))
    #     file_upload = self.selenium.find_element_by_xpath('/html/body/main/div/div/form/li/label').click()
    #     file_upload.send_keys(mini_questions_set.csv)
    #     self.selenium.implicitly_wait(3)
    #     start_upload = self.selenium.find_element_by_id('start_upload').click()
    #     self.selenium.implicitly_wait(3)


class CardImportPageTests(TestCase):

    def setUp(self):
        url = reverse('card_upload')
        self.response = self.client.get(url)

    def test_template(self):
        self.assertEqual(self.response.status_code, 200)
        self.assertTemplateUsed(self.response, 'card_upload.html')
        self.assertContains(self.response, '自作問題')
        self.assertNotContains(self.response, 'Log Out')

    def test_view(self):
        view = resolve('/card_upload')
        self.assertEqual(
            view.func.__name__,
            CardImport.as_view().__name__
        )


class CardNewPageTests(TestCase):

    def setUp(self):
        url = reverse('card_new')

        # anonymous user
        self.response = self.client.get(url)
        # logged in user
        user = get_user_model().objects.create_user(username='testuser')
        user.set_password('testpass123')
        user.save()
        self.client.login(username='testuser', password='testpass123')
        self.logged_in_response = self.client.get(url)

    def test_template(self):
        # redirect to login page for a user not logged in
        self.assertEqual(self.response.status_code, 302)

        # check logged in properly
        self.assertEqual(self.logged_in_response.status_code, 200)

        self.assertTemplateUsed(self.logged_in_response, 'card_new.html')
        self.assertContains(self.logged_in_response, 'testuser')
        self.assertContains(self.logged_in_response, 'Log Out')
        self.assertContains(self.logged_in_response, 'Dashboard')
        self.assertNotContains(self.logged_in_response, 'Sign Up')
        self.assertNotContains(self.logged_in_response, 'Log In')

    def test_view(self):
        view = resolve('/card_new')
        self.assertEqual(
            view.func.__name__,
            CardCreateView.as_view().__name__
        )


class CardListPageTests(TestCase):

    def setUp(self):
        url = reverse('card_list')

        # anonymous user
        self.response = self.client.get(url)
        # logged in user
        user = get_user_model().objects.create_user(username='testuser')
        user.set_password('testpass123')
        user.save()
        self.client.login(username='testuser', password='testpass123')
        self.logged_in_response = self.client.get(url)

    def test_template(self):
        # redirect to login page for a user not logged in
        self.assertEqual(self.response.status_code, 200)
        self.assertTemplateUsed(self.response, 'card_list.html')
        self.assertContains(self.response, 'Guest User')
        self.assertContains(self.response, 'Log In')
        self.assertNotContains(self.response, 'Log Out')

        # check logged in properly
        self.assertEqual(self.logged_in_response.status_code, 200)
        self.assertTemplateUsed(self.logged_in_response, 'card_list.html')
        self.assertContains(self.logged_in_response, 'testuser')
        self.assertContains(self.logged_in_response, 'Log Out')
        self.assertNotContains(self.logged_in_response, 'Log In')

    def test_view(self):
        view = resolve('/card_list')
        self.assertEqual(
            view.func.__name__,
            CardListView.as_view().__name__
        )


class CardDetailPageTests(TestCase):

    def setUp(self):
        # make test user
        user = get_user_model().objects.create_user(username='testuser')
        user.set_password('testpass123')
        user.save()

        # make test card
        card = Card.objects.create(
            card_creator=user,
            title='test_Q',
            question_text='テスト',
            answer_text='test',
            category='テストカテゴリ',
            subcategory='テストサブカテゴリ',
            detail='テスト詳細',
            literary_style=True,
            creation_date=timezone.now(),
        )
        card.save()
        self.url = reverse('card_detail', args=(card.card_id,))

        # anonymous user
        self.response = self.client.get(self.url)
        # logged in user
        self.client.login(username='testuser', password='testpass123')
        self.logged_in_response = self.client.get(self.url)

    def test_template(self):
        # show demo card detial page when not logged in
        self.assertEqual(self.response.status_code, 200)
        self.assertTemplateUsed(self.response, 'card_detail.html')
        self.assertContains(self.response, 'Log In')
        self.assertNotContains(self.response, 'Log Out')

        # check logged in properly
        self.assertEqual(self.logged_in_response.status_code, 200)
        self.assertTemplateUsed(self.logged_in_response, 'card_detail.html')
        self.assertContains(self.logged_in_response, 'testuser')
        self.assertContains(self.logged_in_response, 'Log Out')
        self.assertNotContains(self.logged_in_response, 'Log In')

    def test_view(self):
        view = resolve(self.url)
        # view = reverse('/card_detail')
        self.assertEqual(
            view.func.__name__,
            CardDetailView.as_view().__name__
        )


class CardUpdatePageTests(TestCase):

    def setUp(self):
        # make test user
        user = get_user_model().objects.create_user(username='testuser')
        user.set_password('testpass123')
        user.save()

        # make test card
        card = Card.objects.create(
            card_creator=user,
            title='test_Q',
            question_text='テスト',
            answer_text='test',
            category='テストカテゴリ',
            subcategory='テストサブカテゴリ',
            detail='テスト詳細',
            literary_style=True,
            creation_date=timezone.now()
        )
        card.save()
        self.url = reverse('card_edit', args=(card.card_id,))

        # anonymous user
        self.response = self.client.get(self.url)
        # logged in user
        self.client.login(username='testuser', password='testpass123')
        self.logged_in_response = self.client.get(self.url)

    def test_template(self):
        # show demo card update page when not logged in
        self.assertEqual(self.response.status_code, 302)

        # check logged in properly
        self.assertEqual(self.logged_in_response.status_code, 200)
        self.assertTemplateUsed(self.logged_in_response, 'card_edit.html')
        self.assertContains(self.logged_in_response, 'testuser')
        self.assertContains(self.logged_in_response, 'Log Out')
        self.assertNotContains(self.logged_in_response, 'Log In')

    def test_view(self):
        view = resolve(self.url)
        self.assertEqual(
            view.func.__name__,
            CardUpdateView.as_view().__name__
        )


class CardDeletePageTests(TestCase):

    def setUp(self):
        # make test user
        user = get_user_model().objects.create_user(username='testuser')
        user.set_password('testpass123')
        user.save()

        # make test card
        card = Card.objects.create(
            card_creator=user,
            title='test_Q',
            question_text='テスト',
            answer_text='test',
            category='テストカテゴリ',
            subcategory='テストサブカテゴリ',
            detail='テスト詳細',
            literary_style=True,
            creation_date=timezone.now(),
        )
        card.save()
        self.url = reverse('card_delete', args=(card.card_id,))

        # anonymous user
        self.response = self.client.get(self.url)
        # logged in user
        self.client.login(username='testuser', password='testpass123')
        self.logged_in_response = self.client.get(self.url)

    def test_template(self):
        # show demo card update page when not logged in
        self.assertEqual(self.response.status_code, 302)

        # check logged in properly
        self.assertEqual(self.logged_in_response.status_code, 200)
        self.assertTemplateUsed(self.logged_in_response, 'card_delete.html')
        self.assertContains(self.logged_in_response, 'testuser')
        self.assertContains(self.logged_in_response, 'Log Out')
        self.assertNotContains(self.logged_in_response, 'Log In')

    def test_view(self):
        view = resolve(self.url)
        self.assertEqual(
            view.func.__name__,
            CardDeleteView.as_view().__name__
        )
