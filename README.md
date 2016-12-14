# DDFacet
A facet-based radio imaging package

Copyright (C) 2013-2016  Cyril Tasse, l'Observatoire de Paris,
SKA South Africa, Rhodes University

This program is free software; you can redistribute it and/or
modify it under the terms of the GNU General Public License
as published by the Free Software Foundation; either version 2
of the License, or (at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

## (Users/Recommended) Docker-based installation
Simply pull the latest DDFacet and build the Docker image:
```
git clone git@github.com:cyriltasse/DDFacet.git
cd DDFacet
docker build -t ddf .
```
You should now be able to run DDFacet in a container. Note that your parsets must have filenames relative to the mounted volume inside the container, for instance:
```
docker run --shm-size 6g -v /scratch/TEST_DATA:/mnt ddf /mnt/test-master1.parset
```
Important: if you ran ```git submodule update --init --recursive``` before you may need to remove the cached SkyModel before building the docker image with ```git rm --cached SkyModel```

## (Users): building and installing DDFacet from an Ubuntu 14.04 base

1. You need to add in the radio-astro ppa if you don't already have it:

    ```bash
    sudo add-apt-repository ppa:radio-astro/main
    ```

2. Install each of the dependencies. The latest full list of apt dependencies can be be found in the [Dockerfile](https://github.com/cyriltasse/DDFacet/blob/master/Dockerfile)

3. Then, clone the repository:

    ```bash
    git clone git@github.com:cyriltasse/DDFacet.git
    ```

4. Once checked out you can run the following to pull module dependencies

    ```bash
    git submodule update --init --recursive
    ```

### Installation in user directory

Important: ensure that ```$HOME/.local``` folder is in your ```PATH``` and ```$HOME/.local/lib/python2.7/site-packages``` is in ```PYTHONPATH``` if you want to install using ```--user```.

Navigate to the directory below your checked out copy of DDFacet and run:

```bash
pip install DDFacet/ --user
```

This will install the DDF.py driver files to your .local/bin under Debian

### Virtual Environment installation

Alternatively, create a virtual environment, activate it and run the install. Under 14.04 the bootstrap virtual environment is helpful for upgrading the pip, setuptools and virtualenv packages to more recent (and correct) versions.

```bash
$ virtualenv $HOME/bootstrap
$ source $HOME/bootstrap/bin/activate
(bootstrap) $ pip install -U pip setuptools virtualenv
(bootstrap) $ virtualenv --system-site-packages $HOME/ddfvenv
$ deactive
$ source $HOME/ddfvenv/bin/activate
(ddfvenv) $ pip install DDFacet/
```
Adding the `--system-site-packages` directive ensures that the virtualenv has access to system packages (such as meqtrees).

### Montblanc installation

[Montblanc](https://github.com/ska-sa/montblanc) requires DDFacet to be installed in a virtual environment. **This section requires the DDFacet virtual environment to be activated**:

1. Clone montblanc and checkout the commit to build

    ```bash
    git clone https://github.com/ska-sa/montblanc.git
    cd montblanc
    git checkout 339eb8f8a0f4a44243f340b7f33882fd9656858b
    ```

2. Install the tensorflow CPU [0.11.0][tf_pip_install] release:

    ```bash
    pip install https://storage.googleapis.com/tensorflow/linux/cpu/tensorflow-0.11.0-cp27-none-linux_x86_64.whl
    ```

    If you want GPU acceleration and you have CUDA installed, you can alternatively try installing the tensorflow [GPU version][tf_pip_install].

3. Build montblanc's tensorflow operations:

    ```bash
    cd montblanc/montblanc/impl/rime/tensorflow/rime_ops
    make -j 8
    ```
4. Install montblanc in development mode:

    ```bash
    python setup.py develop
    ```


## Configure max shared memory

Running DDFacet on large images requires a lot of shared memory. Most systems limit the amount of shared memory to about 10%. To increase this limit add the following line to your ``/etc/default/tmpfs`` file:

```
SHM_SIZE=100%
```

A restart will be required for this change to reflect. If you would prefer a once off solution execute the following line

```
sudo mount -o remount,size=100% /run/shm
```

## (Developers): setting up your dev environment

### (easy) Build using setup.py
To setup your local development environment navigate to the DDFacet directory and run
```
git submodule update --init --recursive
python setup.py develop --user (to remove add a --uninstall option with this)
python setup.py build

IMPORTANT NOTE: You may need to remove the development version before running PIP when installing
```
### (debugging) Build a few libraries (by hand with custom flags):

```
(cd DDFacet/ ; mkdir cbuild ; cd cbuild ; cmake -DCMAKE_BUILD_TYPE=Release .. ; make)
# or -DCMAKE_BUILD_TYPE=RelWithDebInfo for developers: this includes debugging symbols
# or -DCMAKE_BUILD_TYPE=Debug to inspect the stacks using kdevelop
```

## Acceptance tests
### Paths
Add this to your ``.bashrc``

```
export DDFACET_TEST_DATA_DIR=[folder where you keep the acceptance test data and images]
export DDFACET_TEST_OUTPUT_DIR=[folder where you want the acceptance test output to be dumped]
```

### To test your branch against the master branch using Jenkins
Most of the core use cases will in the nearby future have reference images and an automated acceptance test.

Please **do not** commit against cyriltasse/master. The correct strategy is to branch/fork and do a pull request on Github
to merge changes into master. Once you opened a pull request add the following comment: "ok to test". This will let the Jenkins server know to start testing. You should see that the pull request and commit statusses shows "Pending". If the test succeeds you should see "All checks have passed" above the green merge button. Once the code is reviewed it will be merged into the master branch.

### To run the tests on your local machine:
You can run the automated tests by grabbing the latest set of measurements and reference images from the web and
extracting them to the directory you set up in your **DDFACET_TEST_DATA_DIR** environment variable. You can run
the automated tests by navigating to your DDFacet directory and running nosetests.

Each of the test cases is labeled by a class name and has reference images and a parset file with the same
name, ie. if the test case that has failed is called "TestWidefieldDirty" the reference images will be called the same. You should investigate the reason for any severe discrepancies between the output of the test case and the images produced by your changed codebase. See the docstring at the top of the class ClassCompareFITSImage for help and
filename conventions.

Acceptance test data can be found on the Jenkins server in the **/data/test-data** directory.

### Adding more tests and creating new reference images.

To resimulate images and add more tests:
In the Jenkins server data directory run **make** to resimulate and set up new reference images. This should only be done with the **origin/master** branch - not your branch or fork! You should manually verify that all the reference images are correct when you regenerate them. Each time you add a new option to DDFacet also add an option to the makefile in this directory. Once the option is set up in the makefile you can build the reference images on Jenkins.

[tf_pip_install]: https://github.com/tensorflow/tensorflow/blob/master/tensorflow/g3doc/get_started/os_setup.md#pip-installation


