# simplevc - A simple Python version control package


A simple library built for version control, backward compatibility and command line scripts on non-standard functions. 

Version control is an important practice in writing program. However, due to the large variations across experiments, sometimes researchers may need to build new customized pipelines to handle data generated under various conditions. As data can be generated in multiple batches with many tiny modifications among them, researchers need to update the pipeline rapidly. As time is tight, it could be very challenging to keep everything under standard version control. 

This package provides several utilities to make life easier for the researchers when building the pipelines:

1. Easy version-control and backward compatibility - One should be able to repeat the analysis and generate the same result, even on an older version of the pipeline.

2. Compatibility between python functions and command line scripts - the pipeline can be called as a python function, or in a bash script.

3. Reusable in the future - The pipelines can be quickly modified and reused in future analysis.

4. Fast to build and easy to learn - Minimize the time to build the pipeline.

Here we build this simple version-control library that fulfills the above requirements. Researchers do not need to make drastic changes in the codes, but only:

1. Register the module the the version-control system.

2. Add version number to the function name.

3. Add a decorator to the function.


The ideas behind this simple version control system:

* There is NO guarantee that the input, output nor behavior of any two versions of the same function remain the same. 

* All the old-version functions should be kept for backward compatibility. They should not be modified (Create a new one with newer version number instead).

* There is no restriction on the function arguments, except the argument name `version` is reserved for version control.

* This is a simple and fast but NOT a standard version control system. 

## Installation

```sh
pip install simplevc
```

## Usage

### Example module registered for version control

```python
### example/pm.py ###

# Suppose you want to set simple version control in pm.py

# These three lines are required to register this module with version control
import sys
import simplevc
simplevc.register(sys.modules[__name__])

# Definition of some_method with version 20200601
@vc
def _some_method_20200601(a, b, c):
	"""
	This is the docstring for method _some_method_20200601
	"""
	print("Call from _some_method_20200601", a, b, c)

# Definition of some_method with version 20200721
@vc
def _some_method_20200721(a, b, c, d):
	"""
	This is the docstring for method _some_method_20200721
	"""
	print("Call from _some_method_20200721", a, b, c, d)

@vc
def _other_method_20200801(a, b, c, d):
	"""
	This is the docstring for method _other_method_20200801
	"""
	# If a method needs to call another method in this module, it is recommended to run the exact version, or the backward compatibility may break.
	_some_method_20200721(a, b, c, d)

@vt(description="File copy method", helps=dict(srcfile="Input source file", dstfile="Output source file"))
@vc
def _copy_file_20200701(srcfile:str, dstfile:str):
	"""
	This is the docstring for method _copy_file_20200701

	Copy srcfile to dstfile.
	"""
	import shutil
	shutil.copyfile(srcfile, dstfile)

# You can still keep your non version control methods
def non_version_control_method():
	print("This method is not version controlled.")


# This is required if you want this module runnable from shell
if __name__ == "__main__":
	main()

```

### Using the example module

```python
### In your python console ###

from example import pm

# Set the pipe methods version to 20200801. By default, date of importing the module is used as the version.  
pm.set_version("20200801") 

# The exposed methods are _other_method_20200801 and _some_method_20200721
# The hidden method is _some_method_20200601

# To call the method in the package,
pm.some_method("A", "B", "C", "D") # some_method of version 20200721 is selected (we are now using version pre-defined 20200801)
# Call from _some_method_20200721 A B C D

pm.some_method("A", "B", "C")  # This is an error, because _some_method_20200701 accepts 4 parameters
# Error

# some_method of version 20200601 is selected
pm.some_method("A", "B", "C", version="20200615") # As of version 20200615, only _some_method_20200601 is defined
# Call from _some_method_20200601 A B C

```

### Running a function from shell or python

```shell
### Running from shell ###

# Running the module, you can find out a list of available methods that can be run from shell. 

python example/pm.py

#usage: pm.py [-h] {copy_file} ...
#
#version-20201201
#
#positional arguments:
#  {copy_file}
#    copy_file  version-20200701
#	
#optional arguments:
#  -h, --help   show this help message and exit


# Running the method copy_file in shell

python pm.py copy_file --srcfile my_src_file --dstfile my_dst_file 
# The file my_src_file will be copied to my_dst_file

```

```python
### Running from python ###

# Running copy_file in python

from example import pm
pm.copy_file(my_src_file, my_dst_file)
```

### Generating a tool manual for the example module

```python
import simplevc
from example import pm
print(simplevc.generate_tool_manual(pm))

```

Output:

```markdown
## All tools
### copy_file
*version: 20200701*
File copy method
#### Parameters
- **-srcfile**: Input source file
- **-dstfile**: Output source file
```

