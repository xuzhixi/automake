#!/usr/bin/python
#coding: UTF-8
#	author:		 XuZhiXi
#	create Time: 2012-08-02 18:15:39

import os
import re


#user global set
g_bin_name = "room_server"	# 生成程序名或动态库名或静态库名
g_debug_bin_name = "room_server_debug"	# 执行make debug时生成的程序名

g_compilers_opt = "-W -Wall -Wpointer-arith -pipe -D_REENTRANT -O3"	# 编译选项
g_debug_compilers_opt = "-W -Wall -Wpointer-arith -pipe -D_REENTRANT"	# debug的编译选项

g_include_opt = "-I/root/ACE_wrappers -I/root/ACE/rsns"	# 包含的头文件选项
g_libs_opt = "-L/root/ACE_wrappers/ace -L/root/lib -lACE -lmysqlclient -lz -ldl -lpthread -lrt -lvspasswd -lip_query"	# 包含的动态库选项

g_ar_opt = "" # 编译静态库时, ar命令的选项

g_program_type = 1		# 1 表示一般程序, 2 表示动态库, 3 表示静态库
g_except_file_list = [] # 不进行编译链接处理的文件
g_handle_subdir = True	# 是否递归对子目录进行编译链接
g_except_dir_list = [ ]	# 不进行编译链接处理的目录, 仅当g_handle_subdir设置为True时才有效



# program global set
COMMON_TYPE = 1		# common program
DYNAMIC_TYPE = 2	# dynamic library
STATIC_TYPE = 3		# static library
g_tabKey = "\t"
g_newLine = g_tabKey
sourceItemList = None
headerItemList = None


def get_depandent_str(fileList, suffix) :
	resultList = []
	for file in fileList :
		ls = get_depandent_list( file )
		resultList.extend( ls )
	resultList = list( set( resultList ) )	# 去重

	return get_str_by_filelist( resultList, suffix ) 

def get_str_by_filelist(fileNameList, suffix = ".o") :
	depandentStr = ""
	for fileName in fileNameList :
		basename = os.path.basename( fileName )
		if basename in sourceItemList :
			depandentStr += ("\\\n" + g_tabKey + basename + suffix)
		elif basename in headerItemList :
			depandentStr += ("\\\n" + g_tabKey + headerItemList[basename])

	return depandentStr

def get_depandent_list(fileName) :
	basedir = os.path.dirname( fileName )
	f = open( fileName, "r" )
	re_obj = re.compile( ur'''^\s*#include\s*"(.+?)\.h"\s*$''' )
	depandentList = []
	for line in f :
		fileNameList = re_obj.findall( line )
		if fileNameList :
			fullName = os.path.abspath( os.path.join( basedir, fileNameList[0] ) )
			if not is_same_file( os.path.splitext( fileName )[0], fullName ) :
				depandentList.append( fullName )

	return depandentList
	
def is_same_file(file1, file2) :
	'''
	是否同一文件
	'''

	fileName1 = os.path.abspath( file1 )
	fileName2 = os.path.abspath( file2 )

	return ( fileName1 == fileName2 )

def is_same_dir(srcDir, dstDir) :
	'''
	是否同一目录
	'''
	
	if os.path.abspath(srcDir) == os.path.abspath(dstDir) :
		return True
	else :
		return False

def get_files(path, typeList, isRecursion = False, exceptFileList = [], exceptDirList = []) :
	'''
	description: 获取符合条件的文件名(包括路径)列表
	param path 指定路径
	param typeList 文件类型
	param isRecursion 是否递归处理子目录
	param exceptFileList 除外的文件
	param exceptDirList 除外的目录,仅当isRecursion为True时才生效
	'''

	resultList = []
	fileNames = os.listdir(path)
	for name in fileNames :
		filePath = os.path.join(path, name)
		fileFullPath = os.path.abspath(filePath)
		isDir = os.path.isdir(filePath)
		if isDir and (isRecursion == True) and (fileFullPath not in exceptDirList) :
			resultList.extend( get_files(filePath, typeList, isRecursion, exceptFileList, exceptDirList) )	# 处理子目录
		elif not isDir and (os.path.splitext(filePath)[1] in typeList) and (fileFullPath not in exceptFileList) :
			resultList.append(filePath)		# 处理文件

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

	print "AR=ar " + g_ar_opt + " cqs"
	print "AR_DEBUG=ar " + g_ar_opt + " cqs"
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
		printTab( "%s$(AR) %s $(OBJECTS)", g_bin_name )
	else :
		printTab( "$(CPP_LINKER) %s $(OBJECTS) $(LIBS)", g_bin_name )
	for name in sourceItemList :
		if name in headerItemList :
			print "%s.o: %s %s%s" % ( name, headerItemList[name], sourceItemList[name], \
					get_depandent_str([ headerItemList[name], sourceItemList[name] ], ".o") )
		else :
			print "%s.o: %s%s" % ( name, sourceItemList[name], get_depandent_str([ sourceItemList[name] ], ".o") )
		if os.path.splitext( sourceItemList[name] )[1] == ".c" :
			printTab( "$(CC) %s.o %s", name, sourceItemList[name] )
		else :
			printTab( "$(CPP) %s.o %s", name, sourceItemList[name] )
	print g_newLine

	print "debug: $(OBJECTS_DEBUG)"
	if g_program_type == STATIC_TYPE :
		printTab( "$(AR_DEBUG) %s $(OBJECTS_DEBUG)", g_debug_bin_name)
	else :
		printTab( "$(CPP_LINKER_DEBUG) %s $(OBJECTS_DEBUG) $(LIBS)", g_debug_bin_name )
	for name in sourceItemList :
		if name in headerItemList :
			print "%s.od: %s %s%s" % (name, headerItemList[name], sourceItemList[name], \
					get_depandent_str([ headerItemList[name], sourceItemList[name] ], ".od") )
		else :
			print "%s.od: %s%s" % ( name, sourceItemList[name], get_depandent_str([ sourceItemList[name] ], ".od") )
		if os.path.splitext( sourceItemList[name] )[1] == ".c" :
			printTab( "$(CC_DEBUG) %s.od %s", name, sourceItemList[name] )	
		else :
			printTab( "$(CPP_DEBUG) %s.od %s", name, sourceItemList[name] )	
	print g_newLine
	
	print "install:"
	printTab( "echo \"install function not set\"" )
	print g_newLine

	print "clean:"
	printTab( "rm -f %s %s", g_bin_name, g_debug_bin_name )
	printTab( "rm -rf *.o *.od" )

def printTab(format, *args) :
	print g_tabKey,
	print format % args


if __name__ == "__main__" :
	path = "."
	sourceTypeList = (".cpp", ".c")
	headerTypeList = (".h", )
	exceptFileList = [ os.path.abspath(i) for i in g_except_file_list ]
	exceptDirList  = [ os.path.abspath(i) for i in g_except_dir_list ]
	sourceItemList = createIndex( get_files(path, sourceTypeList, g_handle_subdir, exceptFileList, exceptDirList) )
	headerItemList = createIndex( get_files(path, headerTypeList, g_handle_subdir, exceptFileList, exceptDirList) )

	if g_program_type == DYNAMIC_TYPE :
		g_libs_opt += " -shared"

	print_compilers()
	print_objects(sourceItemList)
	print_project_file(sourceItemList, headerItemList)
	
