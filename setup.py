from setuptools import setup

from pathlib import Path
this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text()

setup(
    name='django_admin_workflow',
    version='0.8.2',
    description='A workflow app for django admin',
    url='https://github.com/esimorre/django-admin-workflow',
    
    long_description=long_description,
    long_description_content_type='text/markdown',
    
    platforms=['any'],
    packages=["django_admin_workflow", "django_admin_workflow.management.commands",
              "django_admin_workflow.test", "django_admin_workflow.migrations"],
    package_data = {"django_admin_workflow.locale": ["*.po", "*.mo"],
                    "django_admin_workflow.templates": ["*.html", "*.js"]},
    include_package_data=True,
    zip_safe=False,
    keywords=['django', 'workflow'],
    install_requires=['django', 'tomli'],
    classifiers=[  # Optional
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Framework :: Django",
        "License :: OSI Approved :: BSD License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Programming Language :: Python :: 3 :: Only"
    ],
    project_urls = {  # Optional
        "Bug Reports": "https://github.com/esimorre/django-admin-workflow/issues",
        "Source": "https://github.com/esimorre/django-admin-workflow",
    },
)