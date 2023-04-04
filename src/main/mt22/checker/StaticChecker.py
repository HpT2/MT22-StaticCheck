from Visitor import Visitor


class StaticChecker(Visitor):
    
	def visitProgram(self, ctx, o):
		o = [[]]
		for decl in ctx.decls:
			o = self.visit(decl, o)

	def visitVarDecl(self, ctx, o):
		pass

	def visitParamDecl(self, ctx, o):
		pass

	def visitFuncDecl(self, ctx, o):
		pass

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


