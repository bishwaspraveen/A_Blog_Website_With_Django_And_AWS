from typing import Any, Dict
from django.db.models.query import QuerySet
from django.shortcuts import render, get_object_or_404
from .models import Post
from django.views.generic import ListView, DeleteView
from .forms import CommentForm
from django.views import View
from django.http import HttpResponseRedirect
from django.urls import reverse

# Create your views here.

""" def starting_page(request):
    #Ordering the posts in descending order by date field and extracting the first three posts.
    latest_posts = Post.objects.all().order_by("-date")[:3]
    return render(request, "my_blog/index.html", {
        "posts": latest_posts
    }) """

class StartingPageView(ListView):
    template_name = "my_blog/index.html"
    model = Post
    ordering = ["-date"]
    context_object_name = "posts"

    def get_queryset(self):
        queryset = super().get_queryset()
        data = queryset[:3]
        return data

""" def posts(request):
    all_posts = Post.objects.all().order_by("-date")
    return render(request, "my_blog/all-posts.html", {
        "all_posts": all_posts
        }) """

class AllPostsView(ListView):
    template_name = "my_blog/all-posts.html"
    model = Post
    ordering = ["-date"]
    context_object_name = "all_posts"

""" def post_detail(request, slug):
    #Post.objects.get(slug=slug)
    identified_post = get_object_or_404(Post, slug=slug) 
    return render(request, "my_blog/post-detail.html", {
        "post": identified_post,
        "post_tags": identified_post.tags.all()
    }) """

""" class PostDetailView(DeleteView):
    template_name = "my_blog/post-detail.html"
    model = Post
    # Slug here is auto generated. So we dont have to handle it manually. However, we have to handle tags manually as shown below.

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["post_tags"] = self.object.tags.all()
        context["comment_form"] = CommentForm()
        return context """
    
class PostDetailView(View):
    def is_stored_post(self, request, post_id):
        stored_posts = request.session.get("stored_posts")
        if stored_posts is not None:
            is_saved_for_later = post_id in stored_posts
        else:
            is_saved_for_later = False
        
        return is_saved_for_later

    def get(self, request, slug):
        post = Post.objects.get(slug=slug)
        
        context = {
            "post": post,
            "post_tags": post.tags.all(),
            "comment_form": CommentForm(),
            "comments": post.comments.all().order_by("-id"),
            "saved_for_later": self.is_stored_post(request, post.id)
        }
        return render(request, "my_blog/post-detail.html", context)

    def post(self, request, slug):
        comment_form = CommentForm(request.POST)
        post = Post.objects.get(slug=slug)

        if comment_form.is_valid():
            comment = comment_form.save(commit=False)
            comment.post = post
            comment.save()
            return HttpResponseRedirect(reverse("post-detail-page", args=[slug]))
        else:
            context={
                "post": post,
                "post_tags": post.tags.all(),
                "comment_form": comment_form,
                "comments": post.comments.all().order_by("-id"),
                "saved_for_later": self.is_stored_post(request, post.id)
            }
            return render(request, "my_blog/post-detail.html", context)
        
class ReadLaterView(View):
    def get(self, request):
        stored_posts = request.session.get("stored_posts")

        context = {}

        if stored_posts is None or len(stored_posts) == 0:
            context["posts"] = []
            context["has_posts"] = False 
        else:
            posts = Post.objects.filter(id__in=stored_posts)
            context["posts"] = posts
            context["has_posts"] = True 

        return render(request, "my_blog/stored-posts.html", context)


    def post(self, request):
        stored_posts = request.session.get("stored_posts")

        if stored_posts is None:
            stored_posts = []

        if int(request.POST["post_id"]) not in stored_posts:
            stored_posts.append(int(request.POST["post_id"]))
        else:
            stored_posts.remove(int(request.POST["post_id"]))

        request.session["stored_posts"] = stored_posts

        return HttpResponseRedirect("/")
