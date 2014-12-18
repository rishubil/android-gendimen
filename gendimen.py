from lxml import etree as ET
import re
import copy
from pprint import pprint
import sys
import argparse
from pygraph.classes.digraph import digraph
from pygraph.algorithms.cycles import find_cycle


def parseUnit(string):
    for unit in ('px', 'in', 'mm', 'pt', 'dp', 'sp'):
        regex = re.compile("(^|[\s\W\.])(\d*\.?\d*)(%s)" % unit)
        s = regex.search(string)
        if s:
            result = {}
            result['size'] = s.group(2)
            result['unit'] = s.group(3)

            if '.' in result['size']:
                result['size'] = float(result['size'])
            else:
                result['size'] = int(result['size'])

            return result


def mergeUnit(unit):
    return str(unit['size']) + unit['unit']


def getXml(filename):
    dimen_xml = open(filename, 'r')

    parser = ET.XMLParser(remove_comments=False)
    e = ET.fromstring(dimen_xml.read(), parser=parser)
    dimen_xml.close()
    return e


def saveXml(e, filename):
    new_xml = ET.tostring(e, pretty_print=True)
    dimen_xml = open(filename, 'w')
    dimen_xml.write(new_xml)
    dimen_xml.close()


def parseDimens(e, dimens):
    for dimen in e.findall(".dimen"):
        size = parseUnit(dimen.text)
        dimens[dimen.attrib['name']] = size


def setDimens(e, dimens):
    for dimen in e.findall(".dimen"):
        dimen.text = dimens[dimen.attrib['name']]


def getChanges(dimens, ori_dimens):
    changes = []
    for k in dimens.keys():
        if dimens[k] != ori_dimens[k]:
            changes.append(" * %s : %s -> %s" % (k, ori_dimens[k], dimens[k]))
    return changes


def confirm(changes, yes):
    if changes:
        print("[-] Following dimens will be changed.")
        print("\n")
        for s in changes:
            print(s)
        print("\n")

        if not yes:
            isOK = raw_input("[=] Procced?[y/N]: ")
            if not isOK in ('Y', 'y'):
                sys.stderr.write("[-] Cancled.")
                sys.exit(-2)
    else:
        print("[-] Nothing to change.")
        sys.exit(0)


def getExprFromComment(element):
    if not element.tag is ET.Comment:
        return None
    comment = element.text
    regex = re.compile("{{(.*)}}")

    s = regex.search(comment)
    if not s:
        return None
    expr = s.group(1).strip()
    if "{{" in expr or "}}" in expr:
        sys.stderr.write("[!] Abnormal Expression: %s" % comment)
        sys.exit(-1)
    return expr


def addEdge(gp, expr):
    (left_expr, right_expr) = expr.split('=')
    lefts = []
    rights = []

    for dimen in dimens.keys():
        if dimen in left_expr:
            lefts.append(dimen)
        if dimen in right_expr:
            rights.append(dimen)

    for left in lefts:
        for right in rights:
            gp.add_edge((left, right))


def run(dimens):
    expr = None
    gp = digraph()
    gp.add_nodes(dimens.keys())

    for element in e.iter():
        if expr:
            if element.tag is ET.Comment:
                continue
            if not "=" in expr:
                left = element.attrib['name']
                expr = "%s = %s" % (left, expr)

            addEdge(gp, expr)
            runExpr(expr, dimens)
            expr = None
        else:
            expr = getExprFromComment(element)
            if not expr:
                continue
            if "=" in expr:
                addEdge(gp, expr)
                runExpr(expr, dimens)
                expr = None

    if '__builtins__' in dimens:
        del dimens['__builtins__']

    cycles = find_cycle(gp)
    if cycles:
        sys.stderr.write("[!] Exist dependency cycle: %s" % (cycles))
        sys.exit(-1)


def runExpr(expr, dimens):
    unit = None
    for dimen in dimens.keys():
        if dimen in expr:
            if unit and unit != dimens[dimen]['unit']:
                sys.stderr.write("[!] Unit mismatched: %s" % expr)
                sys.exit(-1)
            unit = dimens[dimen]['unit']
            expr = expr.replace(dimen, "%s['size']" % dimen)
    exec expr in dimens


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("filename", help="Filename of dimens.xml")
    parser.add_argument("-y", "--yes", help="Reply 'Y' for all interactions", action="store_true")
    args = parser.parse_args()

    e = getXml(args.filename)

    dimens = {}
    parseDimens(e, dimens)

    ori_dimens = copy.deepcopy(dimens)

    run(dimens)

    for k in dimens.keys():
        dimens[k] = mergeUnit(dimens[k])
        ori_dimens[k] = mergeUnit(ori_dimens[k])

    changes = getChanges(dimens, ori_dimens)

    confirm(changes, args.yes)

    setDimens(e, dimens)
    saveXml(e, args.filename)

    print("[-] Complete.")
    sys.exit(0)
