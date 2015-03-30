from distutils.core import setup
import os

version = "0.1.9"

# Compile the list of packages available, because distutils doesn't have
# an easy way to do this.
packages, data_files = [], []
root_dir = os.path.dirname(__file__)
if root_dir:
    os.chdir(root_dir)

for dirpath, dirnames, filenames in os.walk('django_sockjs_server'):
    # Ignore dirnames that start with '.'
    for i, dirname in enumerate(dirnames):
        if dirname.startswith('.'): del dirnames[i]
    if '__init__.py' in filenames:
        pkg = dirpath.replace(os.path.sep, '.')
        if os.path.altsep:
            pkg = pkg.replace(os.path.altsep, '.')
        packages.append(pkg)
    elif filenames:
        prefix = dirpath[13:]
        for f in filenames:
            data_files.append(os.path.join(prefix, f))


setup(name='django-sockjs-server',
      version=version,
      description='SockJS server for Django',
      author='Sergey Kravchuk',
      author_email='alfss.obsd@gmail.com',
      url='https://github.com/alfss/django-sockjs-server',
      download_url='https://github.com/alfss/django-sockjs-server/archive/0.1.9.tar.gz',
      package_dir={'django_sockjs_server': 'django_sockjs_server'},
      packages=packages,
      install_requires=['sockjs-tornado >= 1.0.0',
                        'pika >= 0.9.12',
                        'redis >= 2.9.1'
      ],
      package_data={'django_sockjs_server': data_files},
      classifiers=['Development Status :: 5 - Production/Stable',
                   'Environment :: Web Environment',
                   'Framework :: Django',
                   'Intended Audience :: Developers',
                   'License :: OSI Approved :: BSD License',
                   'Operating System :: OS Independent',
                   'Programming Language :: Python',
                   'Topic :: Internet :: WWW/HTTP :: HTTP Servers'],
      zip_safe=False,
)
