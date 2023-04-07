from Visitor import Visitor
from StaticError import *
from AST import *

class StaticChecker(Visitor):
    
	def visitProgram(self, ctx, o):
		o = [[]]
		for decl in ctx.decls:
			#print(decl)
			o = self.visit(decl, o)
		return ctx

	def visitVarDecl(self, ctx, o):
		for decl in o[0]:
			if decl.name == ctx.name:
				raise Redeclared(Variable(),ctx.name)
		if ctx.init is not None:
			expr_type = self.visit(ctx.init, o)
			if type(expr_type) != type(ctx.typ):
				raise TypeMismatchInStatement(ctx)
		o[0] += [ctx]
		return o

	def visitParamDecl(self, ctx, o):
		for decl in o[0]:
			if decl.name == ctx.name:
				raise Redeclared(Parameter(),ctx.name)
		o[0] += [ctx]
		return o

	def visitFuncDecl(self, ctx, o):
		for decl in o[0]:
			if decl.name == ctx.name:
				raise Redeclared(Function(),ctx.name)
		o[0] += [ctx]
		env = [[]] + o
		for param in ctx.params:
			env = self.visit(param, env)
		self.visit(ctx.body, env)
		return o

	def visitBinExpr(self, ctx, o):
		#left_type = self.visit(ctx.left, o)
		#right_type = self.visit(ctx.right, o)
		if ctx.op in ['+', '-', '*', '/', '%', '==', '!=', '>', '>=', '<', '<=']:
			pass

		if ctx.op in ['&&', '||', '!=']:
			pass

		if ctx.op == "::":
			pass

	def visitUnExpr(self, ctx, o):
		if ctx.op == '-':
			pass

		if ctx.op == '!':
			pass

	def visitId(self, ctx, o):
		for env in o:
			for var in env:
				if var.name == ctx.name:
					return var.typ
		raise Undeclared(Identifier(), ctx.name)

	def visitArrayCell(self, ctx, o):
		pass

	def visitIntegerLit(self, ctx, o):
		return IntegerType()

	def visitFloatLit(self, ctx, o):
		return FloatType()

	def visitStringLit(self, ctx, o):
		return StringType()

	def visitBooleanLit(self, ctx, o):
		return BooleanType()

	def visitArrayLit(self, ctx, o):
		pass

	def visitFuncCall(self, ctx, o):
		pass

	def visitAssignStmt(self, ctx, o):
		pass

	def visitBlockStmt(self, ctx, o):
		env = [[]] + o
		for stmt in ctx.body:
			if type(stmt) == VarDecl:
				env = self.visit(stmt, env)
			else:
				self.visit(stmt, env)

	def visitForStmt(self, ctx, o):
		pass

	def visitIfStmt(self, ctx, o):
		pass

	def visitWhileStmt(self, ctx, o):
		pass

	def visitDoWhileStmt(self, ctx, o):
		pass

	def visitBreakStmt(self, ctx, o):
		pass

	def visitContinueStmt(self, ctx, o):
		pass

	def visitReturnStmt(self, ctx, o):
		pass

	def visitCallStmt(self, ctx, o):
		pass


