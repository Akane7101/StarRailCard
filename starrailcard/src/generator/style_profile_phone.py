import asyncio
from PIL import ImageDraw, Image, ImageChops
from ..tools import pill, git, options

_of = git.ImageCache()

url_character_image = "https://raw.githubusercontent.com/Mar-7th/StarRailRes/refs/heads/master/image/character_portrait/{id}.png"

class HSRProfileCard:
    def __init__(self, profile, lang, img, hide, uid, background) -> None:
        self.profile = profile
        self.lang = lang
        self.img = img
        self.hide = hide
        self.uid = uid
        self.background = background

    async def get_background(self):
        position = (0, -63)
        if self.background:
            banner = await pill.get_download_img(self.background)
            banner = await pill.get_center_size((757, 298), banner)
            position = (0, 0)
        else:
            banner = random.choice([await _of.bg_1, await _of.bg_2, await _of.bg_3, await _of.bg_5])
            banner = await pill.get_center_size((757, 361), banner)

        color = await pill.get_background_colors(banner, 15, common=True, radius=5, quality=800)
        background = Image.new("RGBA", (757, 717), color)
        background_banner = Image.new("RGBA", (757, 717), (0, 0, 0, 0))
        background_banner.alpha_composite(banner, position)
        profile_bg_mask, overlay = await asyncio.gather(_of.profile_bg_mask, _of.overlay_profile)
        background.paste(background_banner, (0, 0), profile_bg_mask.convert("L"))
        background = ImageChops.screen(background, overlay.convert("RGBA"))
        background_shadow = Image.new("RGBA", (757, 717), (0, 0, 0, 150))
        background.alpha_composite(background_shadow)
        return background

    async def create_avatar_info(self):
        background = Image.new("RGBA", (757, 156), (0, 0, 0, 0))
        background_avatar = Image.new("RGBA", (120, 120), (0, 0, 0, 0))
        avatar_url = self.profile.player.avatar.icon if self.profile.player.avatar else None
        avatar_url = avatar_url or "https://api.ambr.top/assets/UI/UI_AvatarIcon_Paimon.png"
        
        avatar, mask_avatar, ab_ac = await asyncio.gather(
            pill.get_download_img(avatar_url, size=(120, 120)),
            _of.avatar_mask, _of.ab_ac
        )
        background_avatar.paste(avatar, (0, 0), mask_avatar.convert("L"))
        background.alpha_composite(background_avatar, (320, 7))
        background.alpha_composite(ab_ac, (274, 23))

        font_15 = await pill.get_font(15)
        d = ImageDraw.Draw(background)

        level = f"{self.lang['lvl']}: {self.profile.player.level}"
        world_level = f"{self.lang['WL']}: {self.profile.player.world_level}"
        uid_text = 'UID: Hide' if self.hide else f"UID: {self.uid}"

        d.text((447, 20), self.profile.player.nickname, font=font_15, fill=(255, 255, 255, 255))
        d.text((447, 44), level, font=font_15, fill=(255, 255, 255, 255))
        d.text((447, 68), world_level, font=font_15, fill=(255, 255, 255, 255))
        d.text((447, 92), uid_text, font=font_15, fill=(255, 255, 255, 255))

        abyss_info = f"{self.profile.player.abyss_floor}-{self.profile.player.abyss_room}"
        x = font_15.getlength(abyss_info)
        d.text((int(268 - x), 88), abyss_info, font=font_15, fill=(255, 255, 255, 255))

        achievements = str(self.profile.player.achievements)
        x = font_15.getlength(achievements)
        d.text((int(268 - x), 35), achievements, font=font_15, fill=(255, 255, 255, 255))

        signature = await pill.create_image_with_text(self.profile.player.signature, 15, max_width=744, color=(255, 255, 255, 255))
        background.alpha_composite(signature, (int(380 - signature.size[0] / 2), 135))
        return background

    async def create_character_card(self, key):
        background = Image.new("RGBA", (180, 263), (0, 0, 0, 0))
        url = self.img.get(str(key.id), url_character_image.format(id=key.id))

        splash, mask, shadow = await asyncio.gather(
            pill.get_download_img(url), _of.art_profile_mask, _of.shadow_art_profile
        )
        splash = await pill.get_center_size((180, 263), splash)
        background.paste(splash, (0, 0), mask.convert("L"))
        background.alpha_composite(shadow)

        stars = await pill.get_stars(key.rarity)
        background.alpha_composite(stars.resize((58, 17)), (25, 235))

        name = await pill.create_image_with_text(key.name, 15, max_width=112, color=(255, 255, 255, 255))
        background.alpha_composite(name, (29, int(219 - name.size[1])))

        font_15 = await pill.get_font(15)
        level = f"{self.lang['lvl']}: {key.level}"
        d = ImageDraw.Draw(background)
        d.text((29, 219), level, font=font_15, fill=(255, 255, 255, 255))
        return background

    async def build_profile(self):
        self.background.alpha_composite(self.avatar, (0, 10))
        x, y = 9, 170
        for i, character in enumerate(self.character_cards):
            self.background.alpha_composite(character, (x, y))
            x += 185
            if i == 3:
                x = 9
                y += 277

    async def start(self):
        self.background, self.avatar = await asyncio.gather(
            self.get_background(), self.create_avatar_info()
        )
        tasks = [self.create_character_card(key) for key in self.profile.characters]
        self.character_cards = await asyncio.gather(*tasks)
        await self.build_profile()
        return self.background
