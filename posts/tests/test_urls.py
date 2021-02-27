from django.core.cache import cache
from django.test import Client, TestCase

from posts.models import Group, Post, User


class URLTests(TestCase):
    def setUp(self):
        self.group = Group.objects.create(
            title="Тестовый заголовок группы",
            description="Тестовое описание группы",
            slug="test-slug"
        )
        self.guest_client = Client()
        self.user = User.objects.create_user(username="testuser")
        self.user_author = User.objects.create_user(username="userauthor")
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        self.post = Post.objects.create(
            text="Текст тестового поста",
            author=self.user
        )
        self.post_author = Post.objects.create(
            text="Текст тестового поста",
            author=self.user_author
        )
        self.url_names_authorized = {
            "/": 200,
            "/about/tech/": 200,
            "/about/author/": 200,
            "/new/": 200,
            f"/group/{self.group.slug}/": 200,
            f"/{self.user.username}/": 200,
            f"/{self.user.username}/{self.post.id}/": 200,
            f"/{self.user.username}/{self.post.id}/edit/": 200,
            f"/{self.user_author.username}/{self.post_author.id}/edit/": 302,
        }
        self.url_names_anonymous = {
            "/": 200,
            "/about/tech/": 200,
            "/about/author/": 200,
            "/new/": 302,
            f"/group/{self.group.slug}/": 200,
            f"/{self.user.username}/": 200,
            f"/{self.user.username}/{self.post.id}/edit/": 302
        }
        self.templates_url_names = {
            "index.html": "/",
            "group.html": f"/group/{self.group.slug}/",
            "new_post.html": "/new/",
            "about/author.html": "/about/author/",
            "about/tech.html": "/about/tech/",
        }

    def test_urls_correct_status_code_authorized(self):
        for url, status_code in self.url_names_authorized.items():
            with self.subTest():
                response = self.authorized_client.get(url)
                self.assertEqual(response.status_code, status_code)

    def test_urls_correct_status_code_anonymous(self):
        for url, status_code in self.url_names_anonymous.items():
            with self.subTest():
                response = self.guest_client.get(url)
                self.assertEqual(
                    response.status_code,
                    status_code,
                    url
                )

    def test_urls_edit_posts_uses_correct_template(self):
        reverse_name = f"/{self.user.username}/{self.post.id}/edit/"
        response = self.authorized_client.get(reverse_name)
        self.assertTemplateUsed(response, "new_post.html")

    def test_urls_uses_correct_templates(self):
        for template, reverse_name in self.templates_url_names.items():
            with self.subTest():
                cache.clear()
                response = self.authorized_client.get(reverse_name)
                self.assertTemplateUsed(
                    response,
                    template
                )

    def test_urls_server_404_page_not_found(self):
        response = self.authorized_client.get("/page_not_found/")
        self.assertEqual(response.status_code, 404)
