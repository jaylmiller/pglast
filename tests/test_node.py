# -*- coding: utf-8 -*-
# :Project:   pglast -- Test the node.py module
# :Created:   ven 04 ago 2017 09:31:57 CEST
# :Author:    Lele Gaifax <lele@metapensiero.it>
# :License:   GNU General Public License version 3 or later
# :Copyright: © 2017, 2018, 2021 Lele Gaifax
#

import pytest

from pglast import ast, Missing, Node, parse_sql
from pglast.node import Base, List


def test_bad_base_construction():
    pytest.raises(ValueError, Base, {}, parent=1.0)
    pytest.raises(ValueError, Base, [], name=1.0)
    pytest.raises(ValueError, Base, set())


def test_setitem_scalar():
    root = Node(parse_sql("SELECT 1 FROM asdf"))
    for i in root.traverse():
        if hasattr(i, 'attribute_names'):
            if i.node_tag == 'RangeVar':
                i['relname'] = 'qwer'
            if i.node_tag == 'Integer':
                i['val'] = 2
    expected_ast = Node(parse_sql("select 2 from qwer"))
    assert root == expected_ast

def test_setitem_list():
    root = Node(parse_sql("select asdf from qwer join fff on qwer.id = fff.id"))
    root2 = Node(parse_sql('select 1 from asdf'))
    targetlist = None
    for n in root2.traverse():
        if hasattr(n, "attribute_names"):
            if 'targetList' in n.attribute_names:
                targetlist = n['targetList']
    for n in root.traverse():
        if hasattr(n, "attribute_names"):
            print(n.attribute_names)
            if 'targetList' in n.attribute_names:
                n['targetList'] = targetlist
    assert root == Node(parse_sql("select 1 from qwer join fff on qwer.id = fff.id"))

def test_setitem_node():
    root = Node(parse_sql("select asdf from qwer join (select generate_series(1,10) s) ss on qwer.a = ss.b "))  # noqa
    root2 = Node(parse_sql('select 1 from asdf'))
    select = root2[0]['stmt']

    for n in root.traverse():
        if hasattr(n, 'attribute_names') and 'subquery' in n.attribute_names:
            n['subquery'] = select

    assert root == Node(parse_sql("select asdf from qwer join (select 1 from asdf) ss on qwer.a = ss.b "))


def test_to_sql():
    root = Node(parse_sql("SELECT 1 FROM asdf"))
    out = root.to_sql()
    assert out == "\n".join(["SELECT 1", "FROM asdf"])

def test_basic():
    root = Node(parse_sql('SELECT 1'))
    assert root.parent_node is None
    assert root.parent_attribute is None
    assert isinstance(root, List)
    assert len(root) == 1
    assert repr(root) == '[1*{RawStmt}]'
    with pytest.raises(AttributeError):
        root.not_there

    rawstmt = root[0]
    assert rawstmt != root
    assert rawstmt.node_tag == 'RawStmt'
    assert isinstance(rawstmt.ast_node, ast.RawStmt)
    assert rawstmt.parent_node is None
    assert rawstmt.parent_attribute == (None, 0)
    assert repr(rawstmt) == '{RawStmt}'
    assert rawstmt.attribute_names == ('stmt', 'stmt_location', 'stmt_len')
    with pytest.raises(ValueError):
        rawstmt[1.0]

    stmt = rawstmt.stmt
    assert stmt.node_tag == 'SelectStmt'
    assert stmt.parent_node is rawstmt
    assert stmt.parent_attribute == 'stmt'
    assert rawstmt[stmt.parent_attribute] == stmt
    assert stmt.whereClause is Missing
    assert not stmt.whereClause


def test_scalar():
    constraint = ast.Constraint()
    constraint.fk_matchtype = '\00'
    node = Node(constraint)
    assert not node.fk_matchtype
