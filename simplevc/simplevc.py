'''
A simple library built for version control, backward compatibility and command line scripts on non-standard functions. 

Version control is an important practice in writing program. However, due to the large variations across experiments, sometimes researchers may need to build new customized pipelines to handle data generated under various conditions. As data can be generated in multiple batches with many tiny modifications among them, researchers need to update the pipeline rapidly. As time is tight, it could be very challenging to keep everything under standard version control. 

This package provides several utilities to make life easier for the researchers when building the pipelines:

#. Easy version-control and backward compatibility - One should be able to repeat the analysis and generate the same result, even on an older version of the pipeline.
   
#. Compatibility between python functions and command line scripts - the pipeline can be called as a python function, or in a bash script.

#. Reusable in the future - The pipelines can be quickly modified and reused in future analysis.
     
#. Fast to build and easy to learn - Minimize the time to build the pipeline.
 
Here we build this simple version-control library that fulfills the above requirements. Researchers do not need to make drastic changes in the codes, but only:

#. Register the module the the version-control system.

#. Add version number to the function name.
 
#. Add a decorator to the function.


The ideas behind this simple version control system:

* There is NO guarantee that the input, output nor behavior of any two versions of the same function remain the same. 

* All the old-version functions should be kept for backward compatibility. They should not be modified (Create a new one with newer version number instead).

* There is no restriction on the function arguments, except the argument name `version` is reserved for version control.

* This is a simple and fast but NOT a standard version control system. It only serves as a utility for development. 

 
:Example:

.. code-block:: python

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

:Example:

.. code-block:: shell

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

Another important feature simplevc provide is to make methods usable in both python and shell easily. 

:Example:

.. code-block:: shell

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

.. code-block:: python

	### Running from python ###
	
	# Running copy_file in python
	
	from example import pm
	pm.copy_file(my_src_file, my_dst_file)

@author: Alden
'''

def _default_version_control_init():
	from datetime import date
	global _registered_modules
	global _default_version
	_registered_modules = []
	_default_version = date.today().strftime("%Y%m%d")

_default_version_control_init()

def _int_compare(a, b):
	if a < b:
		return -1
	if a == b:
		return 0
	if a > b:
		return 1
	raise Exception()

def _compare_version(v1, v2):
	result = None
	for r1, r2 in [(0, 4), (4, 6), (6, 8)]:
		result = _int_compare(int(v1[r1:r2]), int(v2[r1:r2]))
		if result != 0:
			break
	return result

def _get_first_available_version(available_versions):
	return available_versions[0]

def _get_last_version(available_versions, version):
	import bisect
	idx = bisect.bisect_right(available_versions, version) - 1
	if idx < 0:
		
		return None
	return available_versions[idx]

def _update_module_vc(module, function_name, version):
	'''
	Updates the function wrapper __name__, __doc__ and etc.
	'''
	import functools
	
	method_dict = module._method_dicts[function_name]		
	wrapper = getattr(module, function_name)
	function_version = _get_last_version(sorted(method_dict.keys()), version)
	if function_version is not None:
		functools.update_wrapper(wrapper, method_dict[function_version])
		pass
	else:
		wrapper.__doc__ = f"""The method {function_name} is not available at version {version}.
		The first available version is {_get_first_available_version(sorted(method_dict.keys()))}."""
	wrapper.__name__ = wrapper.__qualname__ = function_name

def set_module_version(module, version):
	'''
	Set the module version
	'''
	module._version = version
	for function_name in module._method_dicts.keys():
		_update_module_vc(module, function_name, version)
		
def get_module_version(module):
	'''
	Get the module version.
	'''
	return module._version
	
def set_default_version(default_version):
	'''
	Set the default version of simplevc, that is used as the default version for any package loading simplevc.
	'''
	global _default_version
	_default_version = default_version
	


def _module_vc(module, func):
	'''
	The core function that `vc` relies on.
	'''
	import functools

	# Parse a function _some_function_yyyymmdd
	# Function name: some_function
	# Version: yyyymmdd
	function_name = func.__name__[1:func.__name__.rindex("_")]
	version = func.__name__[func.__name__.rindex("_") + 1:]
	
	# Register the function to _method_dicts
	if function_name not in module._method_dicts:
		module._method_dicts[function_name] = {}
	method_dict = module._method_dicts[function_name]
	
	method_dict[version] = func	
	@functools.wraps(func)
	def _run_method(*args, version=None, **kwargs):
		if version is None:
			version = module._version
		rversion = _get_last_version(sorted(method_dict.keys()), version)
		if rversion is None:
			raise Exception(f"The method {function_name} is not available at version {version}. \nThe first available version is {_get_first_available_version(sorted(method_dict.keys()))}.")
		return method_dict[rversion](*args, **kwargs)
	setattr(module, function_name, _run_method)
	_update_module_vc(module, function_name, module._version)
	return func


def _module_vt(module, *, description=None, helps={}, types={}, defaults={}, return_routine=None):
	'''
	The core function that `vt` relies on.
	'''
	import inspect 
	def inner(func):
		function_name = func.__name__[1:func.__name__.rindex("_")]
		version = func.__name__[func.__name__.rindex("_") + 1:]
		
		# Register the function to _tools_dicts
		if function_name not in module._tool_dicts:
			module._tool_dicts[function_name] = {}
		module._tool_dicts[function_name][version] = (inspect.signature(func), description, helps, types, defaults, return_routine) 
		return func 
	return inner 

def module_main(module):
	'''
	The default routine for main
	'''
	import argparse
	import sys
	from types import GenericAlias
	import typing
	display_help = False
	i = 1
	while i < len(sys.argv):
		if sys.argv[i] == "-v":
			module.set_version(sys.argv[i + 1])
			i += 2
		elif sys.argv[i] == "-h":
			display_help = True
			i += 1
		else:
			break
	if i == len(sys.argv):
		display_help = True
	
	_parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter, description=f"version-{module._module_display_version}" if module._module_display_version is not None else "")
	
	_subparsers = _parser.add_subparsers(dest='_subparser_name')
	_return_routines = {} 
	for func_name, tool_dict in module._tool_dicts.items():
		version = module._version
		rversion = _get_last_version(sorted(tool_dict.keys()), version)
		if rversion is None:
			continue		
		signature, description, helps, types, defaults, return_routine = tool_dict[rversion]
		ap_kwargs = {}
		if description is not None:
			ap_kwargs["description"] = description
		parser = _subparsers.add_parser(func_name, help=f"version-{rversion}", formatter_class=argparse.ArgumentDefaultsHelpFormatter, argument_default=argparse.SUPPRESS, **ap_kwargs)		
		for param in signature.parameters.values():
			import inspect
			kwargs = {}
			if param.name in helps:
				kwargs["help"] = helps[param.name]
			else:
				kwargs["help"] = "_"

			if param.name in defaults:
				kwargs["default"] = defaults[param.name] 
				kwargs["required"] = False
			elif param.default != inspect._empty:
				kwargs["default"] = param.default 
				kwargs["required"] = False
			else:
				kwargs["required"] = True
				
			if param.name in types:
				kwargs["type"] = types[param.name]
			elif param.annotation != inspect._empty:
				if isinstance(param.annotation, GenericAlias):
					if typing.get_origin(param.annotation) != list:
						raise Exception("Only list is supported in GenericAlias")
					kwargs["type"] = typing.get_args(param.annotation)[0]
					kwargs["nargs"] = "*"
				else:
					kwargs["type"] = param.annotation
				
				
			parser.add_argument(f"-{param.name}", **kwargs)
		
		if return_routine is not None:
			return_params = return_routine[1]
			_return_routines[func_name] = return_routine
			for param_name in return_params:
				kwargs = {}
				if param_name in helps:
					kwargs["help"] = helps[param_name]
				else:
					kwargs["help"] = "_"
					
				if param_name in types:
					kwargs["type"] = types[param_name]
				else:
					raise Exception("")
					
				if param_name in defaults:
					kwargs["default"] = defaults[param_name] 
					kwargs["required"] = False
				else:
					kwargs["required"] = True
					
				parser.add_argument(f"-{param_name}", **kwargs)

	if display_help:
		_parser.print_help()
	else:
		try:
			args = _parser.parse_args(sys.argv[i:])
			_subparser_name = args._subparser_name
			del args._subparser_name  
			
			if _subparser_name in _return_routines:
				return_func, return_params = _return_routines[_subparser_name]
				method_args = {k:v for k, v in vars(args).items() if k not in return_params}
				return_func_args = {k:v for k, v in vars(args).items() if k in return_params}
				result = getattr(module, _subparser_name)(**method_args)
				return_func(result, **return_func_args)
			else:
				getattr(module, _subparser_name)(**vars(args))
			
				
		except argparse.ArgumentError:
			print("Some errors occur in arguments")

def register(module, module_display_version=None):
	'''
	Register the simple version control system to the target module. 
	
	'''
	global _default_version
	global _registered_modules
	
	setattr(module, "_method_dicts", {})
	setattr(module, "_tool_dicts", {})
	set_module_version(module, _default_version)
	setattr(module, "_module_display_version", module_display_version)
	
	def set_version(version):
		'''
		Set the module version to use. 
		
		:param version: version of format yyyymmdd.

		:Example:
		
		.. code-block:: python
		
			import some_module
			
			some_module.set_version("20201001")
			
			some_module.get_version()
			# 20201001
		
		'''
		return set_module_version(module, version)
	setattr(module, "set_version", set_version)
	
	def get_version():
		'''
		Returns the current module version
		
		:Example:
		
		.. code-block:: python
		
			import some_module
			
			some_module.set_version("20201001")
			
			some_module.get_version()
			# 20201001
		'''
		return get_module_version(module)
	setattr(module, "get_version", get_version)

	def vc(func):
		'''
		Add this decorator to make the function under version control in the module.

		A function to be registered should follow the rules below: 

		#. The argument `version` is reserved and should not be used.

		#. The function name should start with an underscore and end with an underscore and a version number

		For example, a function some_function of version yyyymmdd should be defined as _some_function_yyyymmdd

		:Example: 

		.. code-block:: python

			import sys
			import simplevc
			simplevc.register(sys.modules[__name__])


			# Definition of version 20200601
			@vc
			def _some_method_20200601():
				print("Hello from 20200601")

			# Definition of version 20200701
			@vc
			def _some_method_20200701():
				print("Hello from 20200701")

		.. code-block:: python

			# By default today's date (e.g. 20200801) is used as the current version. 
			# The latest version as of the selected date of some_method is used.
			some_method()
			# Hello from 20200701
			some_method(version="20200615")
			# Hello from 20200601
			some_method(version="20200501")
			# Exception - because this method is not yet created on 20200501!
		'''
		return _module_vc(module, func)
	setattr(module, "vc", vc)

	def vt(*, description=None, helps={}, types={}, defaults={}, return_routine=None):
		'''
		Register the function as a tool that can be accessed when running the module as __main__

		:Example:

		.. code-block:: python

			@vt(description="File copy method", helps=dict(srcfile="Input source file", dstfile="Output source file"))
			@vc
			def _copy_file_20200701(srcfile:str, dstfile:str):
				import shutil
				shutil.copyfile(srcfile, dstfile)

		''' 
		return _module_vt(module, description=description, helps=helps, types=types, defaults=defaults, return_routine=return_routine)
	setattr(module, "vt", vt)

	def main():
		'''
		The module main.
		
		:Example:
		
		.. code-block:: python
		
			if __name__ == "__main__":
				main()
				
		'''
		return module_main(module)
	setattr(module, "main", main)
	
	
	_registered_modules.append(module)
	
def generate_tool_manual(module, version=None):
	'''
	Automatically generate a tool manual for a registered module.
	
	'''
	from types import GenericAlias
	import simplevc
	import typing
	import inspect
	lines = []
	lines.append("## " + "All tools")
	root_version = version
	for func_name, tool_dict in module._tool_dicts.items():
		if root_version is not None:
			version = root_version
		else:
			version = module._version
		rversion = _get_last_version(sorted(tool_dict.keys()), version)
		if rversion is None:
			continue		
		signature, description, helps, types, defaults, return_routine = tool_dict[rversion]
		lines.append("### " + func_name)
		lines.append(f"*version: {rversion}*")
		lines.append(description if description is not None else "")
		lines.append("#### Parameters")

		for param in signature.parameters.values():
			kwargs = {}
			if param.name in helps:
				kwargs["help"] = helps[param.name]
			else:
				kwargs["help"] = "_"

			if param.name in defaults:
				kwargs["default"] = defaults[param.name] 
				kwargs["required"] = False
			elif param.default != inspect._empty:
				kwargs["default"] = param.default 
				kwargs["required"] = False
			else:
				kwargs["required"] = True

			if param.name in types:
				kwargs["type"] = types[param.name]
			elif param.annotation != inspect._empty:
				if isinstance(param.annotation, GenericAlias):
					if typing.get_origin(param.annotation) != list:
						raise Exception("Only list is supported in GenericAlias")
					kwargs["type"] = typing.get_args(param.annotation)[0]
					kwargs["nargs"] = "*"
				else:
					kwargs["type"] = param.annotation
			lines.append(f"- **-{param.name}**: {'[optional] ' if not kwargs['required'] else ''}{kwargs['help']}{(' [default: ' + str(kwargs['default']) + ']') if 'default' in kwargs else ''}")
	return("\n".join(lines))