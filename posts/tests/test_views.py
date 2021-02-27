import datetime
import shutil
import tempfile

from django import forms
from django.conf import settings
from django.core.cache import cache
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase
from django.urls import reverse, reverse_lazy

from posts.models import Comment, Follow, Group, Post, User


class PagesTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        settings.MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)
        cls.PAGE_NAME = "page"
        cls.test_username = "test_user"
        cls.user = User.objects.create_user(username=PagesTest.test_username)
        cls.user_for_subscribe = User.objects.create_user(
            username="user_for_subscribe"
        )
        cls.another_user = User.objects.create_user(
            username="another_user"
        )
        cls.authorized_client = Client()
        cls.anonymous_client = Client()
        cls.authorized_client.force_login(PagesTest.user)
        cls.group1 = Group.objects.create(
            title="Тестовый заголовок группы",
            description="Тестовое описание группы",
            slug="test-slug"
        )
        cls.group2 = Group.objects.create(
            title="Тестовый заголовок группы2",
            description="Тестовое описание группы2",
            slug="test-slug2"
        )
        cls.post = Post.objects.create(
            text="Заголовок текстового поста",
            pub_date="20210121",
            author=PagesTest.user,
            group=PagesTest.group1
        )
        cls.small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x02\x00'
            b'\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
            b'\x00\x00\x00\x2C\x00\x00\x00\x00'
            b'\x02\x00\x01\x00\x00\x02\x02\x0C'
            b'\x0A\x00\x3B'
        )
        cls.uploaded = SimpleUploadedFile(
            name='small.gif',
            content=PagesTest.small_gif,
            content_type='image/gif'
        )
        cls.post_sub = Post.objects.create(
            text="Заголовок поста 2",
            author=PagesTest.user_for_subscribe
        )
        cls.post_another = Post.objects.create(
            text="Заголовок поста 1",
            author=PagesTest.another_user
        )

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(settings.MEDIA_ROOT, ignore_errors=True)
        super().tearDownClass()

    def test_pages_uses_correct_template(self):
        templates_pages_names = {
            "index.html": reverse("index"),
            "group.html": (
                reverse("group_posts", kwargs={"slug": PagesTest.group1.slug})
            ),
            "new_post.html": reverse("new_post"),
            "about/author.html": reverse("about:author"),
            "about/tech.html": reverse("about:tech")
        }
        for template, reverse_name in templates_pages_names.items():
            with self.subTest(reverse_name=reverse_name):
                cache.clear()
                response = self.authorized_client.get(reverse_name)
                self.assertTemplateUsed(response, template)

    def test_home_page_show_correct_context(self):
        response = self.authorized_client.get(reverse("index"))
        self.assertContains(response, PagesTest.post.text)

    def test_group_page_show_correct_context(self):
        response = self.authorized_client.get(reverse("group_posts", kwargs={
            "slug": PagesTest.group1.slug
        }))
        post = response.context.get(PagesTest.PAGE_NAME)[0]
        post_text_0 = post.text
        post_pub_date_0 = post.pub_date
        post_author_0 = post.author
        post_group_0 = post.group
        self.assertEqual(post_text_0, PagesTest.post.text)
        self.assertEqual(
            post_pub_date_0.strftime("%d %m %Y"),
            datetime.date.today().strftime("%d %m %Y")
        )
        self.assertEqual(post_author_0.username, PagesTest.test_username)
        self.assertEqual(post_group_0.slug, PagesTest.group1.slug)

    def test_new_post_page_show_correct_context(self):
        response = self.authorized_client.get(reverse("new_post"))
        form_fields = {
            "text": forms.fields.CharField,
            "group": forms.models.ModelChoiceField,
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get("form").fields.get(value)
                self.assertIsInstance(
                    form_field,
                    expected,
                    f"value={value} {form_field} != {expected}"
                )

    def test_edit_post_page_show_correct_context(self):
        response = self.authorized_client.get(reverse("post_edit", kwargs={
            "username": PagesTest.user.username,
            "post_id": PagesTest.post.id
        }))
        form_fields = {
            "text": forms.fields.CharField,
            "group": forms.models.ModelChoiceField,
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get("form").fields.get(value)
                self.assertIsInstance(
                    form_field,
                    expected,
                    f"value={value} {form_field} != {expected}"
                )

    def test_profile_page_show_correct_context(self):
        response = self.authorized_client.get(reverse("profile", kwargs={
            "username": PagesTest.user.username
        }))
        post_text_0 = response.context.get(PagesTest.PAGE_NAME)[0].text
        post_pub_date_0 = response.context.get(PagesTest.PAGE_NAME)[0].pub_date
        post_author_0 = response.context.get(PagesTest.PAGE_NAME)[0].author
        post_group_0 = response.context.get(PagesTest.PAGE_NAME)[0].group
        self.assertEqual(post_text_0, PagesTest.post.text)
        self.assertEqual(
            post_pub_date_0.strftime("%d %m %Y"),
            datetime.date.today().strftime("%d %m %Y")
        )
        self.assertEqual(post_author_0.username, PagesTest.test_username)
        self.assertEqual(post_group_0.slug, PagesTest.group1.slug)

    def test_post_page_show_correct_context(self):
        reverse_post = reverse("post", kwargs={
            "username": PagesTest.user.username,
            "post_id": PagesTest.post.id
        })
        response = self.authorized_client.get(reverse_post)
        post_text_0 = response.context.get("post").text
        post_pub_date_0 = response.context.get("post").pub_date
        post_author_0 = response.context.get("post").author
        post_group_0 = response.context.get("post").group
        self.assertEqual(post_text_0, PagesTest.post.text)
        self.assertEqual(
            post_pub_date_0.strftime("%d %m %Y"),
            datetime.date.today().strftime("%d %m %Y")
        )
        self.assertEqual(post_author_0.username, PagesTest.test_username)
        self.assertEqual(post_group_0.slug, PagesTest.group1.slug)

    def test_post_with_group_in_index(self):
        cache.clear()
        response = self.authorized_client.get(reverse("index"))
        self.assertContains(response, PagesTest.group1.slug)

    def test_post_with_group_in_page_group(self):
        response = self.authorized_client.get(
            reverse("group_posts", kwargs={"slug": PagesTest.group1.slug})
        )
        post_group = response.context.get(PagesTest.PAGE_NAME)[0].group.slug
        self.assertEqual(post_group, PagesTest.group1.slug)

    def test_post_with_group_unavailable_another_group(self):
        response = self.authorized_client.get(reverse("group_posts", kwargs={
            "slug": PagesTest.group2.slug
        }))
        self.assertNotContains(response, PagesTest.post.text)

    def test_about_author_available_anonymous(self):
        response = self.anonymous_client.get(reverse_lazy("about:author"))
        status_code = response.status_code
        self.assertEqual(status_code, 200)

    def test_about_tech_available_anonymous(self):
        response = self.anonymous_client.get(reverse_lazy("about:tech"))
        status_code = response.status_code
        self.assertEqual(status_code, 200)

    def test_about_tech_show_correct_template(self):
        response = self.anonymous_client.get(reverse_lazy("about:tech"))
        self.assertTemplateUsed(response, "about/tech.html")

    def test_about_author_show_correct_template(self):
        response = self.anonymous_client.get(reverse_lazy("about:author"))
        self.assertTemplateUsed(response, "about/author.html")

    def test_paginator_show_correct_posts_count(self):
        cache.clear()
        response = self.authorized_client.get(reverse("index"))
        count = len(response.context.get(PagesTest.PAGE_NAME).object_list)
        self.assertEqual(count, 3)

    def test_context_contains_image(self):
        post_with_image = Post.objects.create(
            text="Пост с картинкой",
            pub_date="20210202",
            author=self.user,
            group=self.group1,
            image=self.uploaded
        )
        tests_urls = {
            "index": None,
            "profile": {"username": self.user.username},
            "group_posts": {"slug": self.group1.slug},
        }
        for url, kwargs in tests_urls.items():
            with self.subTest(msg=url):
                cache.clear()
                response = self.authorized_client.get(reverse(url,
                                                              kwargs=kwargs))
                response_image = response.context.get("page")[0].image
                self.assertIsNotNone(response_image)
        response = self.authorized_client.get(reverse("post", kwargs={
            "username": self.user.username,
            "post_id": post_with_image.id
        }))
        response_image = response.context.get("post").image
        self.assertIsNotNone(response_image)

    def test_cache_index_page(self):
        cached_content = self.authorized_client.get(reverse("index")).content
        Post.objects.create(
            text="Заголовок тестового поста для проверки кэша",
            author=PagesTest.user
        )
        response = self.authorized_client.get(reverse("index"))
        self.assertEqual(cached_content, response.content)
        cache.clear()
        response = self.authorized_client.get(reverse("index"))
        self.assertNotEqual(cached_content, response.content)

    def test_succes_follow(self):
        self.authorized_client.get(reverse("profile_follow", kwargs={
            "username": self.user_for_subscribe.username
        }))
        follow = Follow.objects.filter(author=self.user_for_subscribe,
                                       user=self.user)
        self.assertIsNotNone(follow)

    def test_succes_unfollow(self):
        self.authorized_client.get(reverse("profile_unfollow", kwargs={
            "username": self.user_for_subscribe.username
        }))
        follow = Follow.objects.filter(author=self.user_for_subscribe,
                                       user=self.user).exists()
        self.assertFalse(follow)

    def test_new_post_show_for_subscriber(self):
        self.authorized_client.get(reverse("profile_follow", kwargs={
            "username": self.user_for_subscribe.username
        }))
        self.authorized_client.get(reverse("profile_follow", kwargs={
            "username": self.another_user.username
        }))
        response = self.authorized_client.get(reverse("follow_index"))
        self.assertIn(self.post_sub, response.context.get("page"))

    def test_new_post_dont_show_for_nonsubscriber(self):
        response = self.authorized_client.get(reverse("follow_index"))
        self.assertNotIn(self.post_sub, response.context.get("page"))

    def test_authorized_user_can_comment(self):
        form_data = {"text": "Текст комментария для теста"}
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
        self.assertTrue(self.post.comments.filter(
            text=form_data["text"]
        ).exists())

    def test_nonauthorized_user_cannot_comment(self):
        form_data = {"text": "Текст комментария"}
        count_comments = Comment.objects.all().count()
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
        self.assertEqual(Comment.objects.all().count(), count_comments)
