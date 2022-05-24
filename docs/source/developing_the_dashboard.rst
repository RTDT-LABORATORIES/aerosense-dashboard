.. _developing_the_dashboard:

========================
Developing The Dashboard
========================

Using a ``.devcontainer``
=========================

The quickest way to get started is to open the project in ``vscode``, since a remote
``.devcontainer`` is prepared with everything pre-installed and configured.

#. Make sure you have docker desktop installed.
#. Clone the repo
#. Add a credentials file to the project root (see `authentication <authentication>`_ for how to get it). Make sure to rename it like ``gcp-credentials-<name>.json``, e.g. mine is ``gcp-credentials-developer-thclark.json``
#. Add a .env file to the project root, whose contents look like:

   .. code-block::

      GOOGLE_APPLICATION_CREDENTIALS="gcp-credentials-<name>.json"

#. Open the project with vscode, and choose the "Open in remote containers" option.
#. If it's your first time, wait for a while whilst everything installs.

.. TIP::

   Renaming the credentials file to ``gcp-credentials-<...>`` is pretty important - it means you'll never accidentally commit your credentials to git.
   Committing credentials means publishing access to all Aerosense data to the entire world!!!

.. ATTENTION::

   The container will not start without a valid ``.env`` file present.


Starting the dashboard
======================

To open up a local version of the dashboard, type (into the terminal):

.. code-block::

   panel serve
