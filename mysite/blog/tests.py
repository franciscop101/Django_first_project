from django.test import TestCase
from django.test import TestCase
from .models import Post, Comment

# Create your tests here.
class PostModelTest(TestCase):
    def setUp(self):
        self.post = Post.objects.create(title='Teste Post', content='Conteúdo de teste')

    def test_post_creation(self):
        self.assertEqual(self.post.title, 'Teste Post')
        self.assertEqual(self.post.content, 'Conteúdo de teste')
        self.assertTrue(isinstance(self.post, Post))

class CommentModelTest(TestCase):
    def setUp(self):
        self.post = Post.objects.create(title='Post para comentário', content='Conteúdo de post')
        self.comment = Comment.objects.create(post=self.post, text='Comentário de teste')

    def test_comment_creation(self):
        self.assertEqual(self.comment.text, 'Comentário de teste')
        self.assertEqual(self.comment.post, self.post)