import re
import json

def parse_notes(notes_text):
    """
    解析微信读书笔记文本为单独的笔记列表。
    
    Args:
    notes_text (str): 原始的微信读书笔记文本。
    
    Returns:
    dict: 包含书名、笔记数量和解析后的笔记列表。
    """
    lines = notes_text.split('\n')
    book_info = {
        'title': '',
        'author': '',
        'note_count': 0,
        'notes': []
    }
    current_chapter = ''
    current_note = {}
    
    # 用于标记是否已经处理过作者和笔记数量
    author_processed = False

    for line in lines:
        line = line.strip()
        if not line:
            continue

        # 提取书名
        if line.startswith('《') and line.endswith('》'):
            book_info['title'] = line.strip('《》')
            continue
        
        # 提取作者和笔记数量（分两步处理）
        if not author_processed:
            # 先检查是否为作者名（通常在书名后的单独一行）
            if not book_info['author'] and not '个笔记' in line and book_info['title']:
                book_info['author'] = line
                continue
            
            # 再检查是否包含笔记数量
            note_count_match = re.match(r'^(\d+)个笔记$', line)
            if note_count_match:
                book_info['note_count'] = int(note_count_match.group(1))
                author_processed = True
                continue

        # 提取章节
        if not line.startswith('◆') and not '来自微信读书' in line:
            current_chapter = line
            continue

        # 提取笔记内容
        if line.startswith('◆'):
            if current_note:
                book_info['notes'].append(current_note)
            current_note = {
                'chapter': current_chapter,
                'content': line[1:].strip()
            }
        elif '-- 来自微信读书' in line:
            if current_note:
                book_info['notes'].append(current_note)
                current_note = {}
        elif current_note:
            current_note['content'] += ' ' + line

    # 添加最后一条笔记（如果有）
    if current_note:
        book_info['notes'].append(current_note)

    return book_info

# 测试函数
def test_parse_notes():
    test_input = """《软能力--吴军（精排版）》

吴军
9个笔记
前言 太初有为

◆ 如果从做成事情这个角度来讲，无疑是能力更重要

第一章 交往力

◆ 交往的能力是衡量一个人能否很好地适应现代社会的标准之一。需要注意的是，交往的能力不仅仅是善于待人接物、善于处理各类复杂的人际关系，它首先是能够识人，能够判断该与什么样的人交往。

-- 来自微信读书"""

    result = parse_notes(test_input)
    print(json.dumps(result, ensure_ascii=False, indent=2))

if __name__ == "__main__":
    test_parse_notes()
