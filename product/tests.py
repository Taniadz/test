from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.test import Client
from django.test import TestCase
from django.utils import timezone

from .forms import CommentForm
from .models import Comment, Product, Votes


# Create your tests here.


# models test
class TestComment(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='test_user1', password='12345test')
        self.product = Product.objects.create(name="test1",
                                              slug="test1",
                                              description="test description",
                                              modified_at=timezone.now())

        self.comment = Comment.objects.create(text="only a test",
                                              added_at=timezone.now(),
                                              product=self.product,
                                              author=self.user)

    def test_comment_creation(self):
        com = self.comment
        self.assertTrue(isinstance(com, Comment))

    def test_comment_view(self):
        com = self.comment
        url = reverse('one_product', kwargs={'slug': com.product.slug})
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 200)
        self.assertIn(com.text.encode(), resp.content)

    def test_valid_form(self):
        com = Comment.objects.create(text='some', product=self.product,
                                     author=User.objects.create_user(username='test_user2'))
        data = {'text': com.text, 'product': str(com.product.id), 'author': com.author, 'slug': str(com.product.slug)}
        form = CommentForm(data=data)
        self.assertTrue(form.is_valid())

    def test_invalid_form(self):
        com = Comment.objects.create(text='', product=self.product,
                                     author=User.objects.create_user(username='test_user2'))
        data = {'text': com.text, 'product': str(com.product.id), 'author': com.author}
        form = CommentForm(data=data)
        self.assertFalse(form.is_valid())


class TestLogin(TestCase):
    def test_login_user(self):
        user = User.objects.create(username='testuser')
        user.set_password('12345test')
        user.save()
        c = Client()
        logged_in = c.login(username='testuser', password='12345test')
        self.assertTrue(logged_in)

    def test_view(self):
        c = Client()
        response = c.post(reverse('login'), {'username': 'john', 'password': 'smith'})
        self.assertEqual(response.status_code, 200)


class TestVotes(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='test_user1', password='12345test')
        self.product = Product.objects.create(name="test1",
                                              slug="test1",
                                              description="test description",
                                              modified_at=timezone.now())

    def test_vote_create_true(self):
        obj, created = Votes.objects.get_or_create(user_id=self.user.id, product_id=self.product.id)

        self.assertTrue(created)

    def test_vote_create_false(self):
        obj1, created = Votes.objects.get_or_create(user_id=self.user.id, product_id=self.product.id)
        obj2, created = Votes.objects.get_or_create(user_id=obj1.user_id, product_id=obj1.product_id)
        self.assertFalse(created)
