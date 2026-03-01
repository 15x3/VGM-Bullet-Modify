
import csv
import xml.etree.ElementTree as ET
import xml.dom.minidom
import os
import re

def update_xml_from_csv(csv_file, xml_file):
    # 读取CSV数据
    csv_data = {}
    with open(csv_file, 'r', encoding='utf-8') as f:
        reader = csv.reader(f)
        headers = next(reader)  # 第一行是标题
        identifiers = headers[1:]  # 第一列是属性名，后面是identifier

        # 初始化数据字典
        for identifier in identifiers:
            csv_data[identifier] = {}

        # 读取每一行数据
        for row in reader:
            attr_name = row[0]  # 第一列是属性名
            values = row[1:]  # 后面是对应的值

            for i, identifier in enumerate(identifiers):
                if i < len(values):
                    csv_data[identifier][attr_name] = values[i]

    # 解析XML文件
    tree = ET.parse(xml_file)
    root = tree.getroot()

    # 遍历每个Item元素
    for item in root.findall('Item'):
        identifier = item.get('identifier')

        # 如果identifier在CSV数据中
        if identifier in csv_data:
            data = csv_data[identifier]

            # 获取Attack元素
            attack = item.find('.//Attack')
            if attack is not None:
                # 更新基本属性
                for attr in ['structuredamage', 'targetforce', 'itemdamage', 'severlimbsprobability', 'penetration']:
                    if attr in data and data[attr]:
                        attack.set(attr, data[attr])

                # 清除现有的Affliction元素
                for affliction in attack.findall('Affliction'):
                    attack.remove(affliction)

                # 添加新的Affliction元素
                for i in range(1, 7):  # 最多6个affliction
                    affliction_key = f'affliction{i}'
                    strength_key = f'strength{i}'
                    probability_key = f'probability{i}'

                    if affliction_key in data and data[affliction_key]:
                        affliction_elem = ET.SubElement(attack, 'Affliction')
                        affliction_elem.set('identifier', data[affliction_key])

                        if strength_key in data and data[strength_key]:
                            affliction_elem.set('strength', data[strength_key])

                        if probability_key in data and data[probability_key]:
                            affliction_elem.set('probability', data[probability_key])

    # 将XML转换为字符串并格式化
    rough_string = ET.tostring(root, encoding='utf-8')
    reparsed = xml.dom.minidom.parseString(rough_string)

    # 获取格式化后的XML，但保持原始的缩进风格
    pretty_xml = reparsed.toprettyxml(indent="    ")

    # 移除空行并处理缩进
    lines = pretty_xml.split('\n')
    cleaned_lines = []

    for line in lines:
        # 移除只包含空格的行
        if line.strip():
            # 修复minidom添加的额外空格
            line = re.sub(r'\s+$', '', line)
            cleaned_lines.append(line)

    # 确保每个Affliction元素单独一行
    final_lines = []
    for i, line in enumerate(cleaned_lines):
        final_lines.append(line)
        # 如果当前行包含Affliction开始标签，但没有结束标签，确保下一行是缩进的Affliction内容
        if '<Affliction' in line and '/>' not in line and i+1 < len(cleaned_lines):
            # 检查下一行是否是另一个元素或结束标签
            next_line = cleaned_lines[i+1]
            if not next_line.strip().startswith('<') or next_line.strip().startswith('</'):
                # 如果不是，插入一个空行
                final_lines.append('')

    # 保存格式化后的XML文件
    with open(xml_file, 'w', encoding='utf-8') as f:
        f.write('\n'.join(final_lines))

    print(f"XML文件 {xml_file} 已更新完成")

if __name__ == "__main__":
    # 文件路径
    csv_file = "45ammos_data.csv"
    xml_file = "Ammos/45ammos.xml"

    # 检查文件是否存在
    if not os.path.exists(csv_file):
        print(f"错误: CSV文件 {csv_file} 不存在")
        exit(1)

    if not os.path.exists(xml_file):
        print(f"错误: XML文件 {xml_file} 不存在")
        exit(1)

    # 更新XML文件
    update_xml_from_csv(csv_file, xml_file)
