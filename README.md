
This package provides utilities for specifying binary data algorithmically,
and executing the specifications to produce the data.

Requirements
============
In addition to a standard Python installation, this package depends on:

 - SpiNNMachine

These requirements can be install using `pip`:

    pip install SpiNNMachine

User Installation
=================
If you want to install for all users, run:

    sudo pip install DataSpecification

If you want to install only for yourself, run:

    pip install DataSpecification --user

To install in a `virtualenv`, with the `virtualenv` enabled, run:

    pip install DataSpecification

Developer Installation
======================
If you want to be able to edit the source code, but still have it referenced
from other Python modules, you can set the install to be a developer install.
In this case, download the source code, and extract it locally, or else clone
the git repository:

    git clone http://github.com/SpiNNakerManchester/DataSpecification.git

To install as a development version which all users will then be able to use,
run the following where the code has been extracted:

    sudo pip install -e .

To install as a development version for only yourself, run:

    pip install -e . --user

To install as a development version in a `virtualenv`, with the `virutalenv`
enabled, run:

    pip install -e .

Test Installation
=================
To be able to run the unitests add [Test] to the pip installs above

    pip install -e .[Test]

Documentation
=============
[DataSpecification python documentation](http://dataspecification.readthedocs.io)
<br>
[Alternate location](https://spinnakermanchester.github.io/DataSpecification/)

[Combined python documentation](http://spinnakermanchester.readthedocs.io)
