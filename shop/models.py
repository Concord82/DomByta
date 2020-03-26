from django.db import models
from django.utils.translation import ugettext_lazy as _
from mptt.models import MPTTModel, TreeForeignKey
from django.utils.html import mark_safe
from django.urls import reverse
from PIL import Image
from io import BytesIO
from django.core.files.uploadedfile import InMemoryUploadedFile
import sys
# Create your models here.


class Category(MPTTModel):
    name = models.CharField(max_length=200, db_index=True)
    slug = models.SlugField(max_length=200, unique=True)
    image = models.ImageField(_('Image'), upload_to='categories/%Y/%m-%d', default='../static/images/noimage.png')
    description = models.TextField(_('description'), blank=True)
    parent = TreeForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='children')

    def image_tag(self):
        return mark_safe('<img src="/media/%s" width="150" height="150" />' % (self.image))

    image_tag.short_description = _('Image product')
    image_tag.allow_tags = True

    def get_absolute_url(self):
        return reverse('catalog:product_list_by_category', args=[self.url_slug])

    def save(self, *args, **kwargs):
        # Opening the uploaded image
        im = Image.open(self.image)
        output = BytesIO()
        # Resize/modify the image
        im = im.resize((128, 128))
        # after modifications, save it to the output
        im.save(output, format='JPEG', quality=100)
        # change the imagefield value to be the newley modifed image value
        self.image = InMemoryUploadedFile(output, 'ImageField', "%s.jpg" % self.image.name.split('.')[0], 'image/jpeg',
                                          sys.getsizeof(output), None)
        output.seek(0)
        super(Category, self).save()

    class Meta:
        ordering = ('name',)
        verbose_name = 'category'
        verbose_name_plural = 'categories'

    def __str__(self):
        return self.name