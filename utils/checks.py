from discord.ext import commands
import discord.utils
import json
import os
from .config import load_settings

class noOwner(commands.CommandError): pass
class noPerms(commands.CommandError): pass
class noRole(commands.CommandError): pass
class noAdmin(commands.CommandError): pass

owner_id = os.environ.get('BOT_OWNER')

def is_owner_check(message):
	if message.author.id == owner_id:
		return True
	raise noOwner()

def is_owner():
	return commands.check(lambda ctx: is_owner_check(ctx.message))

def check_permissions(ctx, perms):
	msg = ctx.message
	if msg.author.id == owner_id:
		return True
	ch = msg.channel
	author = msg.author
	resolved = ch.permissions_for(author)
	if all(getattr(resolved, name, None) == value for name, value in perms.items()):
		return True
	return False

def role_or_perm(t, ctx, check, **perms):
	if check_permissions(ctx, perms):
		return True
	ch = ctx.message.channel
	author = ctx.message.author
	if ch.is_private:
		return False
	role = discord.utils.find(check, author.roles)
	if role is not None:
		return True
	if t:
		return False
	else:
		raise noRole()

admin_perms = ['administrator', 'manage_server']
admin_roles = ('idk up to kabus')
def admin_or_perm(**perms):
	def predicate(ctx):
		if ctx.message.channel.is_private:
			return True
		if role_or_perm(True, ctx, lambda r: r.name.lower() in admin_roles, **perms):
			return True
		for role in ctx.message.author.roles:
			role_perms = []
			for s in role.permissions:
				role_perms.append(s)
			for s in role_perms:
				for x in admin_perms:
					if s[0] == x and s[1] == True:
						return True
		raise noAdmin()
	return commands.check(predicate)


