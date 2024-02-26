# Installation

## Using `install.bat`
Install [miniconda3](https://docs.conda.io/en/latest/miniconda.html). During the installation make sure to add conda to the path environment variables when prompted.

Once installed run:
```powershell
.\install.bat
```

Next, run the command
```powershell
conda activate antecedent_moisture_model-prod
```

This is the preferred method to install antecedent_moisture_model, as it will always install all needed libraries. Alternatively, follow the steps below.

## From source code via `conda`
In the .\conda folder run the following command to install the dependencies to your system:

```powershell
.\create_env.bat
```

Next, run the command
```powershell
conda activate antecedent_moisture_model-prod
```

From the antecedent_moisture_model head directory ".\antecedent_moisture_model" run the following:
```powershell
pip install -e .
```


If you don't have `pip`_ installed, this `Python installation guide`_ can guide
you through the process.

.. _pip: https://pip.pypa.io
.. _Python installation guide: http://docs.python-guide.org/en/latest/starting/installation/


## From sources using `setup.py`


The sources for antecedent_moisture_model can be downloaded from the `GitHub repo`_.

You can either clone the public repository:

.. code-block:: console

    $ git clone git://github.com/confluencywater/antecedent_moisture_model

Or download the `tarball`_:

.. code-block:: console

    $ curl -OJL https://github.com/confluencywater/antecedent_moisture_model/tarball/master

Once you have a copy of the source, you can install it with:

.. code-block:: console

    $ python setup.py install


.. _GitHub repo: https://github.com/confluencywater/antecedent_moisture_model
.. _tarball: https://github.com/confluencywater/antecedent_moisture_model/tarball/master
