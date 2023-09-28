from typing import List, Dict, Tuple, Union
import argparse
from pathlib import Path
import random
import os
import json
import shutil

ROOT = ''
classes = {}


def parse_args():
    description = "you should add those parameter"                   # 步骤二
    parser = argparse.ArgumentParser(description=description)        # 这些参数都有默认值，当调用parser.print_help()或者运行程序时由于参数不正确(此时python解释器其实也是调用了pring_help()方法)时，
                                                                     # 会打印这些描述信息，一般只需要传递description参数，如上。
    
    parser.add_argument('--output', '-o', default='./datasets', help="Root path of dateset")     
    parser.add_argument('--name', '-n', default='project', help="dataset name")
    parser.add_argument('--classes', '-c', default='', help='classes like: class1 class2')
    parser.add_argument('--file', '-f', help='where your data (images and json)')                                     # 图片与标注文件所在的文件夹
    parser.add_argument('--k', default=0.3, type=float, help='rates of test set')               # test 数据集 占比
    
    args = parser.parse_args()    

    global ROOT  
    ROOT = args.output

    if C:=args.classes:
        C = C.split()
        for i, c in enumerate(C):
            classes[c] = i

    return args              

def create_folder(path):
    if not os.path.exists(path):
        os.makedirs(path)


def create_dir(name, root):
    """创建yolo数据格式的目录（仅train，test）
    
    """
    global ROOT
    ROOT = Path(root, name)
    create_folder(ROOT)
    create_folder(ROOT.joinpath('labels'))
    create_folder(ROOT.joinpath('labels', 'train'))
    create_folder(ROOT.joinpath('labels', 'test'))
    create_folder(ROOT.joinpath('images'))
    create_folder(ROOT.joinpath('images', 'train'))
    create_folder(ROOT.joinpath('images', 'test'))
    


def convert_label_json(json_path: Path, save_dir: Path, task = 'detection'):
    """根据任务将labelme生成的json转为txt数据格式
    input:
        - json_path: json文件地址
        - save_dir: 保存目录
        - task: 任务（detection, segment）
    
    """
    with open(json_path,'r') as load_f:
        json_dict = json.load(load_f)
    h, w = json_dict['imageHeight'], json_dict['imageWidth']

    # save txt path
    txt_path = os.path.join(save_dir, json_path.replace('json', 'txt'))

    with open(txt_path, 'w') as f:

        for shape_dict in json_dict['shapes']:
            label = shape_dict['label']
            if (c:=classes.get(label),-1) >= 0:
                label_index = classes.get(label)
            else:
                label_index = len(classes)
                classes[label] = label_index
            points = shape_dict['points']

            # 根据任务处理数据
            if task == 'segment':
                points_nor_list = []
                for point in points:
                    points_nor_list.append(point[0]/w)
                    points_nor_list.append(point[1]/h)
                W = (points[1][0] - points[0][0])/w
                H = (points[1][1] - points[0][1])/h
            
            if task == 'detection':
                C_X = W/2 + points[0][0]/w
                C_Y = H/2 + points[0][1]/h
                points_nor_list = [C_X, C_Y, W, H]

    
            points_nor_list = list(map(lambda x:str(x),points_nor_list))
            points_nor_str = ' '.join(points_nor_list)
            
            label_str = str(label_index) + ' ' +points_nor_str + '\n'
            f.writelines(label_str)




class Data:
    __slots__ = ('image', 'json')
    def __init__(self):
        self.image = ''
        self.json = ''


def main():
    
    args = parse_args()
    create_dir(args.name, ROOT)
    # 保存所有文件对应的图片与标签地址，确保一一对应
    raw_data = {}
    for f in os.listdir(args.file):
        name, type_ = f.rsplit('.', 1)
        raw_data[name] = raw_data.get(name, Data())
        if type_ == 'json':
            raw_data[name].json = f
        elif type_ in ['jpg', 'JPG', 'PNG', 'png']:
            raw_data[name].image = f
    

    random.shuffle(raw_data)
    if args.k < 1:
        k = int(len(raw_data) * args.k)
    assert k < len(raw_data)

    labels_folder = [
         Path(ROOT, 'labels', 'test'),
          Path(ROOT, 'labels', 'train')
    ]
    images_folder = [
         Path(ROOT, 'images', 'test'),
          Path(ROOT, 'images', 'train')
    ]

    for i, name in enumerate(raw_data):
        
        D = raw_data[name]
        if D.json and D.image:
            convert_label_json(D.json,labels_folder[i<=k])
            shutil.copy(D.image, images_folder[i<k])
        else:
            print(name)

    print('over')
