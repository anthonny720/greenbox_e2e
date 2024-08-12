import uuid

# from core.producer import producer
from django.contrib.auth.models import BaseUserManager, AbstractBaseUser, PermissionsMixin
from django.db import models
from django.db.models.signals import pre_save, post_delete
from django.dispatch import receiver
from django.utils.text import slugify


class Departments(models.Model):
    class Meta:
        verbose_name = 'Departmento'
        verbose_name_plural = 'Departmentos'
        ordering = ['name']

    name = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.name

    def get_staff(self):
        if self.staff_area.all().count() > 0:
            return [{'name': staff.name, 'last_name': staff.last_name, 'position': staff.position.name,
                     'area': self.name, } for staff in self.staff_area.all()]
        else:
            return []


class AccessUrl(models.Model):
    class Meta:
        verbose_name = 'URL de Acceso'
        verbose_name_plural = 'URL de Acceso'
        ordering = ['name']

    name = models.CharField(max_length=50, unique=True, verbose_name='Nombre')

    def __str__(self):
        return self.name


class Position(models.Model):
    class Meta:
        verbose_name = 'Cargo'
        verbose_name_plural = 'Cargos'
        ordering = ['name']

    name = models.CharField(max_length=50, unique=True, verbose_name='Cargo')
    salary = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True, verbose_name='Salario',
                                 default=0.00)

    def __str__(self):
        return self.name


def user_directory_path(instance, filename):
    return f'users/picture_{instance.slug}.{filename.split(".")[1]}'


def signature_directory_path(instance, filename):
    return f'users/signature_{instance.slug}.{filename.split(".")[1]}'


class UserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError("User must have an email address")

        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self.db)

        # item = {}
        # item['id'] = str(user.id)
        # item['email'] = user.email
        # item['username'] = user.username
        # producer.produce('user_registered', key='create_user', value=json.dumps(item).encode('utf-8'))

        return user

    def create_superuser(self, email, password, **extra_fields):
        user = self.create_user(email, password, **extra_fields)
        user.is_superuser = True
        user.is_staff = True
        user.save(using=self.db)
        return user


class UserAccount(AbstractBaseUser, PermissionsMixin):
    id = models.UUIDField(default=uuid.uuid4, unique=True, primary_key=True)
    email = models.EmailField(unique=True, verbose_name='Correo Electrónico')
    slug = models.SlugField(max_length=100, unique=True, blank=True, )
    position = models.ForeignKey(Position, on_delete=models.CASCADE, blank=True, null=True, verbose_name='Cargo')
    area = models.ForeignKey(Departments, on_delete=models.CASCADE, blank=True, null=True, verbose_name='Departamento')
    first_name = models.CharField(max_length=100, verbose_name='Nombres')
    last_name = models.CharField(max_length=100, verbose_name='Apellidos')
    signature = models.ImageField(upload_to=signature_directory_path, blank=True, null=True, verbose_name='Firma')
    is_active = models.BooleanField(default=True, verbose_name='Activo')
    is_online = models.BooleanField(default=False, verbose_name='En línea')
    is_staff = models.BooleanField(default=True, verbose_name='Staff')
    access_url = models.ManyToManyField(AccessUrl, blank=True, verbose_name='URL de Acceso')
    is_superuser = models.BooleanField(default=False, verbose_name='Super Usuario')
    picture = models.ImageField(upload_to=user_directory_path, blank=True, null=True,
                                default='media/users/default_profile.webp', verbose_name='Foto de Perfil')

    objects = UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name']

    def save(self, *args, **kwargs):
        username = self.first_name + self.last_name
        self.slug = slugify(username + str(uuid.uuid4())[:8])
        counter = 1
        while UserAccount.objects.filter(slug=self.slug).exists():
            self.slug = f"{self.slug}-{counter}"
            counter += 1
        super().save(*args, **kwargs)

    class Meta:
        verbose_name_plural = 'Usuario'
        verbose_name = 'Usuarios'

    def __str__(self):
        return self.email

    def get_full_name(self):
        return f"{self.first_name} {self.last_name}" if self.first_name and self.last_name else self.email

    def get_short_name(self):
        return self.first_name if self.first_name else self.email

    def get_signature_url(self):
        return self.signature.url if self.signature else None


@receiver(pre_save, sender=UserAccount)
def pre_save_user_signature(sender, instance, **kwargs):
    if not instance.pk:
        return
    try:
        old_file = sender.objects.get(pk=instance.pk).signature
        new_file = instance.signature
        if not old_file == new_file:
            old_file.delete(save=False)
    except sender.DoesNotExist:
        pass


@receiver(post_delete, sender=UserAccount)
def post_delete_user_signature(sender, instance, **kwargs):
    if instance.signature:
        instance.signature.delete(save=False)


@receiver(pre_save, sender=UserAccount)
def pre_save_user_picture(sender, instance, **kwargs):
    if not instance.pk:
        return
    try:
        old_file = sender.objects.get(pk=instance.pk).picture
        new_file = instance.picture
        if not old_file == new_file:
            old_file.delete(save=False)
    except sender.DoesNotExist:
        pass


@receiver(post_delete, sender=UserAccount)
def post_delete_user_picture(sender, instance, **kwargs):
    if instance.picture:
        instance.picture.delete(save=False)
