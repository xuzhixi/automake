#!/usr/bin/python
#	coding: UTF-8
#	author:		 XuZhiXi
#	create Time: 2012-08-02 18:15:39

import os

#user global set
g_bin_name = "libky.so"	# 生成程序名或动态库名或静态库名
g_debug_bin_name = "libky.so"	# 执行make debug时生成的程序名

g_compilers_opt = "-W -Wall -Wpointer-arith -pipe -D_REENTRANT -O3"	# 编译选项
g_debug_compilers_opt = "-W -Wall -Wpointer-arith -pipe -D_REENTRANT"	# debug的编译选项

g_include_opt = ""	# 包含的头文件选项
g_libs_opt = "-lpthread"	# 包含的动态库选项

g_ar_opt = "" # 编译静态库时, ar命令的选项

g_program_type = 2	# 1 表示一般程序, 2 表示动态库, 3 表示静态库
g_handle_subdir = False	# 是否递归对子目录进行编译链接
g_except_dir_list = [ ]	# 不进行编译链接处理的目录, 仅当g_handle_subdir设置为True时才有效



# program global set
COMMON_TYPE = 1		# common program
DYNAMIC_TYPE = 2	# dynamic library
STATIC_TYPE = 3		# static library
g_tabKey = "\t"
g_newLine = g_tabKey


def is_same_dir(srcDir, dstDir) :
	'''
	是否同一目录
	'''
	
	if os.path.abspath(srcDir) == os.path.abspath(dstDir) :
		return True
	else :
		return False

def get_files(path, typeList, isRecursion = False, exceptDirList = []) :
	'''
	description: 获取符合条件的文件名(包括路径)列表
	param path 指定路径
	param typeList 文件类型
	param isRecursion 是否递归处理子目录
	param exceptDirList 除外的目录,仅当isRecursion为True时才生效
	'''

	resultList = []
	fileNames = os.listdir(path)
	for name in fileNames :
		filePath = os.path.join(path, name)
		isDir = os.path.isdir(filePath)
		if isDir and (isRecursion == True) and (os.path.abspath(filePath) not in exceptDirList) :
			resultList.extend( get_files(filePath, typeList, isRecursion, exceptDirList) )
		elif not isDir and (os.path.splitext(filePath)[1] in typeList) :
			resultList.append(filePath)

	return resultList

def createIndex(fileList) :
	'''
	建立索引
	'''

	resultDict = {}
	for filePath in fileList :
		fileName = os.path.split(filePath)[1]
		fileName = os.path.splitext(fileName)[0]
		resultDict[fileName] = filePath

	return resultDict

def print_compilers() :
	print "################################################################################"
	print "### Compilers ##################################################################"
	print "################################################################################"
	print g_newLine

	print "INCLUDEPATH=" + g_include_opt
	print "LIBS=" + g_libs_opt
	print g_newLine

	print "CC=gcc -c $(INCLUDEPATH) " + g_compilers_opt + " -o"
	print "CC_DEBUG=gcc -g -c $(INCLUDEPATH) " + g_debug_compilers_opt + " -o"
	print "CC_LINKER=gcc $(INCLUDEPATH) " + g_compilers_opt + " -o"
	print "CC_LINKER_DEBUG=gcc -g $(INCLUDEPATH) " + g_debug_compilers_opt + " -o"
	print g_newLine

	print "CPP=g++ -c $(INCLUDEPATH) " + g_compilers_opt + " -o"
	print "CPP_DEBUG=g++ -g -c $(INCLUDEPATH) " + g_debug_compilers_opt + " -o"
	print "CPP_LINKER=g++ $(INCLUDEPATH) " + g_compilers_opt + " -o"
	print "CPP_LINKER_DEBUG=g++ -g $(INCLUDEPATH) " + g_debug_compilers_opt + " -o"
	print g_newLine

	print "AR=ar " + g_ar_opt + " crs"
	print "AR_DEBUG=ar " + g_ar_opt + " crs"
	print g_newLine

def print_objects(sourceItemList) :
	print "################################################################################"
	print "### Generated object files #####################################################"
	print "################################################################################"
	print g_newLine

	objFileListStr = ""
	objDebugFileListStr = ""
	for name in sourceItemList :
		objFileListStr += ( g_tabKey + name + ".o\\\n" )
		objDebugFileListStr += ( g_tabKey + name + ".od\\\n")
	print "OBJECTS=\\"
	print objFileListStr + g_tabKey
	print "OBJECTS_DEBUG=\\"
	print objDebugFileListStr + g_tabKey

def print_project_file(sourceItemList, headerItemList):
	print "################################################################################"
	print "### Project Files ##############################################################"
	print "################################################################################"
	print g_newLine

	print "all: $(OBJECTS)"
	if g_program_type == STATIC_TYPE :
		print "%s$(AR) %s $(OBJECTS)" % (g_tabKey, g_bin_name)
	else :
		print "%s$(CPP_LINKER) %s $(OBJECTS) $(LIBS)" % (g_tabKey, g_bin_name)
#if g_program_type == DYNAMIC_TYPE :
#print "%schcon -t texrel_shlib_t %s" % (g_tabKey, g_bin_name)
	for name in sourceItemList :
		if name in headerItemList :
			print "%s.o: %s %s" % (name, headerItemList[name], sourceItemList[name])
		else :
			print "%s.o: %s" % (name, sourceItemList[name])
		if os.path.splitext( sourceItemList[name] )[1] == ".c" :
			print "%s$(CC) %s.o %s" % (g_tabKey, name, sourceItemList[name])
		else :
			print "%s$(CPP) %s.o %s" % (g_tabKey, name, sourceItemList[name])
	print g_newLine

	print "debug: $(OBJECTS_DEBUG)"
	if g_program_type == STATIC_TYPE :
		print "%s$(AR_DEBUG) %s $(OBJECTS_DEBUG)" % (g_tabKey, g_debug_bin_name)
	else :
		print "%s$(CPP_LINKER_DEBUG) %s $(OBJECTS_DEBUG) $(LIBS)" % (g_tabKey, g_debug_bin_name)
#if g_program_type == DYNAMIC_TYPE :
#print "%schcon -t texrel_shlib_t %s" % (g_tabKey, g_debug_bin_name)
	for name in sourceItemList :
		if name in headerItemList :
			print "%s.od: %s %s" % (name, headerItemList[name], sourceItemList[name])
		else :
			print "%s.od: %s" % (name, sourceItemList[name])
		if os.path.splitext( sourceItemList[name] )[1] == ".c" :
			print "%s$(CC_DEBUG) %s.od %s" % (g_tabKey, name, sourceItemList[name])	
		else :
			print "%s$(CPP_DEBUG) %s.od %s" % (g_tabKey, name, sourceItemList[name])	
	print g_newLine
	
	print "install:"
	print "%secho \"install function not set\"" % g_tabKey
	print g_newLine

	print "clean:"
	print "%srm -f %s %s" % (g_tabKey, g_bin_name, g_debug_bin_name)
	print "%srm -rf *.o *.od" % g_tabKey


if __name__ == "__main__" :
	path = "."

	sourceTypeList = (".cpp", ".c")
	headerTypeList = (".h", )
	exceptDirList = [ os.path.abspath(i) for i in g_except_dir_list ]
	sourceItemList = createIndex( get_files(path, sourceTypeList, g_handle_subdir, exceptDirList) )
	headerItemList = createIndex( get_files(path, headerTypeList, g_handle_subdir, exceptDirList) )

	if g_program_type == DYNAMIC_TYPE :
		g_libs_opt += " -shared"

	print_compilers()
	print_objects(sourceItemList)
	print_project_file(sourceItemList, headerItemList)
	
