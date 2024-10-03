from django.test import TestCase, Client 
from .models import Post , Comment
from django.urls import reverse
from django.contrib.auth.models import User, Group
from django.core.files.uploadedfile import SimpleUploadedFile
from .forms import ContactForm
import tempfile
from PIL import Image
from django.utils import timezone

class CustomLogoutTest(TestCase):

    def setUp(self):
        # Create a test user and log in
        self.user = User.objects.create_user(username='user_test', password='password123')
        self.client = Client()
        self.client.login(username='user_test', password='password123')

    def test_logout_redirect(self):
        # Test logout and redirection
        response = self.client.get(reverse('logout'))
        self.assertRedirects(response, reverse('post_list'))

class RegisterViewTest(TestCase):

    def setUp(self):
        self.group = Group.objects.create(name='Users')

    def test_register_user(self):
        form_data = {
            'username': 'newuser',
            'password1': 'strongpassword123',
            'password2': 'strongpassword123',
            'email': 'newuser@example.com',
        }
        response = self.client.post(reverse('register'), data=form_data)
        
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('login'))
        user = User.objects.get(username='newuser')
        self.assertTrue(user)
        self.assertTrue(user.groups.filter(name='Users').exists())


class PostListViewTest(TestCase):

    def setUp(self):
        # Create a user and two posts for testing
        self.user = User.objects.create_user(username='user_test', password='password123')
        Post.objects.create(title='Post 1', content='Content 1', author=self.user)
        Post.objects.create(title='Post 2', content='Content 2', author=self.user)

    def test_post_list_view(self):
        # Testar se a view retorna com status 200
        response = self.client.get(reverse('post_list'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Post 1')
        self.assertContains(response, 'Post 2')

    def test_post_list_search(self):
        # Testar a funcionalidade de pesquisa
        response = self.client.get(reverse('post_list'), {'q': 'Post 1'})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Post 1')
        self.assertNotContains(response, 'Post 2')



class NewPostWithImageTest(TestCase):

    def setUp(self):
        self.group = Group.objects.create(name='Users')
        self.user = User.objects.create_user(username='user_test', password='password123')
        self.user.groups.add(self.group)
        self.client.login(username='user_test', password='password123')

    def test_create_new_post_with_image(self):
        # Create a valid temporary image
        temp_image = tempfile.NamedTemporaryFile(suffix=".jpg")
        image = Image.new('RGB', (100, 100), color = 'red')
        image.save(temp_image, format='JPEG')
        temp_image.seek(0)

        uploaded_image = SimpleUploadedFile(temp_image.name, temp_image.read(), content_type="image/jpeg")

        response = self.client.post(reverse('new_post'), {
            'title': 'Post with Image',
            'content': 'Post content with image',
            'image': uploaded_image,
        })
        
        # Check if the redirection occurs and the post was created with the image
        self.assertRedirects(response, reverse('post_list'))
        self.assertEqual(Post.objects.count(), 1)
        post = Post.objects.first()
        self.assertEqual(post.title, 'Post with Image')
        self.assertTrue(post.image)  # Check if the image was saved
        

class EditPostTest(TestCase):

    def setUp(self):
        # Create a user and a post
        self.user = User.objects.create_user(username='author_test', password='password123')
        self.superuser = User.objects.create_superuser(username='admin', password='admin123')
        self.post = Post.objects.create(title='Original Title', content='Original Content', author=self.user)
    
    def test_author_can_edit_post(self):
        # Author can edit the post
        self.client.login(username='author_test', password='password123')
        response = self.client.post(reverse('edit_post', kwargs={'pk': self.post.pk}), {
            'title': 'Edited Title',
            'content': 'Edited Content'
        })
        self.assertRedirects(response, reverse('post_detail', kwargs={'pk': self.post.pk}))
        self.post.refresh_from_db()
        self.assertEqual(self.post.title, 'Edited Title')
        self.assertEqual(self.post.content, 'Edited Content')

    def test_superuser_can_edit_post(self):
        # Superuser can edit the post
        self.client.login(username='admin', password='admin123')
        response = self.client.post(reverse('edit_post', kwargs={'pk': self.post.pk}), {
            'title': 'Super Edited Title',
            'content': 'Super Edited Content'
        })
        self.assertRedirects(response, reverse('post_detail', kwargs={'pk': self.post.pk}))
        self.post.refresh_from_db()
        self.assertEqual(self.post.title, 'Super Edited Title')
        self.assertEqual(self.post.content, 'Super Edited Content')

    def test_non_author_cannot_edit_post(self):
        # Non-author user cannot edit the post
        other_user = User.objects.create_user(username='user_test', password='password123')
        self.client.login(username='user_test', password='password123')
        response = self.client.post(reverse('edit_post', kwargs={'pk': self.post.pk}), {
            'title': 'Edit Attempt',
            'content': 'Not Allowed Content'
        })
        self.assertRedirects(response, reverse('post_list'))
        self.post.refresh_from_db()
        self.assertEqual(self.post.title, 'Original Title')
        self.assertEqual(self.post.content, 'Original Content')
        







class DeletePostTest(TestCase):
    def setUp(self):
        # Create a user and a test post
        self.user = User.objects.create_user(username='user_test', password='password123')
        self.post = Post.objects.create(title='Test Post', content='Test Content', author=self.user)
        self.client.login(username='user_test', password='password123')

    def test_delete_post(self):
        # Verify if the post was created
        self.assertEqual(Post.objects.count(), 1)
        
        # Make a request to delete the post
        response = self.client.post(reverse('delete_post', kwargs={'pk': self.post.pk}))
        
        # Check if the redirection occurs after deletion
        self.assertRedirects(response, reverse('post_list'))
        
        # Verify if the post was actually deleted
        self.assertEqual(Post.objects.count(), 0)

class PostDetailTest(TestCase):
    def setUp(self):
        # Create a user and a test post
        self.user = User.objects.create_user(username='user_test', password='password123')
        self.post = Post.objects.create(title='Test Post', content='Post content', author=self.user)

    def test_post_detail_comments(self):
        # Create a comment for the post
        Comment.objects.create(post=self.post, user=self.user, content='Test Comment')

        # Test if the post and the comment are displayed
        response = self.client.get(reverse('post_detail', kwargs={'pk': self.post.pk}))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Test Post')
        self.assertContains(response, 'Test Comment')

    def test_add_comment(self):
        # Log in to test adding a comment
        self.client.login(username='user_test', password='password123')
        
        # Simulate submitting a comment form
        response = self.client.post(reverse('post_detail', kwargs={'pk': self.post.pk}), {
            'content': 'New comment'
        })
        
        # Check if the comment was added and redirected to post_detail
        self.assertEqual(response.status_code, 302)
        self.assertTrue(Comment.objects.filter(content='New comment').exists())

class ContactViewTest(TestCase):
    def test_contact_form_success(self):
        # Test if the contact form is successfully submitted
        response = self.client.post(reverse('contact'), {
            'name': 'User Test',
            'email': 'user@test.com',
            'message': 'This is a test message'
        })
        self.assertEqual(response.status_code, 302)  # Should redirect after success
        response = self.client.get(reverse('contact'))  # Follow the redirection
        self.assertContains(response, 'Your message has been sent successfully!', html=True)

    def test_contact_form_error(self):
        # Test if the form returns an error when not validated
        response = self.client.post(reverse('contact'), {
            'name': '',
            'email': 'invalid-email',
            'message': ''
        })
        self.assertEqual(response.status_code, 200)  # Stays on the same page in case of an error
        self.assertContains(response, 'There was an error with your submission. Please try again.', html=True)

class CommentEditTest(TestCase):
    def setUp(self):
        # Create a user, post, and comment
        self.user = User.objects.create_user(username='user1', password='password123')
        self.superuser = User.objects.create_superuser(username='admin', password='admin123')
        self.post = Post.objects.create(title="Test Post", content="Test content", author=self.user, created_at=timezone.now())
        self.comment = Comment.objects.create(post=self.post, user=self.user, content="Initial Comment")

    def test_edit_comment_by_author(self):
        # Test if the author can edit the comment
        self.client.login(username='user1', password='password123')
        response = self.client.post(reverse('edit_comment', args=[self.comment.id]), {'content': 'Edited Comment'})
        self.comment.refresh_from_db()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(self.comment.content, 'Edited Comment')

    def test_edit_comment_by_non_author(self):
        # Log in with another user who is not the author
        other_user = User.objects.create_user(username='user2', password='password123')
        self.client.login(username='user2', password='password123')

        # Attempt to edit the comment
        response = self.client.post(reverse('edit_comment', args=[self.comment.id]), {'content': 'Edit Attempt'})
        
        # Check if the status code is 403 (forbidden)
        self.assertEqual(response.status_code, 403)
        self.comment.refresh_from_db()
        self.assertNotEqual(self.comment.content, 'Edit Attempt')

    def test_edit_comment_invalid_data(self):
        # Test if it fails when submitting invalid data
        self.client.login(username='user1', password='password123')
        response = self.client.post(reverse('edit_comment', args=[self.comment.id]), {'content': ''})
        self.assertEqual(response.status_code, 400)

class CommentDeleteTest(TestCase):
    def setUp(self):
        # Create a user, post, and comment
        self.user = User.objects.create_user(username='user1', password='password123')
        self.superuser = User.objects.create_superuser(username='admin', password='admin123')
        self.post = Post.objects.create(title="Test Post", content="Test content", author=self.user, created_at=timezone.now())
        self.comment = Comment.objects.create(post=self.post, user=self.user, content="Comment to be deleted")

    def test_delete_comment_by_author(self):
        # Test if the author can delete the comment
        self.client.login(username='user1', password='password123')
        response = self.client.post(reverse('delete_comment', args=[self.comment.id]))
        self.assertEqual(response.status_code, 302)
        self.assertFalse(Comment.objects.filter(id=self.comment.id).exists())

    def test_delete_comment_by_superuser(self):
        # Test if the superuser can delete the comment
        self.client.login(username='admin', password='admin123')
        response = self.client.post(reverse('delete_comment', args=[self.comment.id]))
        self.assertEqual(response.status_code, 302)
        self.assertFalse(Comment.objects.filter(id=self.comment.id).exists())

    def test_delete_comment_by_non_author(self):
        # Test if a non-author user cannot delete the comment
        other_user = User.objects.create_user(username='user2', password='password123')
        self.client.login(username='user2', password='password123')
        response = self.client.post(reverse('delete_comment', args=[self.comment.id]))
        self.assertEqual(response.status_code, 302)
        self.assertTrue(Comment.objects.filter(id=self.comment.id).exists())
