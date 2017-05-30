from django.db import models

class Photo(models.Model):
    title = models.CharField(max_length=200)
    date = models.DateTimeField('Date captured')
    post_img = models.ImageField(upload_to='pictures/thumb')
    uploaded = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title
