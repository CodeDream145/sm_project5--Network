from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
import json
from django.urls import reverse

from .models import *


def index(request):
    all_posts = Posts.objects.all().order_by('-timestamp')

    all_page = Paginator(all_posts, 10)
    page_number = request.GET.get("page")
    page_obj = all_page.get_page(page_number)

    return render(request, "network/index.html", {
        "all_posts": page_obj,
    })


def login_view(request):
    if request.method == "POST":

        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, "network/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "network/login.html")

@login_required(login_url="login")
def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))


def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(request, "network/register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "network/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "network/register.html")

@login_required(login_url="login")
def new_post(request):
    if request.method == "POST":
        post = request.POST.get("new_post")
        user = request.user

        if not str(post).strip():
            return render(request, "network/index.html", {
                "error_message": "Nothing to post"
            })

        post = Posts(user = user, post = post,)
        post.save()
        return HttpResponseRedirect(reverse("index"))
    
def profile_page(request, username):
    user_profile = User.objects.get(username=username)
    my_posts = user_profile.my_posts.all().order_by('-timestamp')

    user_posts = Paginator(my_posts, 10)
    page_number = request.GET.get("page")
    page_obj = user_posts.get_page(page_number)
    
    return render(request, "network/profile.html",{
        "user_profile":user_profile,
        "user_posts": page_obj,
    })

@login_required(login_url="login")
def follow(request, username):
    if request.method == "POST":
        u_t_f = User.objects.get(username = username)
        me = User.objects.get(username = request.user)

        try:
           me.my_followings.followings.add(u_t_f)
        except ObjectDoesNotExist:
            my_following = Followings(user = me)
            my_following.save()
            me.my_followings.followings.add(u_t_f)
        me.save()

        try:
            u_t_f.my_followers.followers.add(me)
        except ObjectDoesNotExist:
            u_f = Followers(user = u_t_f)
            u_f.save()
            u_t_f.my_followers.followers.add(me)
        u_t_f.save()

        return HttpResponseRedirect(reverse("profile_page", args=[username]))

@login_required(login_url="login")
def unfollow(request, username):
    if request.method == "POST":
        u_t_f = User.objects.get(username = username)
        me = User.objects.get(username = request.user)

    try:
        me.my_followings.followings.remove(u_t_f)
    except ObjectDoesNotExist:
        my_following = Followings(user = me)
        my_following.save()
        me.my_followings.followings.remove(u_t_f)
    me.save()

    try:
        u_t_f.my_followers.followers.remove(me)
    except ObjectDoesNotExist:
        u_f = Followers(user = u_t_f)
        u_f.save()
        u_t_f.my_followers.followers.remove(me)
    u_t_f.save()

    return HttpResponseRedirect(reverse("profile_page", args=[username]))

@login_required(login_url="login")
def following(request):
    try:
        all_following = request.user.my_followings.followings.all()
    except ObjectDoesNotExist:
        return render(request, "network/following.html")
    
    all_posts = Posts.objects.filter(user__in=all_following).order_by('-timestamp')

    all_page = Paginator(all_posts, 10)
    page_number = request.GET.get("page")
    page_obj = all_page.get_page(page_number)

    return render(request, "network/following.html", {
        "all_posts": page_obj,
    })

@login_required(login_url="login")
@csrf_exempt
def edit_post(request, post_id):
    if request.method != "POST":
        return JsonResponse({"error": "POST request required."}, status=400)

    data = json.loads(request.body)
    post_content = data.get('content')
    
    try:
        post = Posts.objects.get(pk = post_id)
    except ObjectDoesNotExist:
        return JsonResponse({"error": "Post doesnot exists."}, status=404)
    
    if not (post.user == request.user):
        return JsonResponse({"error": "Forbidden Action"}, status=403)

    if len(post_content) <= 0:
        return JsonResponse({"error": "Invalid Post"}, status=400)
    
    post.post = post_content
    post.save()

    return JsonResponse({"message": "Post updated Successfully"}, status=201)
    
@login_required(login_url='login')
@csrf_exempt
def likes(request, post_id):
    if request.method != 'POST':
        return JsonResponse({'error': 'POST request required.'}, status=400)

    data = json.loads(request.body)
    like_status = data.get('like_status')

    if not like_status in [True, False]:
        return JsonResponse({'error': 'Not a valid request'}, status=400)

    try:
        post = Posts.objects.get(pk=post_id)
    except ObjectDoesNotExist:
        return JsonResponse({'error': 'Post does not exist.'}, status=404)

    if not hasattr(post, 'likes'):
        Likes.objects.create(post=post)

    if like_status:
        if request.user not in post.likes.liked_users.all():
            post.likes.liked_users.add(request.user)
            return JsonResponse({'message': 'Post Liked Successfully'}, status=201)
        else:
            return JsonResponse({'message': 'Post Already Liked Successfully'}, status=201)
    elif not like_status:
        if request.user in post.likes.liked_users.all():
            post.likes.liked_users.remove(request.user)
            return JsonResponse({'message': 'Post Unliked Successfully'}, status=201)
        else:
            return JsonResponse({'message': 'Post Already Unliked Successfully'}, status=201)