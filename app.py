import os
from flask import Flask, render_template, request, redirect, url_for
import pandas as pd
import plotly.express as px
import plotly.io as pio
from werkzeug.utils import secure_filename

# 配置 Flask 应用
app = Flask(__name__)
UPLOAD_FOLDER = 'uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# 确保上传目录存在
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def process_file(filepath):
    # 从上传的 Excel 文件中读取数据
    df = pd.read_excel(filepath)

    # 筛选单选题（假设题号以 'A' 开头的是单选题）
    single_choice_df = df[df['题号'].str.startswith('A')]

    # 按班级和题号计算正答率的平均值
    result = single_choice_df.pivot_table(
        index='班级', columns='题号', values='正答率', aggfunc='mean'
    )
    return result

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        # 获取上传的文件
        uploaded_file = request.files['file']
        if uploaded_file:
            filename = secure_filename(uploaded_file.filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            uploaded_file.save(filepath)
            return redirect(url_for('analyze', filename=filename))
    return render_template('index.html')

@app.route('/analyze/<filename>')
def analyze(filename):
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    
    # 处理上传的文件，生成数据结果
    df = process_file(filepath)

    # 生成 Plotly 图表
    fig = px.bar(df, barmode='group', title="各班单选题正答率")
    fig.update_layout(xaxis_title="班级", yaxis_title="正答率 (%)")

    # 将图表转换为 HTML
    graph_html = pio.to_html(fig, full_html=False)

    # 渲染结果页面，并将图表传递给前端
    return render_template('index.html', graph_html=graph_html)

if __name__ == '__main__':
    app.run(debug=True)
