"""
Management command to re-upload local cover images to Cloudinary.

Finds all Book, Script, and Poem objects that have a cover_image value,
opens the corresponding local file from the media/ directory, and
re-saves it through the Django storage backend (Cloudinary when configured).

Usage:
    python manage.py reupload_covers
"""
import os
from django.conf import settings
from django.core.files import File
from django.core.management.base import BaseCommand
from newapp.models import Book, Script, Poem


class Command(BaseCommand):
    help = 'Re-upload local cover images to Cloudinary'

    def handle(self, *args, **options):
        media_root = settings.MEDIA_ROOT or os.path.join(settings.BASE_DIR, 'media')
        models = [
            ('Book', Book),
            ('Script', Script),
            ('Poem', Poem),
        ]

        for label, Model in models:
            items = Model.objects.exclude(cover_image='').exclude(cover_image__isnull=True)
            self.stdout.write(f'\n--- {label}s with cover_image: {items.count()} ---')

            for item in items:
                old_path = item.cover_image.name  # e.g. "book_covers/file.webp"
                local_file = os.path.join(media_root, old_path)

                if not os.path.exists(local_file):
                    self.stdout.write(self.style.WARNING(
                        f'  SKIP {label} #{item.id} "{item.title}" — '
                        f'local file not found: {local_file}'
                    ))
                    continue

                self.stdout.write(f'  Uploading {label} #{item.id} "{item.title}" ({old_path})...')
                try:
                    with open(local_file, 'rb') as f:
                        filename = os.path.basename(old_path)
                        item.cover_image.save(filename, File(f), save=True)
                    self.stdout.write(self.style.SUCCESS(
                        f'    ✓ Done → {item.cover_image.url}'
                    ))
                except Exception as e:
                    self.stdout.write(self.style.ERROR(
                        f'    ✗ Failed: {e}'
                    ))

        self.stdout.write(self.style.SUCCESS('\nFinished re-uploading covers.'))
