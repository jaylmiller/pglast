from pglast import Node, parse_sql, prettify

if __name__ == '__main__':
    # prettify('select 1')
    root = Node(parse_sql("SELECT 1 FROM asdf"))
    root.to_sql()