from flask import Flask, request, render_template, redirect, url_for, send_from_directory
import pandas as pd
import matplotlib.pyplot as plt
import os

app = Flask(__name__)
UPLOAD_FOLDER = 'uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# 确保上传目录存在
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        file = request.files['file']
        if file:
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
            file.save(file_path)
            return redirect(url_for('analyze', filename=file.filename))
    return render_template('index.html')

@app.route('/analyze/<filename>')
def analyze(filename):
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    data = pd.read_excel(file_path)

    # 剔除总分为0的学生
    filtered_data = data[data['总分'] > 0]

    # 按班级计算平均分
    filtered_class_avg_scores = filtered_data.groupby('班级')['总分'].mean().reset_index()
    filtered_class_avg_scores.columns = ['班级', '平均总分']

    # 绘制图表
    plt.figure(figsize=(10, 6))
    bars = plt.bar(filtered_class_avg_scores['班级'], filtered_class_avg_scores['平均总分'])

    for bar in bars:
        height = bar.get_height()
        plt.annotate(f'{height:.2f}', 
                     xy=(bar.get_x() + bar.get_width() / 2, height),
                     xytext=(0, 3),
                     textcoords="offset points",
                     ha='center', va='bottom')

    plt.title('各班平均总分（剔除0分学生）', fontsize=16)
    plt.xlabel('班级', fontsize=12)
    plt.ylabel('平均总分', fontsize=12)

    # 保存图片到 uploads 目录
    chart_path = os.path.join(app.config['UPLOAD_FOLDER'], 'average_scores.png')
    plt.savefig(chart_path)
    plt.close()

    # 返回显示图片的页面
    return f'<img src="/uploads/average_scores.png" alt="班级平均分图表" />'

# 提供静态文件的路由
@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
