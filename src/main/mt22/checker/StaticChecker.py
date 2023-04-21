from Visitor import Visitor
from StaticError import *
from AST import *

class ParamProto:
	def __init__(self, name, typ, inherit) -> None:
		self.name = name
		self.inherit = inherit
		self.typ = typ 

class BuiltIn:
	def __init__(self, name) -> None:
		self.name = name


class Prototype:
	def __init__(self, name, return_type, params = None, parent = None) -> None:
		self.name = name
		self.return_type = return_type
		self.params = params
		self.parent = parent

class StaticChecker(Visitor):
    
	def __init__(self, ast):
		self.ast = ast
 
	def check(self):
		return self.visitProgram(self.ast, [])

	def visitProgram(self, ctx, o):
		o = [[],[],[]]
		entry = False
		for decl in ctx.decls:
			if type(decl) == FuncDecl :
				o[1].append(Prototype(decl.name, decl.return_type, [ParamProto(param.name, param.typ, param.inherit) for param in decl.params], decl.inherit))
				if decl.name == 'main' and len(decl.params)==0 and type(decl.return_type) == VoidType:
					entry = True

		built_in = [Prototype('preventDefault', VoidType(), [], None), Prototype('printString', VoidType(), [ParamProto('anArg',StringType(),None)], None),\
	      Prototype('readString',StringType(),[], None), Prototype('printBoolean',VoidType(),[ParamProto('anArg',BooleanType(),None)],None),\
			Prototype('readBoolean',BooleanType(),[], None), Prototype('writeFloat',VoidType(),[ParamProto('anArg',FloatType(),None)],None),\
				Prototype('readFloat', FloatType(),[],None), Prototype('printInteger', VoidType(),[ParamProto('anArg', IntegerType(),None)],None),\
					Prototype('readInteger',IntegerType(),[],None)]
		o[1] += built_in
		o[0] += [BuiltIn('preventDefault'), BuiltIn('printString'), BuiltIn('readString'), BuiltIn('printBoolean'),\
	   				BuiltIn('readBoolean'), BuiltIn('writeFloat'), BuiltIn('readFloat'), BuiltIn('writeInteger'), BuiltIn('readInteger')]
		for decl in ctx.decls:
			o = self.visit(decl, o)

		if not entry:
			raise NoEntryPoint()

		
	def visitVarDecl(self, ctx, o):
		
		for decl in o[0]:
			if decl.name == ctx.name:
				raise Redeclared(Variable(), ctx.name)
		
		if type(ctx.typ) == AutoType and ctx.init == None:
			raise Invalid(Variable(), ctx.name)

		if ctx.init:
			init_type, o = self.visit(ctx.init, o)

			if type(init_type) == Prototype:
				for prototype in o[-2]:
					if prototype.name == init_type.name:
						prototype.return_type = ctx.typ
						init_type = ctx.typ
						break

			if type(ctx.typ) == AutoType:
				ctx.typ = init_type
			
			if type(ctx.typ) == FloatType and type(init_type) == IntegerType:
				init_type = FloatType()


			if type(ctx.typ) != type(init_type):
				raise TypeMismatchInVarDecl(ctx)
		
		o[0] += [ctx]
		return o

	def visitParamDecl(self, ctx, o):

		for decl in o[0]:
			if ctx.name == decl.name:
				raise Redeclared(Parameter(), ctx.name)

		if ctx.inherit:
			ctx.inherit = False

		o[0] += [ctx]
		
		return o

	def visitFuncDecl(self, ctx, o):
		for decl in o[0]:
			if ctx.name == decl.name:
				raise Redeclared(Function(),ctx.name)
		
		env = [[]] + o

		for prototype in o[-2]:
			if prototype.name == ctx.name:
				cur_proto = prototype

		if ctx.inherit and (len(ctx.body.body) == 0 or type(ctx.body.body[0]) != CallStmt or ctx.body.body[0].name != 'preventDefault'):
			parent = None
			for proto in o[-2]:
				if proto.name == ctx.inherit:
					parent = proto
					break
			
			if parent == None:
				raise Undeclared(Function(), ctx.inherit)
			
			for param in parent.params:
				if param.inherit:
					env[0] += [ParamDecl(param.name, param.typ, False, param.inherit)]

			i= 0
			for cur_param in ctx.params:
				for param in env[0]:
					if cur_param.name == param.name and param.inherit:
						raise Invalid(Parameter(), cur_param.name)
					if type(param.typ) == AutoType:
						param.typ = cur_proto.params[i]
				env = self.visit(cur_param, env)
				i += 1
			
			index = 0
			if len(ctx.body.body) == 0 or type(ctx.body.body[0]) != CallStmt or ctx.body.body[0].name != 'super': 
				if len(parent.params) != 0:
					raise InvalidStatementInFunction(ctx.name)
				index = 0
			else:
				index = 1
				superCall = ctx.body.body[0]

				if len(superCall.args) > len(parent.params):
					raise TypeMismatchInExpression(superCall.args[len(parent.params)])
				
				if len(superCall.args) < len(parent.params):
					raise TypeMismatchInExpression(None)
				
				for i in range(len(superCall.args)):
					superCall_param_type, o = self.visit(superCall.args[i], env)
				
					if type(superCall_param_type) == Prototype:
						for prototype in o[-2]:
							if prototype.name == superCall_param_type.name:
								prototype.return_type = parent.params[i].typ
								superCall_param_type = parent.params[i].typ
								break
					
					if superCall_param_type == AutoType:
						ctx.params[i].typ = parent.params[i].typ
						superCall_param_type = parent.params[i].typ
					
					if type(parent.params[i].typ) == AutoType:
						parent.params[i].typ = superCall_param_type



					if superCall_param_type != parent.params[i].typ:
						raise TypeMismatchInExpression(superCall.args[i])
				
			env[-1] += [parent.name, ctx.name]
				
			while index < len(ctx.body.body):
				env = self.visit(ctx.body.body[index], env)
				index += 1
					
					
			
		else: 
			i = 0
			for param in ctx.params:
				if type(param.typ) == AutoType:
						param.typ = cur_proto.params[i].typ

				env = self.visit(param, env)
				i += 1

			env[-1] += [ctx.name]

			env = self.visit(ctx.body, env)
			

		o[-2] = env[-2]
		o[0] += [ctx]
		return o
			

	def visitBinExpr(self, ctx, o):
		left_type, o = self.visit(ctx.left, o)
		right_type, o = self.visit(ctx.right, o)

		if type(left_type) == Prototype:
				for prototype in o[-2]:
					if prototype.name == left_type.name:
							prototype.return_type = right_type
							left_type = right_type
							break
		
		if type(right_type) == Prototype:
				for prototype in o[-2]:
					if prototype.name == right_type.name:
							prototype.return_type = leftt_type
							right_type = left_type
							break
					

		if ctx.op in ['+', '-','*','/']:
			if type(left_type) != FloatType and type(left_type) != IntegerType and type(right_type) != FloatType and type(right_type) != IntegerType:
				raise TypeMismatchInExpression(ctx)
			
			if type(left_type) == FloatType or type(right_type) == FloatType:
				return (FloatType(), o)
			
			return (IntegerType(), o)
		
		if ctx.op == '%':
			if type(left_type) != IntegerType and type(right_type) != IntegerType:
				raise TypeMismatchInExpression(ctx)
			return (IntegerType(), o)
		
		if ctx.op in ['&&', '||']:
			if type(left_type) != BooleanType and type(right_type) != BooleanType():
				raise TypeMismatchInExpression(ctx)
			return (BooleanType(), o)
		
		if ctx.op in ['==', '!=']:
			if type(left_type) != type(right_type):
				raise TypeMismatchInExpression(ctx)
			if type(left_type) != BooleanType or type(left_type) != IntegerType:
				raise TypeMismatchInExpression(ctx)
			return (BooleanType(), o)
		
		if ctx.op in ['>','<','>=','<=']:
			if type(left_type) != FloatType and type(left_type) != IntegerType and type(right_type) != FloatType and type(right_type) != IntegerType:
				raise TypeMismatchInExpression(ctx)
			return (BooleanType(), o)
		
		#op: ::
		if type(left_type) != StringType or type(right_type) != StringType:
			raise TypeMismatchInExpression(ctx)
		
		return (StringType(), o)



	def visitUnExpr(self, ctx, o):
		operand_type, o = self.visit(ctx.val, o)
		if ctx.op == '!':
			if type(operand_type) == Prototype:
				for prototype in o[-2]:
					if prototype.name == operand_type.name:
							prototype.return_type = BooleanType()
							operand_type = BooleanType()
							break

			if type(operand_type) != BooleanType:
				raise TypeMismatchInExpression(ctx)
			return (BooleanType(), o)
		
		#op: -
		if type(operand_type) != IntegerType and type(operand_type) != FloatType:
			raise TypeMismatchInExpression(ctx)
		
		return (operand_type, o)
	
	def visitId(self, ctx, o):
		for env in o:
			for decl in env:
				if (type(decl) == VarDecl or type(decl) == ParamDecl) and decl.name == ctx.name:
					return (decl.typ, o)
					
		raise Undeclared(Identifier(), ctx.name)

	def visitArrayCell(self, ctx, o):
		pass

	def visitIntegerLit(self, ctx, o):
		return (IntegerType(), o)

	def visitFloatLit(self, ctx, o):
		return (FloatType(), o)

	def visitStringLit(self, ctx, o):
		return (StringType(), o)

	def visitBooleanLit(self, ctx, o):
		return (BooleanType(), o)

	def visitArrayLit(self, ctx, o):
		dimensions = []
		for expr in ctx.expr:
			ret_demension, o = self.visit(expr, o)
		return o
		

	def visitFuncCall(self, ctx, o):
		proto = None
		for prototype in o[-2]:
			if ctx.name == prototype.name:
				proto = prototype
				break
		if not proto:
			raise Undeclared(Function(), ctx.name)
		
		if type(proto.return_type) == VoidType:
			raise TypeMismatchInExpression(ctx)

		if len(ctx.args)  != len(proto.params):
			raise TypeMismatchInExpression(ctx)
		
		for i in range(len(ctx.args)):
			arg_type, o = self.visit(ctx.args[i],o)

			if type(proto.params[i].typ) == AutoType:
				proto.params[i].typ = arg_type

			if type(arg_type) == Prototype:
				for prototype in o[-2]:
					if prototype.name == arg_type.name:
						prototype.return_type = proto.params[i].typ
						arg_type = proto.params[i].typ
						break

			if type(proto.params[i].typ) != type(arg_type):
				raise TypeMismatchInExpression(ctx)
		
		

		return (proto.return_type, o) if type(proto.return_type) != AutoType else (proto, o)


	def visitAssignStmt(self, ctx, o):
		left_type, o = self.visit(ctx.lhs, o)
		right_type, o = self.visit(ctx.rhs, o)

		if type(right_type) == Prototype:
				for prototype in o[-2]:
					if prototype.name == right_type.name:
						prototype.return_type = left_type
						right_type = left_type
						break


		if type(left_type) == AutoType:
			for decl in o[0]:
				if decl.name == ctx.lhs.name:
					decl.typ = right_type
					left_type = right_type
					break

		if type(left_type) != type(right_type) or type(left_type) == ArrayType:
			raise TypeMismatchInStatement(ctx)
		
		return o

	def visitBlockStmt(self, ctx, o):
		for stmt in ctx.body:

			if type(stmt) == BlockStmt:
				env = [[]] + o
				env = self.visit(stmt, env)
			else:
				o = self.visit(stmt, o)
		
		return o

	def visitForStmt(self, ctx, o):
		scalar_var_type,o = self.visit(ctx.init.lhs, o)

		if type(scalar_var_type) != IntegerType:
			raise TypeMismatchInStatement(ctx)
		
		cond_type,o = self.visit(ctx.cond, o)

		if type(cond_type) == Prototype:
			for prototype in o[-2]:
					if prototype.name == cond_type.name:
						prototype.return_type = BooleanType()
						cond_type = BooleanType()
		
		
		if type(cond_type) != BooleanType:
			raise TypeMismatchInStatement(ctx)
		
		upd_type,o = self.visit(ctx.upd, o)
		if type(upd_type) != IntegerType:
			raise TypeMismatchInStatement(ctx)
		env = [[]] + o
		env[-1] = [1] + env[-1]
		o = self.visit(ctx.stmt, env)
		return o
		
		

	def visitIfStmt(self, ctx, o):
		cond_type,o = self.visit(ctx.cond, o)

		
		if type(cond_type) == Prototype:
			for prototype in o[-2]:
					if prototype.name == cond_type.name:
						prototype.return_type = BooleanType()
						cond_type = BooleanType()
						break
		
		if type(cond_type) != BooleanType:
			raise TypeMismatchInStatement(ctx)
		
		env1 = [[]] + o
		env1 = self.visit(ctx.tstmt, env1)
		if ctx.fstmt:
			env2 = [[]] + o
			env2 = self.visit(ctx.fstmt, env2)
		
		return o

	def visitWhileStmt(self, ctx, o):
		cond_type,o = self.visit(ctx.cond, o)

		if type(cond_type) == Prototype:
			for prototype in o[-2]:
					if prototype.name == cond_type.name:
						prototype.return_type = BooleanType()
						cond_type = BooleanType()
						break
		
		if type(cond_type) != BooleanType:
			raise TypeMismatchInStatement(ctx)
		env = [[]] + o
		env = self.visit(ctx.stmt, env)
		return o

	def visitDoWhileStmt(self, ctx, o):
		cond_type,o = self.visit(ctx.cond, o)

		
		if type(cond_type) == Prototype:
			for prototype in o[-2]:
					if prototype.name == cond_type.name:
						prototype.return_type = BooleanType()
						cond_type = BooleanType()
		
		if type(cond_type) != BooleanType:
			raise TypeMismatchInStatement(ctx)
		
		env = [[]] + o
		env = self.visit(ctx.stmt, env)

		return o

	def visitBreakStmt(self, ctx, o):
		if type(o[-1][0]) != type(1):
			raise MustInLoop(ctx)
		return o

	def visitContinueStmt(self, ctx, o):
		if type(o[-1][0]) != type(1):
			raise MustInLoop(ctx)
		return o

	def visitReturnStmt(self, ctx, o):
		expr_type,o = self.visit(ctx.expr, o)

		for proto in o[-2]:
			if proto.name == o[-1][-1]:
				prototype = proto
				break

		if type(proto.return_type) == AutoType:
			proto.return_type = expr_type
		

		if type(expr_type) != type(proto.return_type):
			raise TypeMismatchInStatement(ctx)
		
		return o

	def visitCallStmt(self, ctx, o):
		exist = False
		for proto in o[-2]:
			if proto.name == ctx.name:
				exist = True
				prototype = proto
				break
		
		if not exist:
			raise Undeclared(Function(), ctx.name)
		
		if len(ctx.args) != len(prototype.params):
			raise TypeMismatchInStatement(ctx)
		
		for i in range(len(ctx.args)):
			arg_type, o = self.visit(ctx.args[i], o)

			if type(prototype.params[i].typ) == AutoType:
				prototype.params[i].typ = arg_type

			if type(arg_type) == AutoType:
				for decl in o[0]:
					if decl. name == ctx.args[i].name:
						decl.typ = prototype.params[i].typ
						arg_type = prototype.params[i].typ
						break
				

			if type(arg_type) == Prototype:
				for proto in o[-2]:	
					if proto.name == arg_type.name:
						proto.return_type = prototype.params[i].typ
						arg_type = prototype.params[i].typ
						break


			if type(arg_type) != type(prototype.params[i].typ):
				raise TypeMismatchInStatement(ctx)
			
		return o


