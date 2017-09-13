import setuptools

setuptools.setup(
    name='pack-me-up',
    version='1',
    author='Ben Whitney',
    author_email='ben.e.whitney@post.harvard.edu',
    url='https://github.com/ben-e-whitney/pack-me-up',
    description='Script to make packing lists factoring in the weather.',
    license='GPLv3',
    python_requires='>=3',
    packages=setuptools.find_packages(),
    install_requires=['pyxdg', 'pywapi'],
    entry_points={'console_scripts': ['pack-me-up=pack_me_up.main:main']},
)
