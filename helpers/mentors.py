"""Core functions for Mentorbot's character and region-based mentor commands."""

import discord
from discord.ext import commands

from helpers import helpers


async def mentor_info(ctx, cursor, c=None, r=None):
    """Display an embed listing the mentors of given character/region."""
    # Get character/region name, color, and icon url
    info = helpers.character_info(cursor, character=c, region=r)
    # Create embed
    embed = discord.Embed(
        color=info['color'],
        title=f"Here's a list of our {info['name']} mentors and advisors:")
    embed.set_author(name='Great selection!', icon_url=info['icon'])
    # Mentors
    bot = ctx.bot
    mentors = mentors_of_status(bot, cursor, 'Mentor', c=c, r=r)
    if mentors:
        embed.add_field(name='Mentors', value=mentors, inline=False)
    # Trial Mentors
    trial_mentors = mentors_of_status(bot, cursor, 'Trial', c=c, r=r)
    if trial_mentors:
        embed.add_field(name='Trial Mentors', value=trial_mentors, inline=False)
    # Advisors
    advisors = mentors_of_status(bot, cursor, 'Advisor', c=c, r=r)
    if advisors:
        embed.add_field(name='Advisors', value=advisors, inline=False)
    # DND
    dnd = dnd_mentors(bot, cursor, c=c, r=r)
    if dnd:
        embed.add_field(name='Do Not Disturb', value=dnd, inline=False)
    # Send mentor info
    await ctx.send(embed=embed)


def mentors_of_status(bot, cursor, status, c=None, r=None):
    """Return mentors of given status and character/region for embed."""
    character_region = helpers.character_info(cursor, character=c, region=r)['name']
    mentors = []
    if c:  # If character was given
        cursor.execute('''SELECT discord_id, name, region FROM mentors WHERE status = :status
                        AND characters LIKE :character = 1 AND do_not_disturb = 0''',
                        {'status': status, 'character': f'%{character_region}%'})
        for row in cursor.fetchall():
            try:
                mentor = bot.get_user(row['discord_id'])
                mentors.append(
                    f"{mentor.mention} **{str(mentor)}** ({row['region']})")
            except AttributeError:  # catch if user ID isn't found, eg. left the server
                mentors.append(f"{row['name']} ({row['region']})")
    elif r:  # If region was given
        cursor.execute('''SELECT discord_id, name, characters FROM mentors WHERE 
                        status = :status AND region = :region AND do_not_disturb = 0''',
                        {'status': status, 'region': character_region})
        for row in cursor.fetchall():
            try:
                mentor = bot.get_user(row['discord_id'])
                mentors.append(
                    f"{mentor.mention} **{str(mentor)}** ({row['characters']})")
            except AttributeError:  # catch if user ID isn't found, eg. left the server
                mentors.append(f"{row['name']} ({row['characters']})")
    return '\n'.join(mentors)


def dnd_mentors(bot, cursor, c=None, r=None):
    """Return DND mentors of given character/region for embed."""
    character_region = helpers.character_info(cursor, character=c, region=r)['name']
    mentors = []
    if c:  # If character was given
        cursor.execute('''SELECT discord_id, name, region FROM mentors WHERE
                        characters LIKE :character = 1 AND do_not_disturb = 1''',
                        {'character': f'%{character_region}%'})
        for row in cursor.fetchall():
            try:
                mentor = bot.get_user(row['discord_id'])
                mentors.append(
                    f"{mentor.mention} **{str(mentor)}** ({row['region']})")
            except AttributeError:  # catch if user ID isn't found, eg. left the server
                mentors.append(f"{row['name']} ({row['region']})")
    elif r:  # If region was given
        cursor.execute('''SELECT discord_id, name, characters FROM mentors WHERE 
                        region = :region AND do_not_disturb = 1''',
                        {'region': character_region})
        for row in cursor.fetchall():
            try:
                mentor = bot.get_user(row['discord_id'])
                mentors.append(
                    f"{mentor.mention} **{str(mentor)}** ({row['characters']})")
            except AttributeError:  # catch if user ID isn't found, eg. left the server
                mentors.append(f"{row['name']} ({row['characters']})")
    return '\n'.join(mentors)

