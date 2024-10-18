# Copyright 2024 DEViantUa <t.me/deviant_ua>
# All rights reserved.

import asyncio
import random
from PIL import ImageDraw, Image
from ..tools import pill, git, options

_of = git.ImageCache()

class Create:
    def __init__(self, profile, lang, img, hide, uid, background, remove_logo) -> None:
        self.remove_logo = remove_logo
        self.profile = profile
        self.lang = lang
        self.img = img
        self.hide = hide
        self.uid = uid
        self.background = background
    
    async def create_background(self):
        self.background_profile = Image.new("RGBA", (828, 1078), (0, 0, 0, 0))
        
        mask, frame = await asyncio.gather(_of.maska_prof_bg, _of.menu)
        if self.background is None:
            background_image = random.choice([await _of.bg_1, await _of.bg_2, await _of.bg_3, await _of.bg_5])
            background_shadow = Image.new("RGBA", (828, 1078), (0, 0, 0, 100))
        else:
            background_image = await pill.get_download_img(self.background)
            background_image = await pill.get_center_size((828, 1078), background_image)
            background_shadow = Image.new("RGBA", (828, 1078), (0, 0, 0, 150))
        
        background_image = background_image.convert("RGBA")
        background_image.alpha_composite(background_shadow)
        self.background_profile.paste(background_image, (0, 0), mask.convert("L"))
        self.background_profile.alpha_composite(frame)

    async def create_character(self, key):
        if key.rarity == 5:
            character_profile = await _of.avatar_five
        else:
            character_profile = await _of.avatar_four
        
        character_profile = character_profile.copy()
        
        if self.img is not None and str(key.id) in self.img:
            url_id = self.img[str(key.id)]
        else:
            url_id = f'https://raw.githubusercontent.com/Mar-7th/StarRailRes/refs/heads/master/image/character_portrait/{key.id}.png'
        
        splash, mask = await asyncio.gather(pill.get_download_img(url_id), _of.maska_character)
        splash = await pill.get_center_size((109, 109), splash)
        character_profile.paste(splash, (16, 28), mask.convert("L"))
        name = await pill.create_image_with_text(key.name, 16, max_width=123, color=(255, 255, 255, 255))
        
        character_profile.alpha_composite(name, (136, int(49 - name.size[1] / 2)))

        max_level = options.max_lvl(key.promotion)
        level = f"{self.lang.lvl}: {key.level}/{max_level}"
        
        element_icon = await pill.get_download_img(key.element.icon, size=(28, 28))
        path_icon = await pill.get_download_img(key.path.icon, size=(28, 28))
        
        character_profile.alpha_composite(path_icon, (263, 28))
        character_profile.alpha_composite(element_icon, (293, 28))
        
        d = ImageDraw.Draw(character_profile)
        d.text((19, 7), level, font=self.font_character, fill=(255, 255, 255, 255))

        if key.light_cone is not None:
            icon = await pill.get_download_img(key.light_cone.icon, size=(66, 66))
            character_profile.alpha_composite(icon, (136, 70))
            d.text((201, 95), f"{self.lang.lvl}: {key.light_cone.level}/{options.max_lvl(key.light_cone.promotion)}", 
                   font=self.font_character, fill=(255, 255, 255, 255))
            stars = await options.get_stars(key.light_cone.rarity)
            character_profile.alpha_composite(stars.resize((85, 18)), (224, 114))
            
            background = await _of.light_cone_ups
            background = background.copy()
            
            d = ImageDraw.Draw(background)
            font_12 = await pill.get_font(12)
            up = options.ups(key.light_cone.rank)
            x = int(font_12.getlength(str(up)) / 2)
            d.text((10 - x, 4), up, font=font_12, fill=(255, 217, 144, 255))
            
            character_profile.alpha_composite(background.resize((17, 17)), (202, 114))
        
        return character_profile

    async def get_characters(self):
        tasks = [self.create_character(key) for key in self.profile.characters]
        self.characters = await asyncio.gather(*tasks)

    async def create_avatar(self):
        self.background_profile_avatar = Image.new("RGBA", (625, 254), (0, 0, 0, 0))
        avatar_url = self.profile.player.avatar.icon
        
        avatar, font_20, desc_frame = await asyncio.gather(
            pill.get_download_img(avatar_url, size=(134, 134)), 
            pill.get_font(18), 
            _of.desc_frame
        )
        
        self.background_profile_avatar.alpha_composite(avatar)
        
        d = ImageDraw.Draw(self.background_profile_avatar)
        
        level = f"{self.lang.lvl}: {self.profile.player.level}"
        world_level = f"{self.lang.WL}: {self.profile.player.world_level}"
        uid_text = 'UID: Hide' if self.hide else f"UID: {self.uid}"
        
        d.text((134, 4), self.profile.player.nickname, font=font_20, fill=(255, 255, 255, 255))
        d.text((134, 41), level, font=font_20, fill=(255, 255, 255, 255))
        d.text((134, 78), uid_text, font=font_20, fill=(255, 255, 255, 255))
        d.text((134, 115), world_level, font=font_20, fill=(255, 255, 255, 255))
        
        signature = await pill.create_image_with_text(
            self.profile.player.signature, 18, max_width=606, color=(255, 255, 255, 255)
        )
        self.background_profile_avatar.alpha_composite(desc_frame, (0, 163))
        self.background_profile_avatar.alpha_composite(
            signature, (int(320 - signature.size[0] / 2), int(199 - signature.size[1] / 2))
        )

    async def build(self):
        self.background_profile.alpha_composite(self.background_profile_avatar, (29, 53))

        x, y = 0, 407
        for i, character in enumerate(self.characters):
            self.background_profile.alpha_composite(character, (x, y))
            y += 155
            if i == 3:
                x = 338
                y = 407
        
        if not self.remove_logo:
            logo = await _of.LOGO_GIT_INV
            self.background_profile.alpha_composite(logo, (752, 0))

    async def start(self):
        _of.set_mapping(3)
        self.font_character = await pill.get_font(13)
        
        await asyncio.gather(self.create_background(), self.get_characters(), self.create_avatar())
        await self.build()        
        
        return self.background_profile
