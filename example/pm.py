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
