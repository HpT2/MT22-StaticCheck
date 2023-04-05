from Visitor import Visitor
from StaticError import *

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
		pass

	def visitUnExpr(self, ctx, o):
		pass

	def visitId(self, ctx, o):
		pass

	def visitArrayCell(self, ctx, o):
		pass

	def visitIntegerLit(self, ctx, o):
		pass

	def visitFloatLit(self, ctx, o):
		pass

	def visitStringLit(self, ctx, o):
		pass

	def visitBooleanLit(self, ctx, o):
		pass

	def visitArrayLit(self, ctx, o):
		pass

	def visitFuncCall(self, ctx, o):
		pass

	def visitAssignStmt(self, ctx, o):
		pass

	def visitBlockStmt(self, ctx, o):
		pass

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


