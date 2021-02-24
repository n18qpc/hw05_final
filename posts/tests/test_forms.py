import shutil
import tempfile

from django.conf import settings
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase
from django.urls import reverse

from posts.forms import PostForm
from posts.models import Comment, Post, User


class TaskCreateFormTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        settings.MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)
        cls.form = PostForm()

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(settings.MEDIA_ROOT, ignore_errors=True)
        super().tearDownClass()

    def setUp(self):
        self.user = User.objects.create_user(username="testuser")
        self.anonymous_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        self.post = Post.objects.create(
            text="Текст тестового поста",
            author=self.user
        )

    def test_create_post(self):
        posts_count = Post.objects.count()
        form_data = {
            "text": "Тестовый текст"
        }
        response = self.authorized_client.post(
            reverse("new_post"),
            data=form_data,
            follow=True
        )
        self.assertRedirects(response, reverse("index"))
        self.assertEqual(Post.objects.count(), posts_count + 1)
        self.assertTrue(
            Post.objects.filter(text="Тестовый текст").exists()
        )

    def test_edit_post(self):
        form_data = {"text": "Измененный текст"}
        self.authorized_client.post(
            reverse(
                "post_edit",
                kwargs={
                    "username": self.user.username,
                    "post_id": self.post.id
                }
            ),
            data=form_data,
            follow=True
        )
        self.post.refresh_from_db()
        self.assertEqual(self.post.text, "Измененный текст")

    def test_create_post_with_image(self):
        posts_count = Post.objects.count()
        small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x02\x00'
            b'\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
            b'\x00\x00\x00\x2C\x00\x00\x00\x00'
            b'\x02\x00\x01\x00\x00\x02\x02\x0C'
            b'\x0A\x00\x3B'
        )
        uploaded = SimpleUploadedFile(
            name='small.gif',
            content=small_gif,
            content_type='image/gif'
        )
        Post.objects.create(
            text="Пост с картинкой",
            author=self.user,
            image=uploaded
        )
        self.assertEqual(Post.objects.count(), posts_count + 1)

    def test_only_authorized_user_can_comment(self):
        form_data = {"text": "Текст комментария"}
        count_comments = Comment.objects.all().count()
        self.authorized_client.post(
            reverse(
                "add_comment",
                kwargs={
                    "username": self.user.username,
                    "post_id": self.post.id
                }
            ),
            data=form_data,
            follow=True
        )
        self.assertEqual(Comment.objects.all().count(), count_comments + 1)
        self.anonymous_client.post(
            reverse(
                "add_comment",
                kwargs={
                    "username": self.user.username,
                    "post_id": self.post.id
                }
            ),
            data=form_data,
            follow=True
        )
        self.assertEqual(Comment.objects.all().count(), count_comments + 1)
