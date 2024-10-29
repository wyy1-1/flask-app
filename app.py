import os
from flask import Flask, render_template, request, redirect, url_for
import pandas as pd
import plotly.graph_objects as go
import plotly.io as pio
from werkzeug.utils import secure_filename

# 配置 Flask 应用
app = Flask(__name__)
UPLOAD_FOLDER = 'uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# 确保上传目录存在
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# 定义班级层次分组和对应颜色
grouping = {
    "英才班": ["01", "02", "03", "04", "13", "14", "15", "16"],
    "精英班": ["05", "06", "10", "11", "12"],
    "清北B班": ["07", "09"],
    "清北A班": ["08"]  # 单班级，不做比较
}
color_mapping = {
    "英才班": 'blue',
    "精英班": 'green',
    "清北B班": 'orange',
    "清北A班": 'purple'
}

def process_file(filepath):
    df = pd.read_excel(filepath)
    df['班级'] = df['班级'].apply(lambda x: f"{int(x)}班")
    single_choice_df = df[df['题号'].str.startswith('A')]
    result = single_choice_df.pivot_table(
        index='班级', columns='题号', values='正答率', aggfunc='mean'
    )
    return result

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
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
    df = process_file(filepath)

    graphs = []
    for col in df.columns:
        fig = go.Figure()

        # 遍历层次，分配不同颜色并绘制柱状图
        for level, classes in grouping.items():
            level_classes = [f"{int(c)}班" for c in classes]
            level_data = df[df.index.isin(level_classes)]

            if not level_data.empty:
                color = color_mapping[level]
                for cls in level_data.index:
                    fig.add_trace(go.Bar(
                        x=[cls], y=[level_data.loc[cls, col]],
                        name=f"{level} - {cls}",
                        marker=dict(color=color)
                    ))

        fig.update_layout(
            title=dict(text=f"{col} 的正答率 - 分层对比", font=dict(size=20)),
            xaxis_title=dict(text="班级", font=dict(size=16)),
            yaxis_title=dict(text="正答率 (%)", font=dict(size=16)),
            barmode='group',
            width=900,
            height=600
        )

        graph_html = pio.to_html(fig, full_html=False)
        graphs.append({'html': graph_html, 'title': col})

    return render_template('index.html', graphs=graphs)

if __name__ == '__main__':
    app.run(debug=True)
