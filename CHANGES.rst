Changes
-------

0.6.8 (2021-11-15)
~~~~~~~~~~~~~~~~~~

* Fix ``toggle_query`` support when one word is a fragment of the other.

0.6.7 (2020-05-22)
~~~~~~~~~~~~~~~~~~

* Fixed MANIFEST.in

0.6.6 (2019-03-29)
~~~~~~~~~~~~~~~~~~

* Added support for an except clause to remove all but specifed query vars.

0.6.5 (2018-05-09)
~~~~~~~~~~~~~~~~~~

* Added support for Django 2.x and dropped support for older and
  non-LTS version of Django.

0.6.4 (2015-12-26)
~~~~~~~~~~~~~~~~~~

* Getting ready for Django 1.10 release.
* Dropped support for Django 1.3 and older.

0.6.3 (2015-12-17)
~~~~~~~~~~~~~~~~~~

* Django 1.9 compatible (Albert Koch)

0.6.2 (2015-09-17)
~~~~~~~~~~~~~~~~~~

* Add support for template variables to ``remove_query_param``.
* Handle auth parameters to be able to add username:password to URLs.

0.6.1 (2015-07-14)
~~~~~~~~~~~~~~~~~~

* Python 3 compatible!

0.6.0 (2012-02-23)
~~~~~~~~~~~~~~~~~~

* Upgrade URLObject dependency to 2.0

0.5.0 (2011-12-14)
~~~~~~~~~~~~~~~~~~

* Fix typos in changelog.
* Add family of arguments (\ ``_from``\ ) for combining URLs.
* Add ``toggle_query`` argument.

0.4.0 (2011-12-07)
~~~~~~~~~~~~~~~~~~

* Upgrade URLObject dependency to 0.6.0
* Add ``remove_query_param`` argument.
* Add support for template tags embedded within argument values.
* Extensive refactoring.

0.3.0 (2011-08-18)
~~~~~~~~~~~~~~~~~~

* Add ``set_query`` argument.

0.2.0 (2011-08-08)
~~~~~~~~~~~~~~~~~~

* Add ``as`` argument to insert generated URL into template context.

0.1.0 (2011-07-29)
~~~~~~~~~~~~~~~~~~

* Initial release.
