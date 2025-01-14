# Copyright (C) idoneam (2016-2020)
#
# This file is part of Canary
#
# Canary is free software; you can redistribute it and/or modify it
# under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Canary is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Canary. If not, see <https://www.gnu.org/licenses/>.

import discord

from discord import utils
from discord.ext import commands
from enum import Enum
from typing import Optional, Tuple

from .utils.checks import is_moderator
from .utils.paginator import Pages


class RoleTransaction(Enum):
    ADD = "add"
    REMOVE = "remove"


class Roles(commands.Cog):
    ALL_CATEGORIES = (
        "pronouns",
        "fields",
        "faculties",
        "years",
        "generics",
    )

    CATEGORY_LIMITS = {
        "pronouns": None,
        "fields": 3,
        "faculties": 1,
        "years": 1,
        "generics": None,
    }

    def __init__(self, bot):
        self.bot = bot
        self.roles = self.bot.config.roles
        self.mod_role = self.bot.config.moderator_role

    @staticmethod
    async def paginate_roles(ctx, roles, title="All roles in server"):
        p = Pages(ctx, item_list=[r + "\n" for r in roles], title=title, display_option=(3, 20), editable_content=False)
        await p.paginate()

    async def toggle_role(
        self, ctx, transaction: RoleTransaction, requested_role: Optional[str], categories: Tuple[str, ...]
    ):
        """
        Assigns a single role to a user with no checks from a category of roles
        """

        fcategory = "categories" if len(categories) > 1 else "category"
        if not requested_role:
            roles = []
            for c in categories:
                roles += self.roles[c]  # All roles in the category

            # If no role is specified, list what is available in all possible
            # categories for the command.
            await Roles.paginate_roles(ctx, roles, title=f"Roles in {fcategory} `{', '.join(categories)}`")
            return

        # If a role is specified, narrow the category down to the one with the
        # role in it to impose a proper limit.
        try:
            category = next((c for c in categories if requested_role.lower() in {r.lower() for r in self.roles[c]}))
        except StopIteration:
            await ctx.send(f"Invalid role for {fcategory} `{', '.join(categories)}`.")
            return

        roles = self.roles[category]

        roles_lower = [r.lower() for r in roles]
        requested_role = roles[roles_lower.index(requested_role.lower())]

        limit = Roles.CATEGORY_LIMITS[category]

        role = utils.get(ctx.guild.roles, name=requested_role)
        member = ctx.message.author

        if not role:
            await ctx.send(
                f"Error: Role `{requested_role}` is self-assignable"
                f" but does not exist on the server... "
                f"Please contact your local {self.mod_role}."
            )
            return

        existing_roles = [rr for rr in (utils.get(member.roles, name=r) for r in roles) if rr is not None]

        if transaction == RoleTransaction.ADD:
            # Find existing roles in the category the user has
            if role in existing_roles:
                await ctx.send("You already have this role.")
                return

            if limit == 1 and existing_roles:
                # Treat as exclusive, simply replace roles
                # For roles defined as "exclusive" only one in that category
                # may be applied at a time.
                for old_role in existing_roles:
                    await member.remove_roles(old_role, reason="Self Requested")
                await member.add_roles(role, reason="Self Requested")
                await ctx.send(f"Replaced role for category `{category}`.")
                return

            elif limit and len(existing_roles) == limit:
                await ctx.send(
                    f"You have too many roles in category " f"`{category}` (limit is `{limit}`). " f"Please remove one."
                )
                return

            await member.add_roles(role, reason="Self Requested")
            await ctx.send("Role added.")

        elif transaction == RoleTransaction.REMOVE:
            if role not in existing_roles:
                await ctx.send("You do not have this role.")
                return
            await member.remove_roles(role, reason="Self Requested")
            await ctx.send("Role removed.")

        else:
            await ctx.send("Must `add` or `remove` a role.")

    @commands.command(aliases=["pronouns"])
    async def pronoun(self, ctx, *, pronoun: Optional[str] = None):
        """
        Self-assign a pronoun role to a user.
        If no argument is given, returns a list of roles that can be used with this command.
        """

        await self.toggle_role(ctx, RoleTransaction.ADD, pronoun, ("pronouns",))

    @commands.command(aliases=["fields", "program", "programs", "major", "majors"])
    async def field(self, ctx, *, field: Optional[str] = None):
        """
        Self-assign a field of study role to a user.
        If no argument is given, returns a list of roles that can be used with this command.
        """
        await self.toggle_role(ctx, RoleTransaction.ADD, field, ("fields",))

    @commands.command(aliases=["faculties"])
    async def faculty(self, ctx, *, faculty: Optional[str] = None):
        """
        Self-assign a faculty of study role to a user.
        If no argument is given, returns a list of roles that can be used with this command.
        """
        await self.toggle_role(ctx, RoleTransaction.ADD, faculty, ("faculties",))

    @commands.command(aliases=["years"])
    async def year(self, ctx, year: Optional[str] = None):
        """
        Self-assign a year of study role to a user.
        If no argument is given, returns a list of roles that can be used with this command.
        """
        await Roles.toggle_role(self, ctx, RoleTransaction.ADD, year, ("years",))

    @commands.command(aliases=["iam", "generic", "generics"])
    async def i_am(self, ctx, *, role: Optional[str]):
        """
        Self-assign a generic role to a user.
        If no argument is given, returns a list of roles that can be used with this command.
        """
        await self.toggle_role(ctx, RoleTransaction.ADD, role, Roles.ALL_CATEGORIES)

    @commands.command(aliases=["iamn"])
    async def i_am_not(self, ctx, *, role: Optional[str]):
        """
        Self-unassign a generic role to a user.
        """
        await self.toggle_role(ctx, RoleTransaction.REMOVE, role, Roles.ALL_CATEGORIES)

    @commands.command()
    async def roles(self, ctx, user: discord.Member = None):
        """Returns list of all roles in server or
        the list of a specific user's roles"""
        role_names = [
            role.name for role in (ctx.guild.roles if user is None else user.roles) if role != ctx.guild.default_role
        ]
        role_names.reverse()
        await Roles.paginate_roles(
            ctx,
            role_names,
            title=("all roles in server" if user is None else f"{user.display_name}'s roles") + f" ({len(role_names)})",
        )

    @commands.command()
    async def inrole(self, ctx, *, query_role):
        """Returns list of users in the specified role"""

        role = next((role for role in ctx.guild.roles if role.name.lower() == query_role.lower()), None)

        if role is None:
            return

        names = [str(m) + "\n" for m in role.members]
        header = f"List of users in {role.name} role - {len(names)}"

        # TODO remove for paginator take empty list for embed
        if not names:
            em = discord.Embed(title=header, colour=0xDA291C)
            em.set_footer(text="Page 01 of 01")
            await ctx.send(embed=em)
            return

        pages = Pages(ctx, item_list=names, title=header, display_option=(3, 20), editable_content=False)
        await pages.paginate()

    @commands.command(aliases=["cr", "createrole"])
    @is_moderator()
    async def create_role(self, ctx, *, role: Optional[str] = None):
        role = (role or "").strip()
        if not role:
            await ctx.send("Please specify a role name.")
            return

        role_obj = utils.get(ctx.guild.roles, name=role)
        if role_obj is not None:
            await ctx.send(f"Role `{role}` already exists!")
            return

        await ctx.guild.create_role(name=role, reason="Created with Canary")
        await ctx.send("Role created successfully.")

    @commands.command()
    async def inchannel(self, ctx):
        """Returns list of users in current channel"""
        channel = ctx.message.channel
        members = channel.members

        channel_users = list(map(lambda m: str(m) + "\n", members))
        header = f"List of users in #{channel} - {len(members)}"

        pages = Pages(ctx, item_list=channel_users, title=header, display_option=(3, 20), editable_content=False)
        await pages.paginate()


def setup(bot):
    bot.add_cog(Roles(bot))
