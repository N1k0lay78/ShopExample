from flask import Flask, render_template

app = Flask(__name__)

data = {
    "pages_links": [
        ['/', 'главная'],
        ['/item/1', 'товар номер 1']
    ]
}


def render_page(page: str, title, **kwargs):
    return render_template(page, title=title, data=data, **kwargs)


@app.route('/')
def main_page():
    return render_page('users/main.html', 'Главная')


if __name__ == '__main__':
    app.run(port=8001)
