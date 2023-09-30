from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    pass

class Posts(models.Model):
    user = models.ForeignKey(User, related_name="my_posts", on_delete=models.CASCADE)
    post = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self) :
        return f"{self.id} by User:{self.user} on [{self.timestamp}]"

class Followers(models.Model):
    user = models.OneToOneField(User, related_name="my_followers", on_delete=models.CASCADE)
    followers = models.ManyToManyField(User)

    def __str__(self):
        return f"{self.user} with {self.followers.count()} Followers."

class Followings(models.Model):
    user = models.OneToOneField(User, related_name="my_followings", on_delete=models.CASCADE)
    followings = models.ManyToManyField(User)
    
    def __str__(self):
        return f"{self.user} Follows {self.followings.count()} users."

class  Likes(models.Model):
    post = models.OneToOneField(Posts, related_name="likes", on_delete=models.CASCADE)
    liked_users = models.ManyToManyField(User)

    def __str__(self):
        return f"{self.post} with {self.liked_users.count()}"