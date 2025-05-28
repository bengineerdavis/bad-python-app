from flask import render_template


def sql_injection_search_page(request, app):
    search = request.args.get('q', '')

    # Using SQLite's named parameter style with LIKE pattern
    sql = "SELECT * FROM products WHERE name LIKE :search_pattern"

    db_result = app.db_helper.execute_read(sql, {'search_pattern': f"%{search}%"})

    products = list(
        map(
            lambda p: {
                'id': p[0],
                'name': p[1],
                'price': p[2]
            },
            db_result
        )
    )

    return render_template(
        'sql_injection/search.html',
        products=products,
        search=search,
        sql=sql
    )
