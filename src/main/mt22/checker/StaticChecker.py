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
		self.returned = False

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

		built_in = [Prototype('super', VoidType(), [], None),Prototype('preventDefault', VoidType(), [], None), Prototype('printString', VoidType(), [ParamProto('anArg',StringType(),None)], None),\
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
			
		if type(ctx.typ) == AutoType and not ctx.init:
			raise Invalid(Variable(), ctx.name)

		if ctx.init:
			init_type, o = self.visit(ctx.init, o)
			
			if type(init_type) == ArrayType and type(ctx.typ) == ArrayType:
				
				if len(init_type.dimensions) != len(ctx.typ.dimensions):
					raise TypeMismatchInVarDecl(ctx)
				
				for i in range(len(init_type.dimensions)):
					if init_type.dimensions[i] != ctx.typ.dimensions[i]:
						raise TypeMismatchInVarDecl(ctx)

				if type(init_type.typ) != type(ctx.typ.typ):
					raise TypeMismatchInVarDecl(ctx)

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

		i = 0
		for param in ctx.params:
			if type(param.typ) == AutoType:
					param.typ = cur_proto.params[i].typ

			env = self.visit(param, env)
			i += 1

		if ctx.inherit:
			if len(ctx.body.body) != 0 and type(ctx.body.body[0]) == CallStmt and ctx.body.body[0].name == 'preventDefault':
				if len(ctx.body.body[0].args) > 0:
					raise TypeMismatchInExpression(ctx.body.body[0].args[0])
				ctx.body.body.remove(ctx.body.body[0])
			else:
				exist = False
				for proto in o[-2]:
					if ctx.inherit == proto.name:
						exist = True
						parent = proto
						break
				
				if not exist:
					raise Undeclared(Function(), ctx.inherit)
				
				env[-1] += [parent.name, ctx.name]

				if len(ctx.body.body) == 0 or type(ctx.body.body[0]) != CallStmt or ctx.body.body[0].name != 'super':
					if len(parent.params) != 0: raise InvalidStatementInFunction(ctx.name)

				else:
					parent_params = []
					for param in parent.params:
						
						for name in parent_params:
							if param.name == name: raise Redeclared(Parameter(), param.name)
						
						
						if param.inherit:
							for decl in env[0]:
								if param.name == decl.name: raise Invalid(Parameter(), param.name)
							parent_params.append(param.name)
							env[0] += [ParamDecl(param.name, param.typ, False, False)]

							

					

					superCall = ctx.body.body[0]
					if len(superCall.args) < len(parent.params): raise TypeMismatchInExpression(None)
					if len(superCall.args) > len(parent.params): raise TypeMismatchInExpression(superCall.args[len(parent.params)])

					i = 0
					for arg in superCall.args:
						arg_type, env = self.visit(arg, env)

						if type(arg_type) == IntegerType and type(parent.params[i].typ) == FloatType:
							arg_type = FloatType()

						if type(arg_type) == Prototype:
							for proto in o[-2]:
								if proto.name == arg_type.name:
									arg_type.return_type = parent.params[i].typ
									arg_type = parent.params[i].typ
									break
						
						if type(arg_type) == AutoType:
							for decl in o[0]:
								if decl.name == arg.name:
									decl.typ = parent.params[i].typ
									break

							for param in parent.params:
								if param.name == arg.name:
									param.typ = parent_params[i].typ
									break
							
							arg_type = parent.params[i].typ

						if type(parent.params[i].typ) == AutoType:
							parent.params[i].typ = arg_type

						if type(arg_type) != type(parent.params[i].typ): raise TypeMismatchInExpression(arg)
						i += 1

					ctx.body.body.remove(ctx.body.body[0])
				
				env = self.visit(ctx.body,env)

				o[-2] = env[-2]
				o[0] += [ctx]
				return o
			
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
							prototype.return_type = left_type
							right_type = left_type
							break
					

		if ctx.op in ['+', '-','*','/']:
			
			if (type(left_type) != FloatType and type(left_type) != IntegerType) or (type(right_type) != FloatType and type(right_type) != IntegerType):
				
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

			if (type(left_type) != BooleanType and type(left_type) != IntegerType) or (type(right_type) != BooleanType and type(right_type) != IntegerType) :
				raise TypeMismatchInExpression(ctx)

			return (BooleanType(), o)
		
		if ctx.op in ['>','<','>=','<=']:
			if (type(left_type) != FloatType and type(left_type) != IntegerType) or (type(right_type) != FloatType and type(right_type) != IntegerType):
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
		i = 0
		for env in o:
			if i == len(o) - 2:
				break
			for decl in env:
				if (type(decl) == VarDecl or type(decl) == ParamDecl) and decl.name == ctx.name:
					return (decl.typ, o)
			i += 1
					
		raise Undeclared(Identifier(), ctx.name)

	def visitArrayCell(self, ctx, o):
		cur_id = Id(ctx.name)
		typ, o = self.visit(cur_id, o)

		if type(typ) != ArrayType:
			raise TypeMismatchInExpression(ctx)

		if len(ctx.cell) > len(typ.dimensions):
			raise TypeMismatchInExpression(ctx)
		
		for i in range(len(ctx.cell)):
			cell_type, o = self.visit(ctx.cell[i], o)

			if type(cell_type) == AutoType:
				x = False
				for env in o:
					if x == len(o) - 2:
						break
					for decl in env:
						if decl.name == ctx.cell[i].name:
							decl.typ = IntegerType()
							cell_type = IntegerType()
							x = True
							break


			if type(cell_type) == Prototype:
				for prototype in o[-2]:
					if prototype.name == ctx.cell[i].name:
						prototype.return_type = IntegerType()
						cell_type = IntegerType()
						break

			if type(cell_type) != IntegerType:
				raise TypeMismatchInExpression(ctx)
		
		if len(ctx.cell) < len(typ.dimensions):
			return ArrayType(typ.dimensions[len(ctx.cell):], typ.typ), o
		
		return typ.typ, o


	def visitIntegerLit(self, ctx, o):
		return (IntegerType(), o)

	def visitFloatLit(self, ctx, o):
		return (FloatType(), o)

	def visitStringLit(self, ctx, o):
		return (StringType(), o)

	def visitBooleanLit(self, ctx, o):
		return (BooleanType(), o)

	def visitArrayLit(self, ctx, o):
		prev_type, o = self.visit(ctx.explist[0], o)
		cur_dimension = [len(ctx.explist)] 
		for expr in ctx.explist:
			cur_type, o = self.visit(expr, o)

			if type(cur_type) != type(prev_type):
				raise IllegalArrayLiteral(ctx)
			
			if type(cur_type) == ArrayType:
				if len(cur_type.dimensions) != len(prev_type.dimensions):
					raise IllegalArrayLiteral(ctx)
				
				for i in range(len(cur_type.dimensions)):
					if cur_type.dimensions[i] != prev_type.dimensions[i]:
						raise IllegalArrayLiteral(ctx)
				
				if type(cur_type.typ) != type(prev_type.typ):
					raise IllegalArrayLiteral(ctx)
			
		return (ArrayType(cur_dimension, cur_type),o) if type(cur_type) in [IntegerType, BooleanType, StringType, FloatType]\
			else (ArrayType(cur_dimension + cur_type.dimensions, cur_type.typ), o)
		

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
			
			if type(arg_type) == AutoType:
				x = False
				for env in o:
					if x:
						break
					for decl in env:
						if decl.name == ctx.args[i].name:
							decl.typ = proto.params[i].typ
							arg_type = proto.params[i].typ
							x= True
							break


			if type(proto.params[i].typ) == AutoType:
				proto.params[i].typ = arg_type

			if type(arg_type) == Prototype:
				for prototype in o[-2]:
					if prototype.name == arg_type.name:
						prototype.return_type = proto.params[i].typ
						arg_type = proto.params[i].typ
						break
			
			if type(arg_type) == IntegerType and type(proto.params[i].typ) == FloatType:
				arg_type = FloatType()

			if type(proto.params[i].typ) != type(arg_type):
				raise TypeMismatchInExpression(ctx)

			i += 1
		

		return (proto.return_type, o) if type(proto.return_type) != AutoType else (proto, o)


	def visitAssignStmt(self, ctx, o):

		right_type, o = self.visit(ctx.rhs, o)

		for prototype in o[-2]:
			if prototype.name == o[-1][-1]:
				proto = prototype
				break
		
		isNonAutoParam = False
		for param in proto.params:
			if param.name == ctx.lhs.name and type(param.typ) != AutoType:
				left_type = param.typ
				isNonAutoParam = True
				break
		if not isNonAutoParam:
			left_type, o = self.visit(ctx.lhs, o)
		
		
		
		if type(left_type) == ArrayType:
			raise TypeMismatchInStatement(ctx)

		if type(right_type) == Prototype:
				for prototype in o[-2]:
					if prototype.name == right_type.name:
						prototype.return_type = left_type
						right_type = left_type
						break
		
		if type(left_type) == FloatType and type(right_type) == IntegerType:
				right_type = FloatType()

		if type(left_type) == AutoType:
			i = False
			for env in o:
				if i:
					break
				for decl in env:
					if decl.name == ctx.lhs.name:
						decl.typ = right_type
						left_type = right_type
						i = True
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

		if type(scalar_var_type) == AutoType:
			scalar_var_type = IntegerType()
			x = False
			for env in o:
				if x:
					break
				for decl in env:
					if decl. name == ctx.init.lhs.name:
						decl.typ = IntegerType()
						x = True
						break
			

		if type(scalar_var_type) != IntegerType:
			raise TypeMismatchInStatement(ctx)
		
		o = self.visit(ctx.init, o)
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
		env[-1] = [1,2] + env[-1]
		env = self.visit(ctx.stmt, env)
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
		env1[-1] = [2] + env1[-1]
		env1 = self.visit(ctx.tstmt, env1)
		if ctx.fstmt:
			env2 = [[]] + o
			env2[-1] = [2] + env2[-1]
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
		env[-1] = [1,2] + env[-1]
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
		env[-1] = [1,2] + env[-1]
		env = self.visit(ctx.stmt, env)

		return o

	def visitBreakStmt(self, ctx, o):
		if 1 not in o[-1]:
			raise MustInLoop(ctx)
		return o

	def visitContinueStmt(self, ctx, o):
		if 1 not in o[-1]:
			raise MustInLoop(ctx)
		return o

	def visitReturnStmt(self, ctx, o):

		for proto in o[-2]:
			if proto.name == o[-1][-1]:
				prototype = proto
				break

		if (prototype.returned and 2 not in o[-1]) or (3 in o[-1]):
			return o

		if not ctx.expr:
			expr_type = VoidType()
		else:
			expr_type,o = self.visit(ctx.expr, o)

		

		if type(expr_type) == AutoType:
			expr_type = prototype.return_type
			x = False
			for env in o:
				if x :
					break
				for decl in env:
					if decl.name == ctx.expr.name:
						decl.typ = prototype.return_type
						x = True
						break



		if type(prototype.return_type) == AutoType:
			prototype.return_type = expr_type
		
		if type(expr_type) == IntegerType and type(prototype.return_type) == FloatType:
			expr_type = FloatType()

		if type(expr_type) != type(prototype.return_type):
			raise TypeMismatchInStatement(ctx)
		
		if 2 not in o[-1]:
			prototype.returned = True

		if 2 in o[-1]:
			o[-1].remove(2)
			o[-1] = [3] + o[-1]

		return o

	def visitCallStmt(self, ctx, o):
		if ctx.name == 'super' or ctx.name == 'preventDefault':
			raise InvalidStatementInFunction(Function(),o[-1][-1])

		exist = False
		for proto in o[-2]:
			if proto.name == ctx.name:
				exist = True
				prototype = proto
				break
		
		if not exist:
			raise Undeclared(Function(), ctx.name)
		
		for p in o[-2]:
			if p.name == o[-1][-1]:
				proto = p
				break

		if len(ctx.args) != len(prototype.params):
			raise TypeMismatchInStatement(ctx)
		
		for i in range(len(ctx.args)):
			arg_type, o = self.visit(ctx.args[i], o)

			if type(prototype.params[i].typ) == AutoType:
				prototype.params[i].typ = arg_type

			x = False
			if type(arg_type) == AutoType:
				for param in proto.params:
					if param.name == ctx.args[i].name:
						param.typ = prototype.params[i].typ
						arg_type = prototype.params[i].typ
						break

				for env in o:
					if x :
						break
					for decl in env:
						if decl. name == ctx.args[i].name:
							decl.typ = prototype.params[i].typ
							arg_type = prototype.params[i].typ
							x = True
							break

				

			if type(arg_type) == Prototype:
				for proto in o[-2]:	
					if proto.name == arg_type.name:
						proto.return_type = prototype.params[i].typ
						arg_type = prototype.params[i].typ
						break
			
			if type(arg_type) == IntegerType and type(prototype.params[i].typ) == FloatType:
				arg_type = FloatType()

			if type(arg_type) != type(prototype.params[i].typ):
				raise TypeMismatchInStatement(ctx)
			
		return o


