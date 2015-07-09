from __future__ import unicode_literals, print_function, division
from lxml import etree
import re
import copy
import sys
import argparse
from pygraph.classes.digraph import digraph
from pygraph.algorithms.cycles import find_cycle

allowed_float_error = 1e-08


class Dimension(object):
    parsable_unit = ('', 'px', 'in', 'mm', 'pt', 'dp', 'sp')
    parse_regex = re.compile(r"(\d*\.?\d*)(\w*)")

    dimensions = dict()
    original_dimensions = None

    def __init__(self, name, value, unit):
        """
        :param name: name of dimension
        :type name: unicode
        :param value: value of dimension
        :type value: float | int
        :param unit: unit of dimension
        :type unit: unicode
        """
        assert unit in Dimension.parsable_unit, "wrong unit: %s" % unit
        self.name = name
        self.unit = unit
        self.value = value

    def __eq__(self, other):
        return self.name == other.name and self.unit == other.unit and abs(
            self.value - other.value) < allowed_float_error

    def __ne__(self, other):
        return not self.__eq__(other)

    def value_string(self):
        if type(self.value) == float:
            converted = int(self.value)
            error = self.value - converted
            if error < allowed_float_error:
                self.value = converted
            elif 1 - error < allowed_float_error:
                self.value = converted + 1

        return unicode(self.value) + self.unit

    @classmethod
    def parse(cls, name, value_string):
        """Parse size and unit from string.

        If there isn't dimension, it will return None.

        :param name: name of dimension
        :type name: unicode
        :param value_string: string to parse size and unit
        :type value_string: unicode
        :return: parsed Dimension object
        :rtype: Dimension
        """
        if value_string is None:
            value_string = ""
        value_string = value_string.strip()
        m = Dimension.parse_regex.match(value_string)
        if m:
            value = m.group(1)
            unit = m.group(2)

            if value:
                if '.' in value:
                    value = float(value)
                else:
                    value = int(value)
            else:
                value = 0

            return Dimension(name, value, unit)

        return None

    @staticmethod
    def update_original():
        """set original dimensions to current dimensions dictionary"""
        Dimension.original_dimensions = copy.deepcopy(Dimension.dimensions)

    @staticmethod
    def get_changes():
        """Generate strings of changed dimensions.

        :return: strings of changed dimensions
        :rtype: list[str]
        """
        change_strings = list()
        for name in Dimension.dimensions.keys():
            original_dimension = Dimension.original_dimensions[name]
            dimension = Dimension.dimensions[name]
            if dimension != original_dimension:
                change_strings.append(
                    " * %s : %s -> %s" % (
                        name, original_dimension.value_string(), dimension.value_string()))
        return sorted(change_strings)


class Expression(object):
    substitution_operator = "<="
    sign_begin = "{\*"
    sign_end = "\*}"
    parse_regex = re.compile(sign_begin + r"(.*)" + sign_end)
    tokenable_chars = "1234567890_abcdefghijklnmopqrstuvwxyzABCDEFGHIJKLNMOPQRSTUVWXYZ"

    expressions = list()
    dependency_graph = digraph()

    def __init__(self, expression_string):
        """
        :param expression_string: expression string
        :type expression_string: unicode
        """
        self.right_tokens = list()
        self.expression_string = expression_string
        count = expression_string.count(Expression.substitution_operator)
        assert count <= 1, "Expression string cannot have more than one substitution operator."
        if count == 1:
            (self.left, self.right) = (string.strip() for string in
                                       expression_string.split(Expression.substitution_operator))
        else:  # doesn't have substitution operator. it will be added soon.
            self.left = None
            self.right = expression_string

    def run_expression(self, force):
        """Run the expression

        :param force: ignore warning
        :type force: bool
        """
        left_dimension = Dimension.dimensions[self.left]
        runnable_string = ""
        for token in self.right_tokens:
            if type(token) == Dimension:
                if left_dimension.unit == '':
                    left_dimension.unit = token.unit
                if token.unit != left_dimension.unit:
                    print("[!] Unit mismatched: %s" % self.expression_string, file=sys.stderr)
                    if not force:
                        sys.exit(-1)
                runnable_string += unicode(token.value)
            else:
                runnable_string += unicode(token)
        left_dimension.value = eval(runnable_string)
        assert type(left_dimension.value) == int or type(left_dimension.value) == float, \
            "result of expression must be int or float: %s" % self.expression_string

    @staticmethod
    def parse(element):
        """Parse expression string from comment.

        If comment is not a etree.Comment object or don't have any expression, it will return None.

        :param element: element to get expression
        :type element: etree.Element
        :return: pared expression
        :rtype: Expression
        """
        if element.tag is not etree.Comment:
            return None
        comment = element.text

        s = Expression.parse_regex.search(comment)
        if not s:
            return None
        expr_string = s.group(1).strip()
        if Expression.sign_begin in expr_string or Expression.sign_end in expr_string:
            print("[!] Abnormal Expression: %s" % comment, file=sys.stderr)
            sys.exit(-1)
        return Expression(expr_string)

    @staticmethod
    def split_by_dimension(string):
        """Get a list of found dimension and other expression string what are contained in string.

        :param string: string to parse
        :type string: unicode
        :return: a list of token
        :rtype: list[Dimension | unicode]
        """

        founds = list()
        stack = ""
        possible_stack = ""
        flag = False
        for c in string:
            if flag:
                if c not in Expression.tokenable_chars:
                    if possible_stack in Dimension.dimensions.keys():
                        if stack:
                            founds.append(stack)
                        founds.append(Dimension.dimensions[possible_stack])
                        stack = c
                    else:
                        stack += possible_stack + c
                    flag = False
                    possible_stack = ""
                else:
                    possible_stack += c
            else:
                if c in Expression.tokenable_chars:
                    flag = True
                    possible_stack += c
                else:
                    stack += c
        if possible_stack in Dimension.dimensions.keys():
            if stack:
                founds.append(stack)
            founds.append(Dimension.dimensions[possible_stack])
        else:
            stack += possible_stack
            founds.append(stack)
        return founds

    @staticmethod
    def add_dependency_edge(expression):
        """Add expression to dependency graph as an edge.

        :param expression: expression to add
        :type expression: Expression
        """
        expression.right_tokens = Expression.split_by_dimension(expression.right)
        right_dimensions = [token for token in expression.right_tokens if type(token) == Dimension]

        for right_dimension in right_dimensions:
            Expression.dependency_graph.add_edge((expression.left, right_dimension.name))

    @staticmethod
    def add_dependency_node():
        """Add dimensions to dependency graph as nodes."""
        Expression.dependency_graph.add_nodes(Dimension.dimensions.keys())

    @staticmethod
    def check_cycle():
        cycles = find_cycle(Expression.dependency_graph)
        if cycles:
            print("[!] Exist dependency cycle: %s" % (cycles,), file=sys.stderr)
            sys.exit(-1)


def read_xml(filename):
    """Read xml file.

    :param filename: filename to read
    :type filename: unicode
    :return: parsed ElementTree
    :rtype: etree.ElementTree
    """
    dimension_xml = open(filename, 'r')
    xml_parser = etree.XMLParser(remove_comments=False)
    et = etree.fromstring(dimension_xml.read(), parser=xml_parser)
    dimension_xml.close()
    return et


def save_xml(et, filename):
    """Save ElementTree to file.

    :param et: ElementTree to save
    :type et: etree.ElementTree
    :param filename: filename to save
    :type filename: unicode
    """
    new_xml = etree.tostring(et, encoding="utf-8", pretty_print=True)
    dimension_xml = open(filename, 'w')
    dimension_xml.write(new_xml)
    dimension_xml.close()


def parse_dimensions(et):
    """Parse dimensions on ElementTree and add to dimensions them all.

    :param et: ElementTree to parse
    :type et: etree.ElementTree
    """
    for dimen_element in et.findall(".dimen"):
        name = dimen_element.attrib['name']
        value_string = dimen_element.text
        dimension = Dimension.parse(name, value_string)
        Dimension.dimensions[name] = dimension
    Dimension.update_original()


def set_dimensions(et):
    """Set dimension element value from dimensions.

    :param et: ElementTree to set
    :type et: etree.ElementTree
    """
    for dimension_element in et.findall(".dimen"):
        name = dimension_element.attrib['name']
        dimension_element.text = Dimension.dimensions[name].value_string()


def confirm(changes_string, yes):
    """Check applying changes or not.

    If it had nothings to change or user answered negative, exit.

    :param changes_string: strings of changed dimensions
    :type changes_string: list[str]
    :param yes: skip user input with this value
    :type yes: bool
    """
    if changes_string:
        print("[-] Following dimensions will be changed.\n")
        for s in changes_string:
            print(s)
        print("\n")

        if not yes:
            is_ok = raw_input("[=] Proceed? [y/N]: ")
            if is_ok not in ('Y', 'y'):
                print("[-] Canceled.", file=sys.stderr)
                sys.exit(-2)
    else:
        print("[-] Nothing to change.")
        sys.exit(0)


def calculate(et, force):
    """Calculate new dimensions

    :param et: ElementTree to set
    :type et: etree.ElementTree
    :param force: ignore warning
    :type force: bool
    """
    expression = None
    Expression.add_dependency_node()

    for element in et.iter():
        if expression is None:
            expression = Expression.parse(element)
            Expression.expressions.append(expression)
            if expression is None:
                continue
            if expression.left is not None:
                Expression.add_dependency_edge(expression)
                expression.run_expression(force)
                expression = None
        else:
            if element.tag is etree.Comment:
                continue
            if expression.left is None:
                expression.left = element.attrib['name']

            Expression.add_dependency_edge(expression)
            expression.run_expression(force)
            expression = None


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("filename", help="Filename of dimens.xml")
    parser.add_argument("-y", "--yes", help="Reply 'Y' for all interactions", action="store_true")
    parser.add_argument("-f", "--force", help="Ignore all warnings", action="store_true")
    args = parser.parse_args()

    xml = read_xml(args.filename)
    parse_dimensions(xml)
    calculate(xml, args.force)
    Expression.check_cycle()
    confirm(Dimension.get_changes(), args.yes)
    set_dimensions(xml)
    save_xml(xml, args.filename)

    print("[-] Complete.")
    sys.exit(0)
