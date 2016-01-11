from setuptools import setup, find_packages
import os

setup(
    name='stt-watson',
    version='1.0.1',
    packages=['utils', 'config', 'recording', 'watson_client', 'watson_client.websocket', 'stt_watson'],
    url='https://github.com/HomeHabbit/stt-watson',
    license='MIT',
    author='Arthur Halet',
    author_email='arthurh.halet@gmail.com',
    long_description=open(os.path.join(os.path.dirname(__file__), 'README.md')).read(),
    description='Continuous speech to text using watson in python with websocket and record from microphone',
    keywords='text-to-speech watson websocket',
    classifiers=['Topic :: Multimedia :: Sound/Audio :: Analysis',
                 'Topic :: Multimedia :: Sound/Audio :: Capture/Recording',
                 'Topic :: Software Development :: Libraries',
                 'License :: OSI Approved :: MIT License'],
    platforms='ALL',
    install_requires=[
        'autobahn>=0.10.9',
        'pyOpenSSL>=0.13.1',
        'requests>=2.8.1',
        'Twisted>=13.2.0',
        'txaio>=2.0.4',
        'pyaudio>=0.2.9',
        'pyyaml>=3.08',
    ],
    package_data={
        'config': ['config.sample.yml']
    },
    entry_points={
        'console_scripts': [
            'stt-watson=stt_watson.__main__:main',
        ],
    },
)
