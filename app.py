from flask import Flask, render_template, jsonify, request
import os
import sys

sys.path.append(os.path.dirname(__file__))

from src.crawler import DangdangCrawler
from src.visualizer import DataVisualizer

app = Flask(__name__)


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/crawl', methods=['POST'])
def crawl():
    try:
        pages = int(request.json.get('pages', 5))

        crawler = DangdangCrawler()
        books = crawler.crawl(max_pages=pages)

        if books:
            crawler.save_to_csv(books)
            return jsonify({
                'success': True,
                'message': f'成功爬取{len(books)}本书籍数据',
                'count': len(books)
            })
        else:
            return jsonify({
                'success': False,
                'message': '爬取失败，未获取到数据'
            })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'爬取出错: {str(e)}'
        })


@app.route('/visualize')
def visualize():
    try:
        visualizer = DataVisualizer()

        if not visualizer.load_data():
            return jsonify({
                'success': False,
                'message': '数据文件不存在，请先爬取数据'
            })

        price_pie = visualizer.create_price_pie()
        price_bar = visualizer.create_price_bar()
        comment_bar = visualizer.create_comment_bar()
        stats = visualizer.get_statistics()

        price_pie.render('static/price_pie.html')  # type: ignore
        price_bar.render('static/price_bar.html')  # type: ignore
        comment_bar.render('static/comment_bar.html')  # type: ignore

        return jsonify({
            'success': True,
            'message': '可视化图表生成成功',
            'statistics': stats
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'可视化出错: {str(e)}'
        })


@app.route('/chart/<chart_type>')
def get_chart(chart_type):
    chart_files = {
        'price_pie': 'static/price_pie.html',
        'price_bar': 'static/price_bar.html',
        'comment_bar': 'static/comment_bar.html'
    }

    chart_file = chart_files.get(chart_type)
    if chart_file and os.path.exists(chart_file):
        with open(chart_file, 'r', encoding='utf-8') as f:
            return f.read()
    else:
        return '图表文件不存在', 404


if __name__ == '__main__':
    os.makedirs('data', exist_ok=True)
    os.makedirs('static', exist_ok=True)
    os.makedirs('templates', exist_ok=True)

    app.run(debug=True, host='0.0.0.0', port=5001)
