
# Installing in Virtualenv

Install the virtualenv

```bash
pip3 install virtualenv
pip3 install virtualenvwrapper-win
```

# Install snakemake in Virtualenv for Windows

To create an installation in a virtual environment, use the following commands:
The version of python must be 2.7.

```bash
virtualenv -p python venv_win
./venv_win/Scripts/activate
pip install pandas
pip install matplotlib
pip install scipy
pip install xlrd
```

Note: To active on windows the virtualenv you must to execute:

```bash
Set-ExecutionPolicy Unrestricted -Force
```
# References

Python, Pip, virtualenv installation on Windows
http://timmyreilly.azurewebsites.net/python-pip-virtualenv-installation-on-windows/

virtualenv won't activate on windows
https://stackoverflow.com/questions/18713086/virtualenv-wont-activate-on-windows

# Contact
Jose Rodriguez <jmrodriguezc@cnic.es>