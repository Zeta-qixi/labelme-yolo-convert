# labelme-yolo-convert
### labelme 转为yolo数据格式，并构建对应dataset

### 参数说明
- ROOT 保存目录 默认 ./dataset  
./your_dataset_root

- raw_folder 图片与labels标签所在目录   
./data 

- save_folder_name dataset下的项目名称  
task

- k test数据集占比  
0 - 1

- classes 类别 空格隔开,不填则自动编号
apple bike