# 3dtiles_downloader
      用于从cesium.ion 上下载转换后的3dtiles数据

## 示例
```shell
python downloader.py -u https://assets.cesium.com/1/tileset.json -d /path/ -t access-token-key
```
其中 access-token-key 是指通过web请求https://assets.cesium.com/1/tileset.json数据时自动生成的token，而非cesium.ion的token，并且这个token只在一段时间内有效，会动态改变，有效期貌似是一个小时左右