try:
    import musicbrainz
except ImportError:
    print "\nWARNING: cannot find MusicBrainz module.  cdscrobbler will not work without it.\n"

from distutils.core import setup
setup(
    name='cdscrobbler', version='1.0',
    author='Ross Burton', author_email='ross@burtonini.com',
    py_modules=['scrobbler'],
    scripts=['cdscrobbler.py']
    )
