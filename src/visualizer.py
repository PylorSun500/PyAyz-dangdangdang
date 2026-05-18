import pandas as pd
import re
from pyecharts import options as opts
from pyecharts.charts import Pie, Bar
from pyecharts.globals import ThemeType


class DataVisualizer:
    def __init__(self, csv_file='data/dangdang_books.csv'):
        self.df = None
        self.csv_file = csv_file

    def load_data(self):
        try:
            self.df = pd.read_csv(self.csv_file, encoding='utf-8-sig')
            self.df['售价'] = pd.to_numeric(self.df['售价'], errors='coerce')
            self.df['评论数'] = pd.to_numeric(self.df['评论数'], errors='coerce')
            return True
        except Exception as e:
            print(f'加载数据失败: {e}')
            return False

    def create_price_pie(self):
        if self.df is None:
            return None

        price_ranges = ['0-30元', '30-70元', '70-100元', '100元以上']
        counts = [
            len(self.df[self.df['售价'] <= 30]),
            len(self.df[(self.df['售价'] > 30) & (self.df['售价'] <= 70)]),
            len(self.df[(self.df['售价'] > 70) & (self.df['售价'] <= 100)]),
            len(self.df[self.df['售价'] > 100])
        ]

        pie = (
            Pie(init_opts=opts.InitOpts(theme=ThemeType.LIGHT, width='100%', height='500px', bg_color='#ffffff'))
            .add(
                '',
                [list(z) for z in zip(price_ranges, counts)],
                radius=['40%', '70%'],
                label_opts=opts.LabelOpts(
                    formatter='{b}: {c}本 ({d}%)',
                    color='#333333'
                )
            )
            .set_global_opts(
                title_opts=opts.TitleOpts(
                    title='图书售价区间分布',
                    pos_left='center',
                    title_textstyle_opts=opts.TextStyleOpts(color='#333333')
                ),
                legend_opts=opts.LegendOpts(
                    orient='vertical',
                    pos_left='left',
                    textstyle_opts=opts.TextStyleOpts(color='#333333')
                )
            )
        )

        return pie

    def _get_top_n_deduplicated(self, value_col, n=15):
        """获取TOP N数据，并对相似书名去重（合并不同版次的同一本书）"""
        if self.df is None:
            return None

        # 取更大的范围用于去重后仍有足够条目
        top = self.df.nlargest(n * 3, value_col)[['书名', value_col]].copy()
        top = top.dropna(subset=[value_col])

        # 生成标准化去重key：去标点→转小写→取前15字
        def make_key(title):
            key = re.sub(
                r'[：:;；,，。.！!？?、\s（(）)）【】\[\]"\'《》<>『』「」　]',
                '', str(title)
            )
            return key[:15].lower()

        top['_key'] = top['书名'].apply(make_key)

        # 同key的书籍合并，取价值最高的那个
        result = top.loc[top.groupby('_key')[value_col].idxmax()].copy()
        result = result.nlargest(n, value_col)[['书名', value_col]]

        return result

    def _format_title(self, name, max_len=18):
        """统一格式化书名：过长则截断，过短则不变"""
        name = str(name).strip()
        if len(name) > max_len:
            return name[:max_len] + '...'
        return name

    def create_price_bar(self):
        if self.df is None:
            return None

        top_books = self._get_top_n_deduplicated('售价', 15)
        if top_books is None:
            return None
        top_books = top_books.sort_values('售价', ascending=True)

        # 统一格式化书名
        book_names = [self._format_title(name) for name in top_books['书名'].tolist()]

        bar = (
            Bar(init_opts=opts.InitOpts(theme=ThemeType.LIGHT, width='100%', height='600px', bg_color='#ffffff'))
            .add_xaxis(book_names)
            .add_yaxis(
                '售价(元)',
                top_books['售价'].tolist(),
                itemstyle_opts=opts.ItemStyleOpts(
                    color='#5470c6'
                )
            )
            .set_global_opts(
                title_opts=opts.TitleOpts(
                    title='图书售价TOP15',
                    pos_left='center',
                    title_textstyle_opts=opts.TextStyleOpts(color='#333333')
                ),
                xaxis_opts=opts.AxisOpts(
                    axislabel_opts=opts.LabelOpts(rotate=45, interval=0, color='#333333')
                ),
                yaxis_opts=opts.AxisOpts(
                    name='售价(元)',
                    axislabel_opts=opts.LabelOpts(color='#333333'),
                    name_textstyle_opts=opts.TextStyleOpts(color='#333333')
                ),
                datazoom_opts=[opts.DataZoomOpts(type_='slider')]
            )
        )

        return bar

    def create_comment_bar(self):
        if self.df is None:
            return None

        top_comments = self._get_top_n_deduplicated('评论数', 15)
        if top_comments is None:
            return None
        top_comments = top_comments.sort_values('评论数', ascending=True)

        # 统一格式化书名
        book_names = [self._format_title(name) for name in top_comments['书名'].tolist()]

        bar = (
            Bar(init_opts=opts.InitOpts(theme=ThemeType.LIGHT, width='100%', height='600px', bg_color='#ffffff'))
            .add_xaxis(book_names)
            .add_yaxis(
                '评论数',
                top_comments['评论数'].tolist(),
                itemstyle_opts=opts.ItemStyleOpts(
                    color='#91cc75'
                ),
                markline_opts=opts.MarkLineOpts(
                    data=[
                        opts.MarkLineItem(type_='average', name='平均值'),
                        opts.MarkLineItem(type_='max', name='最大值'),
                        opts.MarkLineItem(type_='min', name='最小值')
                    ],
                    label_opts=opts.LabelOpts(color='#333333')
                )
            )
            .set_global_opts(
                title_opts=opts.TitleOpts(
                    title='图书评论数TOP15',
                    pos_left='center',
                    title_textstyle_opts=opts.TextStyleOpts(color='#333333')
                ),
                xaxis_opts=opts.AxisOpts(
                    axislabel_opts=opts.LabelOpts(rotate=45, interval=0, color='#333333')
                ),
                yaxis_opts=opts.AxisOpts(
                    name='评论数',
                    axislabel_opts=opts.LabelOpts(color='#333333'),
                    name_textstyle_opts=opts.TextStyleOpts(color='#333333')
                ),
                datazoom_opts=[opts.DataZoomOpts(type_='slider')],
                legend_opts=opts.LegendOpts(
                    textstyle_opts=opts.TextStyleOpts(color='#333333')
                )
            )
        )

        return bar

    def get_statistics(self):
        if self.df is None:
            return {}

        return {
            '总书籍数': len(self.df),
            '平均售价': round(self.df['售价'].mean(), 2),
            '平均评论数': round(self.df['评论数'].mean(), 0),
            '最高售价': round(self.df['售价'].max(), 2),
            '最低售价': round(self.df['售价'].min(), 2),
            '总评论数': int(self.df['评论数'].sum())
        }
