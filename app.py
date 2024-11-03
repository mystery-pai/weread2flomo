"""
微信读书笔记处理器 - 主程序

这个模块实现了一个基于Streamlit的Web应用，用于处理微信读书笔记。
主要功能包括:
1. 解析微信读书笔记文本
2. 使用LLM对笔记进行润色和标签生成
3. 将处理后的笔记导出到Flomo
"""

import streamlit as st
from modules.note_parser import parse_notes
from modules.llm_processor import process_with_llm
from modules.flomo_exporter import export_to_flomo
from config.settings import LLM_API_KEY, FLOMO_API_ENDPOINT
import asyncio
from concurrent.futures import ThreadPoolExecutor
import threading
import time

def init_session_state():
    """
    初始化Streamlit会话状态
    """
    if 'processed_notes' not in st.session_state:
        st.session_state.processed_notes = []
    if 'original_notes' not in st.session_state:
        st.session_state.original_notes = None
    if 'processing_tasks' not in st.session_state:
        st.session_state.processing_tasks = {}  # 存储正在处理的任务状态

def process_single_note(note, index):
    """
    处理单条笔记
    
    Args:
        note (dict): 原始笔记数据
        index (int): 笔记在列表中的索引
    """
    try:
        # 构建完整的数据结构，包含书籍信息
        note_data = {
            'title': st.session_state.original_notes.get('title', ''),
            'author': st.session_state.original_notes.get('author', ''),
            'notes': [note]
        }
        result = process_with_llm(note_data, LLM_API_KEY)[0]
        st.session_state.processed_notes[index] = result
        st.session_state.processing_tasks[index] = 'completed'
    except Exception as e:
        st.session_state.processing_tasks[index] = 'failed'
        print(f"处理笔记时出错: {str(e)}")

def export_single_note(note):
    """
    导出单条笔记到Flomo
    
    Args:
        note (dict): 处理后的笔记数据
    
    Returns:
        bool: 导出是否成功
    """
    try:
        return export_to_flomo([note])
    except Exception as e:
        st.error(f"导出笔记时出错: {str(e)}")
        return False

def update_processed_note(index, field, value):
    """
    更新处理后笔记的指定字段
    
    Args:
        index (int): 笔记索引
        field (str): 要更新的字段名
        value: 新的值
    """
    if st.session_state.processed_notes[index]:
        st.session_state.processed_notes[index][field] = value

def main():
    """
    主函数，实现Web应用的界面和交互逻辑
    包括：
    - 笔记输入界面
    - 笔记解析功能
    - 批量处理功能
    - 单条笔记处理功能
    - 笔记导出功能
    """
    st.title("微信读书笔记处理器")
    st.write("将微信读书笔记转换为结构化内容并导出到 Flomo")
    
    init_session_state()

    # 输入区域
    notes_text = st.text_area("请粘贴您的微信读书笔记文本：", height=200)

    if st.button("解析笔记"):
        if not notes_text:
            st.error("请输入笔记文本")
            return

        try:
            # 解析笔记
            parsed_notes = parse_notes(notes_text)
            st.session_state.original_notes = parsed_notes
            st.session_state.processed_notes = [None] * len(parsed_notes['notes'])
            st.session_state.processing_tasks = {}  # 重置处理状态
            
            # 显示书籍信息
            title = parsed_notes.get('title', '未知')
            author = parsed_notes.get('author', '未知')
            
            st.success(f"成功解析 {len(parsed_notes['notes'])} 条笔记")
            st.info(f"📖 书名：{title}")
            st.info(f"✍️ 作者：{author}")

        except Exception as e:
            st.error(f"解析笔记时出错: {str(e)}")
            return

    # 显示单个笔记卡片
    if st.session_state.original_notes:
        for i, note in enumerate(st.session_state.original_notes['notes']):
            with st.container():
                st.markdown("---")
                col1, col2 = st.columns(2)
                
                # 左侧：原始笔记
                with col1:
                    st.markdown(f"**章节**：{note['chapter']}")
                    st.text_area("原文", note['content'], key=f"original_{i}", height=150)
                    
                    # 获取当前处理状态
                    processing_status = st.session_state.processing_tasks.get(i)
                    
                    # 润色按钮
                    if st.button("润色", key=f"process_{i}", 
                               disabled=processing_status == 'processing'):
                        st.session_state.processing_tasks[i] = 'processing'
                        # 启动处理
                        process_single_note(note, i)
                        st.experimental_rerun()
                    
                    # 显示处理状态
                    if processing_status == 'processing':
                        st.spinner("处理中...")
                    elif processing_status == 'completed':
                        st.success("处理成功！")
                    elif processing_status == 'failed':
                        st.error("处理失败")
                
                # 右侧：处理后的笔记
                with col2:
                    processed = st.session_state.processed_notes[i]
                    if processed:
                        # 小标题输入
                        new_sub_title = st.text_input(
                            "小标题", 
                            processed['sub_title'], 
                            key=f"sub_title_{i}"
                        )
                        if new_sub_title != processed['sub_title']:
                            update_processed_note(i, 'sub_title', new_sub_title)
                        
                        # 润色后文本输入
                        new_refined_text = st.text_area(
                            "润色后文本", 
                            processed['refined_text'], 
                            key=f"refined_{i}", 
                            height=100
                        )
                        if new_refined_text != processed['refined_text']:
                            update_processed_note(i, 'refined_text', new_refined_text)
                        
                        # 标签输入和编辑
                        tags_str = ", ".join(processed['tags'])
                        new_tags = st.text_input(
                            "标签（用逗号分隔）", 
                            tags_str, 
                            key=f"tags_{i}",
                            help="多个标签请用逗号分隔，例如：标签1, 标签2, 标签3"
                        )
                        if new_tags != tags_str:
                            new_tags_list = [tag.strip() for tag in new_tags.split(",") if tag.strip()]
                            update_processed_note(i, 'tags', new_tags_list)
                        
                        # 显示当前标签
                        st.markdown("**当前标签：**")
                        for tag in processed['tags']:
                            st.markdown(f"- {tag}")
                        
                        if st.button("导出到Flomo", key=f"export_{i}"):
                            if export_single_note(processed):
                                st.success("导出成功！")
                    else:
                        if processing_status == 'processing':
                            st.info("正在处理中...")
                        else:
                            st.info("点击左侧'润色'按钮处理笔记")

if __name__ == "__main__":
    main()
