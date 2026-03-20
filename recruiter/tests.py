from django.test import TestCase, override_settings
from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile

from django.conf import settings


class ResumeUploadTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='tester', password='password123')
        self.client.login(username='tester', password='password123')

    def test_upload_invalid_file_type(self):
        file_data = SimpleUploadedFile('resume.exe', b'This is fake exe content', content_type='application/octet-stream')
        response = self.client.post('/upload', {'resume': file_data, 'job_desc': 'test desc'})

        self.assertEqual(response.status_code, 200)
        self.assertIn('upload_errors', response.context)
        self.assertTrue(any('unsupported file type' in message.lower() for message in response.context['upload_errors']))

    def test_upload_exceeds_max_size(self):
        large_content = b'a' * (settings.MAX_UPLOAD_SIZE + 1)
        file_data = SimpleUploadedFile('resume.pdf', large_content, content_type='application/pdf')
        response = self.client.post('/upload', {'resume': file_data, 'job_desc': 'test desc'})

        self.assertEqual(response.status_code, 200)
        self.assertIn('upload_errors', response.context)
        self.assertTrue(any('exceeds max upload size' in message.lower() for message in response.context['upload_errors']))


class RazorpayConfigTests(TestCase):
    def test_pricing_warning_when_razorpay_not_configured(self):
        with override_settings(RAZORPAY_KEY_ID='', RAZORPAY_KEY_SECRET=''):
            response = self.client.get('/pricing')

            self.assertEqual(response.status_code, 200)
            self.assertContains(response, 'Payments are not configured')
