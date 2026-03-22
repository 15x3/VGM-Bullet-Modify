#!/usr/bin/env python3
"""
脚本用于从45ammos.xml文件中提取所有identifier，
并生成对应的本地化模板文件Template.xml
"""

import xml.etree.ElementTree as ET
import os
import re
from pathlib import Path

def extract_identifiers_from_xml(xml_file_path):
    """
    从XML文件中提取所有Item标签的identifier属性
    """
    identifiers = []

    try:
        # 解析XML文件
        tree = ET.parse(xml_file_path)
        root = tree.getroot()

        # 查找所有Item标签
        for item in root.findall('Item'):
            identifier = item.get('identifier')
            if identifier:
                identifiers.append(identifier)

    except ET.ParseError as e:
        print(f"解析XML文件错误: {e}")
        return []
    except Exception as e:
        print(f"处理文件时发生错误: {e}")
        return []

    return identifiers

def generate_template_xml(identifiers, output_file_path):
    """
    生成本地化模板XML文件
    """
    # 创建XML根元素
    root = ET.Element('infotexts')
    root.set('language', 'English')
    root.set('nowhitespace', 'true')
    root.set('translatedname', 'English')

    # 为每个identifier创建对应的本地化条目
    for identifier in identifiers:
        # 创建实体名称条目
        name_elem = ET.SubElement(root, f'entityname.{identifier}')
        name_elem.text = f'{identifier}.name'

        # 创建实体描述条目
        desc_elem = ET.SubElement(root, f'entitydescription.{identifier}')
        desc_elem.text = f'{identifier}.description'

    # 格式化XML输出
    indent_xml(root)

    # 保存到文件
    tree = ET.ElementTree(root)
    tree.write(output_file_path, encoding='utf-8', xml_declaration=True)

    print(f"成功生成模板文件: {output_file_path}")
    print(f"共处理了 {len(identifiers)} 个identifier")

def indent_xml(elem, level=0):
    """
    为XML添加缩进，使其更易读
    """
    i = "\n" + level * "  "
    if len(elem):
        if not elem.text or not elem.text.strip():
            elem.text = i + "  "
        if not elem.tail or not elem.tail.strip():
            elem.tail = i
        for child in elem:
            indent_xml(child, level + 1)
        if not child.tail or not child.tail.strip():
            child.tail = i
    else:
        if level and (not elem.tail or not elem.tail.strip()):
            elem.tail = i

def main():
    # 定义文件路径
    current_dir = Path(__file__).parent
    xml_file = current_dir / "Ammos" / "45ammos.xml"
    output_dir = current_dir / "Localization"
    output_file = output_dir / "Template.xml"

    # 检查输入文件是否存在
    if not xml_file.exists():
        print(f"错误: 找不到输入文件 {xml_file}")
        return

    # 确保输出目录存在
    output_dir.mkdir(exist_ok=True)

    # 提取identifiers
    print(f"正在从 {xml_file} 提取identifiers...")
    identifiers = extract_identifiers_from_xml(xml_file)

    if not identifiers:
        print("未找到任何identifier")
        return

    print(f"找到 {len(identifiers)} 个identifier:")
    for id in identifiers:
        print(f"  - {id}")

    # 生成模板文件
    print(f"\n正在生成模板文件...")
    generate_template_xml(identifiers, output_file)

if __name__ == "__main__":
    main()