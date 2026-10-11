// Lossless coefficient reader for the existing expanded binary format.
#define PY_SSIZE_T_CLEAN
#include <Python.h>
#include <cstdint>
#include <stdexcept>
#include <memory>
struct Drop{void operator()(PyObject*p)const{Py_XDECREF(p);}};
typedef std::unique_ptr<PyObject,Drop> Obj;
struct R{
 const unsigned char*p;size_t n,k;
 R(const char*d,size_t s):p((const unsigned char*)d),n(s),k(0){}
 uint32_t u(){if(n-k<4)throw std::runtime_error("short record");uint32_t v=0;for(int j=0;j<4;j++)v|=uint32_t(p[k++])<<(8*j);return v;}
 PyObject* big(){
  if(k==n)throw std::runtime_error("short integer");
  unsigned sign=p[k++];uint32_t len=u();if(sign>1||len>1048576||n-k<len)throw std::runtime_error("invalid integer");
  PyObject*x=_PyLong_FromByteArray(p+k,len,1,0);k+=len;
  if(!x)throw std::runtime_error("integer allocation");
  if(sign){PyObject*y=PyNumber_Negative(x);Py_DECREF(x);if(!y)throw std::runtime_error("integer sign");x=y;}
  return x;
 }
};
static PyObject* expanded(PyObject*,PyObject*args){
 const char*data;Py_ssize_t length;PyObject*keys;
 if(!PyArg_ParseTuple(args,"y#O",&data,&length,&keys))return NULL;
 try{
  if(length<0||length>67108864||!PyList_Check(keys)||PyList_Size(keys)>512)throw std::runtime_error("record limit");
  size_t total=0;
  for(Py_ssize_t i=0;i<PyList_Size(keys);i++){PyObject*row=PyList_GetItem(keys,i);if(!PyList_Check(row)||PyList_Size(row)>4)throw std::runtime_error("master keys");total+=PyList_Size(row);}
  R r(data,length);uint32_t loops=r.u();if(loops<1||loops>32)throw std::runtime_error("loop count");
  Obj result(PyDict_New());if(!result)throw std::bad_alloc();
  for(uint32_t l=0;l<loops;l++){
   Obj L(r.big());Obj label(PyObject_Str(L.get()));uint32_t count=r.u();if(count!=total||count>2048)throw std::runtime_error("coefficient count");
   Obj flat(PyList_New(count));if(!flat)throw std::bad_alloc();
   for(uint32_t j=0;j<count;j++){
    uint32_t degree=r.u();if(degree>14)throw std::runtime_error("degree");
    Obj poly(PyList_New(degree));if(!poly)throw std::bad_alloc();
    for(uint32_t k=0;k<degree;k++){
     Obj num(r.big()),den(r.big()),pair(PyList_New(2));if(!pair)throw std::bad_alloc();
     if(Py_SIZE((PyLongObject*)den.get())<=0)throw std::runtime_error("denominator");
     PyList_SET_ITEM(pair.get(),0,num.release());PyList_SET_ITEM(pair.get(),1,den.release());PyList_SET_ITEM(poly.get(),k,pair.release());
    }
    PyList_SET_ITEM(flat.get(),j,poly.release());
   }
   Obj rows(PyList_New(PyList_Size(keys)));if(!rows)throw std::bad_alloc();size_t pos=0;
   for(Py_ssize_t j=0;j<PyList_Size(keys);j++){
    PyObject*kk=PyList_GetItem(keys,j);Obj row(PyDict_New());if(!row)throw std::bad_alloc();
    for(Py_ssize_t k=0;k<PyList_Size(kk);k++){
     Obj key(PyObject_Str(PyList_GetItem(kk,k)));if(!key||PyDict_SetItem(row.get(),key.get(),PyList_GetItem(flat.get(),pos++))<0)throw std::bad_alloc();
    }
    PyList_SET_ITEM(rows.get(),j,row.release());
   }
   if(!label||PyDict_SetItem(result.get(),label.get(),rows.get())<0)throw std::bad_alloc();
  }
  if(r.k!=r.n)throw std::runtime_error("trailing record");
  return result.release();
 }catch(const std::exception&e){if(!PyErr_Occurred())PyErr_SetString(PyExc_ValueError,e.what());return NULL;}
 catch(...){PyErr_SetString(PyExc_RuntimeError,"binary reader failure");return NULL;}
}
static PyMethodDef methods[]={{"expanded",expanded,METH_VARARGS,"Read exact expanded integer coefficients."},{NULL,NULL,0,NULL}};
static PyModuleDef module={PyModuleDef_HEAD_INIT,"_exact_reader",NULL,-1,methods};
PyMODINIT_FUNC PyInit__exact_reader(void){return PyModule_Create(&module);}
