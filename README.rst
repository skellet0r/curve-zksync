curve-zksync
============

Host machine requirements:

#. GNU/Linux Operating System
#. Python 3.8+
#. Docker + docker-compose

Development
-----------

#. Clone the repository (including the submodules)

    .. code-block:: bash

        $ git clone --recurse-submodules

#. Install python requirements

    .. code-block:: bash

        $ pip install -r requirements.txt

#. Pull docker images for the zkSync v2 devnet

    .. code-block:: bash

        $ docker pull matterlabs/geth:latest
        $ docker pull postgres:12
        $ docker pull matterlabs/local-node:latest2.0

Testing
-------

#. Start the local zkSync v2 devnet in a separate process

    .. code-block:: bash

        $ cd lib/zksync-node && ./start.sh

    Note: The devnet takes approximately 2 minutes to initialize on its first run.

#. Run the test suite

    .. code-block:: bash

        $ ape test
