import discord
from discord.ext import commands

# --- الإعدادات ---
TOKEN = 'MTUwNjU1ODcwMzA4MjUzNzA4Mw.GK9Nvs.H-oTNhJgIOOT4qMssqgsxNcDxOMH2CWFUT3dog'
OWNER_ID = 1272949209917689987
STAFF_ROLE_ID = 1506609144369774663 
TICKET_CHANNEL_ID = 1506311185220374558
VERIFY_CHANNEL_ID = 1507035940189769849
VERIFIED_ROLE_ID = 1507033052818178231

intents = discord.Intents.all()
bot = commands.Bot(command_prefix="!", intents=intents)

user_tickets = {}

class TicketManageView(discord.ui.View):
    def __init__(self): super().__init__(timeout=None)
    
    async def is_authorized(self, interaction):
        return interaction.user.id == OWNER_ID or any(role.id == STAFF_ROLE_ID for role in interaction.user.roles)

    @discord.ui.button(label="استلام التكت 🛠️", style=discord.ButtonStyle.primary, custom_id="persistent_view:claim")
    async def claim(self, interaction: discord.Interaction, button: discord.ui.Button):
        if not await self.is_authorized(interaction):
            return await interaction.response.send_message("❌ للإدارة فقط!", ephemeral=True)
        await interaction.response.send_message(f"✅ تم استلام التكت بواسطة {interaction.user.mention}")

    @discord.ui.button(label="إغلاق التكت 🔒", style=discord.ButtonStyle.danger, custom_id="persistent_view:close")
    async def close(self, interaction: discord.Interaction, button: discord.ui.Button):
        if not await self.is_authorized(interaction):
            return await interaction.response.send_message("❌ للإدارة فقط!", ephemeral=True)
        await interaction.channel.delete()

class TicketSelect(discord.ui.Select):
    def __init__(self):
        super().__init__(placeholder="اختر نوع تذكرتك...", custom_id="persistent_view:select", options=[
            discord.SelectOption(label="دعم فني", value="دعم فني", emoji="⚙️"),
            discord.SelectOption(label="شكوى", value="شكوى", emoji="⚠️"),
            discord.SelectOption(label="استفسار", value="استفسار", emoji="❓")])

    async def callback(self, interaction: discord.Interaction):
        user_id = interaction.user.id
        user_tickets[user_id] = user_tickets.get(user_id, 0) + 1
        
        if user_tickets[user_id] > 4:
            try: await interaction.user.send("⚠️ تم طردك بسبب سبام التذاكر.")
            except: pass
            await interaction.user.kick(reason="سبام تذاكر")
            return await interaction.response.send_message("🚨 تم طرد العضو بسبب السبام!", ephemeral=True)

        overwrites = {interaction.guild.default_role: discord.PermissionOverwrite(read_messages=False),
                      interaction.user: discord.PermissionOverwrite(read_messages=True, send_messages=True),
                      interaction.guild.get_role(STAFF_ROLE_ID): discord.PermissionOverwrite(read_messages=True, send_messages=True)}
        
        channel = await interaction.guild.create_text_channel(f"ticket-{interaction.user.name}", overwrites=overwrites)
        
        embed = discord.Embed(
            title=f"🎫 تذكرة جديدة | {self.values[0]}",
            description=f"أهلاً {interaction.user.mention}، سيقوم أحد أعضاء الإدارة بالرد عليك قريباً.\nيرجى وضع استفسارك أو شكواك هنا.",
            color=0x3498db
        )
        embed.set_footer(text="Xed Community | نظام التذاكر")
        
        staff_role = interaction.guild.get_role(STAFF_ROLE_ID)
        await channel.send(content=f"{staff_role.mention if staff_role else '@Staff'}", embed=embed, view=TicketManageView())
        await interaction.response.send_message(f"✅ تم فتح التكت: {channel.mention}", ephemeral=True)

class TicketView(discord.ui.View):
    def __init__(self): super().__init__(timeout=None); self.add_item(TicketSelect())

class VerifyView(discord.ui.View):
    def __init__(self): super().__init__(timeout=None)
    @discord.ui.button(label="✅ اضغط للتوثيق", style=discord.ButtonStyle.success, custom_id="persistent_view:verify")
    async def verify(self, interaction: discord.Interaction, button: discord.ui.Button):
        role = interaction.guild.get_role(VERIFIED_ROLE_ID)
        if role: await interaction.user.add_roles(role)
        await interaction.response.send_message("تم التوثيق بنجاح! 🎉", ephemeral=True)

@bot.event
async def on_ready():
    bot.add_view(TicketView()); bot.add_view(TicketManageView()); bot.add_view(VerifyView())
    print("🚀 نظام التكت والتوثيق المحصن يعمل الآن!")

@bot.command()
@commands.has_permissions(administrator=True)
async def setup_all(ctx):
    if ctx.author.id != OWNER_ID: return await ctx.send("❌ للأونر فقط.")
    t_ch = ctx.guild.get_channel(TICKET_CHANNEL_ID)
    v_ch = ctx.guild.get_channel(VERIFY_CHANNEL_ID)
    if t_ch: await t_ch.send("🎫 **مركز الدعم:**", view=TicketView())
    if v_ch: await v_ch.send("✅ **للتوثيق:**", view=VerifyView())
    await ctx.send("✅ تم توزيع الأنظمة بالكامل!")

bot.run('MTUwNjU1ODcwMzA4MjUzNzA4Mw.Guci9S.eVkdKgvliBNDgx5dtYL6fC0ehsU4IRqLsz2GBI')
