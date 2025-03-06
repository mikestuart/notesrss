
SITENAME = 'Evernote Notes Blog (Pelican)'
SITEURL = 'https://test.evernoterss.com'  # Adjust this when deploying

PATH = 'content'
TIMEZONE = 'UTC'
DEFAULT_LANG = 'en'
THEME = 'themes/notmyidea'
FEED_ALL_RSS = 'feeds/all.rss.xml'
FEED_ALL_ATOM = 'feeds/all.atom.xml'
DEFAULT_PAGINATION = 10
AUTHOR = "Evernote User"
STATIC_PATHS = ['articles']
STATIC_EXCLUDE_SOURCES = True
PLUGIN_PATHS = ['pelican-plugins']
PLUGINS = []
SUMMARY_MAX_LENGTH = 50  # Adjust this value as needed
RSS_FEED_SUMMARY_ONLY = True  # Include full content in RSS feed
    