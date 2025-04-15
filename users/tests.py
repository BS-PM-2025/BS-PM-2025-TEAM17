from django.test import TestCase, Client
from django.contrib.auth import get_user_model, logout
from django.urls import reverse
from django.contrib.messages import get_messages

# Use the custom user model defined in your project
User = get_user_model()

class LogoutUserTest(TestCase):
    def setUp(self):
        """
        Setup test client and create a user.
        This method runs before every individual test.
        """
        self.client = Client()
        self.user = User.objects.create_user(username='testuser', password='testpass123')

    def test_logout_when_logged_in(self):
        """
        Test that a logged in user is correctly logged out.
        1. Login the user.
        2. Access the logout view.
        3. Verify that the user's session no longer contains the authentication key.
        4. Check that the flash message 'your session has ended' is present.
        5. Ensure that after logout, the user is redirected to the login page.
        """
        # Step 1: Log in the user
        login_successful = self.client.login(username='testuser', password='testpass123')
        self.assertTrue(login_successful, "Login failed — please ensure the user exists.")

        # Step 2: Call the logout view via the URL name 'logout'
        response = self.client.get(reverse('logout'))

        # Step 3: Verify that the user is logged out (session no longer contains auth key)
        self.assertNotIn('_auth_user_id', self.client.session, "User session still contains auth user id.")

        # Step 4: Check the flash message using Django's messaging framework
        messages = list(get_messages(response.wsgi_request))
        self.assertTrue(
            any("your session has ended" in str(message) for message in messages),
            "Expected logout message not found in messages."
        )

        # Step 5: Ensure the response is a redirect to the login page
        self.assertRedirects(response, reverse('login'), msg_prefix="After logout, the user was not redirected to login.")

    def test_logout_when_not_logged_in(self):
        """
        Test the logout view when no user is logged in.
        1. Call the logout view without logging in.
        2. Verify that no authentication exists in session.
        3. Optionally, check for the same flash message (depending on your desired behavior).
        4. Ensure that the response redirects to the login page.
        """
        # Since no user is logged in, calling logout should still redirect to login page
        response = self.client.get(reverse('logout'))

        # No user should be logged in; check the absence of the auth key in session
        self.assertNotIn('_auth_user_id', self.client.session, "Session should not contain auth user id when not logged in.")

        # You may expect the logout message to be added even if no user was logged in
        messages = list(get_messages(response.wsgi_request))
        self.assertTrue(
            any("your session has ended" in str(message) for message in messages),
            "Expected logout message not found in messages even when not logged in."
        )

        # Check that the user is redirected to the login page
        self.assertRedirects(response, reverse('login'), msg_prefix="User not logged in should still be redirected to login.")
