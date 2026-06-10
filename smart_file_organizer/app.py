import os
import shutil


types = {
    ".zip":"Archives",
    ".rar":"Archives",
    
    ".txt":"Documents",
    ".pdf":"Documents",
    ".docx":"Documents",
    ".doc":"Documents",
    ".xls":"Documents",
    ".pptx":"Documents",
    ".csv":"Documents",
    ".ppt":"Documents",
    ".md":"Documents",
    
    ".py":"Code",
    ".js":"Code",
    ".ts":"Code",
    ".cpp":"Code",
    ".html":"Code",
    ".css":"Code",
    ".php":"Code",
    ".c":"Code",
    ".ru":"Code",
    ".java":"Code",
    
    ".mp4":"Videos",
    ".mkv":"Videos",
    ".avi":"Videos",
    ".wmv":"Videos",
    ".mov":"Videos",
    
    
    ".png":"Images",
    ".jpg":"Images",
    ".jpeg":"Images",
    ".gif":"Images",
    ".webp":"Images",
    ".svg":"Images",
    ".bmb":"Images",
    ".ico":"Images",
    }


for file in os.listdir():
    if os.path.isfile(file):
        ext = os.path.splitext(file)[1].lower()
        if ext in types:
            folder = types[ext]
            os.mkdir(f"{folder}")
            shutil.move(file,folder)