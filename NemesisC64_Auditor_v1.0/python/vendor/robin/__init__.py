# Makes 'robin' a proper Python package for package-style imports.
# The runner will try both:
#   import search
#   import robin.search
__all__ = ["search", "scrape"]
__version__ = "1.0"
