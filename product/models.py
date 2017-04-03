from django.contrib.auth.models import User
from django.core.cache import cache
from django.core.urlresolvers import reverse
from django.db import models
from django.db.models import F
from django.db.models.signals import post_save, post_delete
from django.template.defaultfilters import slugify


# Create your models here.
class Product(models.Model):
    name = models.CharField(max_length=200)
    description = models.TextField()
    slug = models.SlugField()
    price = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField()
    votes = models.IntegerField(default=0)
    image = models.ImageField(blank=True, upload_to='user_media')

    def get_absolute_url(self):
        return reverse('one_product',
                       kwargs={'slug': self.slug})

    def save(self, *args, **kwargs):
        self.slug = slugify(self.name)
        super(Product, self).save(*args, **kwargs)

    def __str__(self):
        return self.name


# increase product.votes by 1 after receiving a signal
def vote_saved_handler(sender, instance, **kwargs):
    Product.objects.filter(id=instance.product_id).update(votes=F('votes') + 1)


def invalidate_cache(sender, instance, **kwargs):
    cache.clear()


post_save.connect(invalidate_cache, sender=Product)
post_delete.connect(invalidate_cache, sender=Product)


class Votes(models.Model):
    user_id = models.IntegerField(null=False, default=0)
    product_id = models.IntegerField(null=False, default=0)
    date = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = (("user_id", "product_id"),)


# send signal
post_save.connect(vote_saved_handler, sender=Votes)


class Comment(models.Model):
    text = models.TextField()
    added_at = models.DateTimeField(blank=True, auto_now_add=True)
    product = models.ForeignKey(Product, related_name='comments', on_delete=models.CASCADE)
    author = models.ForeignKey(User, default=1)

    def __str__(self):
        return self.text

    def get_absolute_url(self):
        return reverse('one_product',
                       kwargs={'slug': self.product.slug})


post_save.connect(invalidate_cache, sender=Comment)
post_delete.connect(invalidate_cache, sender=Comment)
