# Copyright 2008-2009, Karljohan Lundin Palmerius
#

"""This file provides extra functionality to the Candy package.

This script automatically loads the correct shared object library file
for the current platform. For the Linux and MacOS platform the library
loaded is 'lib*.so' or 'lib*.dylib', respectively. For Windows
platforms the script searches for the first occurance of a dll with
the correct prefix. The script will attempt to automatically select
debug or no-debug library but the result can be manually overridden by
an argument in the X3D file.


Include this to load the Candy library:

<PythonScript url="urn:candy:python/AutoLoadSO.py"/>


Include this to load library for XYZ:

<PythonScript url="urn:candy:python/AutoLoadSO.py">
<MetadataString name="library" value="XYZ" containerField="references"/>
</PythonScript>


Include this to force loading the debug version of XYZ:

<PythonScript url="urn:candy:python/AutoLoadSO.py">
<MetadataString name="library" value="XYZ" containerField="references"/>
<MetadataInteger name="debug" value="1" containerField="references"/>
</PythonScript>


It is also possible to force verbose information, by settings the
"verbose" argument to 1 (one):

<MetadataInteger name="verbose" value="1" containerField="references"/>


You may also specify an alternative root for the path to the
library. This functionality supports both environment variable
substitution and URNs:

<MetadataString name="root" value="/usr/local/lib"
                containerField="references"/>

<MetadataString name="root" value="$(VHTK_ROOT)/lib"
                containerField="references"/>

<MetadataString name="root" value="urn:vhtk:"
                containerField="references"/>



This file is part of Candy.

Candy is free software; you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation; either version 2 of the License, or
(at your option) any later version.

Candy is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with Candy; if not, write to the Free Software
Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA

"""


from H3D import *
from H3DInterface import *

import sys, os, re, struct

arch_suffix = "64" if struct.calcsize("P") == 8 else "32"

IMPORT = """<ImportLibrary library="%s"/>"""
DEBUG = False
VERBOSE = False
LIBS = []

ALT_ROOT = [ ".", "$(H3D_ROOT)" ]
ALT_PATH = [ "%s", "%s/lib", "%s/bin", "%s/lib"+arch_suffix, "%s/bin"+arch_suffix, "%s/../lib", "%s/../bin", "%s/../lib"+arch_suffix, "%s/../bin"+arch_suffix, "%s/Plugins", "%s/../Plugins",
             "/usr/lib/", "/usr/local/lib" ]
ALT_DBG = { "unix": "^lib%s_d.so$",
            "win32": "^%s.*_d\.dll$",
            "mac": "^lib%s_d.dylib$" }
ALT_REL = { "unix": "^lib%s\.so.*$",
            "win32": "^%s.*\.dll$",
            "mac": "^lib%s\.dylib$" }

if not re.compile("_d(\.exe|\.app)?$").search(sys.argv[0]) is None:
  DEBUG = True
  print "Force debug mode from application name: %s" % sys.argv[0]

ref_nodes = references.getValue()
for node in ref_nodes:
  
  if not hasattr(node,"name"):
    print "AutoLoadSO: Non metadata argument not supported"
    continue
  
  node_name = node.name.getValue()
  
  if node_name == "library":
    LIBS.extend(node.value.getValue())
  
  elif node_name == "debug":
    DEBUG = int(node.value.getValue()[0]) != 0
    if verbose:
      print "Force Debug mode from reference"
  
  elif node_name == "verbose":
    VERBOSE = int(node.value.getValue()[0]) != 0
  
  elif node_name == "root":
    for root in reversed(node.value.getValue()):
      ALT_ROOT.insert(0,root)
  
  else:
    print "AutoLoadSO: Unrecognized argument '%s'" % node_name

if len(LIBS) < 1:
  LIBS.append("Candy")

def substitute_variables(str):
  pattern = re.compile("^([^$]*)\$\(([^)]+)\)(.*)$")
  match = pattern.search(str)
  while not match is None:
    var = os.getenv(match.group(2))
    var = "(%s UNDEFINED)" % match.group(2) if var is None else var
    
    str = match.group(1) + var + match.group(3)
    
    match = pattern.search(str)
    
  return str


if sys.platform == "win32":
  platform = "win32"
elif sys.platform == "mac" or sys.platform == "darwin":
  platform = "mac"
else:
  platform = "unix"
  

real_paths = []
for path in ALT_PATH:
  
  if path.find("%") == -1:
    
    path2 = substitute_variables(path)
    if path2 == '':
      if VERBOSE:
        print "AutoLoadSO: could not substitute variables in '%s'" % path
      real_paths.append(path1)
      
    if path2.find("urn:") == 0:
      try:
        path3 = resolveURLAsFolder(path2)
      except:
        path3 = resolveURLAsFile(path2)
      if path3 == '':
        if VERBOSE:
          print "AutoLoadSO: could not resolve URL '%s' as folder" % path2
        real_paths.append(path2)
      real_paths.append(path3)
    
    else:
      real_paths.append(path2)
    
  else:
    for root in ALT_ROOT:
      
      path1 = path%root
      if path1 == '':
        if VERBOSE:
          print "AutoLoadSO: possible bug",
          print " - could not find root of '%s'" % path
        real_paths.append(path)
      
      path2 = substitute_variables(path1)
      if path2 == '':
        if VERBOSE:
          print "AutoLoadSO: possible bug",
          print " - could not substitute variables in '%s'" % path1
        real_paths.append(path1)
      
      if path2.find("urn:") == 0:
        try:
          path3 = resolveURLAsFolder(path2)
        except:
          path3 = resolveURLAsFile(path2)
        if path3 == '':
          if VERBOSE:
            print "AutoLoadSO: possible bug",
            print " - could not resolve URL '%s' as file" % path2
          real_paths.append(path2)
        real_paths.append(path3)
      
      else:
        real_paths.append(path2)


if VERBOSE:
  print "Platform: %s" % platform
  print "Verbose: %d" % VERBOSE
  print "Debug: %d" % DEBUG
  print "Libs:", LIBS
  print "Alt. root: %s" % ALT_ROOT
  print "Alt. path: %s" % ALT_PATH
  print "Paths:", real_paths

for lib in LIBS:
  lib_found = False
  
  if VERBOSE:
    print "Searching for library '%s'" % lib
    print "DBG Regex for library '%s'" % ALT_DBG[platform] % lib
    print "REL Regex for library '%s'" % ALT_REL[platform] % lib
  
  pattern_dbg = re.compile( ALT_DBG[platform] % lib )
  pattern_rel = re.compile( ALT_REL[platform] % lib )

  for path in real_paths:
    path = path.replace("/", os.path.sep)
    path = path.replace("\\", os.path.sep)
    if VERBOSE:
      print "  Checking in path '%s'" % path

    if not os.path.isdir(path):
      if VERBOSE:
        print "  Is not a valid path '%s'" % path
      continue

    filenames = os.listdir(path)
    filenames.sort()

    lib_file = None
    for filename in filenames:
      if DEBUG:
        if pattern_dbg.search(filename) is not None:
          lib_file = filename
          break
      else:
        if pattern_dbg.search(filename) is None and \
               pattern_rel.search(filename) is not None:
          lib_file = filename
          break
      if VERBOSE:
        print "  Not matching '%s'" % filename, pattern_dbg.search(filename), pattern_rel.search(filename)

    if not lib_file is None:
      if VERBOSE:
        print "  Found match '%s'" % lib_file
      createX3DNodeFromString( IMPORT % ("%s%s%s"%(path,os.path.sep,lib_file)) )
      lib_found = True
      break

  if not lib_found:
    print "AutoLoadSO: could not find library '%s'" % lib
