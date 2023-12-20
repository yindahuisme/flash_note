import tkinter as tk
from tkinter import ttk
import os
import json
from time import time, localtime, strftime
from uuid import getnode as get_machine_id
from collections import Counter

# 获取机器唯一ID
machine_id = str(get_machine_id())

# 笔记文件名
note_filename = f'note_{machine_id}.json'

# 确保笔记文件存在
if not os.path.exists(note_filename):
    with open(note_filename, 'w') as f:
        json.dump({}, f)

# 当前选中的文档时间戳
selected_note_timestamp = None

# 保存笔记
def save_note():
    note_title = title_entry.get().strip()
    note_content = content_text_box.get("1.0", tk.END).strip()
    if note_title and note_content:
        with open(note_filename, 'r+') as f:
            notes = json.load(f)
            note_data = {'title': note_title, 'content': note_content}
            if selected_note_timestamp:
                # 更新选中的文档
                notes[selected_note_timestamp] = note_data
            else:
                # 创建新的文档
                notes[str(time())] = note_data
            f.seek(0)
            json.dump(notes, f)
            f.truncate()
        status_label.config(text="保存成功!")
        create_new_document()
        refresh_search_results()
    else:
        status_label.config(text="标题或内容为空!")

# 创建新文档
def create_new_document():
    global selected_note_timestamp
    selected_note_timestamp = None
    search_results.selection_clear(0, tk.END)
    title_entry.delete(0, tk.END)
    content_text_box.delete("1.0", tk.END)
    refresh_search_results()

# 删除文档
def delete_note():
    global selected_note_timestamp
    if selected_note_timestamp:
        with open(note_filename, 'r+') as f:
            notes = json.load(f)
            if selected_note_timestamp in notes:
                del notes[selected_note_timestamp]
                f.seek(0)
                json.dump(notes, f)
                f.truncate()
                status_label.config(text="文档已删除!")
                create_new_document()
                refresh_search_results()
            else:
                status_label.config(text="文档不存在!")
    else:
        status_label.config(text="没有选中的文档!")

# 刷新搜索结果
def refresh_search_results():
    search_query = search_box.get()
    if search_query:
        update_search_results(None)
    else:
        display_notes()

# 展示所有文档
def display_notes():
    with open(note_filename, 'r') as f:
        notes = json.load(f)
    # 按时间戳倒序排列，取前100个
    sorted_notes = sorted(notes.items(), key=lambda x: -float(x[0]))[:100]
    search_results.delete(0, tk.END)
    for timestamp, note_data in sorted_notes:
        local_time = strftime("%Y-%m-%d", localtime(float(timestamp) ))  # 转换为北京时间
        display_text = f"{local_time} {note_data['title']}"
        search_results.insert(tk.END, display_text)

# 搜索并返回匹配的文档内容
def search_notes(search_query):
    matches = []
    with open(note_filename, 'r') as f:
        notes = json.load(f)
    for timestamp, note_data in notes.items():
        keyword_frequency = calculate_keyword_frequency(note_data, search_query.lower())
        if search_query.lower() in note_data['title'].lower() or search_query.lower() in note_data['content'].lower():
            matches.append((timestamp, note_data, keyword_frequency))
    # Sort by keyword frequency and timestamp (newest first)
    matches.sort(key=lambda x: (-x[2], -float(x[0])))
    return matches

# 更新搜索结果
def update_search_results(event):
    search_query = search_box.get()
    if search_query:
        matches = search_notes(search_query)
        search_results.delete(0, tk.END)
        for timestamp, note_data, _ in matches:
            local_time = strftime("%Y-%m-%d", localtime(float(timestamp) ))  # 转换为北京时间
            display_text = f"{local_time} {note_data['title']}"
            search_results.insert(tk.END, display_text)
            if search_query.lower() in note_data['title'].lower() or search_query.lower() in note_data['content'].lower():
                search_results.itemconfig(tk.END, {'bg':'yellow'})  # 高亮显示匹配的文本
    else:
        display_notes()

# 计算关键词出现的频率
def calculate_keyword_frequency(note_data, keyword):
    title_freq = Counter(note_data['title'].lower().split())
    content_freq = Counter(note_data['content'].lower().split())
    return title_freq[keyword] + content_freq[keyword]

# 创建GUI界面
root = tk.Tk()
root.title("闪念笔记")

# 搜索框
search_box = tk.Entry(root)
search_box.pack()

# 搜索结果下拉框
search_results = tk.Listbox(root)
search_results.pack()

search_box.bind('<KeyRelease>', update_search_results)

# 选中搜索结果事件处理
def on_select_search_result(event):
    global selected_note_timestamp
    selection = event.widget.curselection()
    if selection:
        index = selection[0]
        selected_note_timestamp, note_data, _ = search_notes(search_box.get())[index]
        title_entry.delete(0, tk.END)
        title_entry.insert(tk.END, note_data['title'])
        content_text_box.delete("1.0", tk.END)
        content_text_box.insert(tk.END, note_data['content'])

search_results.bind('<<ListboxSelect>>', on_select_search_result)

# 笔记标题输入框
title_label = tk.Label(root, text="标题")
title_label.pack()
title_entry = tk.Entry(root)
title_entry.pack()

# 笔记内容文本框
content_label = tk.Label(root, text="内容")
content_label.pack()
content_text_box = tk.Text(root, height=10, width=50)
content_text_box.pack()

# 保存按钮
save_button = tk.Button(root, text="保存", command=save_note)
save_button.pack()

# 新建文档按钮
new_document_button = tk.Button(root, text="新建文档", command=create_new_document)
new_document_button.pack()

# 删除文档按钮
delete_button = tk.Button(root, text="删除文档", command=delete_note)
delete_button.pack()

# 状态标签
status_label = tk.Label(root, text="")
status_label.pack()

# 当程序启动时，展示所有文档
display_notes()

root.mainloop()
