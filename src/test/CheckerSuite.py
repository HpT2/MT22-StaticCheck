import unittest
from TestUtils import TestChecker
from AST import *

class CheckerSuite(unittest.TestCase):

	def test1(self):
		input = """
		main: function auto (a:integer, b: string){
			return "1";
		}"""
		expect = "No entry point"
		self.assertTrue(TestChecker.test(input, expect, 401))

	def test2(self):
		input = """
		main: function void (a:integer, b: string){
		
		}
		main: function void (a:integer, b: string){
		
		}"""
		expect = "Redeclared Function: main"
		self.assertTrue(TestChecker.test(input, expect, 402))

	def test3(self):
		input = """
		foo: function void (a:integer, b: string) inherit main{
			super();
		}
		main: function void (){
		
		}"""
		expect = ""
		self.assertTrue(TestChecker.test(input, expect, 403))

	def test4(self):
		input = """
		main: function void (a:integer, b: string) inherit hoo{
		
		}"""
		expect = "Undeclared Function: hoo"
		self.assertTrue(TestChecker.test(input, expect, 404))

	def test5(self):
		input = """
		main: function void (a:integer, b: string) inherit hoo{
		
		}
		hoo: function void (inherit a:integer){}"""
		expect = "Invalid Parameter: a"
		self.assertTrue(TestChecker.test(input, expect, 405))

	def test6(self):
		input = """
		main: function void () inherit hoo{

		}
		hoo: function void (){}"""
		expect = ""
		self.assertTrue(TestChecker.test(input, expect, 406))
	
	def test7(self):
		input = """
		main: function void () inherit hoo{
			super("1");

		}
		hoo: function void (inherit a: string){}"""
		expect = ""
		self.assertTrue(TestChecker.test(input, expect, 407))
	
	
	def test8(self):
		input = """
		main: function void (z:integer, b: string) inherit hoo{
			super("1");

		}
		hoo: function void (){}"""
		expect = "Type mismatch in expression: StringLit(1)"
		self.assertTrue(TestChecker.test(input, expect, 408))
	
	def test9(self):
		input = """
		main: function void (z:integer, b: string) inherit hoo{
			super();

		}
		hoo: function void (a: string){}"""
		expect = "Type mismatch in expression: "
		self.assertTrue(TestChecker.test(input, expect, 409))
	
	def test10(self):
		input = """
		main: function void (z:integer, b: string) inherit hoo{
			super("1");

		}
		hoo: function void (a: string, a:string){}"""
		expect = "Type mismatch in expression: "
		self.assertTrue(TestChecker.test(input, expect, 410))

	def test11(self):
		input = """
		foo: function void (z:integer, b: string){

		}
		main: function void () inherit foo{
			super(1,"1");
		}"""
		expect = ""
		self.assertTrue(TestChecker.test(input, expect, 411))
	
	def test12(self):
		input = """
		foo: function void (inherit z:integer, b: string){
		
		}
		main: function void () inherit foo{
			super(z,"1");
		}"""
		expect = ""
		self.assertTrue(TestChecker.test(input, expect, 412))
	
	def test13(self):
		input = """
		foo: function void (inherit z:integer, b: string) inherit hoo{
			super(a);
		}
		hoo: function void (inherit a: string){
		}
		main:function void () {}"""	
		expect = ""
		self.assertTrue(TestChecker.test(input, expect, 413))
	
	def test14(self):
		input = """
		main: function void () inherit hoo{
			super(a);
		}
		hoo: function void (inherit a: string){
		}"""
		expect = ""
		self.assertTrue(TestChecker.test(input, expect, 414))

	def test15(self):
		input = """
		goo: function string (inherit z:integer, b: string) inherit hoo{
			super(a);
			return	a;
		}
		hoo: function void (inherit a: string){
		}
		main:function void () {}"""
		expect = ""
		self.assertTrue(TestChecker.test(input, expect, 415))

	def test16(self):
		input = """
		main: function string (inherit z:integer, b: string) inherit hoo{
			super(a);
			return	z;
		}
		hoo: function void (inherit a: string){
		}"""
		expect = "Type mismatch in statement: ReturnStmt(Id(z))"
		self.assertTrue(TestChecker.test(input, expect, 416))
	
	def test17(self):
		input = """
		goo: function auto (inherit z:integer, b: string) inherit hoo{
			super(a);
			return	z;
		}
		hoo: function void (inherit a: string){
		}
		main: function void(){}"""
		expect = ""
		self.assertTrue(TestChecker.test(input, expect, 417))
	
	def test18(self):
		input = """
		main: function auto (inherit z:integer, b: string) inherit hoo{
			return	z;
		}
		hoo: function void (inherit a: string){
		}"""
		expect = "Invalid statement in function: main"
		self.assertTrue(TestChecker.test(input, expect, 418))
	
	def test19(self):
		input = """
		a : integer;
		foo: function auto (inherit z:integer, b: string){
			return	z;
		}
		main:function void() {}"""
		expect = ""
		self.assertTrue(TestChecker.test(input, expect, 419))
	
	def test20(self):
		input = """
		a : string;
		foo: function auto (inherit a:integer, b: string){
			return a;
		}
		main: function void(){}"""
		expect = ""
		self.assertTrue(TestChecker.test(input, expect, 420))
	
	def test21(self):
		input = """
		a : integer;
		main: function void (){
			
		}"""
		expect = ""
		self.assertTrue(TestChecker.test(input, expect, 421))
	
	def test22(self):
		input = """
		foo: function auto (inherit z:integer, b: string) inherit hoo{
			preventDefault();
			return	z;
		}
		hoo: function void (inherit a: string){
		}
		main: function void(){}"""
		expect = ""
		self.assertTrue(TestChecker.test(input, expect, 422))
	
	def test23(self):
		input = """
		main: function auto (inherit z:integer, b: string) inherit hoo{
			preventDefault();
			a : integer;
			return	z;
		}
		hoo: function void (inherit a: string){
		}"""
		expect = "No entry point"
		self.assertTrue(TestChecker.test(input, expect, 423))
	
	def test24(self):
		input = """a:integer = 10;
			main:function void (a:integer){}
		"""
		expect = "No entry point"
		self.assertTrue(TestChecker.test(input, expect, 424))
	
	def test25(self):
		input = """a:integer = "1";
			main:function void (){}
		"""
		expect = "Type mismatch in Variable Declaration: VarDecl(a, IntegerType, StringLit(1))"
		self.assertTrue(TestChecker.test(input, expect, 425))

	def test26(self):
		input = """a:integer ;
			main:function void (){
				for(a = 1, a<1, a + 1){
					break;
				}
			}
		"""
		expect = ""
		self.assertTrue(TestChecker.test(input, expect, 426))
	
	def test27(self):
		input = """a:integer ;
			main:function void (){
				break;
			}
		"""
		expect = "Must in loop: BreakStmt()"
		self.assertTrue(TestChecker.test(input, expect, 427))

	def test28(self):
		input = """a:integer ;
			main:function void (){
				for(a = 1, a<1, a + 1){
					{
						break;
					}
				}
			}
		"""
		expect = ""
		self.assertTrue(TestChecker.test(input, expect, 428))

	def test29(self):
		input = """a:integer ;
			main:function void (){
				for(a = 1, a<1, a + 1){
					for(a = 1, a > 2, a - 2){
						break;
					}
					continue;
				}
			}
		"""
		expect = ""
		self.assertTrue(TestChecker.test(input, expect, 429))

	def test30(self):
		input = """a:integer ;
			main:function auto (){
				for(a = 1, a<1, a + 1){
					for(a = 1, a > 2, a - 2){
						return 2;
					}
					continue;
				}
			}
		"""
		expect = "No entry point"
		self.assertTrue(TestChecker.test(input, expect, 430))
	
	def test31(self):
		input = """a:integer ;
			main:function string (){
				for(a = 1, a<1, a + 1){
					for(a = 1, a > 2, a - 2){
						return 2;
					}
					continue;
				}
			}
		"""
		expect = "Type mismatch in statement: ReturnStmt(IntegerLit(2))"
		self.assertTrue(TestChecker.test(input, expect, 431))
	
	def test32(self):
		input = """a:string ;
			foo: function void () inherit goo {
				super(a);
			}

			goo:function string (inherit x: auto){
				
			}
			main:function void(){}
		"""
		expect = ""
		self.assertTrue(TestChecker.test(input, expect, 432))

	
	def test33(self):
		input = """a:integer = 1 + 2;
		main:function void (){}
		"""
		expect = ""
		self.assertTrue(TestChecker.test(input, expect, 433))
	
	def test34(self):
		input = """a:float = 1 + 2;
		main:function void (){}
		"""
		expect = ""
		self.assertTrue(TestChecker.test(input, expect, 434))

	def test35(self):
		input = """a:string = 1 + 2;
		main:function void (){}
		"""
		expect = "Type mismatch in Variable Declaration: VarDecl(a, StringType, BinExpr(+, IntegerLit(1), IntegerLit(2)))"
		self.assertTrue(TestChecker.test(input, expect, 435))
	
	def test36(self):
		input = """a:string = "1"::"2";
		main:function void (){}
		"""
		expect = ""
		self.assertTrue(TestChecker.test(input, expect, 436))

	def test37(self):
		input = """a:float = -1.2;
		main:function void (){}
		"""
		expect = ""
		self.assertTrue(TestChecker.test(input, expect, 437))

	def test38(self):
		input = """a:boolean = !(true || false);
		main:function void (){}
		"""
		expect = ""
		self.assertTrue(TestChecker.test(input, expect, 438))

	def test39(self):
		input = """a:boolean = foo();
		main:function void (){}
		"""
		expect = "Undeclared Function: foo"
		self.assertTrue(TestChecker.test(input, expect, 439))

	def test40(self):
		input = """a:boolean = foo();
		foo:function boolean (){}
		main:function void(){}
		"""
		expect = ""
		self.assertTrue(TestChecker.test(input, expect, 440))

	def test41(self):
		input = """a:boolean = foo(foo(false));
		foo:function boolean (a: boolean){}
		main:function void(){}
		"""
		expect = ""
		self.assertTrue(TestChecker.test(input, expect, 441))

	def test42(self):
		input = """a:boolean = foo(foo(false));
		main: function void(){}
		foo:function auto (a: boolean){}
		"""
		expect = ""
		self.assertTrue(TestChecker.test(input, expect, 442))

	def test43(self):
		input = """a:integer = 1 + foo(foo(false));
		foo:function auto (a: boolean){}
		main:function void(){}
		"""
		expect = ""
		self.assertTrue(TestChecker.test(input, expect, 443))

	def test44(self):
		input = """a:integer = 1 + main(main(false));
		b: string = main(main(false));
		main:function auto (a: boolean){}
		"""
		expect = "Type mismatch in Variable Declaration: VarDecl(b, StringType, FuncCall(main, [FuncCall(main, [BooleanLit(False)])]))"
		self.assertTrue(TestChecker.test(input, expect, 444))

	def test45(self):
		input = """a:integer = main(1);
		main:function auto (a: boolean){}
		"""
		expect = "Type mismatch in expression: FuncCall(main, [IntegerLit(1)])"
		self.assertTrue(TestChecker.test(input, expect, 445))
	
	def test46(self):
		input = Program([VarDecl("a", IntegerType(), IntegerLit(5)), VarDecl("c", AutoType())])
		expect = "Invalid Variable: c"
		self.assertTrue(TestChecker.test(input, expect, 446))

	def test47(self):
		input = """a:integer = foo(true);
		foo:function auto (z: boolean){
			for (a=1,a<5.0, a + 2){
				break;
				return a;
			}
		}
		main:function void(){}
		"""
		expect = ""
		self.assertTrue(TestChecker.test(input, expect, 447))

	def test48(self):
		input = """
		foo:function integer (z: auto){
			z = 1;
		}
		main:function void (){
			a: integer = foo("1");
			b:integer = foo(2);
		}
		"""
		expect = "Type mismatch in expression: FuncCall(foo, [IntegerLit(2)])"
		self.assertTrue(TestChecker.test(input, expect, 448))

	def test49(self):
		input = """
		foo:function integer (z: auto){
			z = 1;
			z = "1";
		}
		main:function void (){
			a: integer = foo("1");
			b:integer = foo(2);
		}
		"""
		expect = "Type mismatch in statement: AssignStmt(Id(z), StringLit(1))"
		self.assertTrue(TestChecker.test(input, expect, 449))

	def test50(self):
		input = """
		main:function void () inherit foo {
			super(1);
		}
		foo:function auto (inherit z : auto){
			 z= "5";
		}
		"""
		expect = "Type mismatch in statement: AssignStmt(Id(z), StringLit(5))"
		self.assertTrue(TestChecker.test(input, expect, 450))
	
	def test51(self):
		input = """
		main:function void () {
			while(true){}
		}

		"""
		expect = ""
		self.assertTrue(TestChecker.test(input, expect, 451))

	def test52(self):
		input = """
		main:function void () {
			while(foo()){}
		}
		foo: function auto(){
			return 1;
		}
		"""
		expect = "Type mismatch in statement: ReturnStmt(IntegerLit(1))"
		self.assertTrue(TestChecker.test(input, expect, 452))

	def test53(self):
		input = """
		main:function void () {
			while(foo(1)){}
		}
		foo: function auto(a: auto){
			a = true;
			return 1;
		}
		"""
		expect = "Type mismatch in statement: AssignStmt(Id(a), BooleanLit(True))"
		self.assertTrue(TestChecker.test(input, expect, 453))

	def test54(self):
		input = """
		main:function void () {
			if(true){
				a:integer;
			}
		}
		"""
		expect = ""
		self.assertTrue(TestChecker.test(input, expect, 454))

	def test55(self):
		input = """
		main:function void () {
			if(true){
				a:integer;
			}else{
				a:integer;
			}
		}
		"""
		expect = ""
		self.assertTrue(TestChecker.test(input, expect, 455))

	
	def test56(self):
		input = """
		main:function void () {
			if(foo()){
				a:integer;
			}
		}
		foo: function auto (){
			return "1";
		}
		"""
		expect = "Type mismatch in statement: ReturnStmt(StringLit(1))"
		self.assertTrue(TestChecker.test(input, expect, 456))

	def test57(self):
		input = """
		main:function void () {
			do {
				a:integer = 1;
			}while(false || true);
		}
		"""
		expect = ""
		self.assertTrue(TestChecker.test(input, expect, 457))

	def test58(self):
		input = """
		main:function void () inherit foo{
			super(1);
			a = 1;
			a = true;
		}
		foo: function void (inherit a: auto){
		
		}
		"""
		expect = "Type mismatch in statement: AssignStmt(Id(a), BooleanLit(True))"
		self.assertTrue(TestChecker.test(input, expect, 458))
	
	def test59(self):
		input = """
		main:function void () inherit foo{
			super(1);
			a = 1;
			b : integer;
			b = foo(1);
		}
		foo: function auto (inherit a: auto){
			return false;
		}
		"""
		expect = "Type mismatch in statement: ReturnStmt(BooleanLit(False))"
		self.assertTrue(TestChecker.test(input, expect, 459))

	def test60(self):
		input = """
		main:function void () inherit foo{
			preventDefault();
			a = 1;
		}
		foo: function auto (inherit a: auto){
			a = true;
		}
		"""
		expect = "Undeclared Identifier: a"
		self.assertTrue(TestChecker.test(input, expect, 460))

	def test61(self):
		input = """
		main:function void () {
			
		}
		goo:function string (a:string){}
		foo: function auto ( a: auto){
			goo(a);
			a = 1;

		}
		"""
		expect = "Type mismatch in statement: AssignStmt(Id(a), IntegerLit(1))"
		self.assertTrue(TestChecker.test(input, expect, 461))

	def test62(self):
		input = """
		main:function void () {
			goo(foo());
			a : integer = foo();
		}
		goo:function string (a:string){}
		foo: function auto (){}
		"""
		expect = "Type mismatch in Variable Declaration: VarDecl(a, IntegerType, FuncCall(foo, []))"
		self.assertTrue(TestChecker.test(input, expect, 462))

	def test63(self):
		input = """
		test: function string (y : auto){
			 y = 2;
			 return "1";
		}
		main:function void (){
			test(true);
		}
		"""
		expect = ""
		self.assertTrue(TestChecker.test(input, expect, 463))