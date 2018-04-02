runtastic2strava
================

This a Python script used to send sport sessions from Runtastic_ to Strava_.

To run it, export the following variables in your environment and run the
script::

  export RUNTASTIC_EMAIL="foo@example.com"
  export RUNTASTIC_PASS="s3cur3"
  export RUNTASTIC_USERNAME="foo"
  export STRAVA_ACCESS_TOKEN="22kdwd021k210ncbqdwq"

You can use the `get-token.py` script to get a Strava access token.

By default it only send activities for the last four days, but you can
extend that range if you wish to synchronize older sessions.

.. _runtastic: http://runtastic.com
.. _strava: http://strava.com
