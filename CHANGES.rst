
Changelog
---------

0.6.6
~~~~~


* Added support for an except clause to remove all but specifed query vars.

0.6.5
~~~~~


* Added support for Django 2.x and dropped support for older and
  non-LTS version of Django.

0.6.4
~~~~~


* Getting ready for Django 1.10 release.
* Dropped support for Django 1.3 and older.

0.6.3
~~~~~


* Django 1.9 compatible (Albert Koch)

0.6.2
~~~~~


* Add support for template variables to ``remove_query_param``.
* Handle auth parameters to be able to add username:password to URLs.

0.6.1
~~~~~


* Python 3 compatible!

0.6
~~~


* Upgrade URLObject dependency to 2.0

0.5
~~~


* Fix typos in changelog.
* Add family of arguments (\ ``_from``\ ) for combining URLs.
* Add ``toggle_query`` argument.

0.4
~~~


* Upgrade URLObject dependency to 0.6.0
* Add ``remove_query_param`` argument.
* Add support for template tags embedded within argument values.
* Extensive refactoring.

0.3
~~~


* Add ``set_query`` argument.

0.2
~~~


* Add ``as`` argument to insert generated URL into template context.

0.1
~~~


* Initial release.
