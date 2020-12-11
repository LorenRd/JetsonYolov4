import glob
import os
import xml.etree.ElementTree as ET
import pandas as pd
import PIL

from PIL import Image
from sklearn.model_selection import train_test_split


def xml_to_yolo(path):
    #Etiquetas en el mismo orden que el archivo .names
    clases = ["with_mask", "without_mask", "mask_weared_incorrect"]
    bounding_boxes = []
    for xml_file in glob.glob(path+"/*.xml"):
        tree = ET.parse(xml_file)
        root = tree.getroot()
        imageName = root.find('filename').text
        try:
            with open("../images/"+imageName) as f:
                image = Image.open("../images/"+imageName)
                imageWidth, imageHeight = image.size
                f.close()
                cuadro = ""
                text_file = open(imageName.split('.')[0]+".txt", "w")
                for object in root.findall('object'):
                    name = object.find('name').text
                    classIndex = clases.index(name)

                    xmin = int(object.find('bndbox').find('xmin').text)
                    ymin = int(object.find('bndbox').find('ymin').text)
                    xmax = int(object.find('bndbox').find('xmax').text)
                    ymax = int(object.find('bndbox').find('ymax').text)

                    width = xmax - xmin
                    height = ymax - ymin

                    xCenter = ((xmin + width + xmin)/2)/imageWidth
                    yCenter = ((ymin + height + ymin)/2)/imageHeight
                    width_yolo = (xmax - xmin)/imageWidth
                    height_yolo = (ymax - ymin)/imageHeight

                    #class x y width height
                    cuadro = cuadro + str(classIndex) + " " + str(round(xCenter,6)) + " " + str(round(yCenter,6)) + " " + str(round(width_yolo,6)) + " " + str(round(height_yolo,6)) + "\n"
                    value = (name, imageName)
                    bounding_boxes.append(value)
                text_file.write(cuadro)
                text_file.close()
        except IOError:
            print("File not accessible xml")
    column_name = ["ClassName","FileName"]
    yolo_df = pd.DataFrame(bounding_boxes, columns=column_name)
    return yolo_df

def generateTrainValidTxt(df, trainMode):
    if trainMode:
        text_file = open("train.txt", "w")
        files = ""
        for column in df['FileName']:
            files = files + column + "\n"
        text_file.write(files)
        text_file.close()
    else:
        text_file = open("test.txt", "w")
        files = ""
        for column in df['FileName']:
            files = files + column + "\n"
        text_file.write(files)
        text_file.close()


def main():
    pandasDF = xml_to_yolo(os.path.abspath(os.getcwd()))
    y = pandasDF['ClassName']
    train_set, test_set = train_test_split(pandasDF, test_size=0.1,random_state=25, stratify=y)
    generateTrainValidTxt(train_set, True)
    generateTrainValidTxt(test_set, False)
if __name__ == "__main__":
    main()
