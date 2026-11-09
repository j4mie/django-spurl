SECRET_KEY = "DUMMY_SECRET_KEY"  # noqa: S105

# Application definition

PROJECT_APPS = ["spurl.tests", "spurl"]

INSTALLED_APPS = [
    *PROJECT_APPS,
]

ROOT_URLCONF = "spurl.tests.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "OPTIONS": {
            "builtins": ["spurl.templatetags.spurl"],
        },
    },
]
