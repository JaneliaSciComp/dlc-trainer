#! /usr/bin/python3

import os
import shutil

if os.path.exists('videos-to-compress'):    
    shutil.rmtree('videos-to-compress')
shutil.copytree('videos-to-compress-read-only', 'videos-to-compress')

if os.path.exists('videos-that-are-compressed'):    
    shutil.rmtree('videos-that-are-compressed')
os.mkdir('videos-that-are-compressed')

os.system('python3 cyvasse.py videos-to-compress videos-that-are-compressed')
