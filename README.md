# FruityVSTStats
Made by [Noway](https://linktr.ee/n0way)

This is a little python script I made that scans through all the FL Studio flp project files in the folder you select and gives you stats about the vsts you use and a few extra things.\
It uses the [PyFLP](https://github.com/demberto/PyFLP) library to read the flps 

NOTE : this script automatically skips the "Backup" folders that FL creates

# Requirements
Install **Python 3.10** from [here](https://www.python.org/downloads/)\
WARNING : Python 3.11 and 3.12 **WILL NOT WORK** because of a [bug](https://github.com/demberto/PyFLP/issues/183) in the library I use to read flps

# How to use
- Run "run_scan.bat" and wait for the libraries to install
- Select the folder you want to scan
- Wait for the scan to finish
- Select the folder you want to save the stats in
- Enjoy !
