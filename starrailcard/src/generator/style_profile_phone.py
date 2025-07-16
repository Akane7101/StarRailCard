# Copyright 2024 DEViantUa <t.me/deviant_ua>
# All rights reserved.

import asyncio
import random
from PIL import ImageDraw, Image, ImageChops
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
       
        self.DEFAULT_AVATAR = "https://i.pinimg.com/1200x/de/7b/26/de7b262604b6a35f5ddd1f670672cbb9.jpg"
    
    async def create_background(self):
        self.background_profile = Image.new("RGBA", (828, 1078), (0,0,0,0))
        
        mask, frame = await asyncio.gather(_of.maska_prof_bg, _of.menu)
        if self.background is None:
            background_image = random.choice([await _of.bg_1, await _of.bg_2, await _of.bg_3, await _of.bg_5])
            background_shadow = Image.new("RGBA", (828, 1078), (0,0,0,100))
        else:
            try:
                background_image = await pill.get_download_img(self.background)
                background_image = await pill.get_center_size((828,1078), background_image)
            except Exception as e:
                print(f"Background download failed, using default: {e}")
                background_image = random.choice([await _of.bg_1, await _of.bg_2, await _of.bg_3, await _of.bg_5])
            background_shadow = Image.new("RGBA", (828, 1078), (0,0,0,150))
        
        background_image = background_image.convert("RGBA")
        background_image.alpha_composite(background_shadow)
        self.background_profile.paste(background_image, (0,0), mask.convert("L"))
        self.background_profile.alpha_composite(frame)

    async def get_character_icon(self, key):
        """Helper function to safely get character icon with fallback"""
        if self.img is not None and str(key.id) in self.img:
            url_id = self.img[str(key.id)]
        else:
            url_id = f'https://raw.githubusercontent.com/Mar-7th/StarRailRes/master/icon/avatar/{key.id}.png'
        
        try:
            splash = await pill.get_download_img(url_id)
            return splash
        except Exception as e:
            print(f"Failed to load character {key.id} image: {e}")
            try:
                return await _of.default_character
            except:
                placeholder = Image.new("RGBA", (109, 109), (100, 100, 100, 255))
                draw = ImageDraw.Draw(placeholder)
                draw.text((10, 40), "No Image", fill=(255, 255, 255, 255))
                return placeholder

    async def create_charter(self, key):
        if key.rarity == 5:
            charter_profile = await _of.avatar_five
        else:
            charter_profile = await _of.avatar_four
        
        charter_profile = charter_profile.copy()
        
        try:
            splash, mask = await asyncio.gather(
                self.get_character_icon(key),
                _of.maska_character
            )
            splash = await pill.get_center_size((109,109), splash)
            charter_profile.paste(splash, (16,28), mask.convert("L"))
        except Exception as e:
            print(f"Error processing character {key.id}: {e}")
        
        try:
            name = await pill.create_image_with_text(key.name, 16, max_width=123, color=(255, 255, 255, 255))
            charter_profile.alpha_composite(name, (136, int(49-name.size[1]/2)))
        except:
            pass

        max_level = options.max_lvl(key.promotion)
        level = f"{self.lang.lvl}: {key.level}/{max_level}"
        
        try:
            element_icon = await pill.get_download_img(key.element.icon, size=(28,28))
            path_icon = await pill.get_download_img(key.path.icon, size=(28,28))
            charter_profile.alpha_composite(path_icon, (263,28))
            charter_profile.alpha_composite(element_icon, (293,28))
        except:
            pass
        
        d = ImageDraw.Draw(charter_profile)
        d.text((19,7), level, font=self.font_charter, fill=(255,255,255,255))
        
        if key.light_cone is not None:
            try:
                icon = await pill.get_download_img(key.light_cone.icon, size=(66,66))
                charter_profile.alpha_composite(icon, (136,70))
                d.text((201,95), f"{self.lang.lvl}: {key.light_cone.level}/{options.max_lvl(key.light_cone.promotion)}", 
                      font=self.font_charter, fill=(255, 255, 255, 255))
                
                starts = await options.get_stars(key.light_cone.rarity)
                charter_profile.alpha_composite(starts.resize((85,18)), (224,114))
                
                background = await _of.light_cone_ups
                background = background.copy()
                d = ImageDraw.Draw(background)
                font_12 = await pill.get_font(12)
                up = options.ups(key.light_cone.rank)
                x = int(font_12.getlength(str(up))/2)
                d.text((10-x, 4), up, font=font_12, fill=(255, 217, 144, 255))
                charter_profile.alpha_composite(background.resize((17,17)), (202,114))
            except Exception as e:
                print(f"Error processing light cone: {e}")
            
        return charter_profile
    
    async def get_charter(self):
        task = []
        for key in self.profile.characters:
            task.append(self.create_charter(key))
            
        self.charter = await asyncio.gather(*task)
    
    async def create_avatar(self):
        self.background_profile_avatar = Image.new("RGBA", (625, 254), (0,0,0,0))
        
    
        mask = Image.new("L", (134, 134), 0)
        draw = ImageDraw.Draw(mask)
        draw.ellipse((0, 0, 134, 134), fill=255)
        
        try:
       
            avatar = await pill.get_download_img(self.profile.player.avatar.icon, size=(134,134))
            
           
            avatar_circle = Image.new("RGBA", (134, 134))
            avatar_circle.paste(avatar, (0, 0), mask)
            self.background_profile_avatar.alpha_composite(avatar_circle)
        except Exception as e:
            print(f"Failed to load avatar image, trying default: {e}")
            try:
              
                avatar = await pill.get_download_img(self.DEFAULT_AVATAR, size=(134,134))
                
              
                avatar_circle = Image.new("RGBA", (134, 134))
                avatar_circle.paste(avatar, (0, 0), mask)
                self.background_profile_avatar.alpha_composite(avatar_circle)
            except Exception as e:
                print(f"Failed to load default avatar: {e}")
               
                placeholder = Image.new("RGBA", (134,134), (100,100,100,255))
                draw = ImageDraw.Draw(placeholder)
                draw.ellipse((0, 0, 134, 134), fill=(100,100,100,255))
                draw.text((20,50), "No Avatar", fill=(255,255,255,255))
                placeholder_circle = Image.new("RGBA", (134, 134))
                placeholder_circle.paste(placeholder, (0, 0), mask)
                self.background_profile_avatar.alpha_composite(placeholder_circle)

        try:
            font_20, desc_frame = await asyncio.gather(
                pill.get_font(18),
                _of.desc_frame
            )
            
            d = ImageDraw.Draw(self.background_profile_avatar)
            
            level = f"{self.lang.lvl}: {self.profile.player.level}"
            Wlevel = f"{self.lang.WL}: {self.profile.player.world_level}"
            uid = 'UID: Hide' if self.hide else f"UID: {self.uid}"
            
            d.text((134,4), self.profile.player.nickname, font=font_20, fill=(255,255,255,255))
            d.text((134,41), level, font=font_20, fill=(255,255,255,255))
            d.text((134,78), uid, font=font_20, fill=(255,255,255,255))
            d.text((134,115), Wlevel, font=font_20, fill=(255,255,255,255))
            
            if self.profile.player.signature:
                signature = await pill.create_image_with_text(
                    self.profile.player.signature, 
                    18, 
                    max_width=606, 
                    color=(255, 255, 255, 255)
                )
                self.background_profile_avatar.alpha_composite(desc_frame, (0,163))
                self.background_profile_avatar.alpha_composite(
                    signature, 
                    (int(320-signature.size[0]/2), int(199-signature.size[1]/2))
                )  
        except Exception as e:
            print(f"Error creating avatar text elements: {e}")
    
    async def build(self):
        self.background_profile.alpha_composite(self.background_profile_avatar, (29,53))

        x, y = 0, 407  
        for i, key in enumerate(self.charter):
            if key:
                self.background_profile.alpha_composite(key, (x,y))
            y += 155
            if i == 3:
                x = 338
                y = 407
                
        if not self.remove_logo:
            try:
                logo = await _of.LOGO_GIT_INV
                self.background_profile.alpha_composite(logo, (752,0))
            except Exception as e:
                print(f"Failed to add logo: {e}")
                
    async def start(self):
        _of.set_mapping(3)
        self.font_charter = await pill.get_font(13)
        
        try:
            await asyncio.gather(
                self.create_background(), 
                self.get_charter(), 
                self.create_avatar()
            )
            await self.build()        
        except Exception as e:
            print(f"Error during profile creation: {e}")
            if not hasattr(self, 'background_profile'):
                self.background_profile = Image.new("RGBA", (828, 1078), (0,0,0,255))
                draw = ImageDraw.Draw(self.background_profile)
                draw.text((100,100), "Profile Generation Error", fill=(255,255,255,255))
                draw.text((100,130), str(e), fill=(255,255,255,255))
        
        return self.background_profile
