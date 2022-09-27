from django.core.exceptions import ValidationError
import os

def allow_only_image_validator(value):
    # covr-image.jpg [1] will select .jpg
    file_extension = os.path.splitext(value.name)[1]
    valid_extensions = [
        '.png', '.jpg', '.jpeg'
    ]

    if not file_extension.lower() in valid_extensions:
        raise ValidationError('Unsupported file extension. allowed extensions are: ' + str(valid_extensions))

