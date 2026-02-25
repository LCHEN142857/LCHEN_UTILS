#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
My Todo - 打包脚本
使用PyInstaller将Python程序打包为独立的exe可执行文件
"""

import os
import sys
import subprocess
import shutil


def clean_build():
    """清理之前的构建文件"""
    dirs_to_remove = ['build', 'dist', '__pycache__']
    files_to_remove = ['main.spec', '*.pyc']
    
    for dir_name in dirs_to_remove:
        if os.path.exists(dir_name):
            print(f"删除目录: {dir_name}")
            shutil.rmtree(dir_name)
    
    for file_pattern in files_to_remove:
        import glob
        for file in glob.glob(file_pattern):
            print(f"删除文件: {file}")
            os.remove(file)
    
    print("清理完成！\n")


def build_exe():
    """使用PyInstaller打包exe"""
    
    # PyInstaller命令参数
    pyinstaller_args = [
        'pyinstaller',
        '--name=My Todo',  # 应用程序名称
        '--windowed',  # 窗口模式（不显示控制台）
        '--onefile',  # 打包为单个exe文件
        '--noconfirm',  # 不确认覆盖
        '--clean',  # 清理临时文件
        
        # 添加数据文件
        '--add-data', 'todo_data.db;.',
        
        # 图标（如果有的话）
        # '--icon=icon.ico',
        
        # 隐藏导入
        '--hidden-import', 'PyQt5.sip',
        '--hidden-import', 'PyQt5.QtCore',
        '--hidden-import', 'PyQt5.QtGui',
        '--hidden-import', 'PyQt5.QtWidgets',
        
        # 优化
        '--strip',  # 去除符号表
        
        # 主程序文件
        'main.py'
    ]
    
    print("开始打包...")
    print(f"命令: {' '.join(pyinstaller_args)}\n")
    
    try:
        result = subprocess.run(pyinstaller_args, check=True, capture_output=True, text=True)
        print(result.stdout)
        print("打包成功！\n")
        return True
    except subprocess.CalledProcessError as e:
        print(f"打包失败！\n")
        print(f"错误信息: {e.stderr}")
        return False


def create_distribution():
    """创建发布版本"""
    dist_dir = 'dist'
    release_dir = 'release'
    
    if not os.path.exists(dist_dir):
        print("错误: 未找到dist目录，打包可能失败！")
        return False
    
    # 创建发布目录
    if os.path.exists(release_dir):
        shutil.rmtree(release_dir)
    os.makedirs(release_dir)
    
    # 复制exe文件
    exe_name = 'My Todo.exe'
    src_exe = os.path.join(dist_dir, exe_name)
    dst_exe = os.path.join(release_dir, exe_name)
    
    if os.path.exists(src_exe):
        shutil.copy2(src_exe, dst_exe)
        print(f"复制: {exe_name}")
    else:
        print(f"错误: 未找到 {exe_name}")
        return False
    
    # 创建启动脚本
    bat_content = '''@echo off
chcp 65001 >nul
echo 正在启动My Todo...
start "" "%~dp0My Todo.exe"
'''
    bat_path = os.path.join(release_dir, '启动.bat')
    with open(bat_path, 'w', encoding='utf-8') as f:
        f.write(bat_content)
    print("创建: 启动.bat")
    
    # 复制README
    if os.path.exists('README.md'):
        shutil.copy2('README.md', os.path.join(release_dir, '使用说明.txt'))
        print("复制: 使用说明.txt")
    
    print(f"\n发布版本已创建在 '{release_dir}' 目录中！")
    return True


def main():
    """主函数"""
    print("=" * 50)
    print("My Todo - 打包工具")
    print("=" * 50)
    print()
    
    # 检查PyInstaller是否安装
    try:
        import PyInstaller
        print(f"PyInstaller版本: {PyInstaller.__version__}")
    except ImportError:
        print("错误: 未安装PyInstaller！")
        print("请先运行: pip install pyinstaller")
        sys.exit(1)
    
    print()
    
    # 清理之前的构建
    clean_build()
    
    # 打包
    if build_exe():
        # 创建发布版本
        create_distribution()
        print("\n打包完成！")
        print("可执行文件位于: dist/My Todo.exe")
        print("发布版本位于: release/")
    else:
        print("\n打包失败，请检查错误信息！")
        sys.exit(1)


if __name__ == '__main__':
    main()
