import json

from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

from .models import DataPlatform, PasswordEntry


class DataPlatformTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='owner', password='test-pass')
        self.other_user = User.objects.create_user(username='other', password='test-pass')
        self.client.login(username='owner', password='test-pass')

    def test_create_note_platform_and_save_content(self):
        response = self.client.post(reverse('create_data_platform'), {
            'name': 'Project Notes',
            'platform_type': 'note',
        })
        platform = DataPlatform.objects.get(name='Project Notes')
        self.assertRedirects(response, reverse('edit_data_platform', args=[platform.pk]))

        self.client.post(reverse('edit_data_platform', args=[platform.pk]), {
            'note_content': 'Important information',
        })
        platform.refresh_from_db()
        self.assertEqual(platform.note_content, 'Important information')

    def test_sheet_data_is_saved_as_json(self):
        platform = DataPlatform.objects.create(
            user=self.user,
            name='Customers',
            platform_type='sheet',
        )
        sheet = [['Name', 'Email'], ['Niran', 'niran@example.com']]
        self.client.post(reverse('edit_data_platform', args=[platform.pk]), {
            'sheet_data': json.dumps(sheet),
        })
        platform.refresh_from_db()
        self.assertEqual(platform.sheet_data, sheet)

    def test_platforms_are_private_to_their_owner(self):
        platform = DataPlatform.objects.create(
            user=self.other_user,
            name='Private',
            platform_type='note',
        )
        response = self.client.get(reverse('edit_data_platform', args=[platform.pk]))
        self.assertEqual(response.status_code, 404)


class PasswordLogoTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='owner', password='test-pass')
        self.client.login(username='owner', password='test-pass')

    def test_logo_is_optional_when_creating_password(self):
        response = self.client.post(reverse('add_entry'), {
            'platform': 'Example',
            'username': 'owner@example.com',
            'password': 'secret',
            'category': 'other',
        })
        self.assertRedirects(response, reverse('dashboard'))
        self.assertFalse(PasswordEntry.objects.get(platform='Example').logo)

    def test_custom_logo_address_is_saved_and_displayed(self):
        logo_url = 'https://example.com/logo.png'
        self.client.post(reverse('add_entry'), {
            'platform': 'Example',
            'logo_url': logo_url,
            'username': 'owner@example.com',
            'password': 'secret',
            'category': 'other',
        })
        entry = PasswordEntry.objects.get(platform='Example')
        self.assertEqual(entry.logo_image_url, logo_url)
