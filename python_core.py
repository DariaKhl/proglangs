import sys
import copy
import time
import datetime
import xml.dom.minidom
import cpp_extension


test_str = '''<?xml version="1.0" ?>
<schematics>
<net description="GND" id="1"/>
<net id="2"/>
<net description="Vcc" id="3"/>
<diode net_from="1" net_to="3"
resistance="84.986"
reverse_resistance="19295131.171"
/>
<diode net_from="1" net_to="2"
resistance="128.445"
reverse_resistance="19629496.476"
/>
<resistor net_from="3" net_to="1"
resistance="1000.000"
/>
<capacitor net_from="3" net_to="2"
resistance="423074289.097"
/>
</schematics>'''


def matrix_from_xml(xml_file, is_string=False):
    ''' Generating NxN dependency matrix (N - num of 'net' elements in xml schema) '''

    if (is_string):
        dom = xml.dom.minidom.parseString(xml_file)
    else:
        dom = xml.dom.minidom.parse(xml_file)

    num_v = len(dom.getElementsByTagName('net'))
    matrix = [[0] * num_v for i in range(num_v)]
#    print(matrix)

    #Main loop of xml parsing. There are 3 available elements in task
    for element_name in ('diode', 'resistor', 'capacitor'):
        for element in dom.getElementsByTagName(element_name):
            element_attr = {}
            element_attr['from'] = int(element.getAttribute('net_from')) - 1  #Since in python we are starting from 0, not from 1
            element_attr['to'] = int(element.getAttribute('net_to')) - 1
            element_attr['R'] = float(element.getAttribute('resistance'))
            element_attr['R_rev'] = element_attr['R']

            # Diode have special backward resistance, not equal to forward one
            if element_name == 'diode':
                element_attr['R_rev'] = float(element.getAttribute('reverse_resistance'))

            if matrix[element_attr['from']][element_attr['to']] != 0.0:
                matrix[element_attr['from']][element_attr['to']] = 1.0 / (
                    1.0 / matrix[element_attr['from']][element_attr['to']] + 1.0 / element_attr['R'])
                matrix[element_attr['to']][element_attr['from']] = 1.0 / (
                    1.0 / matrix[element_attr['to']][element_attr['from']] + 1.0 / element_attr['R_rev'])
            else:
                matrix[element_attr['from']][element_attr['to']] = element_attr['R']
                matrix[element_attr['to']][element_attr['from']] = element_attr['R_rev']

#            print('{} info:'.format(element_name))
#            print('from {from}, to {to}, R{from}{to} = {R}, R{to}{from} = {R_rev}, '.format(**element_attr))
#            print()

#    print('Dependency matrix')
#    print(matrix)
    return matrix


def Floyd_Warshall(elem_matrix: list) -> list:
    matrix = copy.deepcopy(elem_matrix)
    n = len(matrix[0])
    for k in range(n):
        for i in range(n):
            for j in range(n):
                matrix[i][j] = min(matrix[i][j], matrix[i][k] + matrix[k][j])
            #print i,j,k,matrix
            #if (matrix[i][j] > 0.0) and (matrix[i][k] > 0) and (matrix[k][j] > 0):
            #	matrix[i][j] = 1.0/(1.0/matrix[i][j] + 1.0/(matrix[i][k] + matrix[k][j]))
    return matrix

def print_matrix(matrix, name='matrix'):
    output_file.write('{}:\n'.format(name))
    for row in matrix:
        for elem in row:
            output_file.write('{:20.6f}, '.format(elem))
        output_file.write('\n')


if __name__ == "__main__":

    elem_matrix = None
    to_file = False

    if (len(sys.argv) == 3):
        print('Using {} file as xml source, using {} as output file'.format(sys.argv[1], sys.argv[2]))
        to_file = True
        elem_matrix = matrix_from_xml(sys.argv[1], False)
    else:
        print('Using test string instead of extern file (see test_str in python_core.py), using stdout as output')
        elem_matrix = matrix_from_xml(test_str, True)

    python_start = time.process_time()
    python_result = Floyd_Warshall(elem_matrix)
    python_end = time.process_time()
    python_time = python_end - python_start
    print("Python calculations time: {:.4f} sec".format(python_time))

    cxx_fast_start = time.process_time()
    cxx_fast_result = cpp_extension.floyd_warshall_fast(elem_matrix)
    cxx_fast_end = time.process_time()
    cxx_fast_time = cxx_fast_end - cxx_fast_start
    print("Pure C++ calculations time: {:.1f} sec".format(cxx_fast_time))
    
    if (to_file):
        with open(sys.argv[2], 'a') as output_file:
            output_file.write(str(datetime.datetime.now()) + ':\n\n')
            print_matrix(elem_matrix, name='Source matrix')

            output_file.write('\n')
            print_matrix(python_result, name='Result matrix, obtained by python')
            output_file.write("Python calculations time: {:.4f} sec\n".format(python_time))

            output_file.write('\n')
            print_matrix(cxx_fast_result, name='Result matrix, obtained by pure C/C++')
            output_file.write("C++ calculations time: {:.4f} sec\n".format(python_time))

            output_file.write('\n' + '#'*100 + '\n\n')

#    cxx_start = time.process_time()
#    cxx_res = cpp_extension.floyd_warshall(elem_matrix)
#    cxx_end = time.process_time()
#    cxx_time = cxx_end - cxx_start
#    print("C++/PyObject calculations time: {:.1f} sec".format(cxx_time))
#    print(cxx_res)
