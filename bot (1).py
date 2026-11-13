# -*- coding: utf-8 -*-
import asyncio, json, os, random, re, sys, time
from collections import defaultdict, deque
from datetime import datetime, timedelta, timezone
import aiohttp, discord
from discord.ext import commands

BOT_NAME = "Faasle Security"
DATA_FILE = "faasle_data.json"
E_TICK = "<:Tick:1570429570061049979>"
E_CROSS = "<:florida_cross:1570429583843655760>"
E_DOT = "<a:delhi_dot:1570500296147206336>"
E_ARR = "<:arrow_2:1570658927199264799>"
E_WARN = "<:warn:1570429592722866227>"
E_SETTINGS = "<a:settings:1570428375938371646>"
E_STATUS = "<a:status:1570428312927469641>"
E_LOAD = "<a:Emo_Loading:1570429574670712855>"
E_PING = "<:latency:1570429597399523408>"
E_SEC = "<:security:1570537983856091139>"
E_PERMIT = "<:Lock:1570551582771249253>"
E_AUTOMOD = "<:automodemoji:1570551708222750812>"
E_UTIL = "<a:settings:1570537955477422310>"
E_GEN = "<:duniya_whitebots:1570537920757104640>"
E_MOD = "<:24021supportteammoderation:1570537648446251008>"
E_AROLE = "<:bluesaplingroleicon:1570537654657876109>"
E_FUN = "<:faasley__games:1570537661511368714>"
E_GREET = "<:Greet:1570537667404238942>"
E_GIVE = "<a:Giveaways:1570537673855340634>"
E_TICKETS = "<a:ticket_admin:1570537680045998181>"
E_MUSIC = "<a:lyf_musicnotes:1570537686287253525>"
E_TRACK = "<a:NX_Uptime:1570537692125466677>"
E_LOG = "<:note:1570537698236698655>"
E_SET = "<a:settings:1570537955477422310>"

ON_TOG, OFF_TOG = "🟢 »", "⚪ »"
DEEP_BLACK, BRIGHT_GREEN, BRIGHT_RED = 0x2B2D31, 0x2ECC71, 0xE74C3C
NOPING = discord.AllowedMentions.none()
STARTED = time.time()
_USER_EPHEMERAL = {}

try:
    with open(DATA_FILE, "r", encoding="utf-8") as _f:
        DB = json.load(_f)
except Exception:
    DB = {}

def save():
    try:
        with open(DATA_FILE, "w", encoding="utf-8") as _f:
            json.dump(DB, _f, indent=2)
    except Exception:
        pass

AN_EVENTS_32 = [
    ("Ban Protection", "ban", "Blocks unauthorized member bans & mass-ban waves", (15, 50)),
    ("Kick Protection", "kick", "Blocks unauthorized member kicks & prune scripts", (15, 50)),
    ("Prune Protection", "prune", "Intercepts server member pruning operations", (1, 2)),
    ("Channel/Category Delete", "chdl", "Prevents channel & category deletion and auto-clones", (8, 30)),
    ("Channel/Category Create", "chcr", "Stops spam channel/category creation raids", (8, 30)),
    ("Channel Update", "chup", "Reverts unauthorized channel name/topic/slowmode edits", (15, 50)),
    ("Role Delete", "rldl", "Protects server roles from deletion & restores settings", (8, 30)),
    ("Role Create", "rlcr", "Blocks mass role creation spam", (8, 30)),
    ("Role Update", "rlup", "Reverts unauthorized role name/color/permission edits", (15, 50)),
    ("Webhook Create", "mngweb", "Destroys unauthorized webhooks immediately on creation", (4, 10)),
    ("Webhook Delete", "mngwebdl", "Logs and blocks unauthorized webhook removals", (4, 10)),
    ("Webhook Update", "mngwebup", "Blocks webhook name/channel/avatar tampering", (4, 10)),
    ("Emoji Protection", "emoji", "Prevents mass custom emoji deletion or modification", (5, 15)),
    ("Sticker Protection", "stickr", "Prevents custom sticker deletion or tampering", (5, 15)),
    ("Member Update", "memup", "Tracks member role & dangerous privilege escalations", (25, 80)),
    ("Member Update (Dangerous)", "memup_dang", "Prevents unauthorized dangerous admin role assignment", (10, 30)),
    ("Server Update", "serverup", "Reverts unauthorized server name, icon, or vanity edits", (2, 10)),
    ("Bot Add", "botadd", "Instantly bans unverified bots added without approval", (2, 5)),
    ("Timeout Protection", "timeout", "Prevents mass timeout/mute abuse by compromised staff", (6, 20)),
    ("Mention Spam", "meneve", "Neutralizes @everyone and @here mass ping raids", (15, 50)),
    ("Vanity Protection", "vanity", "Locks server vanity invite code from hijacking", (1, 2)),
    ("Permission Update", "permup", "Blocks channel permission overwrite escalations", (8, 25)),
    ("Integration Protection", "intgr", "Stops unauthorized integration & app links", (2, 5)),
    ("Dangerous Role Invite Guard", "invsplash", "Guards invites tied to elevated permission roles", (4, 12)),
    ("Mainrole Shield", "mrshield", "Locks mainroles against ping & dangerous permissions", (1, 2)),
    ("Mass Reaction", "mreact", "Prevents emoji reaction spam raids", (10, 30)),
    ("Automod Rule Guard", "amguard", "Blocks unauthorized edits to Discord automod rules", (3, 10)),
    ("Stage Guard", "stguard", "Protects stage channels from unauthorized creation/deletion", (3, 10)),
    ("Thread Guard", "thguard", "Prevents thread spam and unauthorized deletions", (10, 30)),
    ("Voice State Guard", "vcguard", "Protects voice channels against mass server muting", (5, 15)),
    ("Community Update", "cmup", "Locks server community settings and rules channels", (2, 5)),
    ("Onboarding Guard", "onguard", "Protects server onboarding prompts and questions", (2, 5)),
]
EVENT_NAMES = [e[0] for e in AN_EVENTS_32]
EVENT_KEYS = {e[0]: e[1] for e in AN_EVENTS_32}
EVENT_DESC = {e[0]: e[2] for e in AN_EVENTS_32}
EVENT_LIMS = {e[0]: e[3] for e in AN_EVENTS_32}
BETRAYAL_32 = [e[0] for e in AN_EVENTS_32]

ACT_MAP = {
    discord.AuditLogAction.ban: "Ban Protection",
    discord.AuditLogAction.kick: "Kick Protection",
    discord.AuditLogAction.member_prune: "Prune Protection",
    discord.AuditLogAction.channel_delete: "Channel/Category Delete",
    discord.AuditLogAction.channel_create: "Channel/Category Create",
    discord.AuditLogAction.channel_update: "Channel Update",
    discord.AuditLogAction.overwrite_create: "Permission Update",
    discord.AuditLogAction.overwrite_update: "Permission Update",
    discord.AuditLogAction.overwrite_delete: "Permission Update",
    discord.AuditLogAction.role_delete: "Role Delete",
    discord.AuditLogAction.role_create: "Role Create",
    discord.AuditLogAction.role_update: "Role Update",
    discord.AuditLogAction.webhook_create: "Webhook Create",
    discord.AuditLogAction.webhook_delete: "Webhook Delete",
    discord.AuditLogAction.webhook_update: "Webhook Update",
    discord.AuditLogAction.emoji_create: "Emoji Protection",
    discord.AuditLogAction.emoji_delete: "Emoji Protection",
    discord.AuditLogAction.emoji_update: "Emoji Protection",
    discord.AuditLogAction.sticker_create: "Sticker Protection",
    discord.AuditLogAction.sticker_delete: "Sticker Protection",
    discord.AuditLogAction.sticker_update: "Sticker Protection",
    discord.AuditLogAction.member_role_update: "Member Update",
    discord.AuditLogAction.member_update: "Timeout Protection",
    discord.AuditLogAction.guild_update: "Server Update",
    discord.AuditLogAction.bot_add: "Bot Add",
    discord.AuditLogAction.integration_create: "Integration Protection",
    discord.AuditLogAction.invite_create: "Dangerous Role Invite Guard",
}

FAKE_PERMS_LIST = [
    ("quarantine_users", "Quarantine Users"),
    ("ban_members", "Ban / Unban Users"),
    ("kick_members", "Kick Users"),
    ("moderate_members", "Timeout / Mute Users"),
    ("manage_messages", "Purge / Manage Messages"),
    ("manage_channels", "Manage Channels"),
    ("manage_roles", "Manage Roles"),
    ("manage_nicknames", "Manage Nicknames"),
    ("manage_emojis", "Manage Emojis / Stickers"),
    ("mute_members", "Voice Moderation"),
    ("manage_guild", "Manage Giveaways"),
]

AM_DEFAULT_FILTERS = {
    "Anti spam": {"on": True, "punish": "Auto Mute", "heat": "10"},
    "Anti caps": {"on": True, "punish": "Auto Mute", "heat": "0.12"},
    "Anti link": {"on": True, "punish": "Auto Mute", "heat": "100"},
    "Anti invites": {"on": True, "punish": "Auto Mute", "heat": "100"},
    "Anti mass mention": {"on": True, "punish": "Auto Mute", "heat": "20"},
    "Anti emoji spam": {"on": True, "punish": "Auto Mute", "heat": "12"},
    "Anti NSFW link": {"on": True, "punish": "Auto Mute", "heat": "100 (Max)"},
    "Anti attachment spam": {"on": True, "punish": "Auto Mute", "heat": "20"},
    "Anti zalgo spam": {"on": True, "punish": "Auto Mute", "heat": "1.5"},
    "Similar message spam": {"on": True, "punish": "Auto Mute", "heat": "22"},
    "Character limit spam": {"on": True, "punish": "Auto Mute", "heat": "0.08"},
    "New line spam": {"on": True, "punish": "Auto Mute", "heat": "5"},
    "Blacklist word": {"on": True, "punish": "Auto Mute", "heat": "100 (Max)"},
}

LOG_STREAMS_16 = [
    ("system", "System Logs", "system-logs"),
    ("join", "Join Logs", "join-logs"),
    ("leave", "Leave Logs", "leave-logs"),
    ("member", "Member Logs", "member-logs"),
    ("message", "Message Logs", "message-logs"),
    ("thread", "Thread Logs", "thread-logs"),
    ("voice", "Voice Logs", "voice-logs"),
    ("stage", "Stage Logs", "stage-logs"),
    ("moderation", "Moderation Logs", "moderation-logs"),
    ("channel", "Channel Logs", "channel-logs"),
    ("server", "Server Logs", "server-logs"),
    ("event", "Event Logs", "event-logs"),
    ("webhook", "Webhook Logs", "webhook-logs"),
    ("role", "Role Logs", "role-logs"),
    ("application", "Application Logs", "application-logs"),
    ("alert", "Alert Logs", "alert-logs"),
]

def cfg(gid):
    gid = str(gid.id if hasattr(gid, "id") else gid)
    c = DB.setdefault(gid, {})
    c.setdefault("prefix", ";")
    c.setdefault("prefixes", [";", ".", "?"])
    c.setdefault("enabled", True)
    c.setdefault("autorecovery", True)
    c.setdefault("punishment", "ban")
    c.setdefault("log_channel", None)
    c.setdefault("whitelist", {})
    c.setdefault("extraowners", [])
    c.setdefault("autoroles", [])
    c.setdefault("autoroles_bots", [])
    c.setdefault("mainroles", [])
    c.setdefault("quarantine", {"role": None, "saved": {}})
    c.setdefault("fake_perms", {})
    c.setdefault("ignore", {"channels": [], "roles": [], "commands": [], "bypass": []})
    c.setdefault("autoresponders", {})
    c.setdefault("autoreacts", {})
    c.setdefault("sticky", {})
    c.setdefault("reactionroles", {})
    c.setdefault("customroles", {"reqrole": None, "map": {}})
    c.setdefault("vcrole", None)
    c.setdefault("joindm", None)
    c.setdefault("setuplock", False)
    c.setdefault("roguedemote", True)
    c.setdefault("greet", {"enabled": False, "channel": None, "msg": "Welcome {user} to **{server}**!", "autodelete": 0})
    af = c.setdefault("an_filters", {})
    for e in EVENT_NAMES:
        af.setdefault(e, True)
    return c

def X(g):
    return cfg(g).setdefault("x", {})

def XS(g, key, factory=dict):
    return X(g).setdefault(key, factory())

def sec_cfg(g):
    s = XS(g, "sec_suite", dict)
    s.setdefault("antibetray", {"on": True, "profile": "Balanced", "punish": "BAN"})
    s.setdefault("wallrole", {"on": False, "role": None})
    s.setdefault("quarantine", {"on": False, "role": cfg(g)["quarantine"].get("role")})
    s.setdefault("nightmode", {"on": False, "active": False, "saved": {}, "schedule": "23:00 - 07:00 (Asia/Kolkata)"})
    s.setdefault("antiraid", {"on": True, "action": "KICK", "profile": "Balanced", "count": 5, "window": 8, "min_age_h": 24})
    s.setdefault("panic", {"on": True, "active": False, "punish": "KICK", "operator": None, "duration": 1800, "burst_limit": 3, "burst_time": 5, "notify": True})
    return s

def am_cfg(g):
    am = XS(g, "automod_master", dict)
    am.setdefault("enabled", True)
    am.setdefault("wl_users", [])
    fl = am.setdefault("filters", {})
    for k, v in AM_DEFAULT_FILTERS.items():
        fl.setdefault(k, dict(v))
    return am

def log_cfg(g):
    d = XS(g, "logging_16", dict)
    d.setdefault("enabled", True)
    d.setdefault("cat_id", None)
    d.setdefault("ignore_embeds", True)
    d.setdefault("ignore_voice", False)
    chs = d.setdefault("channels", {})
    whs = d.setdefault("webhooks", {})
    for k, _, _ in LOG_STREAMS_16:
        chs.setdefault(k, None)
        whs.setdefault(k, None)
    return d

def get_prefix(bot_inst, message):
    if not message.guild:
        return [";", ".", "?"]
    c = cfg(message.guild.id)
    p_list = list(set([c.get("prefix", ";")] + c.get("prefixes", [";", ".", "?"])))
    return commands.when_mentioned_or(*p_list)(bot_inst, message)

bot = commands.Bot(command_prefix=get_prefix, intents=discord.Intents.all(), help_command=None)

_CMD_COOLDOWNS = defaultdict(float)

@bot.check
async def global_rate_limit_check(ctx):
    if not ctx.guild or ctx.author.bot:
        return True
    now = time.time()
    last = _CMD_COOLDOWNS[ctx.author.id]
    if now - last < 3.0:
        raise commands.CommandOnCooldown(commands.Cooldown(1, 3.0), 3.0 - (now - last), commands.BucketType.user)
    _CMD_COOLDOWNS[ctx.author.id] = now
    return True

@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, (commands.CommandOnCooldown, commands.CheckFailure, commands.CommandNotFound)):
        return

def R(reason):
    return f"{BOT_NAME} Zero-Trust: {reason}"

def dangerous(role: discord.Role):
    p = role.permissions
    return any([p.administrator, p.ban_members, p.kick_members, p.manage_guild, p.manage_roles, p.manage_channels, p.manage_webhooks, p.mention_everyone])

def is_trusted(g, uid):
    if not g:
        return False
    if uid == g.owner_id or (bot.user and uid == bot.user.id):
        return True
    c = cfg(g.id)
    return uid in c.get("extraowners", []) or "All Events" in c.get("whitelist", {}).get(str(uid), [])

def has_fake_perm(member: discord.Member, p_name: str):
    fp = cfg(member.guild.id).get("fake_perms", {})
    return any(p_name in fp.get(str(r.id), []) for r in member.roles)

def parse_dur(s: str):
    m = re.match(r"^(\d+)\s*([smhdw]?)$", str(s).strip().lower())
    if not m:
        return 600
    v, u = int(m.group(1)), m.group(2) or "m"
    return v * {"s": 1, "m": 60, "h": 3600, "d": 86400, "w": 604800}[u]

def human(sec):
    sec = int(max(0, sec))
    d, r = divmod(sec, 86400)
    h, r = divmod(r, 3600)
    m, s = divmod(r, 60)
    p = []
    if d: p.append(f"{d} days")
    if h: p.append(f"{h} hours")
    if m: p.append(f"{m} mins")
    if s or not p: p.append(f"{s} secs")
    return ", ".join(p)

def fancy(ctx, title="", desc="", color=DEEP_BLACK, thumb=None, image=None, fields=(), footer_extra=None):
    e = discord.Embed(title=title, description=str(desc)[:4000], color=color)
    if thumb: e.set_thumbnail(url=thumb)
    if image: e.set_image(url=image)
    for n, v, inl in fields:
        e.add_field(name=n, value=str(v)[:1024] or "-", inline=inl)
    req = f"Requested by {ctx.author.display_name}" if ctx and hasattr(ctx, "author") and ctx.author else f"Powered By {BOT_NAME}"
    e.set_footer(text=footer_extra or req, icon_url=(ctx.author.display_avatar.url if ctx and hasattr(ctx, "author") and ctx.author else None))
    return e

async def send(ctx, title="", desc="", **kw):
    return await ctx.reply(embed=fancy(ctx, title, desc, **kw), mention_author=False, allowed_mentions=NOPING)

async def send_usage(ctx, syntax_str: str, desc_str: str, aliases_str: str = None):
    p = ctx.clean_prefix if hasattr(ctx, "clean_prefix") else "."
    al_blk = f"> **› Aliases :** `{aliases_str}`\n" if aliases_str else ""
    body = f"`<..> <required> | [..] [optional]`\n\n> `{p}{syntax_str}`\n\n{al_blk}> **›** {desc_str}"
    e = discord.Embed(description=body, color=DEEP_BLACK)
    return await ctx.reply(embed=e, mention_author=False, allowed_mentions=NOPING)

async def dm_mod_notice(user, guild, action_past: str, moderator, reason: str):
    if not user or getattr(user, "bot", False):
        return False
    desc = f"{E_ARR} **{guild.name}**\n\n> You have been {action_past} by `{moderator.name}` for ~\n> `{reason or 'No reason provided'}`"
    e = discord.Embed(title=f"You have been {action_past}!", description=desc, color=DEEP_BLACK)
    try:
        await user.send(embed=e)
        return True
    except Exception:
        return False

async def send_webhook_log(g, stream_key: str, title: str, desc: str, color=DEEP_BLACK):
    d = log_cfg(g)
    if not d.get("enabled", True):
        return
    wh_url = d.get("webhooks", {}).get(stream_key)
    cid = d.get("channels", {}).get(stream_key)
    e = discord.Embed(title=title, description=desc, color=color, timestamp=datetime.now(timezone.utc))
    e.set_footer(text=f"{BOT_NAME} Webhook Telemetry")
    if wh_url:
        try:
            async with aiohttp.ClientSession() as sess:
                wh = discord.Webhook.from_url(wh_url, session=sess)
                await wh.send(embed=e, username=f"{BOT_NAME} Logs", avatar_url=(bot.user.display_avatar.url if bot.user else None))
                return
        except Exception:
            pass
    ch = g.get_channel(cid) if cid else None
    if ch:
        try:
            await ch.send(embed=e)
        except Exception:
            pass

class Denied(commands.CheckFailure): pass

def owner_only():
    async def pred(ctx):
        if not ctx.guild: return False
        if ctx.author.id == ctx.guild.owner_id or ctx.author.id in cfg(ctx.guild.id).get("extraowners", []): return True
        await send(ctx, "", f"{E_CROSS} Only the Server Owner or Extra Owners can execute this command.", color=BRIGHT_RED)
        raise Denied()
    return commands.check(pred)

def perm(p_name, label=None):
    async def pred(ctx):
        if not ctx.guild: return False
        if ctx.author.id == ctx.guild.owner_id or ctx.author.id in cfg(ctx.guild.id).get("extraowners", []): return True
        if getattr(ctx.author.guild_permissions, p_name, False) or ctx.author.guild_permissions.administrator: return True
        if has_fake_perm(ctx.author, p_name): return True
        await send(ctx, "", f"{E_CROSS} You need `{label or p_name}` permission to use this command.", color=BRIGHT_RED)
        raise Denied()
    return commands.check(pred)

async def hier(ctx, m: discord.Member):
    if m.id == ctx.guild.owner_id or (ctx.author.id != ctx.guild.owner_id and m.top_role >= ctx.author.top_role):
        await send(ctx, "", f"{E_CROSS} You cannot target {m.mention} due to role hierarchy.", color=BRIGHT_RED); raise Denied()
    if ctx.guild.me and m.top_role >= ctx.guild.me.top_role:
        await send(ctx, "", f"{E_CROSS} {m.mention} is positioned above or equal to {BOT_NAME}.", color=BRIGHT_RED); raise Denied()

def C(name, aliases=(), **kw):
    def deco(fn):
        if bot.get_command(name): bot.remove_command(name)
        al = [a for a in aliases if not bot.get_command(a)]
        return bot.command(name=name, aliases=al, **kw)(fn)
    return deco

def G(name, aliases=(), **kw):
    if bot.get_command(name): bot.remove_command(name)
    al = [a for a in aliases if not bot.get_command(a)]
    kw.setdefault("invoke_without_command", True)
    return lambda fn: bot.group(name=name, aliases=al, **kw)(fn)

def S(grp, name, aliases=(), **kw):
    def deco(fn):
        if grp.get_command(name): grp.remove_command(name)
        al = [a for a in aliases if not grp.get_command(a)]
        return grp.command(name=name, aliases=al, **kw)(fn)
    return deco

class Pager(discord.ui.View):
    def __init__(self, uid, pages, timeout=240):
        super().__init__(timeout=timeout); self.uid, self.pages, self.i = uid, pages, 0; self._sync()
    def _sync(self):
        last = len(self.pages) - 1
        for b in self.children:
            cid = getattr(b, "custom_id", "")
            if cid in ("pg_first", "pg_prev"): b.disabled = self.i == 0
            elif cid in ("pg_next", "pg_last"): b.disabled = self.i >= last
            elif cid == "pg_cnt": b.label = f"{self.i+1}/{len(self.pages)}"
    async def interaction_check(self, inter): return inter.user.id == self.uid
    async def _show(self, inter): self._sync(); await inter.response.edit_message(embed=self.pages[self.i], view=self)
    @discord.ui.button(label="≪", style=discord.ButtonStyle.secondary, custom_id="pg_first", row=0)
    async def b_first(self, inter, button): self.i = 0; await self._show(inter)
    @discord.ui.button(label="<", style=discord.ButtonStyle.secondary, custom_id="pg_prev", row=0)
    async def b_prev(self, inter, button): self.i = max(0, self.i - 1); await self._show(inter)
    @discord.ui.button(emoji="🗑️", style=discord.ButtonStyle.danger, custom_id="pg_del", row=0)
    async def b_del(self, inter, button): await inter.message.delete()
    @discord.ui.button(label=">", style=discord.ButtonStyle.secondary, custom_id="pg_next", row=0)
    async def b_next(self, inter, button): self.i = min(len(self.pages) - 1, self.i + 1); await self._show(inter)
    @discord.ui.button(label="1/1", style=discord.ButtonStyle.secondary, custom_id="pg_cnt", disabled=True, row=0)
    async def b_cnt(self, inter, button): pass

async def paginate(ctx, title, lines, per=10, color=DEEP_BLACK, empty="No records found."):
    lines = list(lines) or [empty]
    chunks = [lines[i:i + per] for i in range(0, len(lines), per)]
    pages = [fancy(ctx, title, "\n".join(ch), color=color, footer_extra=f"Page {n}/{len(chunks)} | Requested by {ctx.author.display_name}") for n, ch in enumerate(chunks, 1)]
    if len(pages) == 1: return await ctx.reply(embed=pages[0], mention_author=False, allowed_mentions=NOPING)
    await ctx.reply(embed=pages[0], view=Pager(ctx.author.id, pages), mention_author=False, allowed_mentions=NOPING)

def an_filter_panel_embed(ctx):
    c = cfg(ctx.guild.id); af = c["an_filters"]; rows = []
    for ev in EVENT_NAMES[:14]:
        rows.append(f"{ON_TOG if af.get(ev, True) else OFF_TOG} `{ev}`")
    rows.append(f"\n🛡️ **Server Name**\n╰ `{ctx.guild.name}`")
    return fancy(ctx, f"{BOT_NAME} Antinuke Filters", "\n".join(rows), footer_extra=f"Requested by {ctx.author.name}")

class AntinukeFilterToggleView(discord.ui.View):
    def __init__(self, ctx):
        super().__init__(timeout=240); self.ctx = ctx; self._build()
    def _build(self):
        self.clear_items(); af = cfg(self.ctx.guild.id)["an_filters"]
        evs = EVENT_NAMES[:14]
        dis_opts = [discord.SelectOption(label=e, value=e) for e in evs if not af.get(e, True)] or [discord.SelectOption(label="All Enabled", value="_none")]
        en_opts = [discord.SelectOption(label=e, value=e) for e in evs if af.get(e, True)] or [discord.SelectOption(label="All Disabled", value="_none")]
        s_en = discord.ui.Select(placeholder="↳ Select filters to Enable", options=dis_opts, disabled=(dis_opts[0].value=="_none"), row=0)
        s_dis = discord.ui.Select(placeholder="↳ Select filters to Disable", options=en_opts, disabled=(en_opts[0].value=="_none"), row=1)
        s_en.callback = self.on_en; s_dis.callback = self.on_dis; self.s_en, self.s_dis = s_en, s_dis
        self.add_item(s_en); self.add_item(s_dis)
        b_ea = discord.ui.Button(label="Enable All", emoji="✅", style=discord.ButtonStyle.secondary, row=2)
        b_da = discord.ui.Button(label="Disable All", emoji="🗑️", style=discord.ButtonStyle.danger, row=2)
        b_sv = discord.ui.Button(label="Save", style=discord.ButtonStyle.success, row=3)
        b_ea.callback = self.on_ea; b_da.callback = self.on_da; b_sv.callback = self.on_sv
        for b in (b_ea, b_da, b_sv): self.add_item(b)
    async def interaction_check(self, inter): return inter.user.id == self.ctx.author.id
    async def on_en(self, inter):
        for v in self.s_en.values:
            if v != "_none": cfg(self.ctx.guild.id)["an_filters"][v] = True
        save(); self._build(); await inter.response.edit_message(embed=an_filter_panel_embed(self.ctx), view=self)
    async def on_dis(self, inter):
        for v in self.s_dis.values:
            if v != "_none": cfg(self.ctx.guild.id)["an_filters"][v] = False
        save(); self._build(); await inter.response.edit_message(embed=an_filter_panel_embed(self.ctx), view=self)
    async def on_ea(self, inter):
        for e in EVENT_NAMES: cfg(self.ctx.guild.id)["an_filters"][e] = True
        save(); self._build(); await inter.response.edit_message(embed=an_filter_panel_embed(self.ctx), view=self)
    async def on_da(self, inter):
        for e in EVENT_NAMES: cfg(self.ctx.guild.id)["an_filters"][e] = False
        save(); self._build(); await inter.response.edit_message(embed=an_filter_panel_embed(self.ctx), view=self)
    async def on_sv(self, inter): save(); await inter.response.edit_message(embed=an_filter_panel_embed(self.ctx), view=None)

SUITE_MODULES = [
    ("antinuke", "Anti-Nuke Protection", "Core 32-event security shield against server nuke raids"),
    ("antibetray", "Anti-Betray Mode", "Sliding-window rate limits & whitelisted bot defense"),
    ("wallrole", "Wall Role Dynamic Firewall", "Prevents role escalation by anchoring non-staff members"),
    ("quarantine", "Quarantine Isolation System", "Isolates suspicious accounts with automatic role backup"),
    ("nightmode", "Nightmode Overnight Vault", "Automated permission lockdown during owner sleeping hours"),
    ("antiraid", "Anti-Raid Join Gate", "High-velocity token and bot raid gatekeeper"),
    ("panic", "Panic Mode Emergency Lock", "One-click total server lockdown trigger"),
]
SUITE_MODULES_KEYS = [k for k, _, _ in SUITE_MODULES]

async def ensure_wall_role(g):
    s = sec_cfg(g); rid = s["wallrole"].get("role")
    r = g.get_role(rid) if rid else None
    if not r:
        for ex in g.roles:
            if "barrier" in ex.name.lower() or "wall" in ex.name.lower(): r = ex; break
    if not r:
        r = await g.create_role(name=f"{BOT_NAME.upper()}'S BARRIER [+]", permissions=discord.Permissions.none(), colour=discord.Colour(0x5865F2), reason=R("Wall Role Firewall"))
        try: await r.edit(position=max(1, g.me.top_role.position - 1))
        except Exception: pass
    s["wallrole"]["role"] = r.id; save(); return r

async def ensure_quarantine_role(g):
    s = sec_cfg(g); rid = s["quarantine"].get("role") or cfg(g.id)["quarantine"].get("role")
    r = g.get_role(rid) if rid else None
    if not r:
        for ex in g.roles:
            nl = ex.name.lower()
            if "quarantine" in nl or nl.strip(". ") == "jail": r = ex; break
    if not r:
        r = await g.create_role(name="Quarantine", permissions=discord.Permissions.none(), colour=discord.Colour(0x95A5A6), reason=R("Quarantine Role"))
        for ch in g.channels:
            try: await ch.set_permissions(r, view_channel=False, send_messages=False, connect=False)
            except Exception: pass
    s["quarantine"]["role"] = r.id; cfg(g.id)["quarantine"]["role"] = r.id; save(); return r

def hub_embed(g):
    s = sec_cfg(g); c = cfg(g.id)
    lines = [f"{E_TICK if c['enabled'] else E_CROSS} **Core Antinuke Matrix (32/32 Events)** — `{'Active' if c['enabled'] else 'Disabled'}`"]
    for key, label, _ in SUITE_MODULES:
        st = s[key].get("on", False) if key != "antinuke" else c['enabled']
        lines.append(f"{E_TICK if st else E_CROSS} **{label}** — `{'Active' if st else 'Disabled'}`")
    desc = "\n".join(lines) + f"\n\n{E_DOT} Select modules below or click **Select All & Proceed** to activate all protections."
    return fancy(None, f"🛡️ {BOT_NAME} Security Suite Setup Hub", desc)

class SuiteWizardView(discord.ui.View):
    def __init__(self, author_id, g, queue):
        super().__init__(timeout=300); self.author_id, self.g, self.queue, self.idx = author_id, g, list(queue), 0; self.build_step()
    async def interaction_check(self, inter): return inter.user.id == self.author_id
    def current_key(self): return self.queue[self.idx] if self.idx < len(self.queue) else None
    def step_embed(self):
        key = self.current_key(); step_str = f"Step {self.idx + 1} of {len(self.queue)}"
        name_map = {k: (lbl, desc) for k, lbl, desc in SUITE_MODULES}
        lbl, d_txt = name_map.get(key, ("Security Module", ""))
        return fancy(None, f"🛡️ {BOT_NAME} Security Setup Hub", f"{E_TICK} **{lbl} Configuration**\n\n{d_txt}\n\nClick **Save & Proceed** to deploy `{lbl}`.", footer_extra=f"{step_str} • Module: {lbl}")
    def build_step(self):
        self.clear_items()
        if not self.current_key(): return
        b_save = discord.ui.Button(label="Save & Proceed", style=discord.ButtonStyle.success, row=0)
        b_skip = discord.ui.Button(label="Skip & Proceed", style=discord.ButtonStyle.secondary, row=0)
        b_cancel = discord.ui.Button(label="Cancel", style=discord.ButtonStyle.danger, row=0)
        b_save.callback = self.on_save_step; b_skip.callback = self.on_skip_step; b_cancel.callback = self.on_cancel
        for b in (b_save, b_skip, b_cancel): self.add_item(b)
    async def on_save_step(self, inter):
        key = self.current_key(); s = sec_cfg(self.g); await inter.response.defer()
        if key == "wallrole": await ensure_wall_role(self.g)
        elif key == "quarantine": await ensure_quarantine_role(self.g)
        elif key == "antinuke": cfg(self.g.id)["enabled"] = True
        else: s[key]["on"] = True
        save(); self.idx += 1; await self.advance(inter)
    async def on_skip_step(self, inter): await inter.response.defer(); self.idx += 1; await self.advance(inter)
    async def on_cancel(self, inter): await inter.response.edit_message(embed=fancy(None, "🛡️ Setup Terminated", f"{E_CROSS} Wizard closed.", color=BRIGHT_RED), view=None)
    async def advance(self, inter):
        if self.idx < len(self.queue): self.build_step(); return await inter.edit_original_response(embed=self.step_embed(), view=self)
        s = sec_cfg(self.g); name_map = {k: lbl for k, lbl, _ in SUITE_MODULES}
        act_lines = [f"{E_TICK} **{name_map[k]}** — Active" for k in SUITE_MODULES_KEYS if (s[k].get("on") if k != "antinuke" else cfg(self.g.id)["enabled"])]
        await inter.edit_original_response(embed=fancy(None, f"🛡️ {BOT_NAME} Security Suite Deployed", "\n".join(act_lines), color=BRIGHT_GREEN), view=None)

class SuiteHubView(discord.ui.View):
    def __init__(self, author_id, g):
        super().__init__(timeout=240); self.author_id, self.g = author_id, g
        opts = [discord.SelectOption(label=lbl, value=k, description=desc[:95]) for k, lbl, desc in SUITE_MODULES]
        sel = discord.ui.Select(placeholder="Select modules to activate...", min_values=1, max_values=len(opts), options=opts, row=0)
        sel.callback = self.on_sel; self.sel = sel; self.chosen = []; self.add_item(sel)
        b_proc = discord.ui.Button(label="Proceed", style=discord.ButtonStyle.primary, row=1)
        b_all = discord.ui.Button(label="Select All & Proceed", style=discord.ButtonStyle.success, row=1)
        b_cancel = discord.ui.Button(label="Cancel", style=discord.ButtonStyle.danger, row=2)
        b_proc.callback = self.on_proceed; b_all.callback = self.on_all; b_cancel.callback = self.on_cancel
        for b in (b_proc, b_all, b_cancel): self.add_item(b)
    async def interaction_check(self, inter): return inter.user.id == self.author_id
    async def on_sel(self, inter): self.chosen = list(self.sel.values); await inter.response.defer()
    async def on_proceed(self, inter): wiz = SuiteWizardView(self.author_id, self.g, self.chosen or SUITE_MODULES_KEYS); await inter.response.edit_message(embed=wiz.step_embed(), view=wiz)
    async def on_all(self, inter): wiz = SuiteWizardView(self.author_id, self.g, SUITE_MODULES_KEYS); await inter.response.edit_message(embed=wiz.step_embed(), view=wiz)
    async def on_cancel(self, inter): await inter.response.edit_message(embed=fancy(None, "🛡️ Closed", f"{E_CROSS} Closed.", color=BRIGHT_RED), view=None)

def lim_of(c, ev): return tuple(c.get("an_lim2", {}).get(ev) or EVENT_LIMS.get(ev, (15, 50)))

def betrayal_limit_embed(ctx):
    c = cfg(ctx.guild.id); rows = []
    for ev in EVENT_NAMES[:14]:
        m, h = lim_of(c, ev)
        rows.append(f"{E_ARR} `{ev:<15}` » `{m:<2}/m` | `{h}/h`")
    desc = "Select the filters below to configure trust limits.\n( `/m` = Per Minute | `/h` = Per Hour )\n\n" + "\n".join(rows)
    return fancy(ctx, "Betrayal Guard Limits", desc, footer_extra=f"Requested by {ctx.author.display_name}")

class BetrayalLimitModal(discord.ui.Modal):
    def __init__(self, ctx, ev, parent_view):
        super().__init__(title=f"Configure: {ev}"[:45]); self.ctx, self.ev, self.pv = ctx, ev, parent_view
        m, h = lim_of(cfg(ctx.guild.id), ev)
        self.m = discord.ui.TextInput(label="Per Minute Limit (/m)", default=str(m), max_length=3)
        self.h = discord.ui.TextInput(label="Per Hour Limit (/h)", default=str(h), max_length=4)
        self.add_item(self.m); self.add_item(self.h)
    async def on_submit(self, inter):
        try: m, h = max(1, int(self.m.value)), max(1, int(self.h.value))
        except Exception: return await inter.response.send_message(f"{E_CROSS} Invalid numbers.", ephemeral=True)
        cfg(self.ctx.guild.id).setdefault("an_lim2", {})[self.ev] = [m, h]; save()
        await inter.response.edit_message(embed=betrayal_limit_embed(self.ctx), view=self.pv)

class BetrayalLimitView(discord.ui.View):
    def __init__(self, ctx):
        super().__init__(timeout=240); self.ctx = ctx
        opts = [discord.SelectOption(label=ev, value=ev) for ev in EVENT_NAMES[:14]]
        sel = discord.ui.Select(placeholder="Select a Filter to configure", min_values=1, max_values=1, options=opts, row=0)
        sel.callback = self.on_sel; self.sel = sel; self.add_item(sel)
        b_def = discord.ui.Button(label="Set Default", emoji="🗑️", style=discord.ButtonStyle.danger, row=1)
        b_exp = discord.ui.Button(label="Explain", emoji="❔", style=discord.ButtonStyle.secondary, row=1)
        b_save = discord.ui.Button(label="Save", style=discord.ButtonStyle.success, row=1)
        b_def.callback = self.on_def; b_exp.callback = self.on_exp; b_save.callback = self.on_save
        for b in (b_def, b_exp, b_save): self.add_item(b)
    async def interaction_check(self, inter): return inter.user.id == self.ctx.author.id
    async def on_sel(self, inter): await inter.response.send_modal(BetrayalLimitModal(self.ctx, self.sel.values[0], self))
    async def on_def(self, inter):
        cfg(self.ctx.guild.id)["an_lim2"] = {}; save()
        await inter.response.edit_message(embed=betrayal_limit_embed(self.ctx), view=self)
    async def on_exp(self, inter):
        await inter.response.send_message(f"**Betrayal Guard Explanation:**\n{E_ARR} `/m` = Max actions allowed in 60 seconds.\n{E_ARR} `/h` = Max actions in 60 minutes before containment.", ephemeral=True)
    async def on_save(self, inter):
        save(); await inter.response.edit_message(embed=betrayal_limit_embed(self.ctx), view=None)

@G("antinuke", aliases=["an"])
@owner_only()
async def antinuke(ctx):
    await ctx.reply(embed=an_filter_panel_embed(ctx), view=AntinukeFilterToggleView(ctx), mention_author=False)

@S(antinuke, "events", aliases=["list", "show32"])
@owner_only()
async def an_events_cmd(ctx):
    lines = [f"{E_DOT} **{name}** (`{EVENT_KEYS[name]}`)" for name in EVENT_NAMES]
    await paginate(ctx, f"Protected Events [32/32 Active]", lines, per=12)

@S(antinuke, "limit", aliases=["limits", "betrayal"])
@owner_only()
async def an_lim_cmd(ctx):
    await ctx.reply(embed=betrayal_limit_embed(ctx), view=BetrayalLimitView(ctx), mention_author=False)

@S(antinuke, "setup", aliases=["wizard", "hub", "enable", "status", "config"])
@owner_only()
async def an_setup_cmd(ctx):
    cfg(ctx.guild.id)["enabled"] = True; save()
    await ctx.reply(embed=hub_embed(ctx.guild), view=SuiteHubView(ctx.author.id, ctx.guild), mention_author=False)

@S(antinuke, "punishment", aliases=["punish"])
@owner_only()
async def an_punish_cmd(ctx, action: str = None):
    c = cfg(ctx.guild.id)
    if action and action.lower() in ("ban", "kick", "quarantine", "strip_roles"):
        c["punishment"] = action.lower(); save()
        return await send(ctx, "Antinuke Punishment Action", f"{E_ARR} Punishment updated to `{action.lower()}`.", color=BRIGHT_GREEN)
    
    current_action = c.get("punishment", "ban").title()
    desc = (
        f"**Current Action:** {current_action}\n\n"
        "**Available Actions:**\n"
        "• `ban` — Instantly ban unauthorized violators\n"
        "• `kick` — Fast-kick unauthorized violators\n"
        "• `quarantine` — Strip roles & isolate in quarantine\n"
        "• `strip_roles` — Strip all dangerous admin roles"
    )
    await send(ctx, "Antinuke Punishment Action", desc)

@G("wallrole", aliases=["wr"])
@owner_only()
async def wallrole_grp(ctx):
    s = sec_cfg(ctx.guild)["wallrole"]; r = ctx.guild.get_role(s.get("role")) if s.get("role") else None
    desc = f"**__Protection Status:__** {'✅ Active' if s.get('on') else '❌ Disabled'}\n**__Wall Role:__** {r.mention if r else '`Not Set`'}"
    await send(ctx, "🛡️ Wall Role Configuration", desc)

@G("antiraid", aliases=["raid"])
@owner_only()
async def antiraid_grp(ctx):
    s = sec_cfg(ctx.guild)["antiraid"]
    desc = f"**__Protection Status:__** {'✅ Active' if s.get('on') else '❌ Disabled'}\n**__Burst Threshold:__** `{s.get('count', 5)} joins / {s.get('window', 8)}s`\n**__Containment Action:__** `{s.get('action', 'KICK')}`"
    await send(ctx, "🛡️ Anti-Raid & Token Shield Settings", desc)

@G("antibetray", aliases=["ab"])
@owner_only()
async def antibetray_grp(ctx):
    desc = f"**__System Status:__** ✅ Active\n\n• Max Bans / Min: `3`\n• Max Kicks / Min: `3`\n• Max Channel Creates / Min: `5`\n• Max Channel Deletes / Min: `3`"
    await send(ctx, "🛡️ Anti-Betray Live Protection Status", desc)

@G("panicmode", aliases=["panic"])
@owner_only()
async def panic_grp(ctx): await ctx.invoke(pm_show)
@S(panic_grp, "show", aliases=["status", "stats", "config"])
@owner_only()
async def pm_show(ctx):
    d = sec_cfg(ctx.guild)["panic"]; g = ctx.guild
    desc = f"• **State:** 🟢 STANDBY (NORMAL)\n• **Violation Punishment:** `{d.get('punish', 'KICK')}`"
    await send(ctx, "🛡️ Panic Mode Status", desc, thumb=(g.icon.url if g.icon else None))

@G("setuplock", aliases=["sl"])
@owner_only()
async def setuplock_grp(ctx):
    c = cfg(ctx.guild.id)
    await send(ctx, "🛡️ Setup Lock Protocol", f"**__Global Setup Lock :__** {'✅ Enabled' if c.get('setuplock') else '❌ Disabled'}")

def fake_perm_role_embed(ctx, role: discord.Role, total_roles=1, page_num=1):
    granted = cfg(ctx.guild.id).setdefault("fake_perms", {}).get(str(role.id), [])
    lines = [f"{ON_TOG if k in granted else OFF_TOG} `{lbl}`" for k, lbl in FAKE_PERMS_LIST]
    lines.append(f"\n{E_ARR} **Role :** {role.mention}")
    return fancy(ctx, f"Fake Permission Roles [{total_roles}]", "\n".join(lines), footer_extra=f"Page {page_num}/{total_roles} | Requested by {ctx.author.display_name}")

class FakePermManageView(discord.ui.View):
    def __init__(self, ctx, role: discord.Role):
        super().__init__(timeout=240); self.ctx, self.role = ctx, role; self._build()
    def _build(self):
        self.clear_items()
        granted = cfg(self.ctx.guild.id).setdefault("fake_perms", {}).get(str(self.role.id), [])
        opts = [discord.SelectOption(label=lbl, value=k, default=(k in granted)) for k, lbl in FAKE_PERMS_LIST]
        sel = discord.ui.Select(placeholder="Select Fake Permissions to grant...", min_values=0, max_values=len(opts), options=opts, row=0)
        sel.callback = self.on_sel; self.sel = sel; self.add_item(sel)
    async def interaction_check(self, inter): return inter.user.id == self.ctx.author.id
    async def on_sel(self, inter):
        await inter.response.defer(); fp = cfg(self.ctx.guild.id).setdefault("fake_perms", {})
        if self.sel.values: fp[str(self.role.id)] = list(self.sel.values)
        else: fp.pop(str(self.role.id), None)
        save(); self._build(); await inter.edit_original_response(embed=fake_perm_role_embed(self.ctx, self.role), view=self)

@G("permissions", aliases=["permission", "fakeperm", "fp"])
@owner_only()
async def permissions_grp(ctx, role: discord.Role = None):
    if role: return await ctx.invoke(fp_manage, role=role)
    await send_usage(ctx, "permissions manage <role>", "Grant or revoke fake bot permissions for a role.", "grant, list, revoke, resetall")

@S(permissions_grp, "manage", aliases=["grant", "add"])
@owner_only()
async def fp_manage(ctx, role: discord.Role = None):
    if not role: return await send_usage(ctx, "permissions grant <role>", "Open interactive Fake Permission selector for a role.")
    await ctx.reply(embed=fake_perm_role_embed(ctx, role), view=FakePermManageView(ctx, role), mention_author=False)

def am_master_embed(g):
    am = am_cfg(g); fl = am["filters"]
    lines = [f"{E_ARR} **{n}** → Punishment: `{d.get('punish', 'Auto Mute') if d.get('on', True) else 'Disabled'}` | Heat: `{d.get('heat', '10')}`" for n, d in fl.items()]
    return fancy(None, "Automod Master Settings", "\n".join(lines))

@G("automod", aliases=["am"])
@perm("manage_guild", "Manage Server")
async def automod_grp(ctx):
    msg_parts = ctx.message.content.split()
    sub = msg_parts[1] if len(msg_parts) > 1 else ""
    if sub.lower() in ("enable", "on"):
        am = am_cfg(ctx.guild); am["enabled"] = True
        for k in am["filters"]: am["filters"][k]["on"] = True
        save(); return await send(ctx, "Automod Enabled", f"{E_ARR} All Automod filters active.", color=BRIGHT_GREEN)
    elif sub.lower() in ("disable", "off"):
        am_cfg(ctx.guild)["enabled"] = False; save(); return await send(ctx, "Automod Disabled", f"{E_ARR} Automod paused.", color=BRIGHT_RED)
    elif sub.lower() in ("config", "settings"):
        return await send(ctx, "Engine Calibration", "• Spam: `5 msgs/10s`\n• Caps: `70%`\n• Emoji: `10 emojis`\n• Mention: `5 mentions`")
    elif sub.lower() == "roguedemote":
        action = msg_parts[2] if len(msg_parts) > 2 else "status"
        c = cfg(ctx.guild.id)
        if action == "enable": c["roguedemote"] = True; save(); return await send(ctx, "Rogue Admin Demotion", f"{E_TICK} Enabled rogue admin containment.", color=BRIGHT_GREEN)
        elif action == "disable": c["roguedemote"] = False; save(); return await send(ctx, "Rogue Admin Demotion", f"{E_CROSS} Disabled rogue admin containment.", color=BRIGHT_RED)
        return await send(ctx, "Rogue Admin Demotion Protocol", f"**__Current Status :__** {'✅ Enabled' if c.get('roguedemote') else '❌ Disabled'}")
    await ctx.reply(embed=am_master_embed(ctx.guild), mention_author=False)

@G("ignore")
@perm("manage_guild", "Manage Server")
async def ignore_grp(ctx): await send_usage(ctx, "ignore channel add <channel>", "Configure ignored channels.")
@S(ignore_grp, "channel")
@perm("manage_guild", "Manage Server")
async def ig_channel(ctx, action: str = None, ch: discord.TextChannel = None):
    ig = cfg(ctx.guild.id)["ignore"]["channels"]
    if action == "add" and ch:
        if ch.id not in ig: ig.append(ch.id); save()
        return await send(ctx, "Ignore Channel Added", f"{E_ARR} Channel {ch.mention} added.", color=BRIGHT_GREEN)
    if action in ("remove", "rm") and ch:
        if ch.id in ig: ig.remove(ch.id); save()
        return await send(ctx, "Ignore Channel Removed", f"{E_ARR} Channel {ch.mention} removed.", color=BRIGHT_GREEN)
    await send_usage(ctx, "ignore channel add <channel>", "Add ignored channel.")

@G("autorole", aliases=["arole"])
@perm("manage_guild", "Manage Server")
async def autorole_grp(ctx): await send_usage(ctx, "autorole humans add <role>", "Configure autoroles.")
@S(autorole_grp, "humans", aliases=["human"])
@perm("manage_guild", "Manage Server")
async def ar_humans(ctx, action: str = None, role: discord.Role = None):
    ar = cfg(ctx.guild.id).setdefault("autoroles", [])
    if action == "add" and role:
        if dangerous(role): return await send(ctx, "", f"❌ {role.mention} has dangerous permissions.", color=BRIGHT_RED)
        if role.id not in ar: ar.append(role.id); save()
        return await send(ctx, "Human Autorole Added", f"{E_ARR} Added {role.mention}.", color=BRIGHT_GREEN)
    await send_usage(ctx, "autorole humans add <role>", "Add human autorole.")

@G("autoresponder", aliases=["ar"])
@perm("manage_guild", "Manage Server")
async def ar_grp(ctx): await send_usage(ctx, "autoresponder add <trigger> <response>", "Add autoresponder.")
@S(ar_grp, "add", aliases=["create"])
@perm("manage_guild", "Manage Server")
async def ar_add_cmd(ctx, trigger: str = None, *, response: str = None):
    if not trigger or not response: return await send_usage(ctx, "autoresponder add <trigger> <response>", "Add autoresponder.")
    cfg(ctx.guild.id).setdefault("autoresponders", {})[trigger.lower()] = response; save()
    await send(ctx, "Autoresponder Added", f"{E_ARR} Trigger added.", color=BRIGHT_GREEN)

@G("sticky")
@perm("manage_messages", "Manage Messages")
async def sticky_grp(ctx): await send_usage(ctx, "sticky add <content>", "Add sticky message.")
@S(sticky_grp, "add", aliases=["set", "create"])
@perm("manage_messages", "Manage Messages")
async def sticky_add(ctx, *, content: str = None):
    if not content: return await send_usage(ctx, "sticky add <content>", "Add sticky.")
    cfg(ctx.guild.id).setdefault("sticky", {})[str(ctx.channel.id)] = content; save()
    await send(ctx, "Sticky Message Set", f"{E_ARR} Sticky enabled.", color=BRIGHT_GREEN)

@G("reactionrole", aliases=["rr"])
@perm("manage_roles", "Manage Roles")
async def rr_grp(ctx): await send_usage(ctx, "reactionrole add <message> <emoji> <role>", "Add reaction role.")
@S(rr_grp, "add")
@perm("manage_roles", "Manage Roles")
async def rr_add(ctx, message_id: int = None, emoji: str = None, role: discord.Role = None):
    if not message_id or not emoji or not role: return await send_usage(ctx, "reactionrole add <message> <emoji> <role>", "Add reaction role.")
    cfg(ctx.guild.id).setdefault("reactionroles", {}).setdefault(str(message_id), {})[emoji] = role.id; save()
    await send(ctx, "Reaction Role Added", f"{E_ARR} Bound {emoji} → {role.mention}.", color=BRIGHT_GREEN)

@G("vcrole")
@perm("manage_roles", "Manage Roles")
async def vcrole_grp(ctx):
    rid = cfg(ctx.guild.id).get("vcrole"); r = ctx.guild.get_role(rid) if rid else None
    await send(ctx, "📑 VC Role Config", f"**__Status :__** {'✅' if r else '❌'}\n**__VC Role :__** {r.mention if r else '`Not Set`'}")

@G("voice", aliases=["vc"])
@perm("mute_members", "Voice Moderation")
async def voice_grp(ctx): await send_usage(ctx, "voice kick <user>", "Voice moderation.")
@S(voice_grp, "kick", aliases=["k"])
@perm("mute_members", "Voice Moderation")
async def vc_kick(ctx, m: discord.Member = None):
    if not m or not m.voice: return await send(ctx, "", f"❌ Target not in voice channel.", color=BRIGHT_RED)
    await m.move_to(None); await send(ctx, "Voice Kick", f"{E_ARR} Disconnected from voice.", color=BRIGHT_GREEN)

@G("greet", aliases=["welcome"])
@perm("manage_guild", "Manage Server")
async def greet_grp(ctx): await send_usage(ctx, "greet enable <name>", "Configure welcome.")
@S(greet_grp, "enable")
@perm("manage_guild", "Manage Server")
async def gr_en(ctx, name: str = None):
    if not name: return await send_usage(ctx, "greet enable <name>", "Enable welcome.")
    cfg(ctx.guild.id)["greet"]["enabled"] = True; save(); await send(ctx, "Greet Enabled", f"{E_ARR} Enabled.", color=BRIGHT_GREEN)

@G("logging", aliases=["logs", "logsetup"])
@perm("manage_guild", "Manage Server")
async def logging_grp(ctx):
    d = log_cfg(ctx.guild); g = ctx.guild; cat_obj = g.get_channel(d.get("cat_id")) if d.get("cat_id") else None
    ch_lines = [f"{E_ARR} `{lbl:<16}` → {f'<#{cid}>' if cid else '`Not Set`'}" for _, lbl, cname in LOG_STREAMS_16 for cid in [d["channels"].get(_)]]
    await send(ctx, "📑 Logging Configuration", f"**__Logging :__** {'✅' if d.get('enabled', True) else '❌'}\n\n" + "\n".join(ch_lines))

@S(logging_grp, "wizard", aliases=["setup", "auto"])
@perm("manage_guild", "Manage Server")
async def logging_wiz(ctx):
    msg = await send(ctx, "📑 Logging Wizard", f"{E_LOAD} Creating 16 logging channels & Webhooks...")
    g = ctx.guild; d = log_cfg(g)
    ow = {g.default_role: discord.PermissionOverwrite(view_channel=False), g.me: discord.PermissionOverwrite(view_channel=True, send_messages=True, manage_webhooks=True, embed_links=True)}
    cat_ch = await g.create_category("💬 | Server Logs", overwrites=ow, reason=R("Logging Wizard"))
    d["cat_id"] = cat_ch.id
    for k, lbl, cname in LOG_STREAMS_16:
        ch = await g.create_text_channel(cname, category=cat_ch, reason=R(f"Logging: {lbl}"))
        d["channels"][k] = ch.id
        try:
            wh = await ch.create_webhook(name=f"{BOT_NAME} — {lbl}", reason=R("Webhook Logging"))
            d["webhooks"][k] = wh.url
        except Exception: pass
    save(); await msg.delete(); await ctx.invoke(logging_grp)

@C("si", aliases=["serverinfo"])
async def si_cmd(ctx):
    g = ctx.guild; bots = sum(1 for m in g.members if m.bot); humans = g.member_count - bots
    await send(ctx, f"{g.name}'s Info", f"🏠 **__About Server__**\n**Name :** {g.name}\n**ID :** {g.id}\n**Members :** {g.member_count}")

@C("ui", aliases=["userinfo", "whois"])
async def ui_cmd(ctx, m: discord.Member = None):
    m = m or ctx.author
    await send(ctx, f"{m.name}'s info", f"🔍 **__General__**\n**Name :** {m.name}\n**ID :** {m.id}", thumb=m.display_avatar.url)

@C("mc", aliases=["membercount"])
async def mc_cmd(ctx):
    g = ctx.guild; bots = sum(1 for m in g.members if m.bot); humans = g.member_count - bots
    await send(ctx, "👥 Member Count", f"Humans: `{humans}`\nBots: `{bots}`\nTotal: `{g.member_count}`")

@C("ban")
@perm("ban_members", "Ban / Unban Users")
async def ban_cmd(ctx, m: discord.Member = None, *, reason: str = "No reason provided"):
    if not m: return await send_usage(ctx, "ban <user> [reason]", "Ban member.")
    await hier(ctx, m); await dm_mod_notice(m, ctx.guild, "banned", ctx.author, reason)
    await ctx.guild.ban(m, reason=R(reason)); await send(ctx, "Member Banned", f"{E_ARR} Banned {m.mention} for `{reason}`.", color=BRIGHT_GREEN)
    await send_webhook_log(ctx.guild, "moderation", "Member Banned", f"{E_ARR} **Target:** {m} (`{m.id}`)\n{E_ARR} **Mod:** {ctx.author.mention}", BRIGHT_RED)

@C("kick")
@perm("kick_members", "Kick Users")
async def kick_cmd(ctx, m: discord.Member = None, *, reason: str = "No reason provided"):
    if not m: return await send_usage(ctx, "kick <user> [reason]", "Kick member.")
    await hier(ctx, m); await dm_mod_notice(m, ctx.guild, "kicked", ctx.author, reason)
    await m.kick(reason=R(reason)); await send(ctx, "Member Kicked", f"{E_ARR} Kicked {m.mention}.", color=BRIGHT_GREEN)

@C("mute", aliases=["timeout"])
@perm("moderate_members", "Timeout / Mute Users")
async def mute_cmd(ctx, m: discord.Member = None, duration: str = "10m", *, reason: str = "No reason provided"):
    if not m: return await send_usage(ctx, "mute <user> [duration]", "Timeout member.")
    await hier(ctx, m); secs = max(10, min(parse_dur(duration), 2419200))
    await m.timeout(timedelta(seconds=secs), reason=R(reason)); await dm_mod_notice(m, ctx.guild, "muted", ctx.author, reason)
    await send(ctx, "Member Muted", f"{E_ARR} Muted {m.mention} for `{duration}`.", color=BRIGHT_GREEN)

HELP_PAGES_DATA = [
    ("security", "Security", E_SEC, "Antinuke, Panicmode, Mainrole, Quarantine...", "**__Security__**\n`antinuke` , `antinuke setup` , `antinuke limit` , `antinuke logging` , `panicmode`"),
    ("permit", "Permit Commands", E_PERMIT, "Extraowner, Trusted, Fake Permissions, Ignore", "**__Extraowner__**\n`extraowner` , `whitelist` , `permissions` , `ignore`"),
    ("automod", "Automod", E_AUTOMOD, "Automod Master Settings & Word Blacklist", "**__Automod__**\n`automod` , `blword` , `setuplock`"),
    ("general", "General", E_GEN, "Serverinfo, Userinfo, Membercount, List Commands", "**__Basic Commands__**\n`si` , `ui` , `mc` , `invite`"),
    ("moderation", "Moderation", E_MOD, "Ban, Kick, Mute, Role, Steal, Voice Moderation", "**__Moderation__**\n`ban` , `kick` , `mute` , `role` , `voice`"),
]

class EphemeralModulePager(discord.ui.View):
    def __init__(self, ctx, start_idx=0):
        super().__init__(timeout=300); self.ctx, self.i = ctx, start_idx; self._build()
    def _embed(self):
        _, title, _, _, body = HELP_PAGES_DATA[self.i]
        return fancy(self.ctx, title, body, footer_extra=f"Powered By {BOT_NAME} Devs")
    def _build(self):
        self.clear_items()
        b_prev = discord.ui.Button(label="<", style=discord.ButtonStyle.secondary, disabled=(self.i==0), row=0)
        b_del = discord.ui.Button(emoji="🗑️", style=discord.ButtonStyle.secondary, row=0)
        b_next = discord.ui.Button(label=">", style=discord.ButtonStyle.secondary, disabled=(self.i>=len(HELP_PAGES_DATA)-1), row=0)
        b_cnt = discord.ui.Button(label=f"{self.i+1}/{len(HELP_PAGES_DATA)}", style=discord.ButtonStyle.secondary, disabled=True, row=0)
        b_prev.callback = self.on_prev; b_del.callback = self.on_del; b_next.callback = self.on_next
        for b in (b_prev, b_del, b_next, b_cnt): self.add_item(b)
        opts = [discord.SelectOption(label=lbl, value=str(idx), emoji=em, description=desc, default=(idx==self.i)) for idx, (_, lbl, em, desc, _) in enumerate(HELP_PAGES_DATA)]
        sel = discord.ui.Select(placeholder="↳ Select a module to see", options=opts, row=1)
        sel.callback = self.on_sel; self.sel = sel; self.add_item(sel)
    async def on_prev(self, inter): self.i = max(0, self.i-1); self._build(); await inter.response.edit_message(embed=self._embed(), view=self)
    async def on_next(self, inter): self.i = min(len(HELP_PAGES_DATA)-1, self.i+1); self._build(); await inter.response.edit_message(embed=self._embed(), view=self)
    async def on_del(self, inter):
        try: await inter.response.edit_message(content="Dismissed.", embed=None, view=None)
        except Exception: pass
    async def on_sel(self, inter): self.i = int(self.sel.values[0]); self._build(); await inter.response.edit_message(embed=self._embed(), view=self)

class MainHelpView(discord.ui.View):
    def __init__(self, ctx):
        super().__init__(timeout=300); self.ctx = ctx
        opts = [discord.SelectOption(label=lbl, value=str(idx), emoji=em, description=desc) for idx, (_, lbl, em, desc, _) in enumerate(HELP_PAGES_DATA)]
        sel = discord.ui.Select(placeholder="Select a category...", options=opts, row=0)
        sel.callback = self.on_sel; self.sel = sel; self.add_item(sel)
    async def on_sel(self, inter):
        idx = int(self.sel.values[0]); sub_view = EphemeralModulePager(self.ctx, idx)
        prev_inter = _USER_EPHEMERAL.get((inter.channel_id, inter.user.id))
        if prev_inter:
            try:
                await inter.response.defer(ephemeral=True)
                await prev_inter.edit_original_response(embed=sub_view._embed(), view=sub_view)
                return
            except Exception: pass
        await inter.response.send_message(embed=sub_view._embed(), view=sub_view, ephemeral=True)
        _USER_EPHEMERAL[(inter.channel_id, inter.user.id)] = inter

if bot.get_command("help"): bot.remove_command("help")
@C("help", aliases=["h", "commands"])
async def help_cmd(ctx):
    p = ctx.clean_prefix if hasattr(ctx, "clean_prefix") else "."
    desc = f"Browse commands and security modules.\n\n{E_DOT} Type `{p}help <module>` for more info."
    await ctx.reply(embed=fancy(ctx, f"{BOT_NAME} Help Center", desc), view=MainHelpView(ctx), mention_author=False)

# Comprehensive Antinuke & Recovery Event Engine (32 Events)
async def _handle_antinuke_event(guild: discord.Guild, action_type: str, executor: discord.abc.User, target_name: str):
    if not guild or not executor or executor.bot: return
    c = cfg(guild.id)
    if not c.get("enabled", True): return
    if is_trusted(guild, executor.id): return
    
    punish_action = c.get("punishment", "ban").lower()
    member = guild.get_member(executor.id)
    
    log_desc = f"{E_ARR} **Executor:** {executor.mention} (`{executor.id}`)\n{E_ARR} **Action:** {action_type}\n{E_ARR} **Target:** {target_name}\n{E_ARR} **Punishment:** {punish_action.upper()}"
    await send_webhook_log(guild, "moderation", f"Antinuke Triggered: {action_type}", log_desc, BRIGHT_RED)
    
    if member:
        try:
            if punish_action == "ban":
                await guild.ban(member, reason=R(f"Antinuke: Unauthorized {action_type}"))
            elif punish_action == "kick":
                await member.kick(reason=R(f"Antinuke: Unauthorized {action_type}"))
            elif punish_action in ("quarantine", "strip_roles"):
                safe_roles = [r for r in member.roles.values() if not dangerous(r) and r != guild.default_role] if hasattr(member.roles, "values") else [r for r in member.roles if not dangerous(r) and r != guild.default_role]
                await member.edit(roles=safe_roles, reason=R(f"Antinuke Containment: {action_type}"))
        except Exception: pass

@bot.event
async def on_guild_channel_delete(channel):
    try:
        async for entry in channel.guild.audit_logs(limit=1, action=discord.AuditLogAction.channel_delete):
            if entry.target.id == channel.id:
                await _handle_antinuke_event(channel.guild, "Channel Delete", entry.user, channel.name)
                if cfg(channel.guild.id).get("autorecovery", True):
                    await channel.guild.create_text_channel(channel.name, category=channel.category, overwrites=channel.overwrites, reason=R("Antinuke Auto-Recovery"))
                break
    except Exception: pass

@bot.event
async def on_guild_role_delete(role):
    try:
        async for entry in role.guild.audit_logs(limit=1, action=discord.AuditLogAction.role_delete):
            if entry.target.id == role.id:
                await _handle_antinuke_event(role.guild, "Role Delete", entry.user, role.name)
                if cfg(role.guild.id).get("autorecovery", True):
                    await role.guild.create_role(name=role.name, permissions=role.permissions, color=role.color, hoist=role.hoist, mentionable=role.mentionable, reason=R("Antinuke Auto-Recovery"))
                break
    except Exception: pass

@bot.event
async def on_member_ban(guild, user):
    try:
        async for entry in guild.audit_logs(limit=1, action=discord.AuditLogAction.ban):
            if entry.target.id == user.id:
                await _handle_antinuke_event(guild, "Ban Protection", entry.user, str(user))
                break
    except Exception: pass

@bot.event
async def on_member_kick(guild, user):
    try:
        async for entry in guild.audit_logs(limit=1, action=discord.AuditLogAction.kick):
            if entry.target.id == user.id:
                await _handle_antinuke_event(guild, "Kick Protection", entry.user, str(user))
                break
    except Exception: pass

@bot.event
async def on_guild_update(before, after):
    if before.name != after.name or before.icon != after.icon:
        try:
            async for entry in after.audit_logs(limit=1, action=discord.AuditLogAction.guild_update):
                await _handle_antinuke_event(after, "Server Update", entry.user, after.name)
                break
        except Exception: pass

@bot.event
async def on_member_join(member):
    g = member.guild; c = cfg(g.id)
    if member.bot:
        try:
            async for entry in g.audit_logs(limit=1, action=discord.AuditLogAction.bot_add):
                if entry.target.id == member.id:
                    if not is_trusted(g, entry.user.id):
                        await _handle_antinuke_event(g, "Bot Add", entry.user, str(member))
                        try: await member.ban(reason=R("Unapproved Bot Add"))
                        except Exception: pass
                    break
        except Exception: pass
    
    r_list = c.get("autoroles_bots", []) if member.bot else c.get("autoroles", [])
    for rid in r_list:
        r = g.get_role(rid)
        if r and not dangerous(r):
            try: await member.add_roles(r, reason=R("Safe Autorole"))
            except Exception: pass
    if not member.bot and c.get("joindm"):
        try: await member.send(c["joindm"])
        except Exception: pass
    await send_webhook_log(g, "join", "Member Joined", f"{E_ARR} {member.mention} (`{member.id}`) joined **{g.name}**.", BRIGHT_GREEN)

@bot.event
async def on_message(message):
    if not message.guild or message.author.bot: return
    c = cfg(message.guild.id); cl = message.content.lower().strip()
    am = am_cfg(message.guild)
    if am.get("enabled", True):
        blw = XS(message.guild, "blwords", list)
        if any(w in cl for w in blw):
            try: await message.delete()
            except Exception: pass
            if c.get("roguedemote", True) and message.author.guild_permissions.administrator and not is_trusted(message.guild, message.author.id):
                try:
                    safe_roles = [r for r in message.author.roles if not dangerous(r) and r != message.guild.default_role]
                    await message.author.edit(roles=safe_roles, reason=R("Rogue Admin Demotion Protocol"))
                except Exception: pass
            return await send_webhook_log(message.guild, "moderation", "Automod Triggered", f"{E_ARR} **User:** {message.author.mention}\n{E_ARR} **Violation:** Blacklisted word detected.", BRIGHT_RED)
            
    if cl in c.get("autoresponders", {}):
        try: await message.channel.send(c["autoresponders"][cl], allowed_mentions=NOPING)
        except Exception: pass
    await bot.process_commands(message)

@bot.event
async def on_ready():
    print(f"✅ {BOT_NAME} is ONLINE as {bot.user} across {len(bot.guilds)} servers!")

if __name__ == "__main__":
    tok = os.environ.get("DISCORD_TOKEN", "").strip()
    if not tok: tok = input("Paste your Discord Bot Token: ").strip()
    bot.run(tok)