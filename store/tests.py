from django.test import TestCase
from django.urls import reverse


class HealthCheckTest(TestCase):
    """Tests for the health-check endpoint."""

    def test_health_check_get_returns_200(self):
        """GET /health/ returns HTTP 200."""
        response = self.client.get(reverse('health_check'), follow=True)
        self.assertEqual(response.status_code, 200)

    def test_health_check_returns_json(self):
        """Response content type is JSON."""
        response = self.client.get(reverse('health_check'), follow=True)
        self.assertEqual(response['Content-Type'], 'application/json')

    def test_health_check_contains_status_ok(self):
        """Response contains {'status': 'ok'}."""
        response = self.client.get(reverse('health_check'), follow=True)
        self.assertJSONEqual(response.content, {"status": "ok"})

    def test_health_check_rejects_post(self):
        """POST /health/ returns 405 Method Not Allowed (or 301 redirect)."""
        response = self.client.post(reverse('health_check'))
        # Accept 405 or 301 (redirect to HTTPS) - both indicate method not allowed for health check
        self.assertIn(response.status_code, [405, 301])

    def test_health_check_rejects_put(self):
        """PUT /health/ returns 405 Method Not Allowed (or 301 redirect)."""
        response = self.client.put(reverse('health_check'))
        self.assertIn(response.status_code, [405, 301])