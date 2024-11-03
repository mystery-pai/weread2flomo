import requests
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config.settings import FLOMO_API_ENDPOINT, MAX_RETRIES, TIMEOUT
from utils.api_helpers import retry_request
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def export_to_flomo(processed_notes):
    """
    将处理后的笔记导出到Flomo。

    Args:
    processed_notes (list): 处理后的笔记列表。
    api_key (str): Flomo API密钥。

    Returns:
    bool: 导出是否成功。
    """
    headers = {
        "Content-Type": "application/json",
    }

    success_count = 0
    total_notes = len(processed_notes)

    for note in processed_notes:
        content = f"【{note['sub_title']}】\n\n{note['refined_text']}"
        if note['chapter']:
            content = f"{content} \n\n章节：{note['chapter']}"
        # if note['page']:
        #     content += f"\n\n页码：{note['page']}"
        # 添加书名作为标签
        # logger.info(f"note['title']: {note['title']}")
        # if note['title']:
        #     note['tags'].append(note['title'])
        tags = ' '.join([f"#{tag}" for tag in note['tags']])
        content += f"\n\n{tags}"

        data = {
            "content": content
        }

        try:
            response = retry_request(
                lambda: requests.post(FLOMO_API_ENDPOINT, headers=headers, json=data, timeout=TIMEOUT),
                max_retries=MAX_RETRIES
            )
            response.raise_for_status()
            success_count += 1
        except Exception as e:
            print(f"导出笔记到Flomo时出错: {str(e)}")

    success_rate = success_count / total_notes
    print(f"成功导出 {success_count}/{total_notes} 条笔记到Flomo")

    return success_rate > 0.8  # 如果成功率超过80%，则认为整体导出成功


def test_export_to_flomo():
    """
    测试导出到Flomo的功能。
    使用示例笔记数据测试export_to_flomo函数。
    """
    # 准备测试数据
    test_notes = [
        {
            'title':'软能力',
            'chapter': '前言 太初有为',
            'sub_title': '能力与成功',
            'refined_text': '在成就事业的过程中，能力的重要性远超其他因素。',
            'tags': ['人生观', '职业发展'],
            # 'page': '3'
        }
    ]
    

    # 执行测试
    result = export_to_flomo(test_notes)
    
    # 打印测试结果
    print(f"导出测试结果: {'成功' if result else '失败'}")

if __name__ == "__main__":
    test_export_to_flomo()
