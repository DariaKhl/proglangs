#include <iostream>
#include <vector>

extern "C" {
#include <Python.h>
}

static PyObject * floyd_warshall(PyObject* module, PyObject* args)
{
	PyObject* matrix_tuple = PyTuple_GetItem(args, 0);
	int dimension = PyObject_Length(matrix_tuple);

	PyObject* matrix = PyList_New(0);

	for (int i = 0; i < dimension; i++) {
		PyList_Append(matrix, PySequence_GetItem(matrix_tuple, i));
	}

	for (int i = 0; i < dimension; i++) {
		for (int j = 0; j < dimension; j++) {
			for (int k = 0; k < dimension; k++) {
				PyObject* matrix_i =  PySequence_GetItem(matrix, i);
				PyObject* matrix_k =  PySequence_GetItem(matrix, k);

				PyObject* matrix_i_j = PySequence_GetItem(matrix_i, j);
				PyObject* matrix_i_k = PySequence_GetItem(matrix_i, k);
				PyObject* matrix_k_j = PySequence_GetItem(matrix_k, j);

				PyObject* i_k_plus_k_j = PyNumber_Add(matrix_i_k, matrix_k_j);

				const double elem1 = PyFloat_AsDouble(matrix_i_j);
				const double elem2 = PyFloat_AsDouble(i_k_plus_k_j);
				std::cout << elem1 << " " << elem2 << ": ";
				if (elem2 < elem1)
					matrix_i_j = i_k_plus_k_j;
				std::cout << PyFloat_AsDouble(matrix_i_j) << std::endl;
			}
		}
	}

	return matrix;
}

namespace matrixops {
	typedef std::vector<double>  row_t;
	typedef std::vector<row_t>   matrix_t;

	static matrix_t floyd_warshall_fast(const matrix_t &a)
	{
		matrix_t result;
		size_t matrix_size = a.size();
		result.resize(matrix_size);
		for (size_t i = 0; i < matrix_size; i++) {
			result[i].resize(matrix_size);
			for (size_t j = 0; j < matrix_size; j++) {
				result[i][j] = a[i][j];
/*				double res_elem = 0.0;
				for (size_t r=0; r<b.size(); ++r) {
					const double a_elem = a[i][r];
					const double b_elem = b[r][j];
					res_elem += a_elem * b_elem;
				}
				result[i][j] = res_elem;
*/
			}
		}

		for (size_t i = 0; i < matrix_size; i++) {
			for	(size_t j = 0; j < matrix_size; j++) {
				for	(size_t k = 0; k < matrix_size; k++) {
					result[i][j] = std::min(result[i][j], result[i][k] + result[k][j]);
				}
			}
		}

		return result;
	}
}

static matrixops::matrix_t pyobject_to_cxx(PyObject * py_matrix)
{
	matrixops::matrix_t result;
	result.resize(PyObject_Length(py_matrix));
	for (size_t i=0; i<result.size(); ++i) {
		PyObject * py_row = PyList_GetItem(py_matrix, i);
		matrixops::row_t & row = result[i];
		row.resize(PyObject_Length(py_row));
		for (size_t j=0; j<row.size(); ++j) {
			PyObject * py_elem = PyList_GetItem(py_row, j);
			const double elem = PyFloat_AsDouble(py_elem);
			row[j] = elem;
		}
	}
	return result;
}

static PyObject * cxx_to_pyobject(const matrixops::matrix_t &matrix)
{
	PyObject * result = PyList_New(matrix.size());
	for (size_t i=0; i<matrix.size(); ++i) {
		const matrixops::row_t & row = matrix[i];
		PyObject * py_row = PyList_New(row.size());
		PyList_SetItem(result, i, py_row);
		for (size_t j=0; j<row.size(); ++j) {
			const double elem = row[j];
			PyObject * py_elem = PyFloat_FromDouble(elem);
			PyList_SetItem(py_row, j, py_elem);
		}
	}
	return result;
}

static PyObject * floyd_warshall_fast(PyObject * module, PyObject * args)
{
	PyObject * source_py_matrix = PyTuple_GetItem(args, 0);

	/* Convert to C++ structure */
	const matrixops::matrix_t source_cpp_matrix = pyobject_to_cxx(source_py_matrix);

	/* Perform calculations */
	const matrixops::matrix_t result = matrixops::floyd_warshall_fast(source_cpp_matrix);

	/* Convert back to Python object */
	PyObject * py_result = cxx_to_pyobject(result);
	return py_result;
}

PyMODINIT_FUNC PyInit_cpp_extension()
{
	static PyMethodDef ModuleMethods[] = {
		{ "floyd_warshall", floyd_warshall, METH_VARARGS, "Floyd-Warshall algo for circuit effective resistance calculation" },
		{ "floyd_warshall_fast", floyd_warshall_fast, METH_VARARGS, "Faster Floyd-Warshall matrix calculation" },
		{ NULL, NULL, 0, NULL }
	};
	static PyModuleDef ModuleDef = {
		PyModuleDef_HEAD_INIT,
		"cpp_extension",
		"Circuit element-to-element resistance calculation",
		-1, ModuleMethods,
		NULL, NULL, NULL, NULL
	};
	PyObject * module = PyModule_Create(&ModuleDef);
	return module;
}
