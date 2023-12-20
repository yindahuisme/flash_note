import tkinter as tk
import os
import json
import subprocess
from uuid import getnode as get_machine_id

# 获取机器唯一ID
machine_id = str(get_machine_id())

# 笔记存储路径
notes_directory = f'notes_{machine_id}'
if not os.path.exists(notes_directory):
    os.makedirs(notes_directory)

# 保存笔记
def save_note():
    note_text = note_text_box.get("1.0", tk.END)
    note_file_path = os.path.join(notes_directory, f'note_{machine_id}.json')
    with open(note_file_path, 'w') as f:
        json.dump({'note': note_text}, f)
    status_label.config(text="Note saved successfully!")
    commit_changes()

# 提交更改到Git
def commit_changes():
    subprocess.run(['git', 'add', '.'], cwd=notes_directory)
    commit_message = "Update notes"
    subprocess.run(['git', 'commit', '-m', commit_message], cwd=notes_directory)

# 搜索并返回匹配的笔记文件
def search_notes(search_query):
    matches = []
    for filename in os.listdir(notes_directory):
        if filename.endswith('.json'):
            with open(os.path.join(notes_directory, filename), 'r') as f:
                content = json.load(f).get('note', '')
            if search_query.lower() in content.lower():
                matches.append((filename, content))
    return matches

# 创建GUI
root = tk.Tk()
root.title("闪念笔记")

# 搜索框
search_box = tk.Entry(root)
search_box.pack()

# 搜索结果下拉框
search_results = tk.Listbox(root)
search_results.pack()

# 更新搜索结果
def update_search_results(event):
    search_query = search_box.get()
    matches = search_notes(search_query)
    search_results.delete(0, tk.END)
    for filename, content in matches:
        display_text = f"{filename}: {content[:50]}"  # Show file name and first 50 characters
        search_results.insert(tk.END, display_text)

search_box.bind('<KeyRelease>', update_search_results)

# 选中搜索结果事件处理
def on_select_search_result(event):
    selection = event.widget.curselection()
    if selection:
        index = selection[0]
        filename, _ = search_results.get(index).split(': ', 1)
        note_file_path = os.path.join(notes_directory, filename)
        with open(note_file_path, 'r') as f:
            note_content = json.load(f).get('note', '')
        note_text_box.delete("1.0", tk.END)
        note_text_box.insert(tk.END, note_content)

search_results.bind('<<ListboxSelect>>', on_select_search_result)

# 笔记文本框
note_text_box = tk.Text(root, height=10, width=50)
note_text_box.pack()

# 实时保存笔记
note_text_box.bind('<KeyRelease>', lambda event: save_note())

# 状态标签
status_label = tk.Label(root, text="")
status_label.pack()

root.mainloop()
