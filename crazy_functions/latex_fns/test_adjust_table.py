import re
def adjust_table_widths(content, max_width=0.90, min_width=0.15):
    """
    智能调整 LaTeX 表格列宽
    参数:
        content (str): LaTeX 文档内容
        max_width (float): 每列宽度相对于 \textwidth 的最大比例
        min_width (float): 每列宽度相对于 \textwidth 的最小比例
    返回:
        str: 调整后的 LaTeX 文档内容
    """
    def extract_table_content(table_str):
        """提取表格内容和列定义"""
        # 提取列定义
        col_def_match = re.search(r'\\begin{tabular}{([^}]*)}', table_str, re.DOTALL)
        if not col_def_match:
            return None, None, None
                
        col_def = col_def_match.group(1)
        
        # 提取表格内容
        table_content = table_str[col_def_match.end():]
        end_pos = table_content.find('\\end{tabular}')
        if end_pos == -1:
            return None, None, None
                
        table_content = table_content[:end_pos]
        return col_def, table_content, table_str

    def analyze_table_content(content):
        """分析表格内容, 返回每列的最大内容长度"""
        col_lengths = []
        lines = content.split('\\\\')
        for line in lines:
            line = line.strip()
            # 移除行中的 \hline 和 \cline 命令，而不是跳过整行
            line = re.sub(r'\\(hline|cline{[^}]*})', '', line).strip()
            if not line:  # 如果去除命令后行为空则跳过
                continue
            cells = line.split('&')
            # 确保 col_lengths 长度与当前行的列数一致
            if len(cells) > len(col_lengths):
                col_lengths.extend([0] * (len(cells) - len(col_lengths)))
            for i, cell in enumerate(cells):
                # 清理 cell 内容，移除 LaTeX 命令
                clean_cell = re.sub(r'\\[a-zA-Z]+\*?(?:\[[^\]]*\])?(?:\{[^}]*\})?', '', cell)
                clean_cell = clean_cell.strip()
                cell_length = len(clean_cell)
                if cell_length > col_lengths[i]:
                    col_lengths[i] = cell_length
        return col_lengths

    def get_column_spec(col_lengths, orig_spec):
        """生成新的列规格"""
        if not col_lengths:
            return orig_spec
                
        # 计算相对宽度
        total_len = sum(col_lengths) or 1
        widths = []
        
        for length in col_lengths:
            if length <= 10:
                widths.append('c')
            else:
                # 计算相对宽度，但确保不会太窄
                width_ratio = length / total_len
                width = max(min_width, width_ratio * max_width)
                # 限制宽度不超过 1，以避免超过 \textwidth
                width = min(width, 1.0)
                widths.append(f"p{{{width:.2f}\\textwidth}}")
                    
        # 保留原始的垂直线
        if orig_spec.startswith('|'):
            new_spec = '|' + '|'.join(widths) + '|'
        else:
            new_spec = ''.join(widths)
                
        return new_spec

    def process_table(match):
        """处理单个表格"""
        table_str = match.group(0)
        col_def, content, full_str = extract_table_content(table_str)
        
        if not col_def or not content:
            return table_str
                
        col_lengths = analyze_table_content(content)
        new_spec = get_column_spec(col_lengths, col_def)
        
        # 保持原始内容，只替换列定义
        return table_str.replace(f"{{tabular}}{{{col_def}}}", f"{{tabular}}{{{new_spec}}}")

    # 匹配完整的表格环境，包括嵌套环境
    # 使用非贪婪匹配，并考虑可能的换行符
    pattern = r'\\begin{tabular}{[^}]*}.*?\\end{tabular}'
    return re.sub(pattern, process_table, content, flags=re.DOTALL)

content = r"""
Table 7: Performance (\%) of closed-source models regarding different task categories.

\begin{center}
\adjustbox{max width=\textwidth}{
\begin{tabular}{|c|c|c|c|c|c|c|c|c|c|}
\hline
\multicolumn{2}{|c|}{Model} & \multicolumn{2}{|c|}{Graph Theory} & \multicolumn{2}{|c|}{Graph Statistical Learning} & \multicolumn{2}{|c|}{Graph Embedding} & \multicolumn{2}{|c|}{Overall} \\
\cline{3-10}
\multicolumn{2}{|c|}{\phantom{X}} & Pass Rate & Accuracy & Pass Rate & Accuracy & Pass Rate & Accuracy & Pass Rate & Accuracy \\
\cline{1-10}
\multirow{4}{*}{Claude 3 Haiku} & No RAG & 52.9 & 31.6 & 23.4 & 9.7 & 32.6 & 2.9 & 42.2 & 22.4 \\
\cline{2-10}
 & RAG 3 & 68.9 & 47.7 & 22.1 & 11.4 & 23.9 & 1.1 & 50.8 & 32.6 \\
\cline{2-10}
 & RAG 5 & 63.5 & 44.4 & 29.9 & 16.4 & 15.2 & 2.5 & 49.0 & 32.2 \\
\cline{2-10}
 & RAG 7 & 65.4 & 51.0 & 25.3 & 15.2 & 17.4 & 6.5 & 49.0 & 36.2 \\
\cline{1-10}
\multirow{4}{*}{Claude 3 Sonnet} & No RAG & 57.1 & 33.2 & 15.6 & 4.6 & 10.9 & 0.0 & 40.4 & 21.6 \\
\cline{2-10}
 & RAG 3 & 63.5 & 45.8 & 13.6 & 7.6 & 19.6 & 5.8 & 44.5 & 30.7 \\
\cline{2-10}
 & RAG 5 & 63.5 & 45.5 & 16.2 & 9.7 & 21.7 & 4.7 & 45.9 & 31.1 \\
\cline{2-10}
 & RAG 7 & 66.4 & 50.0 & 25.3 & 12.3 & 21.7 & 4.3 & 50.0 & 34.6 \\
\cline{1-10}
\multirow{4}{*}{Claude 3 Opus} & No RAG & 69.2 & 47.3 & 31.2 & 15.1 & 47.8 & 14.5 & 55.7 & 34.7 \\
\cline{2-10}
 & RAG 3 & 74.4 & 59.4 & 39.6 & 28.3 & 21.7 & 0.0 & 59.2 & 44.7 \\
\cline{2-10}
 & RAG 5 & 73.4 & 56.4 & 39.6 & 28.8 & 41.3 & 20.7 & 60.4 & 44.9 \\
\cline{2-10}
 & RAG 7 & 75.6 & 59.8 & 42.9 & 28.6 & 32.6 & 13.0 & 61.9 & 46.2 \\
\cline{1-10}
\multirow{4}{*}{GPT-3.5} & No RAG & 64.1 & 35.1 & 24.7 & 8.4 & 15.2 & 1.1 & 47.9 & 24.0 \\
\cline{2-10}
 & RAG 3 & 67.0 & 44.3 & 32.5 & 12.0 & 41.3 & 5.1 & 54.3 & 31.1 \\
\cline{2-10}
 & RAG 5 & 64.4 & 45.2 & 33.1 & 16.2 & 43.5 & 5.4 & 53.1 & 32.9 \\
\cline{2-10}
 & RAG 7 & 64.7 & 45.8 & 33.8 & 15.9 & 37.0 & 3.3 & 52.9 & 33.0 \\
\cline{1-10}
\multirow{4}{*}{GPT-4 turbo} & No RAG & 72.4 & 42.1 & 39.0 & 14.8 & 41.3 & 12.0 & 59.6 & 31.2 \\
\cline{2-10}
 & RAG 3 & 74.7 & 48.5 & 40.3 & 21.4 & 17.4 & 2.2 & 59.2 & 36.2 \\
\cline{2-10}
 & RAG 5 & 75.6 & 50.0 & 56.5 & 29.7 & 50.0 & 2.9 & 67.6 & 39.6 \\
\cline{2-10}
 & RAG 7 & 74.7 & 51.3 & 46.8 & 23.8 & 52.2 & 7.6 & 64.3 & 39.1 \\
\cline{1-10}
\multirow{4}{*}{GPT-40} & No RAG & 69.9 & 48.1 & 48.7 & 21.4 & 32.6 & 5.8 & 60.2 & 36.3 \\
\cline{2-10}
 & RAG 3 & 73.7 & 55.5 & 51.3 & 24.7 & 47.8 & 9.8 & 64.7 & 42.1 \\
\cline{2-10}
 & RAG 5 & 74.7 & 54.8 & 55.2 & 27.8 & 56.5 & 9.1 & 67.2 & 42.6 \\
\cline{2-10}
 & RAG 7 & 76.9 & 57.4 & 48.1 & 24.3 & 54.4 & 4.0 & 66.2 & 42.7 \\
\cline{1-10}
\multirow{4}{*}{Gemini 1.0 Pro} & No RAG & 48.7 & 27.7 & 9.1 & 1.7 & 19.6 & 3.3 & 34.2 & 17.7 \\
\cline{2-10}
 & RAG 3 & 61.5 & 47.4 & 16.2 & 7.5 & 15.2 & 2.2 & 43.8 & 31.3 \\
\cline{2-10}
 & RAG 5 & 62.2 & 44.4 & 15.6 & 6.8 & 13.0 & 0.0 & 43.8 & 29.1 \\
\cline{2-10}
 & RAG 7 & 64.4 & 45.3 & 15.6 & 5.8 & 19.6 & 0.0 & 45.7 & 29.4 \\
\cline{1-10}
\multirow{4}{*}{Gemini 1.5 Pro} & No RAG & 59.6 & 37.2 & 21.4 & 6.6 & 13.0 & 1.8 & 44.0 & 24.8 \\
\cline{2-10}
 & RAG 3 & 70.2 & 52.0 & 24.7 & 12.0 & 30.4 & 13.8 & 52.9 & 36.6 \\
\cline{2-10}
 & RAG 5 & 71.2 & 51.3 & 29.2 & 16.7 & 19.6 & 11.2 & 53.9 & 37.3 \\
\cline{2-10}
 & RAG 7 & 70.5 & 51.9 & 23.4 & 15.3 & 21.7 & 7.3 & 52.0 & 36.9 \\
\cline{1-10}
\hline
\end{tabular}
}
\end{center}

Table 8: Performance (\%) of open-source models regarding different task categories.

\begin{center}
\adjustbox{max width=\textwidth}{
\begin{tabular}{|c|c|c|c|c|c|c|c|c|c|}
\hline
\multicolumn{2}{|c|}{Model} & \multicolumn{2}{|c|}{Graph Theory} & \multicolumn{2}{|c|}{Graph Statistical Learning} & \multicolumn{2}{|c|}{Graph Embedding} & \multicolumn{2}{|c|}{Overall} \\
\cline{3-10}
\multicolumn{2}{|c|}{\phantom{X}} & Pass Rate & Accuracy & Pass Rate & Accuracy & Pass Rate & Accuracy & Pass Rate & Accuracy \\
\cline{1-10}
\multirow{6}{*}{Llama 3} & No Fine-tune & 36.5 & 17.3 & 12.3 & 3.8 & 15.2 & 0.4 & 27.3 & 11.7 \\
\cline{2-10}
 & Code Only & 61.2 & 46.7 & 49.4 & 36.6 & 63.0 & 47.5 & 57.8 & 43.8 \\
\cline{2-10}
 & Code+RAG 3 & 51.6 & 30.1 & 47.4 & 30.9 & 63.0 & 44.2 & 51.4 & 31.6 \\
\cline{2-10}
 & Code+RAG 5 & 47.8 & 25.2 & 44.8 & 28.9 & 56.5 & 40.2 & 47.7 & 27.6 \\
\cline{2-10}
 & Code+RAG 7 & 47.1 & 25.1 & 46.8 & 30.6 & 60.9 & 36.2 & 48.2 & 27.7 \\
\cline{2-10}
 & Doc+Code & 69.6 & 53.2 & 42.9 & 23.2 & 80.4 & 62.0 & 62.5 & 44.9 \\
\cline{1-10}
\multirow{6}{*}{Deepseek Coder} & No Fine-tune & 56.1 & 33.8 & 30.5 & 9.9 & 30.4 & 7.6 & 46.1 & 24.2 \\
\cline{2-10}
 & Code Only & 62.5 & 46.9 & 47.4 & 33.4 & 65.2 & 49.6 & 58.2 & 43.1 \\
\cline{2-10}
 & Code+RAG 3 & 59.0 & 35.9 & 46.8 & 28.8 & 43.5 & 29.4 & 53.9 & 33.2 \\
\cline{2-10}
 & Code+RAG 5 & 52.9 & 32.0 & 43.5 & 32.3 & 30.4 & 24.3 & 48.1 & 31.4 \\
\cline{2-10}
 & Code+RAG 7 & 51.6 & 33.6 & 49.4 & 31.4 & 21.7 & 15.9 & 48.2 & 31.4 \\
\cline{2-10}
 & Doc+Code & 71.2 & 54.1 & 46.1 & 29.8 & 67.4 & 52.5 & 63.3 & 46.6 \\
\cline{1-10}
\hline
\end{tabular}
}
\end{center}
"""

print(adjust_table_widths(content))
