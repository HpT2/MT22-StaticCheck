import unittest
from TestUtils import TestChecker
from AST import *

class CheckerSuite(unittest.TestCase):

	def test1(self):
		input = Program([
	VarDecl('x', IntegerType()),
	VarDecl('x', IntegerType())
])
		expect = "Redeclared Variable: x"
		self.assertTrue(TestChecker.test(input, expect, 401))

	def test2(self):
		input = Program([
	VarDecl('x', IntegerType()),
	VarDecl('x', IntegerType()),
	VarDecl('y', IntegerType()),
	VarDecl('y', IntegerType())
])
		expect = "Redeclared Variable: x"
		self.assertTrue(TestChecker.test(input, expect, 402))

	def test3(self):
		input = Program([
	VarDecl('x', IntegerType()),
	VarDecl('y', IntegerType())
])
		expect = str(input)
		self.assertTrue(TestChecker.test(input, expect, 403))

	def test4(self):
		input = """
		var:integer;
		foo:function void(){}
		"""
		expect = """Program([
	VarDecl(var, IntegerType)
	FuncDecl(foo, VoidType, [], None, BlockStmt([]))
])"""
		self.assertTrue(TestChecker.test(input, expect, 404))
	
	def test5(self):
		input = """
		foo:function void(a:integer){}
		"""
		expect = """Program([
	FuncDecl(foo, VoidType, [Param(a, IntegerType)], None, BlockStmt([]))
])"""
		self.assertTrue(TestChecker.test(input, expect, 405))

	def test6(self):
		input = """
		foo:function void(a:integer, a:integer){}
		"""
		expect = """Redeclared Parameter: a"""
		self.assertTrue(TestChecker.test(input, expect, 406))

	def test7(self):
		input = """
		foo:function void(a:integer){}
		foo:function void(a:integer){}
		"""
		expect = """Redeclared Function: foo"""
		self.assertTrue(TestChecker.test(input, expect, 407))

	def test8(self):
		input = """
		a : string;
		foo:function void(a:integer){}
		"""
		expect = """Program([
	VarDecl(a, StringType)
	FuncDecl(foo, VoidType, [Param(a, IntegerType)], None, BlockStmt([]))
])"""
		self.assertTrue(TestChecker.test(input, expect, 408))

	def test9(self):
		input = """
		a : string;
		a:function void(a:integer){}
		"""
		expect = """Redeclared Function: a"""
		self.assertTrue(TestChecker.test(input, expect, 409))

	