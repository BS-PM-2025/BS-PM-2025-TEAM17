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



# user deletion tests
class DeleteUserViewTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.dashboard_url = reverse('dashboard')  # Assuming this is the redirect target
        # Create a user to be deleted
        self.user_to_delete = User.objects.create_user(
            email='testdelete@example.com',
            password='testpass123',
            username='testdelete@example.com'
        )

    def test_delete_existing_user(self):
        response = self.client.post(reverse('delete_user'), {
            'user_id': self.user_to_delete.id
        }, follow=True)

        # Check user is deleted
        with self.assertRaises(User.DoesNotExist):
            User.objects.get(id=self.user_to_delete.id)

        # Check success message
        messages = list(get_messages(response.wsgi_request))
        self.assertTrue(any("User deleted." in str(m) for m in messages))

        # Check redirection
        self.assertRedirects(response, self.dashboard_url)

    def test_delete_nonexistent_user(self):
        non_existent_id = 9999
        response = self.client.post(reverse('delete_user'), {
            'user_id': non_existent_id
        }, follow=True)

        # Ensure user wasn't deleted (already didn't exist)
        messages = list(get_messages(response.wsgi_request))
        self.assertTrue(any("User not found." in str(m) for m in messages))

        # Check redirection
        self.assertRedirects(response, self.dashboard_url)

    def test_delete_user_with_get_request(self):
        response = self.client.get(reverse('delete_user'))
        self.assertEqual(response.status_code, 405)  # Method Not Allowed


class LoginUserTest(TestCase):
    def setUp(self):
        """
        Setup test client and create users for testing login functionality.
        This method runs before every individual test.
        """
        self.client = Client()
        # Create a standard active user
        self.active_user = User.objects.create_user(
            username='activeuser@example.com', 
            email='activeuser@example.com',
            password='testpass123',
            is_active=True
        )
        # Create an inactive user to test inactive user login
        self.inactive_user = User.objects.create_user(
            username='inactiveuser@example.com', 
            email='inactiveuser@example.com',
            password='testpass123',
            is_active=False
        )
        # Create student and lecturer test users
        self.student_user = User.objects.create_user(
            username='student@example.com', 
            email='student@example.com',
            password='testpass123',
            is_student=True
        )
        self.lecturer_user = User.objects.create_user(
            username='lecturer@example.com', 
            email='lecturer@example.com',
            password='testpass123',
            is_lect=True
        )
        # URL for login
        self.login_url = reverse('login')
        # URL for redirection after successful login
        self.dashboard_url = reverse('dashboard')

    def test_login_page_loads_correctly(self):
        """Test that the login page loads with a GET request."""
        response = self.client.get(self.login_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'users/login.html')

    def test_successful_login(self):
        """Test successful login with valid credentials."""
        response = self.client.post(self.login_url, {
            'email': 'activeuser@example.com',
            'password': 'testpass123'
        }, follow=True)
        
        # Check user is authenticated
        self.assertTrue(response.context['user'].is_authenticated)
        
        # Check redirection to dashboard
        self.assertRedirects(response, self.dashboard_url)
        
        # No error messages should be present
        messages = list(get_messages(response.wsgi_request))
        self.assertFalse(any("somthing went wrong" in str(message) for message in messages))

    def test_failed_login_with_invalid_credentials(self):
        """Test login failure with incorrect password."""
        response = self.client.post(self.login_url, {
            'email': 'activeuser@example.com',
            'password': 'wrongpassword'
        }, follow=True)
        
        # User should not be authenticated
        self.assertFalse(response.context['user'].is_authenticated)
        
        # Check for error message
        messages = list(get_messages(response.wsgi_request))
        self.assertTrue(any("somthing went wrong" in str(message) for message in messages))
        
        # Should redirect back to login page
        self.assertRedirects(response, self.login_url)

    def test_login_with_nonexistent_user(self):
        """Test login attempt with email that doesn't exist in the system."""
        response = self.client.post(self.login_url, {
            'email': 'nonexistent@example.com',
            'password': 'testpass123'
        }, follow=True)
        
        # User should not be authenticated
        self.assertFalse(response.context['user'].is_authenticated)
        
        # Check for error message
        messages = list(get_messages(response.wsgi_request))
        self.assertTrue(any("somthing went wrong" in str(message) for message in messages))
        
        # Should redirect back to login page
        self.assertRedirects(response, self.login_url)

    def test_login_with_inactive_user(self):
        """Test login attempt with inactive user account."""
        response = self.client.post(self.login_url, {
            'email': 'inactiveuser@example.com',
            'password': 'testpass123'
        }, follow=True)
        
        # User should not be authenticated since account is inactive
        self.assertFalse(response.context['user'].is_authenticated)
        
        # Check for error message
        messages = list(get_messages(response.wsgi_request))
        self.assertTrue(any("somthing went wrong" in str(message) for message in messages))
        
        # Should redirect back to login page
        self.assertRedirects(response, self.login_url)

    def test_login_with_student_account(self):
        """Test successful login with student account."""
        response = self.client.post(self.login_url, {
            'email': 'student@example.com',
            'password': 'testpass123'
        }, follow=True)
        
        # Check user is authenticated
        self.assertTrue(response.context['user'].is_authenticated)
        
        # Check user is a student
        self.assertTrue(response.context['user'].is_student)
        
        # Check redirection to dashboard
        self.assertRedirects(response, self.dashboard_url)

    def test_login_with_lecturer_account(self):
        """Test successful login with lecturer account."""
        response = self.client.post(self.login_url, {
            'email': 'lecturer@example.com',
            'password': 'testpass123'
        }, follow=True)
        
        # Check user is authenticated
        self.assertTrue(response.context['user'].is_authenticated)
        
        # Check user is a lecturer
        self.assertTrue(response.context['user'].is_lect)
        
        # Check redirection to dashboard
        self.assertRedirects(response, self.dashboard_url)

    def test_login_with_empty_credentials(self):
        """Test login with empty email and password fields."""
        response = self.client.post(self.login_url, {
            'email': '',
            'password': ''
        }, follow=True)
        
        # User should not be authenticated
        self.assertFalse(response.context['user'].is_authenticated)
        
        # Check for error message
        messages = list(get_messages(response.wsgi_request))
        self.assertTrue(any("somthing went wrong" in str(message) for message in messages))
        
        # Should redirect back to login page
        self.assertRedirects(response, self.login_url)

    def test_login_with_missing_fields(self):
        """Test login with missing fields in the POST data."""
        # Test with missing email
        response1 = self.client.post(self.login_url, {
            'password': 'testpass123'
        }, follow=True)
        
        self.assertFalse(response1.context['user'].is_authenticated)
        
        # Test with missing password
        response2 = self.client.post(self.login_url, {
            'email': 'activeuser@example.com'
        }, follow=True)
        
        self.assertFalse(response2.context['user'].is_authenticated)


class ChangeUserRoleTest(TestCase):
    def setUp(self):
        """Setup test client and create a user to test role changes."""
        self.client = Client()
        
        # Create a test user
        self.test_user = User.objects.create_user(
            username='testuser@example.com',
            email='testuser@example.com',
            password='testpass123',
            is_student=False,
            is_lect=False,
            is_superuser=False
        )
        
        # URL for the role change and dashboard
        self.change_role_url = reverse('change_user_role')
        self.dashboard_url = reverse('dashboard')
        
        # Login with the test user
        self.client.login(username='testuser@example.com', password='testpass123')

    def test_change_to_student(self):
        """Test changing user role to student."""
        response = self.client.post(self.change_role_url, {
            'user_id': self.test_user.id,
            'role': 'student'
        }, follow=True)
        
        # Refresh user from database
        self.test_user.refresh_from_db()
        
        # Verify role was changed properly
        self.assertTrue(self.test_user.is_student)
        self.assertFalse(self.test_user.is_lect)
        self.assertFalse(self.test_user.is_superuser)
        
        # Verify proper redirect
        self.assertRedirects(response, self.dashboard_url)
        
        # Check success message
        messages = list(get_messages(response.wsgi_request))
        self.assertTrue(any("Role updated." in str(message) for message in messages))

    def test_change_to_lecturer(self):
        """Test changing user role to lecturer."""
        response = self.client.post(self.change_role_url, {
            'user_id': self.test_user.id,
            'role': 'lecturer'
        }, follow=True)
        
        # Refresh user from database
        self.test_user.refresh_from_db()
        
        # Verify role was changed properly
        self.assertFalse(self.test_user.is_student)
        self.assertTrue(self.test_user.is_lect)
        self.assertFalse(self.test_user.is_superuser)
        
        # Verify proper redirect
        self.assertRedirects(response, self.dashboard_url)

    def test_user_not_found(self):
        """Test behavior when user ID doesn't exist."""
        response = self.client.post(self.change_role_url, {
            'user_id': 9999,  # A non-existent user ID
            'role': 'student'
        }, follow=True)
        
        # Check for error message
        messages = list(get_messages(response.wsgi_request))
        self.assertTrue(any("User not found." in str(message) for message in messages))
        
        # Verify proper redirect
        self.assertRedirects(response, self.dashboard_url)