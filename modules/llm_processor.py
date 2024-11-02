import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from openai import OpenAI
import json
import logging
from config.settings import LLM_API_ENDPOINT, LLM_API_KEY, LLM_MODEL

# 设置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def process_with_llm(parsed_notes, api_key):
    # 添加详细的调试日志
    logger.debug("Received parsed_notes structure:")
    logger.debug(f"Type: {type(parsed_notes)}")
    logger.debug(f"Keys: {parsed_notes.keys() if isinstance(parsed_notes, dict) else 'Not a dict'}")
    logger.debug(f"Title: {parsed_notes.get('title', 'NO TITLE')}")
    logger.debug(f"Full content: {json.dumps(parsed_notes, ensure_ascii=False)}")
    
    processed_notes = []
    notes = parsed_notes.get('notes', [])
    book_title = parsed_notes.get('title', '')
    
    for index, note in enumerate(notes):
        logger.info(f"Processing note {index + 1}/{len(notes)}")
        
        try:
            prompt = construct_prompt(note)
            response = get_llm_completion(prompt, note['content'], api_key)
            
            if response and hasattr(response, 'choices') and len(response.choices) > 0:
                result = parse_llm_response(response)
                
                # 处理标签：将书名和LLM生成的标签组合
                tags = []
                if book_title:
                    tags.append(book_title)
                if isinstance(result['tags'], list):
                    tags.extend(result['tags'])
                elif isinstance(result['tags'], str):
                    tags.extend([tag.strip() for tag in result['tags'].split(',')])
                
                processed_note = {
                    'title': book_title,
                    'chapter': note.get('chapter', ''),
                    'original_content': note['content'],
                    'refined_text': result['refined_text'],
                    'sub_title': result['sub_title'],
                    'tags': tags
                }
                processed_notes.append(processed_note)
                logger.info(f"Successfully processed note {index + 1}")
                logger.info(f"Processing note with book title: {book_title}")
                logger.info(f"Processed note result: {processed_note}")
            else:
                logger.error(f"Invalid response for note {index + 1}")
                processed_notes.append(create_fallback_note(note, book_title))
        except Exception as e:
            logger.error(f"Error processing note {index + 1}: {str(e)}")
            processed_notes.append(create_fallback_note(note, book_title))

    return processed_notes

def construct_prompt(note):
    content = note['content'] if isinstance(note, dict) else note
    return f"""请对以下笔记进行处理，不要急一步步来：
    1. 润色文本，使其更加流畅和易读。
    2. 为每段文本生成一个总结性的小标题（不超过20个字）。
    3. 为笔记生成2-3个相关标签。

    ## Rules
    1. 不改变原文意思，最大程度保留原文的风格和语义。
    2. 不无中生有。

    ## Input
    原始笔记：{content}

    ## Output
    请以JSON格式返回结果，包含以下字段：
    - refined_text: 润色后的文本
    - sub_title: 生成的小标题
    - tags: 生成的标签列表
    """

def get_llm_completion(prompt, input, api_key):
    try:
        client = OpenAI(api_key=api_key, base_url=LLM_API_ENDPOINT)
        response = client.chat.completions.create(
            model=LLM_MODEL,
            messages=[
                {"role": "system", "content": prompt},
                {"role": "user", "content": input}
            ],
            temperature=0.7
        )
        return response
    except Exception as e:
        logger.error(f"Error in LLM API call: {str(e)}")
        return None

def parse_llm_response(response):
    try:
        content = response.choices[0].message.content
        # 移除可能的markdown代码块标记
        content = content.replace('```json', '').replace('```', '').strip()
        result = json.loads(content)
        
        # 确保所有必需的字段都存在
        required_fields = ['refined_text', 'sub_title', 'tags']
        for field in required_fields:
            if field not in result:
                raise ValueError(f"Missing required field: {field}")
        
        # 确保tags是列表类型
        if isinstance(result['tags'], str):
            result['tags'] = [tag.strip() for tag in result['tags'].split(',')]
        elif not isinstance(result['tags'], list):
            result['tags'] = [str(result['tags'])]
        
        return result
    except (AttributeError, json.JSONDecodeError, IndexError, ValueError) as e:
        logger.error(f"Error parsing LLM response: {str(e)}")
        logger.error(f"Raw response content: {response.choices[0].message.content if hasattr(response, 'choices') and len(response.choices) > 0 else 'No valid response'}")
        raise ValueError("Invalid response format from LLM")

def create_fallback_note(note, book_title=''):
    """创建失败时的备用笔记"""
    return {
        'title': book_title,
        'chapter': note.get('chapter', ''),
        'original_content': note['content'],
        'refined_text': note['content'],
        'sub_title': '处理失败',
        'tags': [book_title, '处理失败'] if book_title else ['处理失败']
    }

# 测试函数
def test_process_with_llm():
    test_notes = {
        "title": "软能力--吴军（精排版）",
        "author": "吴军",
        "note_count": 2,
        "notes": [
            {
                "chapter": "前言 太初有为",
                "content": "如果从做成事情这个角度来讲无疑是能力更重要"
            },
            {
                "chapter": "第一章 交往力",
                "content": "交往的能力是衡量一个人能否很好地适应现代社会的标准之一。需要注意的是，交往的能力不仅仅是善于待人接物、善于处理各类复杂的人际关系，它首先是能够识人，能够判断该与什么样的人交往。"
            }
        ]
    }
    test_api_key = "your_test_api_key_here"
    
    result = process_with_llm(test_notes, test_api_key)
    print(json.dumps(result, ensure_ascii=False, indent=2))

if __name__ == "__main__":
    test_process_with_llm()
