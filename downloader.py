#!/usr/bin/env python 
# coding:utf-8

import io
import gzip
import sys
import traceback
import json
import os
import time
import getopt
import argparse
import urllib
from urllib import request
from urllib.parse import urlparse
import urllib.request
import socket
from threading import Timer

socket.setdefaulttimeout(30)


# 获取tileset.json中的全部uri资源
def getContentsJson(contents, n):
	# 下载content url里的东西
	if n.get('content') is not None:
		c = n['content']
		if (c.get('uri') is not None) and (c['uri'] not in contents):
			contents.append(c['uri'])

	if n.get('children') is not None:
		children = n['children']
		for i in range(len(children)):
			c = children[i]
			getContentsJson(contents, c) 
	return

#gzip解码，输入字节流，返回字节流
def gzipDecode(data):
	compressedStream = io.BytesIO(data)
	gziper = gzip.GzipFile(fileobj=compressedStream)
	data2 = gziper.read()
	return data2

#下载tileset.json
def downloadJson(url, filepath):
	try:
		requestResult = request.urlopen(url,None,30)
		if requestResult.getcode() == 200 :
			file = open(filepath,'w+')
			data = requestResult.read()
			data = gzipDecode(data).decode()
			file.seek(0,0)
			file.write(data)
			file.close()
		return True
	except Exception as e:
		print(e)
		print("url:",url)
	return False

#下载二进制资源文件
def downloadFile(url, filepath):
	try:
		if os.path.exists(filepath) and os.path.getsize(filepath) > 0 :
			return True
		requestResult = request.urlopen(url,None,30)
		if requestResult.getcode() == 200 :
			file = open(filepath,'wb+')
			data = requestResult.read()
			data = gzipDecode(data)
			file.seek(0,0)
			file.write(data)
			file.close()
		return True
	except Exception as e:
		print(e)
	#删除下载失败的文件
	if os.path.exists(filepath):
		try:
			os.remove(filepath)
		except Exception as e:
			print(e)
	return False

#循环下载所有资源文件
def downloadCycle(baseurl , savedir , uu , uris):
	failedFiles = []
	for i in range(len(uris)):
		c = uris[i]

		file = savedir + '/' + c

		dirname = os.path.dirname(file)
		if not os.path.exists(dirname):
			os.makedirs(dirname)

		url = baseurl + c + '?' + uu.query
		if downloadFile(url, file):
			print(str(i+1) + '/' + str(len(uris)) + ' download success: ' + c)
		else:
			print(str(i+1) + '/' + str(len(uris)) + ' download failed: ' + c)
			failedFiles.append(c)
	print("------------------------------------------------------------")
	print(str(len(uris) - len(failedFiles)) + " files download success," + str(len(failedFiles)) + " files download failed ")
	for i in range(len(failedFiles)):
		print(failedFiles[i])
	#选择是否继续下载
	if len(failedFiles)>0 :
		print("------------------------------------------------------------")
		print("Above failed download files will be redownloaded after 10 seconds.....")
		# print("Do you want to continue ? (y/n)")
		t = Timer(10,downloadCycle,args=[baseurl,savedir,uu,failedFiles])
		t.start()
		# ans = input()
		# if ans == 'n':
		# 	t.cancel()

#获取tileset.json文件内容
def getUriFromJsonFile(file):
	try:
		f = open(file,"r")
		data = json.loads(f.read())
		uris = []
		getContentsJson(uris, data['root'])
		return uris
	except Exception as e:
		print(e)





if __name__ == "__main__":

	#参数默认值
	baseurl = "https://assets.cesium.com/1/tileset.json?v=1"
	savedir = "./3dtiles/jczx"
	token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJqdGkiOiI1MDk0YzczMy1lYzk4LTRmNmUtYjA0Zi0zN2RmYjRhNTRhNGIiLCJpZCI6OTc0MzQsImFzc2V0cyI6eyIxMTUxMDA2Ijp7InR5cGUiOiIzRFRJTEVTIn19LCJzcmMiOiI2ZDc2OTFjMC00MjRmLTRkZTktODc1Ny1lZjRmMzk4ZDJiMDYiLCJpYXQiOjE2NTYzMTI2ODIsImV4cCI6MTY1NjMxNjI4Mn0.wRWHId2USvu2OyLXcQ8fVmZYOK80Uvd8wdD72pZoots"

	try:
		opts, args = getopt.getopt(sys.argv[1:], "hu:d:t:", [
								   "url=", "dir=", "token="])
	except getopt.GetoptError:
		print('param error')
		sys.exit(2)

	for opt, arg in opts:
		print(opt,arg)
		if opt in ('-h','--help'):
			print('------options:')
			print("     -h  --help :帮助")
			print("     -u  --url  :tileset的地址")
			print("     -d  --dir  :下载文件的存储路径")
			print("     -t  --token:请求文件的Bearer token")
			print("------usage:")
			print("  python downloader.py -u https://assets.cesium.com/1/tileset.json -d /path/ -t access-token-key")
			sys.exit()
		elif opt in ("-u", "--url"):
			baseurl = arg
		elif opt in ("-d", "--dir"):
			savedir = arg
		elif opt in ("-t", "--token"):
			token = arg

	if baseurl == '':
		print('please input url param')

	if savedir == '':
		print('please input savedir param')
		sys.exit(2)

	if os.path.isfile(savedir):
		print('savedir can not be a file ', savedir)
		sys.exit(2)

	if not os.path.exists(savedir):
		os.makedirs(savedir)

	baseurl += "&access_token=" + token		
	# 解析baseurl
	uu = urlparse(baseurl)
	tileseturl = uu.scheme + "://" + uu.netloc + uu.path
	if not tileseturl.endswith('.json'):
		print('url必须为json文件的地址, 如:https://assets.cesium.com/1/tileset.json')
		sys.exit(2)

	baseurl = tileseturl[0:(tileseturl.rfind('/') + 1)]
	# 文件名
	filename = tileseturl[(tileseturl.rfind('/') + 1):len(tileseturl)]

	opener = urllib.request.build_opener()
	opener.addheaders = [
		('User-agent', 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36')]
	urllib.request.install_opener(opener)

	tilesetfile = savedir + "/" + filename
	tileseturl += '?' + uu.query

	if not downloadJson(tileseturl, tilesetfile):
		print('download ' + filename + ' failed')
		sys.exit(2)
	print('download ' + filename + ' success')

	# 解析tileset.json
	uris = getUriFromJsonFile(tilesetfile)
	#下载所有资源文件
	downloadCycle(baseurl , savedir , uu , uris)

	sys.exit()
	